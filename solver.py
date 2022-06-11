from cgi import print_exception
import copy
import numpy as np
import pandas as pd
import random
import src.solution as sol
import src.fitness as fit
import sys
import plotly.express as px
def try_assign_mission(mission, employees, day):
    assigned = False
    trials = 0
    while not assigned:
        trials += 1
        for i in range(len(employees)):
            if sol.assign_mission(mission, employees[i], day, trials < 2):
                assigned = True
                break

        if trials >= 2 and not assigned:
            fit.debug(mission)
            fit.debug("Can't generate initial solution")
            return False

    return True

week_days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']

generations = 10
if len(sys.argv) > 1:
    generations = (int)(sys.argv[1])

csv_dir = r'./csv/45-4/'
if len(sys.argv) > 2:
    csv_dir = r'./csv/' + sys.argv[2] + r'/'

missions_csv = pd.read_csv(csv_dir + r'/Missions.csv', header=None).transpose()
employees_csv = pd.read_csv(csv_dir + r'/Intervenants.csv', header=None).transpose()
distances = pd.read_csv(csv_dir + r'/Distances.csv', header=None)

missions = []
for i in range(missions_csv.shape[1]):
    missions.append(sol.translate_mission(missions_csv[i]))

employees = []
for i in range(employees_csv.shape[1]):
    employees.append(sol.translate_employee(employees_csv[i]))

sum = 0
for i in range(len(employees)):
    sum += employees[i]["quota"]
zeta = sum / len(employees)

sum = 0
for i in range(len(distances)):
    sum += distances[0][i] * 2
kappa = 100 / (sum / len(employees))


def print_fitness(solution):
    print(fit.fitness(solution, employees, distances, zeta, kappa))

def print_fitnesses(solutions):
    for i in range(len(solutions)):
        print_fitness(solutions[i])

def min_fitness(fitness_val):
    min = 9999999
    solution_id = 0
    index = 0
    for i in range(len(fitness_val)):
        if fitness_val[i][0] < min and fitness_val[i][0] >= 0:
            min = fitness_val[i][0]
            solution_id = fitness_val[i][1]
            index = i
    
    return min, solution_id, index

####
# First generation
####

lsf_missions = [missions[i] for i in range(len(missions)) if missions[i]["skill"] == 0]
lcp_missions = [missions[i] for i in range(len(missions)) if missions[i]["skill"] == 1]

lsf_employees = [employees[i] for i in range(len(employees)) if employees[i]["skill"] == 0]
lcp_employees = [employees[i] for i in range(len(employees)) if employees[i]["skill"] == 1]

population_size = 30 # better be multiple of 10
population = []
fitness_values = [[] for i in range(population_size)]

def generate_solution():
    valid_solution = False
    while not valid_solution:
        solution = sol.init_empty_solution(len(employees))
        for day in range(5):
            
            lsf_day_missions = [lsf_missions[k] for k in range(len(lsf_missions)) if lsf_missions[k]["day"] == day+1]
            lcp_day_missions = [lcp_missions[k] for k in range(len(lcp_missions)) if lcp_missions[k]["day"] == day+1]
                    
            day_mission_index = 0
            while day_mission_index < max(len(lcp_day_missions), len(lsf_day_missions)):
                lcp_day_mission, lsf_day_mission = None, None
                if day_mission_index < len(lcp_day_missions): lcp_day_mission = lcp_day_missions[day_mission_index]
                if day_mission_index < len(lsf_day_missions): lsf_day_mission = lsf_day_missions[day_mission_index]

                random.shuffle(lcp_employees)
                
                assigned = True
                if lsf_day_mission != None:
                    if not try_assign_mission(lsf_day_mission, lsf_employees, solution[day]): 
                        assigned = False
                if lcp_day_mission != None: 
                    if not try_assign_mission(lcp_day_mission, lcp_employees, solution[day]): 
                        assigned = False
                
                if not assigned:
                    fit.debug("Can't assign mission")
                    break

                day_mission_index += 1
            
        fitness_val = [fit.fitness(solution, employees, distances, zeta, kappa), solution_id]

        if fitness_val[0] >= 0:
            valid_solution = True
            break
        

        fit.debug("Invalid solution, loops again")
    return solution, fitness_val

