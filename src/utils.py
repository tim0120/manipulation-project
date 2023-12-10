from typing import *
from copy import deepcopy
from enum import Enum

class Pose:
    def __init__(self, position=None) -> None:
        self.position = position
        
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

class Environment:
    def __init__(self,
                 objects: List[Object],
                 locations: List[str]) -> None:
        # Object ids
        self.objectIds = {obj.id for obj in objects}
        # symbolic locations
        self.locations = set(locations)

class ActionType(Enum):
    MOVE_PICK = 1
    MOVE_PLACE = 2

class State:
    def __init__(self,
                 env: Environment,
                 objects: List[Object],
                 gripPose: Optional[Pose] = None,
                 parent: Optional['State'] = None,
                 prevAction: Optional['Action'] = None,
                 holding: Optional[Object] = None) -> None:
        # None iff initial state
        self.parent = parent
        # Action taken to get to State
        if parent is None:
            assert(prevAction is None)
        self.prevAction = prevAction
        # Pose of gripper
        if parent is None:
            assert(gripPose)
        self.gripPose = gripPose
        # dictionary of Poses of objects
        self.objPoses = {obj.id: obj.pose for obj in objects}
        # check that Objects in State match Objects in Environment
        assert(all([objId in env.objectIds for objId in self.objPoses.keys()]))
        #check that there are the same number of Objects in the State and the Environment
        assert(len(self.objPoses) == len(env.objectIds))

        # if holding Object, is Object, else is None
        self.holding = holding
    
    def satisfies(self, preconditions: 'Preconditions') -> bool:
        preHold = self.holding == preconditions.holding
        prePose = preconditions.gripPose is None or self.gripPose == preconditions.gripPose
        preObj = preconditions.obj is None or self.obj == preconditions.obj
        return preHold and prePose and preObj
    
    # def actions(self) -> List['Action']:

class Preconditions:
    def __init__(self,
                 actionType: ActionType,
                 gripPose: Pose,
                 holding: Optional[Object] = None,
                 obj: Optional[Object] = None) -> None:
        self.actionType = actionType
        self.gripPose = gripPose
        self.holding = holding
        self.obj = obj

class Effects:
    def __init__(self,
                 actionType: ActionType,
                 pose1: Pose,
                 pose2: Optional[Pose] = None,
                 obj: Optional[Object] = None) -> None:
        self.actionType = actionType
        self.pose1 = pose1
        self.pose2 = pose2
        self.obj = obj

class Action:
    def __init__(self,
                 actionType: ActionType,
                 preconditions: Preconditions,
                 effects: Effects) -> None:
        self.actionType = actionType
        
        # check to make sure that the Preconditions matches the ActionType
        # GRIPPOSE USED TO BE OPTIONAL ON PRECONDITIONS, WHY??????
        if preconditions.actionType == ActionType.MOVE_PICK:
            assert(preconditions.holding is None)
            assert(preconditions.obj is not None)
        elif preconditions.actionType == ActionType.MOVE_PLACE:
            assert(preconditions.holding is not None)
            assert(preconditions.obj is None) # Is this what I want?
        self.preconditions = preconditions
        
        # check to make sure that the Effects match the ActionType
        match effects.actionType:
            case ActionType.MOVE_PICK:
                assert()
                assert(effects.pose2)
            case ActionType.MOVE_PLACE:
                assert(effects.pose1)
                assert(effects.pose2)
                assert(effects.obj)
        self.effects = effects
    
    def do(self, state: State) -> State | None:
        # check that preconditions are met
        if not state.satisfies(self.preconditions):
            return None
        # advance to and return next state
        child = deepcopy(state)
        child.parent = state
        child.prevAction = self
        match self.actionType:
            case ActionType.MOVEF | ActionType.MOVEH:
                child.gripPose = self.effects.pose2
            case ActionType.PICK:
                child.holding = self.effects.obj
                child.objPoses[self.effects.obj] = None
            case ActionType.PLACE:
                child.holding = None
                child.objPoses[self.effects.obj] = self.effects.pose
        return child
