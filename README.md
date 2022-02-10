# EVCDgen - Electric Vehicle Charging Demand generator

This page hosts the tool used for generating EV charging demand patterns based on Dutch mobility data. The work is going to be presented in:

Using mobility data and agent based models to generate future e-mobility charging demand patterns, B. Nijenhuis; S. C. Doumen; J. Hönen; G. Hoogsteen; CIRED22 Workshop, Porto.


## How to use:
The file uses input data from the Dutch Mobility study ODiN 2019 [1]. We cannot redistribute this data directly so you should get your own license via https://doi.org/10.17026/dans-xpv-mwpg.

(1) Get access to the ODiN data and place the datafile in ./data
(2) Run prepareData.py to generate the necessary inputs for the schedule generator
(3) Run chargingProbability.py to generate charging probability curves
(4) Run main.py

[1] Centraal Bureau voor de Statistiek (CBS); Rijkswaterstaat (RWS-WVL) (2020): Onderzoek Onderweg in Nederland - ODiN 2019. DANS. https://doi.org/10.17026/dans-xpv-mwpg
