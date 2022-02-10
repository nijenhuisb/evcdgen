# EVCDgen - Electric Vehicle Charging Demand generator

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.

# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.



import pandas as pd
import numpy as np

# Function to import the original data and output the 'prepared_dataset'
def importdata():
	## DATA ##
	# (1) Import data
	file = './data/Databestand_ODiN2019.csv'
	df = pd.read_csv(file)
	# df = df.head(500) # For speed
	
	# (2) Prettify the data
	df = df.fillna(0) #make all NaN's 0
	df = df.replace({'#LEEG!':0})
	df = df.drop(['FactorH', 'FactorP', 'FactorV'], axis=1)
	
	df = df.apply(pd.to_numeric, errors='coerce')
	
	df['VertTijd'] = df['VertUur']*60 + df['VertMin']              # Creates 'verplaatsing' leave time in minutes of day
	df['RVertTijd'] = df['RVertUur']*60 + df['RVertMin']           # Creates 'trip' leave time in minutes of day
	
	df['AankTijd'] = df['AankUur']*60 + df['AankMin']              # Creates 'verplaatsing' leave time in minutes of day
	df['RAankTijd'] = df['RAankUur']*60 + df['RAankMin']
	
	data = df
	
	# (3) Remove specialities
	data = data[data['Feestdag'] == 0] # Only keeps non-'feestdag'

	
	# (4) Filter data based on socio-economic characteristics
	# Drop all except 1, 2, and 7
	data.drop(data[data.MaatsPart == 3].index, inplace=True)
	data.drop(data[data.MaatsPart == 4].index, inplace=True)
	data.drop(data[data.MaatsPart == 5].index, inplace=True)
	data.drop(data[data.MaatsPart == 6].index, inplace=True)
	data.drop(data[data.MaatsPart == 8].index, inplace=True)
 	data.drop(data[data.MaatsPart == 9].index, inplace=True)

	# This works much better:
# 	data = df.query('MaatsPart == 1 | MaatsPart == 2 | MaatsPart == 7')

	# 1	Werkzaam 12 tot 30 uur per week
	# 2	Werkzaam 30 uur of meer per week
	# 3	Eigen huishouding
	# 4	Scholier/student
	# 5	Werkloos
	# 6	Arbeidsongeschikt
	# 7	Gepensioneerd/VUT
	# 8	Overig
	# 9	Onbekend

	# (6) Only keep trips with car as driver
	data = data[data['Rvm'] == 1]
	data = data[data['RvmRol'] == 1]

	return data

# Function that takes a dataset with trips + Motief and Doel as input and outputs dataframe with corresponding sessions
def tripsWithMotiveAndGoal(trips, motive, goal):
    outputDf = trips[trips['KMotiefV'] == motive]       # filter for Motive
    outputDf = outputDf[outputDf['Doel'] == goal]      # filter for Goal
    return outputDf

# Find trip characteristics departure, arrival, travel & activity time and output these to a csv.
def findTripCharacteristics(data, name):

	TimeSlotRange = range(0, 288)
	TimeSlotLength = 5

	departureTime = np.floor(data['RVertTijd'] / TimeSlotLength) # divide minutes of day by 5 to get time slot and round down
	travelTime = np.floor(data['RReisduur'] / TimeSlotLength)
	activityTime = np.floor(data['ActDuur'] / TimeSlotLength)
	arrivalTime = np.floor(data['RAankTijd']/ TimeSlotLength)

	pdf_departureTime = departureTime.value_counts().reindex(TimeSlotRange, fill_value=0) / len(departureTime)  # divide by total number of instances to get probabilities for this time slot
	pdf_travelTime = travelTime.value_counts().reindex(TimeSlotRange, fill_value=0) / len(travelTime)
	pdf_activityTime = activityTime.value_counts().reindex(TimeSlotRange, fill_value=0)  / len(activityTime)
	pdf_arrivalTime = arrivalTime.value_counts().reindex(TimeSlotRange, fill_value=0) / len(arrivalTime)

	output = pd.DataFrame()
	output['departure'] = pdf_departureTime
	output['arrival'] = pdf_arrivalTime
	output['travel'] = pdf_travelTime
	output['activity'] = pdf_activityTime

	output.to_csv('./inputs/'+name+'.csv')

	return output

