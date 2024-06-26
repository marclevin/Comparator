import ast
from typing import List
from ChangeVector import ChangeVector
from astTools import deepcopy
# The State class holds all the relevent information for a solution state

class State:
	id = None
	name = None
	score = None
	feedback = None

	fun = None 
	loadedFun = None
	tree = None

	def __cmp__(this, other):
		if not isinstance(other, State):
			return -1
		c1 = cmp(this.fun, other.fun)
		c2 = cmp(this.name, other.name)
		c3 = cmp(this.id, other.id)
		return c1 if c1 != 0 else c2 if c2 != 0 else c3

	def deepcopy(this):
		s = State()
		s.id = this.id
		s.name = this.name
		s.score = this.score
		s.fun = this.fun
		s.tree = deepcopy(this.tree)

		properties = ["count", "goal", "goal_id", "goalDist",
						"next", "next_id", "edit", "hint", "treeWeight"]
		for prop in properties:
			if hasattr(this, prop):
				setattr(s, prop, getattr(this, prop))
		return s

class OriginalState(State):
	canonicalId = None

	def deepcopy(this):
		s = OriginalState()
		s.id = this.id
		s.canonicalId = this.canonicalId
		s.name = this.name
		s.score = this.score
		s.fun = this.fun
		s.tree = deepcopy(this.tree)

		properties = ["count", "goal", "goal_id", "goalDist",
						"next", "next_id", "edit", "hint", "treeWeight"]
		for prop in properties:
			if hasattr(this, prop):
				setattr(s, prop, getattr(this, prop))
		return s

class CanonicalState(State):
	count = 0 # how many students have submitted this state before?

	goal = None # the eventual goal state for this student
	goalDist = -1
	goal_id = None

	next = None # the next state in the solution space
	next_id = None
	edit = None # the changes on the edge to the next state


class CodeState(State):
    original_ast : ast = None
    goal : State = None # the eventual goal state for this student
    distance_to_goal : int = -1
    edit : List[ChangeVector] = None # the changes on the edge to the next state
    # Constructor
    def __init__(self, tree):
        self.tree = tree
        
	
 
class IntermediateState(State):
    distance_to_goal = -1
    distance_to_original = -1
    change_vectors : list = None
    
    def __init__(self, change_vectors = None, tree = None):
        self.change_vectors = change_vectors
        self.tree = tree
        
  
    
    
class GoalState(State):
    goal_ast: ast = None
    def __init__(self, goal_ast) -> None:
        self.goal_ast = goal_ast
		
    
    
	