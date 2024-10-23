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

from typing import Dict, Tuple

UNCOVER = AI.Action.UNCOVER
FLAG = AI.Action.FLAG
UNFLAG = AI.Action.UNFLAG
LEAVE = AI.Action.LEAVE

class Queue:
	'''
	A basic queue data structure.
	'''
	def __init__(self):
		self.queue = []
	
	def put(self, item):
		self.queue.append(item)
	
	def get(self):
		if len(self.queue) == 0:
			return None
		return self.queue.pop(0)
	
	def view(self):
		if len(self.queue) == 0:
			return None
		return self.queue[0]
	
	def __len__(self):
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
		'''
		if number != -1:
			cell = self.to_explore.get()
			self.explored[cell.pos] = cell.toCS(number)

			if number == 0:
				for adj_cell in self.getAdjCells(cell.pos):
					if adj_cell not in self.explored:
						self.to_explore.put(PeformAction(UNCOVER, adj_cell))
		# 	else:
		# 		adj_cells = self.getAdjCells(cell.pos)
		# 		flagged = 0
		# 		for adj_cell in adj_cells:
		# 			if adj_cell in self.explored and self.explored[adj_cell].flagged:
		# 				flagged += 1
		# 		if flagged == number:
		# 			for adj_cell in adj_cells:
		# 				if adj_cell not in self.explored:
		# 					self.to_explore.put(PeformAction(FLAG, adj_cell))
		# 		elif len(adj_cells) - flagged == number:
		# 			for adj_cell in adj_cells:
		# 				if adj_cell not in self.explored:
		# 					self.to_explore.put(PeformAction(UNCOVER, adj_cell))
		# else:
		# 	cell = self.to_explore.get()
		# 	self.explored[cell.pos] = cell.toCS(-1)

		next_move : PeformAction = self.to_explore.view()
		if next_move is None:
			return Action(LEAVE, 0, 0)
		while next_move.action == UNCOVER and next_move in self.explored:
			self.to_explore.get()
			next_move = self.to_explore.view()
			if next_move is None:
				return Action(LEAVE, 0, 0)
		return next_move.toAction()


if __name__ == '__main__':
	test = MyAI(5, 5, 5, 1, 1)
	print(test.getAdjCells((2, 2)))
	pass