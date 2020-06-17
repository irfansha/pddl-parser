# Irfansha Shaik, 17.06.2020, Aarhus
'''
Using source file "planner.py" as base
url: https://github.com/pucrs-automated-planning/pddl-parser
commit id: 38cc9aa48208d396f4373198ef354918f548e7de
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

if __name__ == '__main__':
    import sys, time
    start_time = time.time()
    domain = sys.argv[1]
    problem = sys.argv[2]
    clause_list = constraints(domain, problem)
    print('Time: ' + str(time.time() - start_time) + 's')
    print('clauses:')
    for clause in clause_list:
       print(clause)
