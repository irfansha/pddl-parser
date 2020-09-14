# Irfansha Shaik, 07.08.2020, Aarhus

'''
Reusing some code from cnf_gen.py
Url: https://github.com/irfansha/pddl-parser/blob/master/cnf_gen.py
Commit id: e9494e8b1db249cdbea02fe223b91c28fb59a448
'''

'''
Todos:
  - Add comments in the print
  - Preprocess the state_variables to remove '-' symbols in names
  - Build dictionary to print integers instead of verbose gates
'''

from PDDL import PDDL_Parser

# XXX refining multiple parameters:
#-------------------------------------------------------------------------------------------
def refine_gate(unrefined_gate):
  temp_refined_gate = []
  for gate in unrefined_gate:
    if (len(gate) <=2):
      temp_refined_gate.append(gate)
    else:
      name = gate.pop(0)
      count = 0
      for var in gate:
        count += 1
        temp_refined_gate.append([name + '_' + str(count), var])
  #print(temp_initial_gate)
  return temp_refined_gate


#-------------------------------------------------------------------------------------------

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
  #initial_gate = refine_gate(initial_gate)
  #print(initial_gate)

  goal_pos = parser.positive_goals
  goal_not = parser.negative_goals
  goal_gate = [goal_pos, goal_not]
  #goal_gate = [refine_gate(goal_pos), refine_gate(goal_not)]
  #print(goal_gate)

  #for act in parser.actions:
  #  #print(act)
  #  act.positive_preconditions = refine_gate(act.positive_preconditions)
  #  act.negative_preconditions = refine_gate(act.negative_preconditions)
  #  act.add_effects = refine_gate(act.add_effects)
  #  act.del_effects = refine_gate(act.del_effects)
  #  #print(act)

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
  condprop_names = []
  for var in state_vars:
    cond_name = '-' + make_compboolvar(var,i,i+1)
    condprop_names.append(make_compboolvar(var,i,i+1))
    temp_condprop_gates.append([cond_name, make_pboolvar(var,i), make_nboolvar(var,i+1)])
    temp_condprop_gates.append([cond_name, make_nboolvar(var,i), make_pboolvar(var,i+1)])
  return temp_condprop_gates, condprop_names

# generates gates:
#-------------------------------------------------------------------------------------------
def gate_gen(constraint_list, state_vars):
  initial_state = constraint_list.pop(0)
  initial_gate = initial_gate_gen(initial_state, state_vars)
  #print(initial_gate)
  goal_state = constraint_list.pop(0)
  goal_gate = goal_gate_gen(goal_state, 'g')
  #print(goal_gate)
  act_imp_gates = act_imp_gate_gen(constraint_list, state_vars, 1)
  cond_prop_gates, cond_prop_names = gen_cond_prop_gates(state_vars,1)
  #print(cond_prop_gates)
  return [initial_gate, goal_gate, act_imp_gates, cond_prop_gates, cond_prop_names]
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
def exists_block_print(state_vars, k, var_map, var_count):
  exists_state_var_mat = []
  exists_state_var_mat_int = []
  for i in range(k+1):
    exists_state_var_list = []
    exists_state_var_list_int = []
    for j in range(len(state_vars)):
      exists_state_var_list.append('S_' + str(i) + '_' + str(j+1))
      if 'S_' + str(i) + '_' + str(j+1) not in var_map:
        var_count += 1
        var_map['S_' + str(i) + '_' + str(j+1)] = var_count
      exists_state_var_list_int.append(str(var_map['S_' + str(i) + '_' + str(j+1)]))
    exists_state_var_mat.append(exists_state_var_list)
    exists_state_var_mat_int.append(exists_state_var_list_int)

  #print(var_map)
  exists_string = ''
  for exists_state_var_list in exists_state_var_mat:
    exists_string += ', '.join(exists_state_var_list) + ', '
  exists_string = exists_string[:-2]
  print('# exists('+ exists_string + ')')
  print("\n")
  exists_int_string = ''
  for exists_state_var_list_int in exists_state_var_mat_int:
    exists_int_string += ', '.join(exists_state_var_list_int) + ', '
  exists_int_string = exists_int_string[:-2]
  print('exists('+ exists_int_string + ')')
  return var_count