# Creates 'persondays': separate dicts for each unique 
def tripsToPersonDays(data):
 	personDays = {}
 	for opid in data['OPID']:
 		 personDays[opid] = data.loc[data['OPID'] == opid]

 	return personDays

# Separates working days from non working days
def separateWorkingDays(personDays):
	workingDays = {}
	nonWorkingDays = {}

	for key in personDays:
		 motives_per_day = personDays[key]['KMotiefV'].to_frame()  # extract the motives
		 motive_exists = motives_per_day['KMotiefV'].isin([1]).any().any()  # check if the desired motive (1 = a trip from/to work) is in the day
		
		 if motive_exists:  # if yes, this is regarded as a workingDay
 			workingDays[key] = personDays[key]
			 
		 if motive_exists == False:  # if not, this is a nonWorkingDay
 			nonWorkingDays[key] = personDays[key]

	dist_working_nonworking = len(workingDays) / len(personDays)

	workingDaysNonWorkingTrips = pd.concat(workingDays.values())  # Convert from Days to Trips
	nonWorkingDaysTrips = pd.concat(nonWorkingDays.values())

	nonWorkingDaysTrips = nonWorkingDaysTrips[nonWorkingDaysTrips['Rvm'] == 1]  # Filter all nonWorkingDaysTrips by car
	nonWorkingDaysTrips = nonWorkingDaysTrips[nonWorkingDaysTrips['ActDuur'] > 5]  # only take trips with activity > 5 minute
	
	workingDaysNonWorkingTrips = workingDaysNonWorkingTrips[workingDaysNonWorkingTrips['KMotiefV'] != 1]  # Remove all trips with motive 'work', so we are left with 'Leisure' trips
	workingDaysNonWorkingTrips = workingDaysNonWorkingTrips[workingDaysNonWorkingTrips['Rvm'] == 1]  # Filter all workingDaysLeisureTrips by car
	workingDaysNonWorkingTrips = workingDaysNonWorkingTrips[workingDaysNonWorkingTrips['ActDuur'] > 5]  # only take trips with activity > 5 minutes

	return workingDaysNonWorkingTrips, nonWorkingDaysTrips



# This is the prepared dataset
prepared_dataset = importdata()

# Home to work trips
trips_fromHomeToWork = tripsWithMotiveAndGoal(prepared_dataset, 1, 2)
hometowork = findTripCharacteristics(trips_fromHomeToWork, 'hometowork')

# The working time is a special case, since the 'activity time' in the original dataset did not reflect the
# time spent at work in all cases. Now, the working time can be created by running 'workingTime.py'.

# We translate the trips to 'persondays' for the working and retired
persondays_working = tripsToPersonDays(prepared_dataset.query('MaatsPart == 1 | MaatsPart == 2'))
persondays_retired = tripsToPersonDays(prepared_dataset.query('MaatsPart == 7'))


# And split the days into 'Working days' (in which OPID had a work trip) and 'Non working days' for W (workers) and R (retired)
W_non_working_trips_on_working_days, W_trips_on_non_working_days = separateWorkingDays(persondays_working)
W_non_working_trips_on_working_days.to_csv('./inputs/W_non_working_trips_on_working_days.csv')
W_trips_on_non_working_days.to_csv('./inputs/W_trips_on_non_working_days.csv')


R_non_working_trips_on_working_days, R_trips_on_non_working_days = separateWorkingDays(persondays_working)
R_non_working_trips_on_working_days.to_csv('./inputs/R_non_working_trips_on_working_days.csv')
R_trips_on_non_working_days.to_csv('./inputs/R_trips_on_non_working_days.csv')