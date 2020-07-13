import numpy as np 
import random
import windows
import doors
import math
from pulp import *


inf = 99999
class LayOpt:
    def __init__(self,l_avail,x = [],tolerance=0.1,ca=6,overhang=150, \
    labour_cost=5,material_cost=7,transport_cost=10,size_of_container=2):
        # x = ['L400','D200','W100','D150']
        L = []
        I = []
        W = []
        D = []
        Nn = len(x)
        self.setback_list = []
        self.leftout = []
        for i in range(Nn):
            if x[i][0] == 'L' : # if wall, make adjustments
                string = x[i]
                string = string[1:]
                setback = 0
                # check for previous element
                if(i==0): #check if there is no previous element
                    setback += 0
                else: #element has a previous element
                    if(x[i-1][0] == 'D' or 'W'): #check if the previous element is a door or window
                        setback += overhang
                        
                if (i==(Nn-1)): #check if wall is last element
                    setback += 0
                else:
                    if(x[i+1][0] == 'D' or 'W'): #check if the next element is a door or window
                        setback += overhang
                self.setback_list.append(setback)
                num = int(string) - setback  
                if (num>99):       
                    L.append(num)
                else:
                    self.leftout.append(num)
                
            elif x[i][0] == 'D':
                string = x[i]
                string = string[1:]
                D.append(string)

            elif x[i][0] == 'W':
                string = x[i]
                string = string[1:]
                W.append(string)
        L = list(map(int, L))
        W = list(map(int, W))
        D = list(map(int, D))

        self.l_avail = l_avail
        self.l_avail_list = list(l_avail.values())
        self.n = len(self.l_avail)
        self.L = L #walls
        self.W = W #windows
        self.D = D #doors
        self.nw = len(self.L) #number of walls
        self.tolerance = tolerance
        self.labour_cost = labour_cost
        self.material_cost = material_cost
        self.transport_cost = transport_cost
        self.size_of_container = size_of_container
        self.ca = ca #cost per unit area
        self.minimal_length = self.tolerance * min(self.l_avail)
        if(self.minimal_length > min((self.l_avail).values())): #ensure minimal length is greater than least panel size
            print("Error:Minimal length must be lesser than least panel size")
        
        self.penalties = []
    def get_door_cost(self):
        '''
        Get the cost of the door panels
        '''
        D = self.D
        Nd = len(D)
        self.door_costs = []
        for i in range(Nd):
            model = doors.Door(D[i])
            door_panels = model.get_design()
            panel_areas = [np.prod(i) for i in door_panels]
            total_area = sum(panel_areas)
            total_cost = self.ca *total_area
            self.door_costs.append(total_cost)
        return self.door_costs

    def get_window_cost(self):
        '''
        Get the cost of the window panels
        '''
        W = self.W
        Nw = len(W)
        self.window_costs = []
        for i in range(Nw):
            model = windows.Window(W[i])
            window_panels = model.get_design()
            panel_areas = [np.prod(i) for i in window_panels]
            total_area = sum(panel_areas)
            total_cost = self.ca *total_area
            self.window_costs.append(total_cost)
        return self.window_costs

    def compute_installation_cost(self,l,n):
        labour_cost = ((l*n) * self.labour_cost) / 480
        return labour_cost

    def compute_production_cost(self,l,n):
        production_cost = self.material_cost * l * n
        return production_cost

    def compute_transportation_cost(self,l,n ):
        transportation_cost = (self.transport_cost * n * l)/self.size_of_container
        return transportation_cost


    def solver(self,L):
        n = len(self.l_avail_list) # number of available options
        # Create the 'prob' variable to contain the problem data
        prob = LpProblem("Layout Problem",LpMinimize)
        objective_function = 0
        lower_constraint = 0
        upper_constraint = 0

        count = 0
        for i in range(n): # create the variables
                variable_name = 'n'+str(i+1)
                globals()[variable_name] = LpVariable(repr(variable_name),0,inf,LpInteger)
                objective_function += self.compute_production_cost(self.l_avail_list[i],globals()[variable_name])  \
                + self.compute_installation_cost(self.l_avail_list[i],globals()[variable_name])        \
                + self.compute_transportation_cost(self.l_avail_list[i],globals()[variable_name])
                
                lower_constraint += self.l_avail_list[i] * globals()[variable_name] 
                upper_constraint += self.l_avail_list[i] * globals()[variable_name] 
                count += globals()[variable_name] 
                
        # set objective function
        prob += objective_function

        # add constraints
        prob += lower_constraint >= L*(1-self.tolerance)
        prob += upper_constraint <= L*(1+self.tolerance)

        # penalize deviation
        prob += (self.labour_cost + self.material_cost + self.transport_cost) *  (upper_constraint - L)   # hack

        # # penalize the number of panels
        prob += (self.labour_cost + self.material_cost + self.transport_cost) * count * np.average(self.l_avail_list)

        # write solution
        prob.writeLP("LayoutModel.lp")

        # choose solver
        
        # solver = PULP_CBC_CMD(msg=0, mip_start=1)
        # solver = CPLEX_CMD(msg=0, mip_start=1)
        solver = GUROBI_CMD(msg=0, mip_start=1)
        # solve problem
        prob.solve(solver)

        return prob

    def solve(self,L):
        self.tolerance = 0.0 # reset the tolerance to 0.0
        solution = self.solver(L)

        # check solution status
        while (LpStatus[solution.status]!='Optimal'):
            print('Tolerance adjusted')
            self.tolerance += 0.1
            # if (L < 500):
            #     self.tolerance = 0.5
            solution = self.solver(L) # resolve problem   
        # results in a list 
    # Each of the variables is printed with it's resolved optimum value
        optimal = []
        for v in solution.variables():
            optimal.append(v.varValue)

        count = 0
        for j in range(len(optimal)):
            if (optimal[j]>0):
                count +=1

        # optimal_length = self.compute_new_wall_lengths(optimal)
        # penalty = (self.labour_cost + self.material_cost + self.transport_cost) *  (optimal_length - L) 
        # penalty += (self.labour_cost + self.material_cost + self.transport_cost) * count * np.average(self.l_avail_list)
        n = len(self.l_avail_list) # number of available options
        objective_function = 0.0
        for i in range(n): # create the variables  
                objective_function += self.compute_production_cost(self.l_avail_list[i],optimal[i])  \
                + self.compute_installation_cost(self.l_avail_list[i],optimal[i])        \
                + self.compute_transportation_cost(self.l_avail_list[i],optimal[i])   

        wall_cost = objective_function
        # wall_cost = value(solution.objective)
        return optimal,wall_cost

    def get_optimal_values(self):
        self.TL = []
        self.new_lengths = []
        self.old_lengths = []
        self.best_costs = []
        for k in range(self.nw):  #loop through the walls and solve
            target = self.L[k]
            optimal,wall_cost = self.solve(target) # call the solver 
            self.new_lengths.append(self.compute_new_wall_lengths(optimal)+self.setback_list[k])
            self.old_lengths.append(self.L[k] + self.setback_list[k])
            self.best_costs.append(wall_cost)
            best_combination = optimal
            self.TL.append(best_combination)
        return self.TL

    def compute_new_wall_lengths(self,optimal_combination):
        length = 0.0
        for i in range(self.n):
            length += self.l_avail_list[i] * optimal_combination[i]
        return length

    def get_original_total_lengths(self):
        original_length = sum(self.W) + sum(self.D) + sum(self.old_lengths) + sum(self.leftout)
        return original_length

    def get_new_total_lengths(self):
        new_length = sum(self.W) + sum(self.D) + sum(self.new_lengths) + sum(self.leftout)
        return new_length

    def get_total_costs(self):
        self.get_window_cost()
        self.get_door_cost()
        total_windows_costs = self.window_costs 
        total_door_costs = self.door_costs
        self.total = sum(self.best_costs) + sum(total_windows_costs) + sum(total_door_costs)
        return self.total


    def print(self):
        # run all the codes
        best = self.get_optimal_values()
        cost = self.get_total_costs()
        old_total = self.get_original_total_lengths()
        new_total = self.get_new_total_lengths()
        print("=============================================================================")
        print("Best combination for wall lengths: {0}".format(best))
        print("=============================================================================")
        print("Total cost for all panels: {0}".format(cost))
        print("=============================================================================")
        print("Original wall lengths: {0}".format(self.old_lengths))
        print("=============================================================================")
        print("After optimization.............")
        print("Optimized wall lengths: {0}".format(self.new_lengths))
        print("=============================================================================")
        print("Original total length: {0}".format(old_total))
        print("=============================================================================")
        print("After optimization.............")
        print("Optimized new length: {0}".format(new_total))


#test
'''
l_avail = {1:400,2:500,3:600,4:800} #a dictionary of available wall lengths
cost = [1.2,1.4,1.7,1.9]

x = ['L1400','W1200','L700','D900','L700','W1200','L1400']
model = LayOpt(l_avail,x,tolerance=0.2,cost=cost,ca=0.001)
model.print()

'''

'''
best = model.get_optimal_values()
cost = model.get_total_costs()
print("Best model for the walls")
print('\n')
print(best)
print("=============================================================================")
print('\n')
print(cost)
'''