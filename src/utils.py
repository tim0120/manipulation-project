from typing import *
from copy import deepcopy
from enum import Enum

class Pose:
    def __init__(self, name, position=None) -> None:
        self.id = id(self)
        self.position = position
        self.name = name
    
    def __repr__(self) -> str:
        return f"Pose(name={self.name})"

    def __eq__(self, other: 'Pose') -> bool:
        return self.id == other.id
        
    # necessary for creating Environment with Poses
    def __hash__(self) -> int:
        return self.id
        
class Object:
    def __init__(self,
                 pose: Pose,
                 objId: Optional[int] = None) -> None:
        # Object id
        if objId:
            self.id = objId
        else:
            self.id = id(self)
        # pose of object (should just be position/general region (eg quadrant) for this?)
        self.pose = pose
    
    def __repr__(self) -> str:
        return f"Object(id={self.id}, pose={self.pose})"

class Environment:
    def __init__(self, locations: List[Pose]) -> None:
        # symbolic locations
        self.locations = set(locations)

class ActionType(Enum):
    MOVE_PICK = 1
    MOVE_PLACE = 2

class State:
    def __init__(self,
                 objects: List[Object],
                 env: Environment,
                 parent: Optional['State'] = None,
                 prevAction: Optional['Action'] = None,
                 holding: Optional[Object] = None,
                 isGoal: Optional[bool] = False) -> None:
        # None iff initial state
        self.parent = parent
        # Action taken to get to State
        if parent is None:
            assert(prevAction is None)
        self.prevAction = prevAction

        # dictionary of Poses of objects
        self.objects = {obj.id: obj for obj in objects}
        self.env = env

        # if holding Object, is Object, else is None
        self.holding = holding

        self.isGoal = isGoal
    
    def unravel(self) -> Tuple[List['State'], List['Action']]:
        if self.parent == None:
            return [self], []
        parents, parent_actions = self.parent.unravel()
        return parents + [self], parent_actions + [self.prevAction]

    def nextStates(self) -> List['State']:
        nextStates = []
        if self.holding:
            actionType = ActionType.MOVE_PLACE
            for loc in self.env.locations:
                preconditions = Preconditions(actionType=actionType, desiredPose=loc, holding=self.holding)
                effects = Effects(actionType=actionType, desiredPose=loc, obj=self.holding)                
                action = Action(actionType=actionType,
                                preconditions=preconditions,
                                effects=effects)
                nextState = action.do(self)
                if nextState is not None:
                    nextStates.append(nextState)
        else:
            actionType = ActionType.MOVE_PICK
            preconditions = Preconditions(actionType=actionType, holding=self.holding)
            for obj in self.objects.values(): 
                effects = Effects(actionType=actionType, obj=obj)                
                action = Action(actionType=actionType,
                                preconditions=preconditions,
                                effects=effects)
                nextStates.append(action.do(self))
        return nextStates
    
    def satisfiesGoal(self, goal: 'State') -> bool:
        assert(goal.isGoal)
        for objId, obj in goal.objects.items():
            if self.objects[objId].pose != obj.pose:
                return False
        if self.holding != goal.holding:
            return False
        return True

    def __repr__(self) -> str:
        return f"State(objects={self.objects}, prevAction={self.prevAction}, holding={self.holding}"

    def __str__(self) -> str:
        return (
            f"State(\n"
            f"\tobjects={self.objects},\n"
            # f"\tparent={self.parent},\n"
            f"\tprevAction={self.prevAction},\n"
            f"\tholding={self.holding}\n"
            ")"
        )


class Preconditions:
    def __init__(self,
                 actionType: ActionType,
                 holding: Optional[Object] = None,
                 desiredPose: Optional[Pose] = None) -> None:
        self.actionType = actionType
        self.holding = holding
        self.desiredPose = desiredPose

        match actionType:
            case ActionType.MOVE_PICK:
                assert(holding is None)
            case ActionType.MOVE_PLACE:
                assert(holding is not None)

    def satisfied(self, state: State) -> bool:
        if self.holding != state.holding:
            return False
        # ensure that there is no Object in desired location
        if self.actionType is ActionType.MOVE_PLACE:
            for obj in state.objects.values():
                if type(obj.pose) == type(self.desiredPose) and obj.pose == self.desiredPose:
                    return False
        return True
    
class Effects:
    def __init__(self,
                 actionType: ActionType,
                 desiredPose: Optional[Pose] = None,
                 obj: Optional[Object] = None) -> None:
        self.actionType = actionType
        self.desiredPose = desiredPose 
        self.obj = obj

        match actionType:
            case ActionType.MOVE_PICK:
                assert(desiredPose is None)
                assert(obj is not None)
            case ActionType.MOVE_PLACE:
                assert(desiredPose is not None)
                assert(obj is not None)

    def apply(self, state: State) -> None:
        match self.actionType:
            case ActionType.MOVE_PICK:
                state.holding = self.obj
            case ActionType.MOVE_PLACE:
                state.objects[self.obj.id] = Object(objId=self.obj.id, pose=self.desiredPose)
                state.holding = None

    def __repr__(self) -> str:
        return f"Effects(actionType={self.actionType}, desiredPose={self.desiredPose}, obj={self.obj})"

class Action:
    def __init__(self,
                 actionType: ActionType,
                 preconditions: Preconditions,
                 effects: Effects) -> None:
        self.actionType = actionType
        self.preconditions = preconditions
        self.effects = effects
    
    def do(self, state: State) -> State | None:
        # check that preconditions are met
        if not self.preconditions.satisfied(state):
            return None
        # advance to and return next state
        child = deepcopy(state)
        child.parent = state
        child.prevAction = self
        self.effects.apply(child)
        return child
    
    def __repr__(self) -> str:
        return f"Action(actionType={self.actionType}, effects={self.effects})"