from typing import *
from utils import *

def bfs(init: State, goal: State) -> Tuple[List[State], List[Action]]:
    
    queue = [init]
    while True:
        cur_state = queue.pop(0)
        
        if cur_state.satisfiesGoal(goal=goal):
            return cur_state.unravel()
        
        queue.extend(cur_state.nextStates())