# Irfansha Shaik, 30.07.2020, Aarhus

'''
Todos:
  - Add functionality to go through each step to get the required plan
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
  cnf_file_name = sys.argv[4]
  # generating and writing cnf file for the problem:
  cnf_list, reverse_var_map, var_count, step_actions_list = cg.generate_cnf(domain, problem, k)
  f = open(cnf_file_name, 'w')
  cg.write_cnf(cnf_list,var_count,f)
  f.close()
  # solving the problem using sat solver
  #(assuming minisat available in current folder):
  command = "./MiniSat_v1.14_linux" + " " + cnf_file_name + " sat_plan_output\n"
  os.system(command)
  var_list = parse_sat_output("sat_plan_output")
  # printing the extracted plan:
  if (var_list):
    for actions in step_actions_list:
      for action in actions:
        if var_list[action-1] == 1:
          print(reverse_var_map[action])