#-------------------------------------------------------------------------------------------

def exists_extra_print(action_vars, untouched_prop_gates, var_map, var_count):
  exists_extra_string = ''
  exists_extra_int_string = ''

  # action vars in forall block:
  for action_var in action_vars:
    if action_var not in var_map:
      var_count += 1
      var_map[action_var] = var_count
    exists_extra_string += action_var + ', '
    exists_extra_int_string += str(var_map[action_var]) + ', '

  # Additional variables for untouched propagation gates:
  for prop_gate in untouched_prop_gates:
    if prop_gate not in var_map:
      var_count += 1
      var_map[prop_gate] = var_count
    exists_extra_string += prop_gate + ', '
    exists_extra_int_string += str(var_map[prop_gate]) + ', '

  exists_extra_string = exists_extra_string[:-2]
  exists_extra_int_string = exists_extra_int_string[:-2]
  #print(var_map, var_count)
  print('# exists(' + exists_extra_string + ')')
  print('exists(' + exists_extra_int_string + ')')
  print("\n")
  return var_count


#-------------------------------------------------------------------------------------------
def forall_block_print(state_vars, var_map, var_count):
  forall_string = ''
  forall_int_string = ''

  for i in range(1,3):
    for state_var in state_vars:
      if state_var + str(i) not in var_map:
        var_count += 1
        var_map[state_var + str(i)] = var_count
      forall_string += state_var + str(i) + ', '
      forall_int_string += str(var_map[state_var + str(i)]) + ', '

  forall_string = forall_string[:-2]
  forall_int_string = forall_int_string[:-2]
  #print(var_map, var_count)
  print('# forall(' + forall_string + ')')
  print("\n")
  print('forall(' + forall_int_string + ')')
  return var_count
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def forall_condition_print(state_vars, k, var_map, var_count):
  g_eq_name = "g_eq_"
  g_eq_conjunction_name_list = []
  g_eq_conjunction_name_int_list = []
  for i in range(k):
    g_eq_name_list = []
    g_eq_name_int_list = []
    for j in range(len(state_vars)):
      temp_name = str(i) + '_' + str(j+1)
      g_eq_name_list.append(g_eq_name + "1_" + temp_name + '_f')

      if g_eq_name + "1_" + temp_name + '_f' not in var_map:
        var_count += 1
        var_map[g_eq_name + "1_" + temp_name + '_f'] = var_count
      g_eq_name_int_list.append(str(var_map[g_eq_name + "1_" + temp_name + '_f']))

      print("# " + g_eq_name + "1_" + temp_name +  "_f = or(-" + state_vars[j] + str(1) + ', S_' + temp_name + ")")
      print(str(var_map[g_eq_name + "1_" + temp_name +  "_f"]) +" = or(-" + str(var_map[state_vars[j] + str(1)]) + ', ' + str(var_map['S_' + temp_name])+ ")")

      g_eq_name_list.append(g_eq_name + "1_" + temp_name + '_s')
      if g_eq_name + "1_" + temp_name + '_s' not in var_map:
        var_count += 1
        var_map[g_eq_name + "1_" + temp_name + '_s'] = var_count

      g_eq_name_int_list.append(str(var_map[g_eq_name + "1_" + temp_name + '_s']))

      print("# " + g_eq_name + "1_" + temp_name +  "_s = or(" + state_vars[j] + str(1) + ', -S_' + temp_name + ")")
      print(str(var_map[g_eq_name + "1_" + temp_name +  "_s"]) +" = or(" + str(var_map[state_vars[j] + str(1)]) + ', ' + str(-var_map['S_' + temp_name])+ ")")
      print("\n")

    g_eq_tuple_name = ', '.join(g_eq_name_list)
    g_eq_tuple_int_name = ', '.join(g_eq_name_int_list)

    print("#" + g_eq_name + "1_" + str(i) + " = and(" + g_eq_tuple_name + ")")
    if g_eq_name + "1_" + str(i) not in var_map:
      var_count += 1
      var_map[g_eq_name + "1_" + str(i)] = var_count
    print(str(var_map[g_eq_name + "1_" + str(i)]) + " = and(" + g_eq_tuple_int_name + ")")
    print("\n")

    g_eq_name_list = []
    g_eq_name_int_list = []

    for j in range(len(state_vars)):
      temp_name = str(i+1) + '_' + str(j+1)
      g_eq_name_list.append(g_eq_name + "2_" + temp_name + '_f')
      if g_eq_name + "2_" + temp_name + '_f' not in var_map:
        var_count += 1
        var_map[g_eq_name + "2_" + temp_name + '_f'] = var_count
      g_eq_name_int_list.append(str(var_map[g_eq_name + "2_" + temp_name + '_f']))

      print('# ' + g_eq_name + "2_" + temp_name +  "_f = or(-" + state_vars[j] + str(2) + ', S_' + temp_name + ")")

      print(str(var_map[g_eq_name + "2_" + temp_name +  "_f"]) + "= or(-" + str(var_map[state_vars[j] + str(2)]) + ', ' + str(var_map['S_' + temp_name]) + ")")

      g_eq_name_list.append(g_eq_name + "2_" + temp_name + '_s')
      if g_eq_name + "2_" + temp_name + '_s' not in var_map:
        var_count += 1
        var_map[g_eq_name + "2_" + temp_name + '_s'] = var_count
      g_eq_name_int_list.append(str(var_map[g_eq_name + "2_" + temp_name + '_s']))

      print("# " + g_eq_name + "2_" + temp_name +  "_s = or(" + state_vars[j] + str(2) + ', -S_' + temp_name + ")")
      print(str(var_map[g_eq_name + "2_" + temp_name +  "_s"]) + " = or(" + str(var_map[state_vars[j] + str(2)]) + ', ' + str(-var_map['S_' + temp_name]) + ")")
      print("\n")

    g_eq_tuple_name = ', '.join(g_eq_name_list)
    g_eq_tuple_int_name = ', '.join(g_eq_name_int_list)
    print("#" + g_eq_name + "2_" + str(i+1) + " = and(" + g_eq_tuple_name + ")")

    if g_eq_name + "2_" + str(i+1) not in var_map:
      var_count += 1
      var_map[g_eq_name + "2_" + str(i+1)] = var_count

    print(str(var_map[g_eq_name + "2_" + str(i+1)]) + " = and(" + g_eq_tuple_int_name + ")")
    print("\n")

    g_eq_conjunction_name_list.append("g_eq_and_1_" + str(i) + "_2_" + str(i+1))
    if "g_eq_and_1_" + str(i) + "_2_" + str(i+1) not in var_map:
      var_count += 1
      var_map["g_eq_and_1_" + str(i) + "_2_" + str(i+1)] = var_count

    g_eq_conjunction_name_int_list.append(str(var_map["g_eq_and_1_" + str(i) + "_2_" + str(i+1)]))


    print("# g_eq_and_1_" + str(i) + "_2_" + str(i+1) + " = and(" + g_eq_name + "1_" + str(i) + ", " +g_eq_name + "2_" + str(i+1) + ")")
    print(str(var_map["g_eq_and_1_" + str(i) + "_2_" + str(i+1)]) + " = and(" + str(var_map[g_eq_name + "1_" + str(i)]) + ", " + str(var_map[g_eq_name + "2_" + str(i+1)]) + ")")
    print("\n")
  print("# g_eq_cond = or(" + ', '.join(g_eq_conjunction_name_list) + ")")
  var_count += 1
  var_map['g_eq_cond'] = var_count
  print(str(var_map["g_eq_cond"]) + "= or(" + ', '.join(g_eq_conjunction_name_int_list) + ")")
  return var_count
