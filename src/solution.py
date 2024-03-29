from copy import copy, deepcopy
import random
from random import randrange
import numpy as np
import src.fitness as fit
import matplotlib.pyplot as plt


def pretty_table(solution):
    # hours = [0 for i in range(len(solution[0][0]))]
    # for hour in range(1,len(solution[0][0])):
    #     if hour % 2 != 0:
    #         hours[hour] = str(hour / 2 + 8)
    #     else:
    #         hours[hour] = str(hour / 2 + 8) + "h30"

    # missions = solution[0]
    
    # fig, ax = plt.subplots() 
    # ax.set_axis_off() 
    # table = ax.table( 
    #     cellText = missions,  
    #     rowLabels = val2,  
    #     colLabels = hours, 
    #     rowColours =["palegreen"] * len(solution[0]),  
    #     colColours =["palegreen"] * len(solution[0][0]), 
    #     cellLoc ='center',  
    #     loc ='upper left')         
    
    # ax.set_title('matplotlib.axes.Axes.table() function Example', 
    #             fontweight ="bold") 
    col_headers = ['id', '8h', '8h30', '9h', '9h30', '10h', '10h30', '11h', '11h30', '12h',
              '12h30', '13h', '13h30', '14h', '14h30', '15h', '15h30', '16h', '16h30', '17h', '17h30',
              '18h', '18h30', '19h', '19h30']

    row_headers = [str(i) for i in range(len(solution[0]))] 
    

    rcolors = plt.cm.BuPu(np.full(len(row_headers), 0.1))
    ccolors = plt.cm.BuPu(np.full(len(col_headers), 0.1))
    
    the_table = plt.table(
                        cellText=solution[0],
                        rowLabels=row_headers,
                        rowColours=rcolors,
                        rowLoc='right',
                        colColours=ccolors,
                        colLabels=col_headers,
                        loc='center'
                        )
    
    
    

    # rcolors = plt.cm.BuPu(np.full(len(row_headers), 0.1))
    # ccolors = plt.cm.BuPu(np.full(len(col_headers), 0.1))
    
    # the_table = plt.table(cellText=[[0 for i in range(len(col_headers))] for i in range(len(row_headers))],
    #                     rowLabels=row_headers,
    #                     rowColours=rcolors,
    #                     rowLoc='right',
    #                     colColours=ccolors,
    #                     colLabels=col_headers,
    #                     loc='center')

    plt.axis("off")
    plt.show() 


def init_empty_day(employees_count):
    day = [[0 for _ in range(25)] for _ in range(employees_count)]

    for i in range(employees_count):
        day[i][0] = i + 1

    return day


def init_empty_solution(employees_count):
    solution = [init_empty_day(employees_count) for i in range(5)]

    return solution


def skill_to_int(skill_string):
    skill = 0
    if (skill_string == "LPC"):
        skill = 1

    return skill


def spe_to_int(spe_string):
    spe = 0
    if spe_string == "Jardinage":
        spe = 0
    if spe_string == "Menuiserie":
        spe = 1
    if spe_string == "Mecanique":
        spe = 2
    if spe_string == "Musique":
        spe = 3
    if spe_string == "Electricite":
        spe = 4

    return spe


def translate_mission(csv_row):
    return {
        "id": csv_row[0],
        "day": csv_row[1],
        "start_hour": csv_row[2] / 60,
        "end_hour": csv_row[3] / 60,
        "skill":  skill_to_int(csv_row[4]),
        "spe": spe_to_int(csv_row[5])
    }


def translate_employee(csv_row):
    return {
        "id": csv_row[0],
        "skill":  skill_to_int(csv_row[1]),
        "spe": spe_to_int(csv_row[2]),
        "quota": csv_row[3]
    }

# Ex : 8h to 0, 9.5h to 3


def hour_to_solution_index(hour):
    return (int)(hour * 2) - 15


def has_mission_between(hour1, hour2, employee, day):
    start_index = hour_to_solution_index(hour1)
    end_index = hour_to_solution_index(hour2)

    if start_index < 1:
        start_index = 1

    for i in range(start_index, end_index):
        if day[employee["id"] - 1][i] != 0:
            return True


