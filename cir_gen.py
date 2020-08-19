# Irfansha Shaik, 07.08.2020, Aarhus

'''
Reusing some code from cnf_gen.py
Url: https://github.com/irfansha/pddl-parser/blob/master/cnf_gen.py
Commit id: e9494e8b1db249cdbea02fe223b91c28fb59a448
'''

'''
Todos:
  - Add the condition gate for transition gates in forall block
  - Build dictionary to print integers instead of verbose gates
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
  gate_list = []
  # Parser
  parser = PDDL_Parser()
  parser.parse_domain(domain)
  parser.parse_problem(problem)

  state = parser.state
  # Initial state gate:
  initial_gate = list(state)
  #print(initial_gate)

  goal_pos = parser.positive_goals
  goal_not = parser.negative_goals
  goal_gate = [goal_pos, goal_not]

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
  gate_list.append(initial_gate)
  gate_list.append(goal_gate)
  gate_list.extend(action_list)
  return gate_list
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

#-------------------------------------------------------------------------------------------
'''
Generates gates with boolean variables for initial state,
'''
def initial_gate_gen(state, state_vars):
  initial_gate = []
  for atom in state:
    var = make_pboolvar(atom,'i')
    initial_gate.append(var)
  for var in state_vars:
    if var not in state:
      var_name = make_nboolvar(var,'i')
      initial_gate.append(var_name)
  return initial_gate


def goal_gate_gen(state,k):
  goal_pos = state[0]
  goal_neg = state[1]
  goal_gate = []
  for atom in goal_pos:
    var = make_pboolvar(atom,k)
    goal_gate.append(var)
  for atom in goal_neg:
    var = make_nboolvar(atom,k)
    goal_gate.append(var)
  return goal_gate

def act_imp_gate_gen(constraints_list, state_vars, i):
  imp_gate = []
  for constraint in constraints_list:
    name = constraint.name + "_" + make_pboolvar(constraint.parameters,i)
    action_var =  name
    temp_imp_gate = []
    for cond in constraint.positive_preconditions:
      temp_imp_gate.append(make_pboolvar(cond,i))
    for cond in constraint.negative_preconditions:
      temp_imp_gate.append(make_nboolvar(cond,i))
    # Identifying touched var:
    touched_vars = []
    for cond in constraint.add_effects:
      if cond not in touched_vars:
        touched_vars.append(cond)
      temp_imp_gate.append(make_pboolvar(cond,i+1))
    for cond in constraint.del_effects:
      if cond not in touched_vars:
        touched_vars.append(cond)
      temp_imp_gate.append(make_nboolvar(cond,i+1))
    # Extracting untouched vars:
    untouched_vars = []
    for var in state_vars:
      if var not in touched_vars:
        untouched_vars.append(var)
    #print(temp_imp_gate)
    for var in untouched_vars:
      temp_imp_gate.append(make_compboolvar(var,i,i+1))
    #print(temp_imp_gate)
    #print(untouched_vars)
    imp_gate.append([action_var, temp_imp_gate])
  return imp_gate

def gen_cond_prop_gates(state_vars,i):
  temp_condprop_gates = []
  for var in state_vars:
    cond_name = '-' + make_compboolvar(var,i,i+1)
    temp_condprop_gates.append([cond_name, make_pboolvar(var,i), make_nboolvar(var,i+1)])
    temp_condprop_gates.append([cond_name, make_nboolvar(var,i), make_pboolvar(var,i+1)])
  return temp_condprop_gates

# generates gates XXX:
#-------------------------------------------------------------------------------------------
def gate_gen(constraint_list, state_vars):
  initial_state = constraint_list.pop(0)
  initial_gate = initial_gate_gen(initial_state, state_vars)
  #print(initial_gate)
  goal_state = constraint_list.pop(0)
  goal_gate = goal_gate_gen(goal_state, 'g')
  #print(goal_gate)
  act_imp_gates = act_imp_gate_gen(constraint_list, state_vars, 1)
  cond_prop_gates = gen_cond_prop_gates(state_vars,1)
  #print(cond_prop_gates)
  return [initial_gate, goal_gate, act_imp_gates, cond_prop_gates]
#-------------------------------------------------------------------------------------------


# complete gate generation:
#-------------------------------------------------------------------------------------------
'''
Takes gate_list and returns updated gate_list
- adds exactly one constraints one moves
'''
def complete_gates_gen(gate_list):
  action_gates = list(gate_list[2])
  action_var_list = []
  for gate in action_gates:
      action_var_list.append(gate[0])
  return gate_list, action_var_list

#-------------------------------------------------------------------------------------------


def variablize_state_vars(state_vars):
  temp_state_vars = []
  for state_var  in state_vars:
    temp_state_vars.append(make_pboolvar(state_var,''))
  return temp_state_vars

# generates circuit encoding:
#-------------------------------------------------------------------------------------------
def generate_cir(domain, problem):
  constraint_list = constraints(domain, problem)
  temp_constraint_list = list(constraint_list)
  #print(temp_constraint_list)
  # extracting all state variables:
  state_vars = extract_state_vars(temp_constraint_list)
  #print(state_vars)
  # initial, goal and actions gates as a list of lists:
  gates = gate_gen(constraint_list,state_vars)

  complete_gates, actions_list = complete_gates_gen(gates)
  #print(complete_gates[0])
  #print(complete_gates[1])
  #print(complete_gates[2])
  #print(complete_gates[3])
  #print(actions_list)
  # Making state vars proper variables:
  proper_state_variables = variablize_state_vars(state_vars)
  return complete_gates, actions_list, proper_state_variables
#-------------------------------------------------------------------------------------------

# Exists block:
#-------------------------------------------------------------------------------------------
def exists_block_print(state_vars, k):
  exists_state_var_mat = []
  for i in range(k+1):
    exists_state_var_list = []
    for j in range(len(state_vars)):
      exists_state_var_list.append('S_' + str(i) + '_' + str(j+1))
    exists_state_var_mat.append(exists_state_var_list)

  exists_string = ''
  for exists_state_var_list in exists_state_var_mat:
    exists_string += ', '.join(exists_state_var_list) + ', '
  exists_string = exists_string[:-2]
  print('exists('+ exists_string + ')')
#-------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------
def forall_block_print(state_vars):
  forall_string = ''
  for i in range(1,3):
    for state_var in state_vars:
      forall_string += state_var + str(i) + ', '
  forall_string = forall_string[:-2]
  print('forall(' + forall_string + ')')
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def forall_condition_print(state_vars, k):
  g_eq_name = "g_eq_"
  g_eq_conjunction_name_list = []
  for i in range(k):
    g_eq_name_list = []
    for j in range(len(state_vars)):
      temp_name = str(i) + '_' + str(j+1)
      g_eq_name_list.append(g_eq_name + "1_" + temp_name)
      print(g_eq_name + "1_" + temp_name +  " = eq(" + state_vars[j] + str(1) + ', S_' + temp_name + ")")
    g_eq_tuple_name = ', '.join(g_eq_name_list)
    print(g_eq_name + "1_" + str(i) + " = and(" + g_eq_tuple_name + ")")
    print("\n")
    g_eq_name_list = []
    for j in range(len(state_vars)):
      temp_name = str(i+1) + '_' + str(j+1)
      g_eq_name_list.append(g_eq_name + "2_" + temp_name)
      print(g_eq_name + "2_" + temp_name +  " = eq(" + state_vars[j] + str(2) + ', S_' + temp_name + ")")
    g_eq_tuple_name = ', '.join(g_eq_name_list)
    print(g_eq_name + "2_" + str(i+1) + " = and(" + g_eq_tuple_name + ")")
    g_eq_conjunction_name_list.append("g_eq_and_1_" + str(i) + "_2_" + str(i+1))
    print("g_eq_and_1_" + str(i) + "_2_" + str(i+1) + " = and(" + g_eq_name + "1_" + str(i) + ", " +g_eq_name + "2_" + str(i+1) + ")")
    print("\n")
  print("g_eq_cond = or(" + ', '.join(g_eq_conjunction_name_list) + ")")

#-------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------


# prints cnf format to stdout:
#-------------------------------------------------------------------------------------------
def print_cir(gates, action_vars, state_vars,k):
  # Heading
  print("#qcir_intermediate_planning_format20")
  # Quantifier blocks:

  # Exists block:
  exists_block_print(state_vars, k)

  # Forall block,
  # assuming the transition is from state_vars1 -> state_vars:
  forall_block_print(state_vars)

  '''
  g_forall_comp_name = 'g_forall_comp_name'
  for i in range(k+1):
  '''
  # Output gate specification:
  print('output(g_o)')

  # Initial gate, g_i:
  initial_gate = gates.pop(0)
  #print(initial_gate)
  i_string = ', '.join(initial_gate)
  i_string = "and(" + i_string + ")"
  print('g_i = ' + i_string)

  # Goal gate, g_g:
  goal_gate = gates.pop(0)
  #print(goal_gate)
  g_string = ', '.join(goal_gate)
  g_string = "and(" + g_string + ")"
  print('g_g = ' + g_string)

  '''
  Transition gates:
  - if gates, g_t_if_*
  - then gates, g_t_then_*
  - untouched propagation gates, g_t_prop_*
  - if then gates, g_t_if_then_*
  - AmoAlo gate, g_t_amoalo
  - final transtion gate, g_t_final
  '''
  #print(action_gates)


  # If gates, g_t_if_*:
  g_t_if_name = "g_t_if_"
  g_t_if_count = 0
  for action_var in action_vars:
    g_t_if_count = g_t_if_count + 1
    g_t_if_string = "and(" + action_var + ")"
    print(g_t_if_name + str(g_t_if_count) + " = " + g_t_if_string)

  # Then gates, g_t_then_*:
  g_t_then_name = "g_t_then_"
  g_t_then_count = 0
  action_gates = gates.pop(0)
  for action_gate in action_gates:
    g_t_then_count = g_t_then_count + 1
    g_t_then_string = ', '.join(action_gate[1])
    g_t_then_string = "and(" + g_t_then_string + ")"
    print(g_t_then_name + str(g_t_then_count) + " = " + g_t_then_string)

  # Untouched propagation gates, g_t_prop_*:
  g_t_prop_name = "g_t_prop_"
  g_t_prop_count = 0
  untouch_prop_gates = gates.pop(0)
  for prop_gate in untouch_prop_gates:
    g_t_prop_count = g_t_prop_count + 1
    g_t_prop_string = ', '.join(prop_gate)
    g_t_prop_string = "and(" + g_t_prop_string + ")"
    print(g_t_prop_name + str(g_t_prop_count) + " = " + g_t_prop_string)
    #print(prop_gate)

  # If then gates, g_t_if_then_*:
  g_t_if_then_name = "g_t_if_then_"
  g_t_if_then_count = 0
  for action_var in action_vars:
    g_t_if_then_count = g_t_if_then_count + 1
    g_t_if_then_string = "it(" + g_t_if_name + str(g_t_if_then_count) + ", " + g_t_then_name + str(g_t_if_then_count) + ")"
    print(g_t_if_then_name + str(g_t_if_then_count) + " = " + g_t_if_then_string)

  # AmoAlo gate, g_t_amoalo:
  if_var_string = ''
  for i in range(len(action_vars)):
      if_var_string += g_t_if_name + str(i+1) + ", "
  if_var_string = if_var_string[:-2]
  print("g_t_amoalo = amoalo(" + if_var_string + ")")
  # Final transtion gate, g_t_final
  if_then_var_string = ''
  for i in range(len(action_vars)):
      if_then_var_string += g_t_if_then_name + str(i+1) + ", "
  #if_then_var_string = if_then_var_string[:-2]
  # for untouched prop:
  untouched_prop_var_string = ''
  for i in range(len(untouch_prop_gates)):
      untouched_prop_var_string += g_t_prop_name + str(i+1) + ", "
  print("g_t_final = and(" + if_then_var_string + untouched_prop_var_string + "g_t_amoalo)")
  # If the conditions in forall quantifier then transition:
  forall_condition_print(state_vars, k)
  print("g_cond_t_final = or(-g_eq_cond, g_t_final)")
  # Output gate, g_o:
  print("g_o = and(g_i, g_g, g_cond_t_final)")
#-------------------------------------------------------------------------------------------


if __name__ == '__main__':
  import sys, time
  #start_time = time.time()
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  gates, action_vars, state_vars = generate_cir(domain, problem)
  print_cir(gates, action_vars, state_vars,k)
