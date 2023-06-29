import subprocess
from io import StringIO
import uproot
import numpy as np


#process

# subprocess.run(['cmsRun','reconstruction.py'])


# totalFks = 0

numAgents = 5
output = uproot.open('output.root')

totalSim = np.zeros(5)
totalRec = np.zeros(5)
totalAss = np.zeros(5)
for i in range(numAgents):
    out = output['simpleValidation' + str(i)]['output']
    totalRec[i] = out['rt'].array()[0]
    totalAss[i] = out['at'].array()[0]
    totalSim[i] = out['st'].array()[0]

print(totalSim, totalAss, totalRec)
print('Efficiency ')
print(totalAss / totalSim)
print('Fake rate ')
print((totalRec - totalAss) / totalRec)