def has_mission_before(hour, employee, day):
    hour_before = hour_to_solution_index(hour)-1
    print(hour_before)
    if hour_before < 1 or hour_before >= len(day[0]):
        return False

    if day[employee["id"] - 1][hour_before] == 0:
        return False

    return True


def assign_mission(mission, employee, day, require_gap_before=False):
    start_hour = mission['start_hour']
    if require_gap_before:
        start_hour -= 0.5
    if has_mission_between(start_hour, mission["end_hour"], employee, day):
        return False

    start_index = hour_to_solution_index(mission["start_hour"])
    end_index = hour_to_solution_index(mission["end_hour"])

    for i in range(start_index, end_index):
        day[employee["id"] - 1][i] = mission["id"]

    return True

# Crossover of 1 day


def cross_over(solution1, solution2):
    child1 = copy(solution1)
    child2 = copy(solution2)

    cross_day = randrange(5)
    cross_day = 3
    child1[cross_day] = solution2[cross_day]
    child2[cross_day] = solution1[cross_day]
    return child1, child2


# Crossover switching 2 employees in 2 solution (not that good)
def cross_over_impr(solution1, solution2, lsf_employees, lcp_employees):

    new_solution1 = deepcopy(solution1)
    new_solution2 = deepcopy(solution2)

    mutation_day = randrange(5)

    skill = random.randrange(2)

    if skill == 0:
        employee1_ind = random.choice(lsf_employees)["id"]-1
    else:
        employee1_ind = random.choice(lcp_employees)["id"]-1

    if skill == 0:
        employee_list = deepcopy(lsf_employees)
    else:
        employee_list = deepcopy(lcp_employees)
    random.shuffle(employee_list)

    for employee in employee_list:
        if(employee["id"] == employee1_ind+1):
            continue
        employee2_ind = employee["id"]-1
        break

    # Switching days
    for hour in range(1, len(solution1[0][0])):
        new_solution1[mutation_day][employee1_ind][hour] = solution2[mutation_day][employee2_ind][hour]
        new_solution2[mutation_day][employee2_ind][hour] = solution1[mutation_day][employee1_ind][hour]

    return [new_solution1, new_solution2]


def mutation(solution, lsf_employees, lcp_employees):

    new_solution = deepcopy(solution)

    mutation_day = randrange(5)

    skill = random.randrange(2)

    if skill == 0:
        employee1_ind = random.choice(lsf_employees)["id"]-1
    else:
        employee1_ind = random.choice(lcp_employees)["id"]-1

    if skill == 0:
        employee_list = deepcopy(lsf_employees)
    else:
        employee_list = deepcopy(lcp_employees)
    random.shuffle(employee_list)

    for employee in employee_list:
        if(employee["id"] == employee1_ind+1):
            continue
        employee2_ind = employee["id"]-1
        break

    # print()
    # print(solution[mutation_day][employee2_ind],solution[mutation_day][employee1_ind]  )
    # print("Muting :")
    # print_day(solution[mutation_day])

    # Switching days
    for hour in range(1, len(solution[0][0])):
        new_solution[mutation_day][employee1_ind][hour] = solution[mutation_day][employee2_ind][hour]
        new_solution[mutation_day][employee2_ind][hour] = solution[mutation_day][employee1_ind][hour]

    # print("Into :")
    # print_day(new_solution[mutation_day])

    return new_solution


def print_table(table):
    for i in range(len(table)):
        print(table[i])


def print_day(day):
    header = ['id', '8h', '8h30', '9h', '9h30', '10h', '10h30', '11h', '11h30', '12h',
              '12h30', '13h', '13h30', '14h', '14h30', '15h', '15h30', '16h', '16h30', '17h', '17h30',
              '18h', '18h30', '19h', '19h30']
    #_sol = sol
    _day = np.vstack([header, day])
    s = [[str(e) for e in row] for row in _day]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))
    return


week_days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
def print_week(solution):
    for i in range(len(solution)):
        print(week_days[i])
        print_day(solution[i])
