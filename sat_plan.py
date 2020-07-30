# Irfansha Shaik, 30.07.2020, Aarhus

'''
Todos:
  - Add parser for sat solver output for plan retreival
'''

import cnf_gen as cg

if __name__ == '__main__':
  import os, sys
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  cnf_file_name = sys.argv[4]
  # generating and writing cnf file for the problem:
  cnf_list, reverse_var_map, var_count = cg.generate_cnf(domain, problem, k)
  f = open(cnf_file_name, 'w')
  cg.write_cnf(cnf_list,var_count,f)
  # solving the problem using sat solver
  #(assuming minisat available in current folder):
  command = "./MiniSat_v1.14_linux" + " " + cnf_file_name + " sat_plan_output"
  os.system(command)
  #for mp in reverse_var_map:
  #  print(mp,reverse_var_map[mp])

