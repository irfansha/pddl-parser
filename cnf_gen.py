# Irfansha Shaik, 17.06.2020, Aarhus
'''
Using source file "planner.py" as base
url: https://github.com/pucrs-automated-planning/pddl-parser
commit id: 38cc9aa48208d396f4373198ef354918f548e7de
'''

'''
Todos:
  - Add clause generator function
  - Add boolean variable creator function
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

def make_boolvar(tup, i):
  var = ''
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
def initial_state_cnf_gen(state):
  initial_clauses = []
  for atom in state:
    var = make_boolvar(atom,1)
    initial_clauses.append(var)
  return initial_clauses

def goal_state_cnf_gen(state):
  print(state)
  return []

def act_cnf_gen(constraints_list):
  return []

def cnfgen(constraint_list):
  initial_state = constraint_list.pop(0)
  #print("Initial state: ", initial_state)
  initial_clauses = initial_state_cnf_gen(initial_state)
  print(initial_clauses)
  goal_state = constraint_list.pop(0)
  goal_state_cnf_gen(goal_state)
  #print("Goal state: ", goal_state)

  #print('clauses:')
  #for clause in constraint_list:
  #   print(clause)
  return []

if __name__ == '__main__':
  import sys, time
  #start_time = time.time()
  domain = sys.argv[1]
  problem = sys.argv[2]
  constraint_list = constraints(domain, problem)
  #print('Time: ' + str(time.time() - start_time) + 's')

  cnf = cnfgen(constraint_list)
  print(cnf)
