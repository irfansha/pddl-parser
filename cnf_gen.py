# Irfansha Shaik, 17.06.2020, Aarhus
'''
Using source file "planner.py" as base
url: https://github.com/pucrs-automated-planning/pddl-parser
commit id: 38cc9aa48208d396f4373198ef354918f548e7de
'''

'''
Todos:
  - Testing needed for correctness
'''


from PDDL import PDDL_Parser

# state extraction from pddl domain and problem:
#-------------------------------------------------------------------------------------------
'''
Takes domain and problem as input and generates list of
- initial state
- goal state
- grounded actions
'''
def constraints(domain, problem):
  clause_list = []
  # Parser
  parser = PDDL_Parser()
  parser.parse_domain(domain)
  parser.parse_problem(problem)

  state = parser.state
  # Initial state clauses:
  initial_clauses = list(state)
  #print(initial_clauses)

  goal_pos = parser.positive_goals
  goal_not = parser.negative_goals
  goal_clauses = [goal_pos, goal_not]

  action_list = []
  # Grounding process
  ground_actions = []
  for action in parser.actions:
    for act in action.groundify(parser.objects):
      ground_actions.append(act)
  # Appending grounded actions:
  for act in ground_actions:
    action_list.append(act)
    #print(act)

  # Appending to one list:
  clause_list.append(initial_clauses)
  clause_list.append(goal_clauses)
  clause_list.extend(action_list)
  return clause_list
#-------------------------------------------------------------------------------------------

# Boolean variable generators:
#-------------------------------------------------------------------------------------------
def make_pboolvar(tup, i):
  var = ''
  for ele in tup:
    var = var + str(ele) + '_'
    #print(ele)
  var = var + str(i)
  #print(var)
  return var

def make_nboolvar(tup, i):
  var = '-'
  for ele in tup:
    var = var + str(ele) + '_'
    #print(ele)
  var = var + str(i)
  #print(var)
  return var

def make_compboolvar(tup, i, j):
  var = ''
  for ele in tup:
    var = var + str(ele) + '_'
    #print(ele)
  var = var + str(i) + '_' + str(j)
  #print(var)
  return var

# Return sign of variable and the variable name without sign:
def extract_var(var):
  if var[0] == '-':
    return (0,var[1:])
  else:
    return (1,var)

#-------------------------------------------------------------------------------------------

# AMO and ALO clauses:
#-------------------------------------------------------------------------------------------

# AtMostOne constraints for every pair of variables:
def amo_alo(var_list):
  #print(var_list)
  amoalo_clause_list = []
  for i in range(0, len(var_list)):
    for j in range(i + 1, len(var_list)):
      amoalo_clause_list.append([-var_list[i], -var_list[j]])
  amoalo_clause_list.append(var_list)
  return amoalo_clause_list
#-------------------------------------------------------------------------------------------

# If then condition expansion:
#-------------------------------------------------------------------------------------------
'''
Expands the if then condition in action rule:
Ex: if x then (a & b) --> (-x V a) & (-x V b)
'''
def if_then_exp(condition):
  expanded_condition = []
  action_var = condition[0]
  condition_vars = condition[1]
  #print(action_var, condition_vars)
  for var in condition_vars:
    expanded_condition.append([-action_var,var])
  return expanded_condition

#-------------------------------------------------------------------------------------------

# State variables extractor:
#-------------------------------------------------------------------------------------------
'''
Extracts all possible states from constraints available:
'''
def extract_state_vars(constraint_list):
  state_vars = []
  initial_state = constraint_list.pop(0)
  for var in initial_state:
    if var not in state_vars:
      state_vars.append(var)
  goal_state = constraint_list.pop(0)
  for var_list in goal_state:
    for var in var_list:
      if var not in state_vars:
        state_vars.append(var)
  # Rest of the actions, considering pre/post conditions:
  for constraint in constraint_list:
    temp_imp_clauses = []
    for cond in constraint.positive_preconditions:
      if cond not in state_vars:
        state_vars.append(cond)
    for cond in constraint.negative_preconditions:
      if cond not in state_vars:
        state_vars.append(cond)
    for cond in constraint.add_effects:
      if cond not in state_vars:
        state_vars.append(cond)
    for cond in constraint.del_effects:
      if cond not in state_vars:
        state_vars.append(cond)
  return state_vars

#-------------------------------------------------------------------------------------------


# Clauses generator:
#-------------------------------------------------------------------------------------------
'''
Generates clauses with boolean variables for initial state,
time step is considered 1:
'''
def initial_clause_gen(state, state_vars):
  initial_clauses = []
  for atom in state:
    var = make_pboolvar(atom,1)
    initial_clauses.append(var)
  for var in state_vars:
    if var not in state:
      var_name = make_nboolvar(var,1)
      initial_clauses.append(var_name)
  return initial_clauses

