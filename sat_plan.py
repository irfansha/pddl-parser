# Irfansha Shaik, 30.07.2020, Aarhus

'''
Todos:
  - Add parameter for arbitrary sat solver.
'''

import cnf_gen as cg

# parsing the sat solver output (assuming minisat):
def parse_sat_output(file_name):
  var_list = []
  f = open(file_name, 'r')
  lines = f.readlines()
  result = lines.pop(0).strip("\n")
  if (result == 'SAT'):
    literals = lines.pop(0)
    literals = literals.strip(" 0 \n").split(" ")
    for literal in literals:
      if int(literal) > 0:
        var_list.append(1)
      else:
        var_list.append(-1)
  return var_list

if __name__ == '__main__':
  import os, sys
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  solver_path = sys.argv[4]
  for i in range(2, k):
    print("Running for length:", i)
    # generating and writing cnf file for the problem:
    cnf_list, reverse_var_map, var_count, step_actions_list = cg.generate_cnf(domain, problem, i)
    cnf_file_name = "input_plan_" + str(i) + ".cnf"
    f = open(cnf_file_name, 'w')
    cg.write_cnf(cnf_list,var_count,f)
    f.close()
    plan_output_filename = "sat_plan_output_" + str(i) + ".txt"
    # solving the problem using sat solver
    #(assuming minisat available in current folder):
    command = solver_path + " " + cnf_file_name + " " + plan_output_filename +" >> stats.txt"
    os.system(command)
    variable_list = parse_sat_output(plan_output_filename)
    # printing the extracted plan:
    if (variable_list):
      for actions in step_actions_list:
        for action in actions:
          if variable_list[action-1] == 1:
            print(reverse_var_map[action])
      break

