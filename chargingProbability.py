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



import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def logistic(x, x0, k, L):
    return L/(1+np.exp(-k*(x-x0)))

x = np.arange(start=0, stop=101, step=1)  # an array from 0 to 100 with a step of 1
L = 100  # maximum point of the curve

f_home = logistic(x=x, x0=60, k=-0.2, L=L)
f_work = logistic(x=x, x0=50, k=-0.2, L=L)
f_public = logistic(x=x, x0=40, k=-0.2, L=L)

fig, ax = plt.subplots(figsize=(6,2))
plt.plot(x, f_home, label='Home')
plt.plot(x, f_work, label='Work')
plt.plot(x, f_public, label='Public')

plt.ylabel("Charging probability [-]")
plt.xlabel("SoC [%]")

plt.legend()
plt.grid()
ax.set_xlim(0,100)
ax.set_ylim(0,100)
plt.show()

result = pd.DataFrame()
result['SoC'] = x
result['home'] = f_home
result['work'] = f_work
result['public'] = f_public

result.to_excel('./inputs/charging_probability.xlsx')