#-------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------


# prints cnf format to stdout:
#-------------------------------------------------------------------------------------------
def print_cir(gates, action_vars, state_vars,k, var_map):
  var_count = 0
  # Heading
  print("#qcir_intermediate_planning_format20")
  # Quantifier blocks:
  print("\n")
  # Exists block:
  var_count = exists_block_print(state_vars, k, var_map, var_count)
  #print(var_map, var_count)
  print("\n")

  # Forall block,
  # assuming the transition is from state_vars1 -> state_vars:
  var_count = forall_block_print(state_vars, var_map, var_count)
  print("\n")

  var_count = exists_extra_print(action_vars, gates[4], var_map, var_count)


  '''
  g_forall_comp_name = 'g_forall_comp_name'
  for i in range(k+1):
  '''
  # Output gate specification:
  print('# output(g_o)')
  print("\n")

  var_count += 1
  var_map['g_o'] = var_count
  print('output(' + str(var_map['g_o']) + ')')
  print("\n")

  # Initial gate, g_i:
  initial_gate = gates.pop(0)
  #print(initial_gate)
  i_string = ''
  i_int_string = ''

  for i in range(len(initial_gate)):
    sign, name = extract_var(initial_gate[i])
    if 'S_0_' + str(i+1) not in var_map:
      var_count += 1
      var_map['S_0_' + str(i+1)] = var_count
    if sign:
      i_string += 'S_0_' + str(i+1) + ', '
      i_int_string += str(var_map['S_0_' + str(i+1)]) + ', '
    else:
      i_string += '-S_0_' + str(i+1) + ', '
      i_int_string += str(-var_map['S_0_' + str(i+1)]) + ', '

  i_string = i_string[:-2]
  i_string = "and(" + i_string + ")"
  print('# g_i = ' + i_string)
  print("\n")

  var_count += 1
  var_map['g_i'] = var_count

  i_int_string = i_int_string[:-2]
  i_int_string = "and(" + i_int_string + ")"
  print(str(var_map['g_i']) + ' = ' + i_int_string)
  print("\n")


  goal_state_vars_map = {}
  for i in range(len(state_vars)):
    goal_state_vars_map[state_vars[i] + 'g'] = i + 1

  # Goal gate, g_g:
  goal_gate = gates.pop(0)
  #print(goal_gate)
  g_string = ''
  g_int_string = ''

  for g_gate in goal_gate:
    sign, name = extract_var(g_gate)
    if 'S_' + str(k) + '_' + str(goal_state_vars_map[name]) not in var_map:
      var_count += 1
      var_map['S_' + str(k) + '_' + str(goal_state_vars_map[name])] = var_count

    if sign:
      g_string += 'S_' + str(k) + '_' + str(goal_state_vars_map[name]) + ', '
      g_int_string += str(var_map['S_' + str(k) + '_' + str(goal_state_vars_map[name])]) + ', '
    else:
      g_string += '-S_' + str(k) + '_' + str(goal_state_vars_map[name]) + ', '
      g_int_string += str(-var_map['S_' + str(k) + '_' + str(goal_state_vars_map[name])]) + ', '

  g_string = g_string[:-2]
  g_string = "and(" + g_string + ")"
  print('# g_g = ' + g_string)
  print("\n")

  var_count += 1
  var_map['g_g'] = var_count

  g_int_string = g_int_string[:-2]
  g_int_string = "and(" + g_int_string + ")"
  print(str(var_map['g_g']) + ' = ' + g_int_string)
  print("\n")



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
    print("# " + g_t_if_name + str(g_t_if_count) + " = " + g_t_if_string)
    if g_t_if_name + str(g_t_if_count) not in var_map:
      var_count += 1
      var_map[g_t_if_name + str(g_t_if_count)] = var_count
    print(str(var_map[g_t_if_name + str(g_t_if_count)]) + " = and(" + str(var_map[action_var]) + ")")
    print("\n")

  # Then gates, g_t_then_*:
  g_t_then_name = "g_t_then_"
  g_t_then_count = 0
  action_gates = gates.pop(0)
  for action_gate in action_gates:
    g_t_then_count = g_t_then_count + 1
    g_t_then_string = ', '.join(action_gate[1])
    g_t_then_int_string = ''
    for then_var in action_gate[1]:
      sign, name = extract_var(then_var)
      if sign:
        g_t_then_int_string += str(var_map[name]) + ', '
      else:
        g_t_then_int_string += str(-var_map[name]) + ', '
    g_t_then_int_string = g_t_then_int_string[:-2]

    g_t_then_string = "and(" + g_t_then_string + ")"
    print("# " + g_t_then_name + str(g_t_then_count) + " = " + g_t_then_string)
    if g_t_then_name + str(g_t_then_count) not in var_map:
      var_count += 1
      var_map[g_t_then_name + str(g_t_then_count)] = var_count
    print(str(var_map[g_t_then_name + str(g_t_then_count)]) + " = and(" + g_t_then_int_string + ")")
    print("\n")
  print("\n")

  # Untouched propagation gates, g_t_prop_*:
  g_t_prop_name = "g_t_prop_"
  g_t_prop_count = 0
  untouch_prop_gates = gates.pop(0)
  for prop_gate in untouch_prop_gates:
    g_t_prop_count = g_t_prop_count + 1
    g_t_prop_string = ', '.join(prop_gate)
    g_t_prop_int_string = ''
    for prop_var in prop_gate:
      sign, name = extract_var(prop_var)
      if sign:
        g_t_prop_int_string += str(var_map[name]) + ', '
      else:
        g_t_prop_int_string += str(-var_map[name]) + ', '
    g_t_prop_int_string = g_t_prop_int_string[:-2]

    g_t_prop_string = "or(" + g_t_prop_string + ")"
    print("# " + g_t_prop_name + str(g_t_prop_count) + " = " + g_t_prop_string)

    if g_t_prop_name + str(g_t_prop_count) not in var_map:
      var_count += 1
      var_map[g_t_prop_name + str(g_t_prop_count)] = var_count
    print(str(var_map[g_t_prop_name + str(g_t_prop_count)]) + " = or(" + g_t_prop_int_string + ")")
    print("\n")
    #print(prop_gate)
  print("\n")

  # If then gates, g_t_if_then_*:
  g_t_if_then_name = "g_t_if_then_"
  g_t_if_then_count = 0
  for action_var in action_vars:
    g_t_if_then_count = g_t_if_then_count + 1
    g_t_if_then_string = "or(-" + g_t_if_name + str(g_t_if_then_count) + ", " + g_t_then_name + str(g_t_if_then_count) + ")"
    print("# " + g_t_if_then_name + str(g_t_if_then_count) + " = " + g_t_if_then_string)
    if g_t_if_then_name + str(g_t_if_then_count) not in var_map:
      var_count += 1
      var_map[g_t_if_then_name + str(g_t_if_then_count)] = var_count
    print(str(var_map[g_t_if_then_name + str(g_t_if_then_count)]) + " = or(-" + str(var_map[g_t_if_name + str(g_t_if_then_count)]) + ", " + str(var_map[g_t_then_name + str(g_t_if_then_count)]) + ")")
  print("\n")

  # AmoAlo gate, g_t_amoalo:
  amoalo_gate_then_count = 0
  for i in range(len(action_vars)):
    temp_string = ''
    temp_int_string = ''
    for j in range(len(action_vars)):
      if i != j:
        temp_string += g_t_if_name + str(j+1) + ", "
        temp_int_string += str(var_map[g_t_if_name + str(j+1)]) + ", "

    temp_string = temp_string[:-2]
    temp_int_string = temp_int_string[:-2]

    amoalo_gate_then_count += 1
    print("# g_t_amoalo_then_"+ str(amoalo_gate_then_count) +   " = or(" + temp_string + ")")
    if "g_t_amoalo_then_"+ str(amoalo_gate_then_count) not in var_map:
      var_count += 1
      var_map["g_t_amoalo_then_"+ str(amoalo_gate_then_count)] = var_count
    print(str(var_map["g_t_amoalo_then_"+ str(amoalo_gate_then_count)]) +   " = or(" + temp_int_string + ")")
    print("\n")
  #print("g_t_amoalo = amoalo(" + if_var_string + ")")
  print("\n")

  amoalo_gate_if_then_not_count = 0
  for i in range(len(action_vars))  :
    print("# g_t_amoalo_if_then_not_" + str(i+1) + " = or(-g_t_if_" + str(i+1) + ", -g_t_amoalo_then_" + str(i+1) + ")")
    if "g_t_amoalo_if_then_not_" + str(i+1) not in var_map:
      var_count += 1
      var_map["g_t_amoalo_if_then_not_" + str(i+1)] = var_count
    print(str(var_map["g_t_amoalo_if_then_not_" + str(i+1)]) + " = or(-" + str(var_map["g_t_if_" + str(i+1)]) + ", -" + str(var_map["g_t_amoalo_then_" + str(i+1)]) + ")")
  print("\n")

  # Alo gate:
  if_var_string = ''
  if_var_int_string = ''

  for i in range(len(action_vars)):
      if_var_string += g_t_if_name + str(i+1) + ", "
      if_var_int_string += str(var_map[g_t_if_name + str(i+1)]) + ", "

  if_var_string = if_var_string[:-2]
  if_var_int_string = if_var_int_string[:-2]

  print("# g_t_alo = or(" + if_var_string + ")")

  var_count += 1
  var_map['g_t_alo'] = var_count

  print(str(var_map['g_t_alo']) + " = or(" + if_var_int_string + ")")
  print("\n")


  # Final amoalo gate:
  amoalo_string = ''
  amoalo_int_string = ''

  for i in range(len(action_vars)):
    amoalo_string += "g_t_amoalo_if_then_not_" + str(i+1) + ', '
    if "g_t_amoalo_if_then_not_" + str(i+1) not in var_map:
      var_count += 1
      var_map["g_t_amoalo_if_then_not_" + str(i+1)] = var_count
    amoalo_int_string += str(var_map["g_t_amoalo_if_then_not_" + str(i+1)]) + ', '

  print("# g_t_amoalo = and(" + amoalo_string + "g_t_alo)")

  var_count += 1
  var_map['g_t_amoalo'] = var_count
  print(str(var_map["g_t_amoalo"]) + " = and(" + amoalo_int_string + str(var_map["g_t_alo"]) + ")")
  print("\n")

  # Final transtion gate, g_t_final
  if_then_var_string = ''
  if_then_var_int_string = ''
  for i in range(len(action_vars)):
      if_then_var_string += g_t_if_then_name + str(i+1) + ", "
      if_then_var_int_string += str(var_map[g_t_if_then_name + str(i+1)]) + ", "
  #if_then_var_string = if_then_var_string[:-2]

  # for untouched prop:
  untouched_prop_var_string = ''
  untouched_prop_var_int_string = ''
  for i in range(len(untouch_prop_gates)):
    untouched_prop_var_string += g_t_prop_name + str(i+1) + ", "
    untouched_prop_var_int_string += str(var_map[g_t_prop_name + str(i+1)]) + ", "

  print("# g_t_final = and(" + if_then_var_string + untouched_prop_var_string + "g_t_amoalo)")

  var_count += 1
  var_map["g_t_final"] = var_count
  print(str(var_map["g_t_final"]) + " = and(" + if_then_var_int_string + untouched_prop_var_int_string + str(var_map["g_t_amoalo"]) + ")")
  print("\n")


  # If the conditions in forall quantifier then transition:
  var_count = forall_condition_print(state_vars, k, var_map, var_count)
  print("\n")
  print("# g_cond_t_final = or(-g_eq_cond, g_t_final)")
  var_count += 1
  var_map['g_cond_t_final'] = var_count
  print(str(var_map['g_cond_t_final']) + ' = or(-' + str(var_map['g_eq_cond']) + ", " + str(var_map['g_t_final']) + ")")
  print("\n")
  # Output gate, g_o:
  print("# g_o = and(g_i, g_g, g_cond_t_final)")
  print(str(var_map['g_o']) + " = and(" + str(var_map['g_i']) + ', ' + str(var_map['g_g']) + ", " + str(var_map['g_cond_t_final']) + ")")
#-------------------------------------------------------------------------------------------


if __name__ == '__main__':
  import sys, time
  #start_time = time.time()
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  gates, action_vars, state_vars = generate_cir(domain, problem)
  var_map = {}
  print_cir(gates, action_vars, state_vars,k, var_map)
  #print(var_map)
