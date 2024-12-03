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

import heapq
import random
from typing import Dict, List, Tuple, TypeVar, Generic, Any


UNCOVER = AI.Action.UNCOVER
FLAG = AI.Action.FLAG
UNFLAG = AI.Action.UNFLAG
LEAVE = AI.Action.LEAVE


class Cell:
	def __init__(self, pos: Tuple[int, int], value: int = -1, flagged: bool = False, fully_explored: bool = False):
		self.pos = pos
		self.value = value
		self.reduced_value = value
		self.flagged = flagged
		self.fully_explored = fully_explored

	def update_rd(self):
		if self.value > 0 and not self.flagged:
			self.reduced_value -= 1

	def __lt__(self, other):
		# Values less than 0 get popped first
		# Then the larger values get popped if all > 0
		# So it would be -2, -1, 4, 3, 2, 1
		# Step 1: Prioritize negative values over positive values.
		if self.reduced_value < 0 and other.reduced_value >= 0:
			return True
		elif self.reduced_value >= 0 and other.reduced_value < 0:
			return False

        # Step 2: When both are negative, order ascending (-2 before -1)
        # or when both are positive, order descending (4 before 3).
		if self.value < 0:
			return self.reduced_value < other.reduced_value
		else:
			return self.reduced_value > other.reduced_value

	def __eq__(self, other):
		if isinstance(other, tuple):
			return self.pos == other
		return self.pos == other.pos

	def __repr__(self):
		return f'Cell({self.pos}, {self.value})\n'
	
	def __str__(self):
		return self.__repr__()
	
	def __hash__(self):
		return hash(self.pos)