for i in range(population_size):
    population.append(sol.init_empty_solution(len(employees)))

for solution_id in range(population_size):
    solution = generate_solution()
    population[solution_id] = solution[0]
    fitness_values[solution_id] = solution[1]

def already_included(solution, population):
    return solution in population

# for i in range(population_size):
    # for day in range(5):
    #     print('\n' + week_days[day])
    #     sol.print_day(population[i][day])
        
    # print(fitness_values[i][0])

print('Generation 0 min =',min_fitness(fitness_values)[0])


# sol.print_week(population[0])
# print_fitness(population[0])

####
# Next generations
####
xabs=[]
yabs=[]
min_sol = 0
for gen in range(1, generations+1):

    # for i in range(population_size):
    #     print_fitness(population[i])

    # Elites selection (10% best)
    next_population = []
    parents = []
    for i in range(round(population_size * 0.1)):
        val, sol_id, index = min_fitness(fitness_values)
        fitness_values.pop(index)
        next_population.append(copy.deepcopy(population[sol_id]))
        parents.append(copy.deepcopy(population[sol_id]))


    # Parents selection (40% best, elites included)
    while len(parents) < population_size * 0.4:
        val, sol_id, index = min_fitness(fitness_values)
        fitness_values.pop(index)

        # 50% chance of generating new random solution /
        # 50% chance of taking a good solution
        if random.randrange(2) == 0: parents.append(population[sol_id])
        else: parents.append(generate_solution()[0])


    # while len(next_population) < population_size-10:
    #     parent1 = random.randrange(0, len(parents))
    #     parent2 = random.randrange(0, len(parents))

    #     while parent2 == parent1:
    #         parent2 = random.randrange(0, len(parents))

    #     # children = sol.cross_over_impr(parents[parent1], parents[parent2], lsf_employees, lcp_employees)
    #     # while already_included(children[0], next_population) or already_included(children[1],next_population):
    #     #     children = sol.cross_over_impr(parents[parent1], parents[parent2], lsf_employees, lcp_employees)


    #     children = sol.cross_over(parents[parent1], parents[parent2])
    #     while already_included(children[0], next_population) or already_included(children[1],next_population):
    #         children = sol.cross_over(parents[parent1], parents[parent2])

    #     next_population.append(children[0])
    #     next_population.append(children[1])
      
        # sol.print_day(parents[parent1][3])
        # print("+")
        # sol.print_day(parents[parent2][3])
        # print("=")
        # sol.print_day(children[0][3])
        # sol.print_day(children[1][3])
        # print()
    while len(next_population)< population_size:
        index = random.randrange(0,len(parents))

        muted = sol.mutation(parents[index],lsf_employees, lcp_employees)
        while already_included(muted, next_population):
            muted = sol.mutation(parents[index],lsf_employees, lcp_employees)

        next_population.append(muted)

    # print()
    # print("Full next gen, length", len(next_population))
    # print_fitnesses(next_population)

    fitness_values = []
    for i in range(population_size):
        population[i] = copy.deepcopy(next_population[i])
        fitness_values.append([fit.fitness(population[i], employees, distances, zeta, kappa), i])

    min_sol = min_fitness(fitness_values)
    xabs.append(gen)
    yabs.append(min_sol[0])
    # sol.print_week(population[min_sol[1]])
    print("Generation", gen, "min =", min_sol[0]) 

print()
# sol.print_week(population[min_sol[1]])
# print_fitness(population[0])

fig = px.line(x=xabs,y=yabs)

fig.show()
#fig.write_html("./plots/gen"+str(gen)+"_"+sys.argv[2]+".html",auto_open=True)