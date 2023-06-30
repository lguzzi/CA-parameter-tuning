import uproot
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep
import csv
# Or choose one of the experiment styles
hep.style.use(hep.style.CMS)

numAgents = 100
numIterations = 3

effs = []
fakes = []

for i in range(numIterations):
    # only 3 iterations, i.e. 3 output files
    output = uproot.open('output/output'+str(i)+'.root')
    totalSim = np.zeros(numAgents)
    totalRec = np.zeros(numAgents)
    totalAss = np.zeros(numAgents)
    for j in range(numAgents):
        out = output['simpleValidation' + str(j)]['output']
        totalRec[j] = out['rt'].array()[0]
        totalAss[j] = out['at'].array()[0]
        totalSim[j] = out['st'].array()[0]
        
    # print(totalSim, totalAss, totalRec)
    # print('Efficiency ')
    effs.append(totalAss / totalSim)
    # print('Fake rate ')
    fakes.append((totalRec - totalAss) / totalRec)
    output.close()

    import matplotlib.animation as animation

fig, ax = plt.subplots()

def animate(i):
    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    num_agents=3
    s=ax.scatter(fakes[0], effs[0], s=10, label='first iteration')
    ax.set_xlabel(r'fakes $=\frac{(N_{rec}-N_{ass})}{N_{rec}}$')
    ax.set_ylabel(r'eff $=\frac{N_{ass}}{N_{sim}}$')
    s=ax.scatter(fakes[i], effs[i], c="red",s=10)
    ax.legend(loc='best')
# print(f'effs={effs}')

ANIMATE_EFF=False
if ANIMATE_EFF==True:
    ani=animation.FuncAnimation(fig, animate, interval=200, frames=range(numIterations))
    ani.save('gifs/output.gif', writer='pillow')



p1s=[]
p2s=[]
p3s=[]
p4s=[]
for i in range(numIterations):
    p1 = []
    p2 = []
    p3 = []
    p4 = []
    with open("params/parameters"+str(i)+".csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            p1.append(float(row[0]))
            p2.append(float(row[1]))
            p3.append(float(row[2]))
            p4.append(float(row[3]))
    p1s.append(p1)
    p2s.append(p2)
    p3s.append(p3)
    p4s.append(p4)
    
fig, ax = plt.subplots( figsize=(10,10))
Params_names={0:'CAThetaCutBarrel',
              1:'CAThetaCutForward',
2:'dcaCutInnerTriplet',                
3:'dcaCutOuterTriplet'}
def animate(i):
    # fig,ax = plt.subplots(1,2,)
    fig.clear()
    ax = fig.add_subplot(121)
    # ax.set_xlim(0.001,0.1)
    # ax.set_ylim(0.001,0.1)
    s=ax.scatter(p1s[i], p2s[i])
    ax.set_xlabel(Params_names[0])
    ax.set_ylabel(Params_names[1])
    ax = fig.add_subplot(122)
    # ax.set_xlim(0.01,1)
    # ax.set_ylim(0.01,1)
    s=ax.scatter(p3s[i], p4s[i])
    ax.set_xlabel(Params_names[2])
    ax.set_ylabel(Params_names[3])
    plt.tight_layout()

ani=animation.FuncAnimation(fig, animate, interval=200, frames=range(numIterations))
ani.save('gifs/animation.gif', writer='pillow')