T = TypeVar('T')
class PriorityQueue(Generic[T]):

	def __init__(self):
		self.queue = []
		self.queue2 = []
	
	def reset(self):
		self.queue.extend(self.queue2)
		self.queue2 = []
		heapq.heapify(self.queue)

	def push(self, item: T):
		self.remove(item)
		heapq.heappush(self.queue, item)

	def pop(self) -> T:
		if self.__len__() == 0:
			return None
		if len(self.queue) == 0:
			self.queue, self.queue2 = self.queue2, self.queue
		value = heapq.heappop(self.queue)
		heapq.heappush(self.queue2, value)
		return value
	
	def peek(self) -> T:
		if self.__len__() == 0:
			return None
		return self.queue[0]

	def remove(self, item: T):
		if item in self.queue:
			self.queue.remove(item)
			heapq.heapify(self.queue)
		elif item in self.queue2:
			self.queue2.remove(item)
			heapq.heapify(self.queue2)

	def __len__(self):
		return len(self.queue)

	def __repr__(self):
		return str(self.queue) + str(self.queue2)

	def __str__(self):
		return self.__repr__()
	
	def __contains__(self, item: T):
		return item in self.queue or item in self.queue2

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self.grid_dim = (rowDimension, colDimension)
		self.totalMines = totalMines
		self.explored_cells : Dict[tuple, Cell] = {}
		self.priority_queue = PriorityQueue[Cell]()
		self.pos = (startX, startY)

		self.flags = 0

		
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
				if 0 <= row + i < self.grid_dim[1] and 0 <= col + j < self.grid_dim[0]:
					adj_cells.append((row + i, col + j))
		return adj_cells
		
	def getAdjUnexplored(self, pos: tuple) -> list:
		'''
		Returns a list of adjacent unexplored cells to the given position.
		The cells are 0-indexed.
		'''
		cells = self.getAdjCells(pos)
		unexplored = []
		for cell in cells:
			if cell not in self.explored_cells:
				unexplored.append(cell)
		return unexplored
	
	def getAdjExplored(self, pos: tuple) -> list:
		'''
		Returns a list of adjacent explored cells to the given position.
		The cells are 0-indexed.
		'''
		cells = self.getAdjCells(pos)
		explored = []
		for cell in cells:
			if cell in self.explored_cells:
				explored.append(cell)
		return explored
	
	def getAdjFlagged(self, pos: tuple) -> list:
		'''
		Returns a list of adjacent flagged cells to the given position.
		The cells are 0-indexed.
		'''
		cells = self.getAdjCells(pos)
		flagged = []
		for cell in cells:
			if cell in self.explored_cells:
				if self.explored_cells[cell].flagged:
					flagged.append(cell)
		return flagged
	
	def respondToAction(self, cell : Cell):
		# If the cell value is -2 it needs to be flagged
		if cell.value == -2:
			self.pos = cell.pos
			return Action(FLAG, cell.pos[0], cell.pos[1])
		# If the cell value is -1 it needs to be explored
		if cell.value == -1:
			self.pos = cell.pos
			return Action(UNCOVER, cell.pos[0], cell.pos[1])
		# If the cell is fully explored, we can remove it from the queue
		if cell.fully_explored:
			self.priority_queue.remove(cell)
			return 'continue'

	def respondToPreviousAction(self, number : int):
		if number == 0:
			# This means we just uncovered a completely safe cell.
			self.priority_queue.remove(Cell(self.pos))
			self.explored_cells[self.pos] = Cell(self.pos, number, False, True)
			adj_cells = self.getAdjUnexplored(self.pos)
			for cell in adj_cells:
				if cell not in self.priority_queue:
					self.priority_queue.push(Cell(cell))
		elif number == -1:
			# This means we just flagged the previous cell.
			self.priority_queue.remove(Cell(self.pos))
			self.explored_cells[self.pos] = Cell(self.pos, -2, True, False)
			self.flags += 1
			# We can now reduce the value of all adjacent cells by 1
			adj_cells = self.getAdjExplored(self.pos)
			for cell in adj_cells:
				self.explored_cells[cell].update_rd()
				cell = self.explored_cells[cell]
				if cell in self.priority_queue:
					self.priority_queue.push(cell)
		else:
			# This means we just uncovered a cell with a number.
			temp_cell = Cell(self.pos, number, False, False)
			adj_cells = self.getAdjUnexplored(self.pos)
			if len(adj_cells) == 0:
				temp_cell.fully_explored = True
			# We can now check for flags around the cell and reduce the value as needed
			temp_cell.reduced_value = number - len(self.getAdjFlagged(self.pos))
			self.explored_cells[self.pos] = temp_cell
			self.priority_queue.push(temp_cell)

	def travelQueue(self, func):
		# A helper function to go through the priority queue and apply the given function.
		while len(self.priority_queue) > 0:
			cell = self.priority_queue.pop()
			action = self.respondToAction(cell)
			if action == 'continue':
				continue
			elif action:
				return action
			func(cell)

	def baseCase(self):
		# Now go through the priority queue and check if we can flag or uncover any cells.
		# This is the simplest case where the two conditions are met.
		def _basecase(cell : Cell):
			# If we are here then this is a cell with a number
			# If a cell is explored and unexplored cells are equal to the number 
			# of mines, flag all unexplored cells
			adj_cells = self.getAdjUnexplored(cell.pos)
			# flagged_cells = self.getAdjFlagged(cell.pos)
			if cell.reduced_value == len(adj_cells) and len(adj_cells) > 0:
				for adj_cell in adj_cells:
					self.priority_queue.push(Cell(adj_cell, -2))
			# If a cell is explored and the number of flags adjacent to the cell is equal 
			# to the number of mines, uncover all unexplored cells
			if cell.reduced_value == 0:
				for adj_cell in self.getAdjUnexplored(cell.pos):
					self.priority_queue.push(Cell(adj_cell))

		return self.travelQueue(_basecase)
	
	def handlePatterns(self):
		# Now go through the priority queue and check if we can apply any patterns.
		# This is the more complex case where we have to apply patterns.
		def _handlepatterns(cell : Cell):
			# 1-1, 1-1R
			result = self.oneOnePattern(cell)
			if result:
				self.priority_queue.push(Cell(result))
			result = self.oneTwoCPattern(cell)
			if result:
				for pos in result:
					self.priority_queue.push(Cell(pos, -2))
			result = self.oneTwoCPlusPattern(cell)
			if result:
				for pos in result:
					self.priority_queue.push(Cell(pos, -2))

		return self.travelQueue(_handlepatterns)
	
	def handleGuess(self):
		# If we are here, then we are in a unlucky situation where we have to guess.
		# Pick the lowest number cell with unexplored values and uncover one if its adjacent cells.
		local : List[Cell] = list(self.priority_queue.queue)
		local = sorted(local, key=lambda x: x.value)
		for cell in local:
			if len(self.getAdjUnexplored(cell.pos)) > 0:
				adj = self.getAdjUnexplored(cell.pos)
				choice = random.choice(adj)
				self.pos = choice
				return Action(UNCOVER, choice[0], choice[1])
		return Action(LEAVE)

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
			set a flag to True for the cell and remove it from the queue.

		This requires:
			 - A dictionary with all explored cells (position, value, flagged, fully explored)
			 - A rotating priority queue by value for explored cells to check
			 	- This is two priority queues, when moving through we pop to the other queue.

		'''
		self.respondToPreviousAction(number)
		self.priority_queue.reset()

		action = self.baseCase()
		if action: return action
		self.priority_queue.reset()

		action = self.handlePatterns()
		if action: return action
		self.priority_queue.reset()

		return self.handleGuess()

	'''
	PATTERNS
	'''
	def oneOnePattern(self, cell : Cell):
		'''
		If the given position follows a 1-1 / 1-1R pattern, return the position of the cell that can be uncovered. 
		Otherwise, return False.
		'''
		# The left one is touching 2 cells. the right one is also touching those two cells. therefore we can open the third cell
		# . . . <- open this cell
		# 1 1 

		def checkOne(cell : Cell):
			return cell.reduced_value == 1 and not cell.flagged

		pos = cell.pos
		#cell value needs to be a one or needs to reduce to one
		if not checkOne(cell):
			return False		
		#there has to be 2 unexplored cells in this pattern
		if len(self.getAdjUnexplored(pos)) != 2:
			return False
		
		adjcells = self.getAdjCells(pos) 
		for cell in adjcells:
			#find a cell with value one that is in the same x or y as our current cell
			if cell in self.explored_cells and checkOne(self.explored_cells[cell]) and (cell[0] == pos[0] or cell[1] == pos[1]):
				targetUnxAdjCells = self.getAdjUnexplored(cell)
				ogUnxAdjCells = self.getAdjUnexplored(pos)
				#they need to share 2 cells
				if len(set(targetUnxAdjCells).intersection(set(ogUnxAdjCells))) != 2:
					continue
				for target in targetUnxAdjCells:
					targetpos = ogUnxAdjCells[0]
					#find possible third cells that are lined up
					if target not in ogUnxAdjCells:
						if target[0] == targetpos[0] or target[1] == targetpos[1]:
							return target

	def oneTwoCPattern(self, cell: Cell):
		"""
		Implements the 1-2C pattern. If applicable, return the position of the flagged cell.
		Otherwise, return False.
		
		Logic:
		1. The given cell must have a reduced value of 1 (and not be flagged).
		2. Find a neighboring cell with a reduced value of 2 (and not flagged).
		3. Identify shared unexplored cells between the 1 and the 2.
		4. If shared cells are fewer than or equal to the number allowed by the 1, proceed.
		5. Deduce the remaining unexplored cell(s) adjacent to the 2 as potential mines.
		"""
		# The cell must be a 1 and not flagged
		if cell.reduced_value != 1 or cell.flagged:
			return False

		# Check adjacent cells for a "2"
		for neighbor_pos in self.getAdjCells(cell.pos):
			if neighbor_pos in self.explored_cells:
				neighbor = self.explored_cells[neighbor_pos]
				
				# Look for a neighboring cell with reduced value 2
				if neighbor.reduced_value == 2 and not neighbor.flagged:
					# Find shared unexplored cells
					shared_unexplored = [
						c for c in self.getAdjUnexplored(cell.pos)
						if c in self.getAdjUnexplored(neighbor_pos)
					]
					
					# Verify shared unexplored cells
					if len(shared_unexplored) == 2:
						# Remaining unexplored cells adjacent to the "2"
						third_cells = [
							c for c in self.getAdjUnexplored(neighbor_pos)
							if c not in shared_unexplored
						]
						
						# If exactly one cell remains, it must be a mine
						if len(third_cells) == 1:
							return [third_cells[0]]  # Return as a list
		
		return False
	
	def oneTwoCPlusPattern(self, cell: Cell):
		"""
		Implements the 1-2C+ pattern.
		If applicable, return a list of positions for cells to be flagged.
		Otherwise, return False.
		
		Logic:
		1. The given cell must have a reduced value of 1 (and not be flagged).
		2. Find a neighboring cell with a reduced value >= 3 (and not flagged).
		3. Identify shared unexplored cells between the 1 and the N.
		4. If shared cells are exactly 2, proceed.
		5. Deduce the remaining unexplored cells adjacent to the N as mines if they match the required mine count.
		"""
		# The cell must be a 1 and not flagged
		if cell.reduced_value != 1 or cell.flagged:
			return False

		# Iterate through all adjacent cells to find a neighbor with reduced_value >= 3
		for neighbor_pos in self.getAdjCells(cell.pos):
			if neighbor_pos in self.explored_cells:
				neighbor = self.explored_cells[neighbor_pos]

				# Look for a neighboring cell with reduced value >= 3 and not flagged
				if neighbor.reduced_value >= 3 and not neighbor.flagged:
					# Find shared unexplored cells between the 1 and the neighbor
					shared_unexplored = [
						c for c in self.getAdjUnexplored(cell.pos)
						if c in self.getAdjUnexplored(neighbor_pos)
					]

					# Ensure there are exactly 2 shared unexplored cells
					if len(shared_unexplored) != 2:
						continue

					# Remaining unexplored cells adjacent only to the neighbor
					remaining_cells = [
						c for c in self.getAdjUnexplored(neighbor_pos)
						if c not in shared_unexplored
					]

					# Calculate remaining mines required in the remaining_cells
					# Since Cell A (1) can have at most 1 mine in shared_unexplored
					remaining_mines = neighbor.reduced_value - 1

					# If the number of remaining cells matches the remaining mines, flag them
					if len(remaining_cells) == remaining_mines and remaining_mines > 0:
						return remaining_cells  # Already a list
		
		return False
