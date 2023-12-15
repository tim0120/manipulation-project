from typing import *
from utils import *
from bfs import *

q1 = Pose('1')
q2 = Pose('2')
q3 = Pose('3')
q4 = Pose('4')

block1 = Object(q1)
block2 = Object(q2)
block3 = Object(q3)

env = Environment(
    locations=[q1, q2, q3]
    # locations=[q1, q2, q3, q4]
)

# simple 1 pick, 1 place
initState = State(objects=[block1, block2], env=env)
goalState = State(objects=[Object(pose=q2, objId=block1.id), Object(pose=q1, objId=block2.id)], env=env, isGoal=True)

states, actions = bfs(init=initState, goal=goalState)
for s in states:
    print(s)
for a in actions:
    print(a)