def goal_clause_gen(state,k):
  goal_pos = state[0]
  goal_neg = state[1]
  goal_clauses = []
  for atom in goal_pos:
    var = make_pboolvar(atom,k)
    goal_clauses.append(var)
  for atom in goal_neg:
    var = make_nboolvar(atom,k)
    goal_clauses.append(var)
  return goal_clauses

def act_imp_clauses_gen(constraints_list, state_vars, i):
  imp_clauses = []
  for constraint in constraints_list:
    name = constraint.name + "_" + make_pboolvar(constraint.parameters,i)
    action_var =  name
    temp_imp_clauses = []
    for cond in constraint.positive_preconditions:
      temp_imp_clauses.append(make_pboolvar(cond,i))
    for cond in constraint.negative_preconditions:
      temp_imp_clauses.append(make_nboolvar(cond,i))
    # Identifying touched var:
    touched_vars = []
    for cond in constraint.add_effects:
      if cond not in touched_vars:
        touched_vars.append(cond)
      temp_imp_clauses.append(make_pboolvar(cond,i+1))
    for cond in constraint.del_effects:
      if cond not in touched_vars:
        touched_vars.append(cond)
      temp_imp_clauses.append(make_nboolvar(cond,i+1))
    # Extracting untouched vars:
    untouched_vars = []
    for var in state_vars:
      if var not in touched_vars:
        untouched_vars.append(var)
    #print(temp_imp_clauses)
    for var in untouched_vars:
      temp_imp_clauses.append(make_compboolvar(var,i,i+1))
    #print(temp_imp_clauses)
    #print(untouched_vars)
    imp_clauses.append([action_var, temp_imp_clauses])
  return imp_clauses

def gen_cond_prop_clauses(state_vars,i):
  temp_condprop_clauses = []
  for var in state_vars:
    cond_name = '-' + make_compboolvar(var,i,i+1)
    temp_condprop_clauses.append([cond_name, make_pboolvar(var,i), make_nboolvar(var,i+1)])
    temp_condprop_clauses.append([cond_name, make_nboolvar(var,i), make_pboolvar(var,i+1)])
  return temp_condprop_clauses

def clause_gen(constraint_list, state_vars, k):
  initial_state = constraint_list.pop(0)
  initial_clauses = initial_clause_gen(initial_state, state_vars)
  goal_state = constraint_list.pop(0)
  goal_clauses = goal_clause_gen(goal_state, k)
  #print(goal_clauses)
  act_imp_clauses = []
  cond_prop_clauses = []
  for i in range(1,k):
    temp_act_imp_clauses = act_imp_clauses_gen(constraint_list, state_vars, i)
    temp_cond_prop_clauses = gen_cond_prop_clauses(state_vars,i)
    act_imp_clauses.append(temp_act_imp_clauses)
    cond_prop_clauses.append(temp_cond_prop_clauses)
  #print(len(act_imp_clauses), len(cond_prop_clauses))
  #print(cond_prop_clauses)
  return [initial_clauses, goal_clauses, act_imp_clauses, cond_prop_clauses]
#-------------------------------------------------------------------------------------------

# Making clauses/variables integer:
#-------------------------------------------------------------------------------------------
def make_clauses_integer(clauses):
  integer_clauses = []
  var_map = {}
  reverse_var_map = {}
  count = 1
  initial_clauses = clauses.pop(0)
  #print("Initial clauses: ", initial_clauses)
  temp_int_initial_clauses = []
  for clause in initial_clauses:
    # checking if the variable is postive:
    (pos,var) = extract_var(clause)
    # Assuming the initial conditions are non-repeatitive:
    var_map[var] = count
    count = count + 1
    if pos:
      temp_int_initial_clauses.append(var_map[var])
    else:
      # Initial clauses do not seem to have negative atoms,
      # adding for generality:
      temp_int_initial_clauses.append(-var_map[var])
  integer_clauses.append(temp_int_initial_clauses)

  # Assuming atleast one step is needed i.e. k > 1:
  goal_clauses = clauses.pop(0)
  #print("Goal clauses: ", goal_clauses)
  temp_int_goal_clauses = []
  for clause in goal_clauses:
    # checking if the variable is postive:
    (pos,var) = extract_var(clause)
    # Assuming the goal conditions are non-repeatitive:
    var_map[var] = count
    count = count + 1
    if pos:
      temp_int_goal_clauses.append(var_map[var])
    else:
      temp_int_goal_clauses.append(-var_map[var])
  integer_clauses.append(temp_int_goal_clauses)

  imp_clauses = clauses.pop(0)
  temp_int_imp_clauses = []
  for imp in imp_clauses:
    temp_step_int_clauses = []
    for clause in imp:
      var = clause[0]
      if var not in var_map:
        var_map[var] = count
        count = count + 1
      temp_action = var_map[var]
      temp_int_then_clauses = []
      for temp_clause in clause[1]:
        (pos,var) = extract_var(temp_clause)
        if var not in var_map:
          var_map[var] = count
          count = count + 1
        if pos:
          temp_int_then_clauses.append(var_map[var])
        else:
          temp_int_then_clauses.append(-var_map[var])
      temp_step_int_clauses.append([temp_action, temp_int_then_clauses])
    temp_int_imp_clauses.append(temp_step_int_clauses)
  integer_clauses.append(temp_int_imp_clauses)

  cond_prop_clauses = clauses.pop(0)
  temp_cond_prop_clauses = []
  for step_cond_prop_clauses in cond_prop_clauses:
    for clause in step_cond_prop_clauses:
      var_clause = []
      for var in clause:
        # checking if the variable is postive:
        (pos,var_name) = extract_var(var)
        if var_name not in var_map:
          var_map[var_name] = count
          count = count + 1
        if pos:
          var_clause.append(var_map[var_name])
        else:
          var_clause.append(-var_map[var_name])
      temp_cond_prop_clauses.append(var_clause)
  integer_clauses.append(temp_cond_prop_clauses)
  for key in var_map:
    reverse_var_map[var_map[key]] = key
  return (integer_clauses,reverse_var_map, count-1)

