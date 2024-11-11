# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action

from typing import Dict, Tuple, TypeVar, Generic

UNCOVER = AI.Action.UNCOVER
FLAG = AI.Action.FLAG
UNFLAG = AI.Action.UNFLAG
LEAVE = AI.Action.LEAVE

T = TypeVar('T')

class Queue(Generic[T]):
	'''
	A basic queue data structure.
	'''
	def __init__(self):
		self.queue = []
	
	def put(self, item : T):
		self.queue.append(item)
	
	def pop(self) -> T | None:
		if len(self.queue) == 0:
			return None
		return self.queue.pop(0)
	
	def peek(self) -> T | None:
		if len(self.queue) == 0:
			return None
		return self.queue[0]
	
	def __len__(self) -> int:
		return len(self.queue)


class PeformAction:
	'''
	Contains the action to be performed, the position of the cell, and the value.
	'''
	def __init__(self, action: AI.Action, pos: tuple, value: int = None):
		self.action = action
		self.pos = pos
		self.value = value

	def toAction(self) -> Action:
		return Action(self.action, self.pos[0], self.pos[1])

	def toCS(self, value) -> 'CellStore':
		'''
		A value of -1 indicates that the cell is flagged.
		'''
		return CellStore(self.pos, value)

	def __str__(self):
		return f'Action: {self.action}, Position: {self.pos}, Value: {self.value}'
	
	def __repr__(self):
		return self.__str__()
	
	def __hash__(self) -> int:
		return hash(self.pos)

	def __eq__(self, other : tuple) -> bool:
		if isinstance(other, tuple):
			return self.pos == other
		return self.pos == other.pos
	
class CellStore:
	'''
	Stores the position of the cell and the value of the cell.
	'''
	def __init__(self, pos: tuple, value: int):
		self.pos = pos
		self.value = value
		self.flagged = value == -1

	def __str__(self):
		return f'Position: {self.pos}, Value: {self.value}'
	
	def __repr__(self):
		return self.__str__()
	
	def __hash__(self) -> int:
		return hash(self.pos)
	
	def __eq__(self, other) -> bool:
		if isinstance(other, tuple):
			return self.pos == other
		return self.pos == other.pos

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self.grid_dim = (rowDimension, colDimension)
		self.totalMines = totalMines
		self.explored : Dict[Tuple, CellStore] = {}
		self.to_explore : Queue[PeformAction] = Queue()
		self.to_explore.put(PeformAction(UNCOVER, (startX, startY)))
		pass

	
	def getAdjCells(self, pos: tuple) -> list:
		'''
		Returns a list of adjacent cells to the given position.
		The cells are 0-indexed.
		'''
		row, col = pos
		adj_cells = []
		for i in range(-1, 2):
			for j in range(-1, 2):
				if i == 0 and j == 0:
					continue
				if 0 <= row + i < self.grid_dim[0] and 0 <= col + j < self.grid_dim[1]:
					adj_cells.append((row + i, col + j))
		return adj_cells
		
	def getAdjUnexplored(self, pos: tuple) -> list:
		pass


	def getAction(self, number: int) -> Action:
		'''
		This function is called repeatedly until the game ends.
		If you perform an uncover action, the input to the next call of getAction 
		will be the number of mines adjacent to that cell (that is what the number arg is).
		If you perform a flag action, the next input will be -1.

		Valid actions are:
		- Action.UNCOVER : number = mines adjacent to this cell
		- Action.FLAG   : number = -1
		- Action.UNFLAG : number = -1
		- Action.LEAVE : exits the game

		Logical method:

		1. If number is 0, uncover all adjacent cells
		2. If a cell is explored and unexplored cells are equal to the number of mines, flag all unexplored cells
		3. If a cell is explored and the number of flags adjacent to the cell is equal to the number of mines, uncover all unexplored cells
		
		In a bit more detail:
		1. We start from a safe place.
		2. Explore all surrounding 9 cells.
		3. If there are any 0's continue expanding those cells and expanding
		4. Once all 0 cells are expanded, go to the cell with the largest number.
		5. Check if the amount of unexplored cells around it is equal to the number.
			5b. A cell is considered explored if it is flagged as a bomb or if it simply explored.
			5c. If it is, flag it as a bomb.
		6. Check if the the number of flagged cells around a cell is equal to its number.
			6b. If it is, explore all the cells around it which are not flagged.
		7. Move to the next largest number. (Keep all explored cells in a priority queue?)
		8. Once the area surrounding a cell is fully explored (meaning only flagged or explored cells around it) 
			set a flag to True for the cell.

		This requires:
			 - A list with all explored cells (position, value, flagged, fully explored)
			 - A priority queue by value for explored cells to check
			 	- A cell is only popped from the list when it is fully explored
					(meaning all cells around it are explored or it is flagged)


		'''
		cell = self.to_explore.pop()
		self.explored[cell.pos] = cell.toCS(number)
		adj_cells = self.getAdjCells(cell.pos)

		if number == 0:
			for adj_cell in adj_cells:
				if adj_cell not in self.explored:
					self.to_explore.put(PeformAction(UNCOVER, adj_cell))
		

		next_move : PeformAction = self.to_explore.peek()
		if next_move is None:
			return Action(LEAVE, 0, 0)
		while next_move.action == UNCOVER and next_move in self.explored:
			self.to_explore.pop()
			next_move = self.to_explore.peek()
			if next_move is None:
				return Action(LEAVE, 0, 0)
		return next_move.toAction()


if __name__ == '__main__':
	test = MyAI(5, 5, 5, 1, 1)
	print(test.getAdjCells((2, 2)))
	pass