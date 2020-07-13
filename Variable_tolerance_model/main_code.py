
import layOpt_new
from matplotlib import pyplot as plt 
from matplotlib import rc
rc('font',**{'family':'serif'})
rc('text', usetex=True)

import numpy as np
class Optimal_Building():
    def __init__(self,l_avail,x = [],tolerance=0.1,ca=0.001,overhang=150):
        self.x = x
        self.l_avail = l_avail
        self.tolerance = tolerance
        self.overhang = overhang
        self.ca = ca #cost per unit area

    def optimize_building(self):
        n = len(self.x)
        self.models = ['m']*n
        for i in range(n):
            self.models[i] = layOpt_new.LayOpt(self.l_avail,self.x[i],self.tolerance,self.ca,self.overhang)
            
    
    def print(self):
        self.total_cost = 0.0
        n = len(self.x)
        for j in range(n):
            self.models[j].print()
            self.total_cost += self.models[j].get_total_costs()
            print('\n')

    def get_total_cost(self):
        return self.total_cost




# '''

# exterior =  [['L2100', 'W1200', 'L1250', 'W1200', 'L350', 'L1200', 'W1200']]

# exterior =  [['L2100', 'W1200', 'L1250', 'W1200', 'L350', 'L1200', 'W1200'],
# ['L10600'],
#  ['L1250', 'W1200', 'L1450', 'W600','W600', 'L1750', 'W1200', 'L1250'],
# ['L1850', 'W1200', 'L1150', 'D900', 'L300', 'W1200', 'L550', 'W1200']]


total = [['L2100', 'W1200', 'L1250', 'W1200', 'L350', 'L1200', 'W1200'],
['L10600'],
 ['L1250', 'W1200', 'L1450', 'W600','W600', 'L1750', 'W1200', 'L1250'],
['L1850', 'W1200', 'L1150', 'D900', 'L300', 'W1200', 'L550', 'W1200'],
    ['L2750','D900','L600'],
['L2150'],
['L1800'],
['L2450','D900','L300','D900'],
['L1500'],
['L3600'],
['L1300'],
['L600','D900','D900','L2300'],
['L3320']
]


l_avail = {1:100,2:250, 3:450, 4:700, 5:900} #a dictionary of available wall lengths


# print("Exterior Wall")
# model = Optimal_Building(l_avail,exterior,tolerance=0.00,ca=0.001)
# model.optimize_building()
# model.print()
# print("Total cost of exterior: {0}".format(model.get_total_cost()))

steps = 50
tolerance = np.linspace(0,0.7,steps)
total_cost = []

for i in range(steps):
    model = Optimal_Building(l_avail,total,tolerance=tolerance[i],ca=0.001)
    model.optimize_building()
    model.print()
    total_cost.append(model.get_total_cost())

fig = plt.figure(1,figsize=(20,18))
plt.plot(tolerance,total_cost)
# plt.ylim(30000,60000)
# plt.legend(fontsize=50)
plt.xlabel("Tolerance",fontsize=60)
plt.ylabel("Total cost (\$)", fontsize = 60)
plt.xticks(fontsize=50)
plt.yticks(fontsize=50)
fig.tight_layout()
filename = 'total_cost_sensitivity'
plt.savefig(filename+".png",dpi=600)
# plt.savefig(filename+".pdf",dpi=600)
plt.show()