#-------------------------------------------------------------------------------------------

# complete clause generation:
#-------------------------------------------------------------------------------------------
'''
Takes clause_list and returns updated clause_list
- adds exactly one constraints one moves
'''
def complete_clauses_gen(clause_list):
  action_clauses = list(clause_list[2])
  amoalo_list = []
  for clause_step in action_clauses:
    temp_amoalo_list = []
    for clause in clause_step:
      temp_amoalo_list.append(clause[0])
    amoalo_list.append(temp_amoalo_list)
    temp_amoalo = amo_alo(temp_amoalo_list)
    clause_list.append(temp_amoalo)
  return clause_list, amoalo_list

#-------------------------------------------------------------------------------------------

# cnf generator from clauses:
#-------------------------------------------------------------------------------------------
'''
Takes complete clause list and generates cnf format for each clause:
'''
def gen_cnf(complete_clauses):
  cnf_list = []
  initial_clauses = complete_clauses.pop(0)
  for var in initial_clauses:
    cnf_list.append([var])

  # Writing goal clauses to cnf:
  goal_clauses = complete_clauses.pop(0)
  for var in goal_clauses:
    cnf_list.append([var])

  # Expanding if then condition and writing to cnf:
  action_clauses = complete_clauses.pop(0)
  for clause_step in action_clauses:
    for clause in clause_step:
      cnf_list.extend(if_then_exp(clause))

  # Adding propagation clauses:
  prop_clauses = complete_clauses.pop(0)
  for clause in prop_clauses:
    cnf_list.append(clause)

  # Appending amoalo clauses to the cnf:
  for amoalo_clauses in complete_clauses:
    cnf_list.extend(amoalo_clauses)
  return cnf_list

#-------------------------------------------------------------------------------------------

# prints cnf format to stdout:
#-------------------------------------------------------------------------------------------
def print_cnf(cnf_list,var_count):
  print("p cnf " + str(var_count) + " " + str(len(cnf_list)))
  for clause in cnf_list:
    temp_str = ''
    for var in clause:
      temp_str = temp_str + str(var) + ' '
    temp_str = temp_str + '0'
    print(temp_str)

#-------------------------------------------------------------------------------------------

# prints cnf format to file:
#-------------------------------------------------------------------------------------------
def write_cnf(cnf_list,var_count, f):
  f.write("p cnf " + str(var_count) + " " + str(len(cnf_list)) + "\n")
  for clause in cnf_list:
    temp_str = ''
    for var in clause:
      temp_str = temp_str + str(var) + ' '
    temp_str = temp_str + '0'
    f.write(temp_str + "\n")

#-------------------------------------------------------------------------------------------


# generates cnf file and variable map:
#-------------------------------------------------------------------------------------------
def generate_cnf(domain, problem, k):
  constraint_list = constraints(domain, problem)
  temp_constraint_list = list(constraint_list)
  #print(temp_constraint_list)
  # extracting all state variables:
  state_vars = extract_state_vars(temp_constraint_list)
  #print('Time: ' + str(time.time() - start_time) + 's')
  # initial, goal and actions clauses as a list of lists:
  clauses = clause_gen(constraint_list,state_vars, k)
  (integer_clauses,reverse_var_map,var_count) = make_clauses_integer(clauses)
  #print(reverse_var_map)
  complete_clauses, step_actions_list = complete_clauses_gen(integer_clauses)
  cnf_list = gen_cnf(complete_clauses)
  return cnf_list, reverse_var_map, var_count, step_actions_list

#-------------------------------------------------------------------------------------------



if __name__ == '__main__':
  import sys, time
  #start_time = time.time()
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  cnf_list, reverse_var_map, var_count, step_actions_list = generate_cnf(domain, problem, k)
  #print_cnf(cnf_list,var_count)
  #for mp in reverse_var_map:
  #  print(mp,reverse_var_map[mp])
