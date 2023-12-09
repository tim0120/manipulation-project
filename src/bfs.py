from typing import *
from utils import *

def bfs(init: State,
        goal: State) -> Tuple[List[State], List[Action]]:
    
    states = []
    actions = []
    return states, actions

x = Pose()
y = Pose()
z = Pose()

block = Object(x)

env = Environment(
    objects=[block],
    locations=[x, y, z]
)

initState = State(
    env=env,
    gripPose=y,
    objects=[block]
)

goalState = State(
    env=env,
    gripPose=x,
    objects=[Object(pose=z, objId=block.id)]
)

a1 = Action(
    actionType=ActionType.MOVEF,
    preconditions=Preconditions(
        actionType=ActionType.MOVEF,
        gripPose=y
    ),
    effects=Effects(
        actionType=ActionType.MOVEF,
        pose1=y,
        pose2=x
    )
)

s = a1.do(initState)
print(s)
# print(s.gripPose)
# print(s.holding)
# print(a1.do(goalState))