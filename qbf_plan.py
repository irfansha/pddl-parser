# Irfansha Shaik, 27.08.2020, Aarhus

'''
Todos:
  - XXX
'''

import cir_gen as cg

# parsing the qbf solver output (assuming quabs):
def parse_qbf_output(file_name, k, num_vars):
  var_list = []
  f = open(file_name, 'r')
  lines = f.readlines()
  result = lines.pop(0).strip("\n")
  if (result != 'r UNSAT'):
    literals = result.split(" ")
    literals.pop()
    literals.pop(0)
    for literal in literals:
      if int(literal) > 0:
        var_list.append(1)
        #var_list.append(literal)
      else:
        var_list.append(-1)
        #var_list.append(literal)
  return var_list


def extract_plan(variable_list, state_vars, constraint_list, i):
  for j in range(i):
    print("step " + str(j+1) + ":")
    precond_neg_state_var = []
    precond_pos_state_var = []
    add_state_var = []
    del_state_var = []

    first_l = j*num_vars
    first_r = (j+1)*num_vars
    first_step_list = list(variable_list[first_l :first_r])

    second_l = (j+1)*num_vars
    second_r = (j+2)*num_vars
    second_step_list = list(variable_list[second_l :second_r])

    for k in range(num_vars):
      if first_step_list[k] == -1:
        precond_neg_state_var.append(state_vars[k])
      elif first_step_list[k] == 1:
        precond_pos_state_var.append(state_vars[k])
      if first_step_list[k] == -1 and second_step_list[k] == 1:
        add_state_var.append(state_vars[k])
      elif first_step_list[k] == 1 and second_step_list[k] == -1:
        del_state_var.append(state_vars[k])

    # XXX check if preconditions hold:
    # XXX check if add effects hold:
    # XXX check if del effects hold:
    for action in constraint_list:
      #print(action)
      valid_action = 1
      for pre_neg in action.negative_preconditions:
        if pre_neg not in precond_neg_state_var:
          valid_action = 0
          break
      for pre_pos in action.positive_preconditions:
        if pre_pos not in precond_pos_state_var:
          valid_action = 0
          break
      for add_svar in add_state_var:
        if add_svar not in action.add_effects:
          valid_action = 0
          break
      for del_svar in del_state_var:
        if del_svar not in action.del_effects:
          valid_action = 0
          break
      if (valid_action):
        print(action.name, action.parameters)
        
    #print(precond_pos_state_var)
    #print(precond_neg_state_var)
    #print(add_state_var)
    #print(del_state_var)


if __name__ == '__main__':
  import os, sys
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  solver_path = sys.argv[4]
  
  constraint_list = cg.constraints(domain, problem)
  # extracting all state variables:
  state_vars = cg.extract_state_vars(constraint_list)
  num_vars = len(state_vars)
  #print(num_vars)
  #for action in constraint_list:
  #  print(action)

  for i in range(2, k):
    print("Running for length:", i)
    # writing circuit file for the problem:
    command = "python3 cir_gen.py " + domain + " " + problem + " " + str(i) + " > test_cir_" + str(i) + ".qcir"
    os.system(command)
    print("Encoding generated")
    plan_output_filename = "qbf_plan_output_" + str(i) + ".txt"
    # solving the problem using qbf solver
    #(assuming quabs solver):
    command = solver_path + " --partial-assignment test_cir_" + str(i) + ".qcir > " + plan_output_filename
    os.system(command)
    print("solver computation completed")
    variable_list = parse_qbf_output(plan_output_filename, i, num_vars)
    print(variable_list)
    # printing the extracted plan:
    if (variable_list):
      extract_plan(variable_list, state_vars, constraint_list, i)
      break
