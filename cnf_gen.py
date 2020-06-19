# Irfansha Shaik, 17.06.2020, Aarhus
'''
Using source file "planner.py" as base
url: https://github.com/pucrs-automated-planning/pddl-parser
commit id: 38cc9aa48208d396f4373198ef354918f548e7de
'''

'''
Todos:
  - update the number of steps for actions from one to k-1
  - add exactly one constraints for moves
  - Update to include propagated boolean variable in time ("untouched" by action)
'''


from PDDL import PDDL_Parser

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
  # Appending intial state clauses:
  clause_list.append(state)

  goal_pos = parser.positive_goals
  goal_not = parser.negative_goals
  # Appending goal state clauses:
  clause_list.append([goal_pos, goal_not])

  # Grounding process
  ground_actions = []
  for action in parser.actions:
    for act in action.groundify(parser.objects):
      ground_actions.append(act)
  # Appending grounded actions:
  for act in ground_actions:
    clause_list.append(act)
  return clause_list

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

'''
Generates clauses with boolean variables for initial state,
time step is considered 1:
'''
def initial_clause_gen(state):
  initial_clauses = []
  for atom in state:
    var = make_pboolvar(atom,1)
    initial_clauses.append(var)
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

def act_imp_clauses_gen(constraints_list,i):
  imp_clauses = []
  for constraint in constraints_list:
    name = constraint.name + "_" + make_pboolvar(constraint.parameters,i)
    action_var =  name
    temp_imp_clauses = []
    for cond in constraint.positive_preconditions:
      temp_imp_clauses.append(make_pboolvar(cond,i))
    for cond in constraint.negative_preconditions:
      temp_imp_clauses.append(make_nboolvar(cond,i))
    for cond in constraint.add_effects:
      temp_imp_clauses.append(make_pboolvar(cond,i+1))
    for cond in constraint.del_effects:
      temp_imp_clauses.append(make_nboolvar(cond,i+1))
    imp_clauses.append([action_var, temp_imp_clauses])
  return imp_clauses
def act_cnf_gen(constraints_list):
  return []

def clause_gen(constraint_list, k):
  initial_state = constraint_list.pop(0)
  initial_clauses = initial_clause_gen(initial_state)
  #print(initial_clauses)
  goal_state = constraint_list.pop(0)
  goal_clauses = goal_clause_gen(goal_state, k)
  #print(goal_clauses)
  act_imp_clauses = act_imp_clauses_gen(constraint_list, 1)
  return [initial_clauses, goal_clauses, act_imp_clauses]

if __name__ == '__main__':
  import sys, time
  #start_time = time.time()
  domain = sys.argv[1]
  problem = sys.argv[2]
  k = int(sys.argv[3])
  constraint_list = constraints(domain, problem)
  #print('Time: ' + str(time.time() - start_time) + 's')
  # initial, goal and actions clauses as a list of lists:
  clauses = clause_gen(constraint_list,k)
