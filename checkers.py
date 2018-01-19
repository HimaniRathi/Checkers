from copy import deepcopy 
import random
import pygame
import sys
from pygame.locals import * 

######################## VARIABLES ########################

turn = 'white' 
selected = (0, 1) 
board = 0
move_limit = [150, 0] 

best_move = () 
black, white = (), () 

window_size = (256, 256)
background_image_filename = 'board_brown.png' 
title = 'Checkers'
board_size = 8 
left = 1 # left mouse button
fps = 5 # framerate of the scene (to save cpu time)
pause = 5 # number of seconds to pause the game for after end of game
start = True

######################## CLASSES ########################

class Piece(object):
	def __init__(self, color, king):
		self.color = color
		self.king = king

class Player(object):
	def __init__(self, type, color, ply_depth):
		self.type = type # cpu or human
		self.color = color # black or white
		self.ply_depth = ply_depth # ply depth for algorithms

######################## INITIALIZE ########################

def init_board():
	global move_limit
	move_limit[1] = 0

	result = [
	[ 0, 1, 0, 1, 0, 1, 0, 1],
	[ 1, 0, 1, 0, 1, 0, 1, 0],
	[ 0, 1, 0, 1, 0, 1, 0, 1],
	[ 0, 0, 0, 0, 0, 0, 0, 0],
	[ 0, 0, 0, 0, 0, 0, 0, 0],
	[-1, 0,-1, 0,-1, 0,-1, 0],
	[ 0,-1, 0,-1, 0,-1, 0,-1],
	[-1, 0,-1, 0,-1, 0,-1, 0]
	] 
	for m in range(8):
		for n in range(8):
			if (result[m][n] == 1):
				piece = Piece('black', False) 
				result[m][n] = piece
			elif (result[m][n] == -1):
				piece = Piece('white', False) 
				result[m][n] = piece
	return result

def init_player(type, color, ply_depth):
	return Player(type, color, ply_depth)

######################## FUNCTIONS ########################
#available moves
def avail_moves(board, player):
    moves = [] 

    for m in range(8):
        for n in range(8):
            if board[m][n] != 0 and board[m][n].color == player:
                if can_jump([m, n], [m+1, n+1], [m+2, n+2], board) == True: moves.append([m, n, m+2, n+2])
                if can_jump([m, n], [m-1, n+1], [m-2, n+2], board) == True: moves.append([m, n, m-2, n+2])
                if can_jump([m, n], [m+1, n-1], [m+2, n-2], board) == True: moves.append([m, n, m+2, n-2])
                if can_jump([m, n], [m-1, n-1], [m-2, n-2], board) == True: moves.append([m, n, m-2, n-2])

    if len(moves) == 0:
        for m in range(8):
            for n in range(8):
                if board[m][n] != 0 and board[m][n].color == player:
                    if can_move([m, n], [m+1, n+1], board) == True: moves.append([m, n, m+1, n+1])
                    if can_move([m, n], [m-1, n+1], board) == True: moves.append([m, n, m-1, n+1])
                    if can_move([m, n], [m+1, n-1], board) == True: moves.append([m, n, m+1, n-1])
                    if can_move([m, n], [m-1, n-1], board) == True: moves.append([m, n, m-1, n-1])
    return moves 

def can_jump(a, via, b, board):
    # destination off board?
    if b[0] < 0 or b[0] > 7 or b[1] < 0 or b[1] > 7:
        return False
    # does destination contain a piece already?
    if board[b[0]][b[1]] != 0: return False
    # are we jumping something?
    if board[via[0]][via[1]] == 0: return False
   
    if board[a[0]][a[1]].color == 'white':
        if board[a[0]][a[1]].king == False and b[0] > a[0]: return False # only move up
        if board[via[0]][via[1]].color != 'black': return False # only jump blacks
        return True 

    if board[a[0]][a[1]].color == 'black':
        if board[a[0]][a[1]].king == False and b[0] < a[0]: return False # only move down
        if board[via[0]][via[1]].color != 'white': return False # only jump whites
        return True 


def can_move(a, b, board):
    # is destination off board?
    if b[0] < 0 or b[0] > 7 or b[1] < 0 or b[1] > 7:
        return False
    # does destination contain a piece already?
    if board[b[0]][b[1]] != 0: return False

    if board[a[0]][a[1]].king == False and board[a[0]][a[1]].color == 'white':
        if b[0] > a[0]: return False # only move up
        return True 
    
    if board[a[0]][a[1]].king == False and board[a[0]][a[1]].color == 'black':
        if b[0] < a[0]: return False # only move down
        return True 
    # for kings
    if board[a[0]][a[1]].king == True: return True 


def make_move(a, b, board):
    board[b[0]][b[1]] = board[a[0]][a[1]] # make the move
    board[a[0]][a[1]] = 0 # delete the source

    if b[0] == 0 and board[b[0]][b[1]].color == 'white': board[b[0]][b[1]].king = True
    if b[0] == 7 and board[b[0]][b[1]].color == 'black': board[b[0]][b[1]].king = True

    if (a[0] - b[0]) % 2 == 0: # we made a jump
        board[(a[0]+b[0])/2][(a[1]+b[1])/2] = 0

######################## CORE FUNCTIONS ########################

# will evaluate board for a player
def evaluate(game, player):

	def simple_score(game, player):
		black, white = 0, 0
		for m in range(8):
			for n in range(8):
				if (game[m][n] != 0 and game[m][n].color == 'black'):
					if game[m][n].king == False: black += 100
					else: black += 175
				elif (game[m][n] != 0 and game[m][n].color == 'white'):
					if game[m][n].king == False: white += 100 
					else: white += 175
		if player != 'black': return white-black
		else: return black-white

	def piece_rank(game, player):
		black, white = 0, 0 
		for m in range(8):
			for n in range(8):
				if (game[m][n] != 0 and game[m][n].color == 'black'):
					if game[m][n].king != True:
						black = black + (m*m)
				elif (game[m][n] != 0 and game[m][n].color == 'white'):
					if game[m][n].king != True:
						white = white + ((7-m)*(7-m))
		if player != 'black': return white-black
		else: return black-white

	def edge_king(game, player):
		black, white = 0, 0 # keep track of score
		for m in range(8):
			if (game[m][0] != 0 and game[m][0].king != False):
				if game[m][0].color != 'white': black += -25
				else: white += -25
			if (game[m][7] != 0 and game[m][7].king != False):
				if game[m][7].color != 'white': black += -25
				else: white += -25
		if player != 'black': return white-black
		else: return black-white
	
	multi = random.uniform(0.97, 1.03) # will add +/- 3 percent to the score to make things more unpredictable
	return simple_score(game, player) + piece_rank(game, player) + edge_king(game, player)

def end_game(board):
	black, white = 0, 0
	for m in range(8):
		for n in range(8):
			if board[m][n] != 0:
				if board[m][n].color == 'black': black += 1 
				else: white += 1 
	return black, white

def alpha_beta(player, board, ply, alpha, beta):
	global best_move
	ply_depth = 0
	if player != 'black': ply_depth = white.ply_depth
	else: ply_depth = black.ply_depth

	end = end_game(board)

	#if(game over in current board position)
	if ply >= ply_depth or end[0] == 0 or end[1] == 0:
		score = evaluate(board, player)
		return score

	moves = avail_moves(board, player)

	if player == turn:
		for i in range(len(moves)):
			new_board = deepcopy(board)
			make_move((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), new_board)

			if player == 'black': player = 'white'
			else: player = 'black'

			score = alpha_beta(player, new_board, ply+1, alpha, beta)

			#found a better best move
			if score > alpha:
				if ply == 0: best_move = (moves[i][0], moves[i][1]), (moves[i][2], moves[i][3])
				alpha = score
			if alpha >= beta:
				return alpha
		return alpha
	
	else: # the opponent is to play on this node...
		for i in range(len(moves)):
			new_board = deepcopy(board)
			make_move((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), new_board)

			if player == 'black': player = 'white'
			else: player = 'black'

			score = alpha_beta(player, new_board, ply+1, alpha, beta)

			''' if score < beta then beta = score (opponent has found a better worse move) '''
			if score < beta: beta = score
			''' if alpha >= beta then return beta (cut off) '''
			if alpha >= beta: return beta
		''' return beta (this is the opponent's best move) '''
		return beta

def end_turn():
	global turn 
	if turn != 'black':	turn = 'black'
	else: turn = 'white'

def cpu_play(player):
	global board, move_limit 

	alpha = alpha_beta(player.color, board, 0, -10000, +10000)
	if alpha == -10000: #no more moves available for the player
		if player.color == white: show_winner("black")
		else: show_winner("white")

	make_move(best_move[0], best_move[1], board)

	move_limit[1] += 1 

	end_turn() 

def ply_check():
	global black, white

	''' if human has higher ply_setting, cpu will do unnecessary calculations '''
	if black.type != 'cpu': black.ply_depth = white.ply_depth
	elif white.type != 'cpu': white.ply_depth = black.ply_depth

######################## GUI FUNCTIONS ########################


def draw_piece(row, column, color, king):
	posX = ((window_size[0]/8)*column) - (window_size[0]/8)/2
	posY = ((window_size[1]/8)*row) - (window_size[1]/8)/2

	if color == 'black':
		border_color = (255, 255, 255)
		inner_color = (0, 0, 0)
	elif color == 'white':
		border_color = (0, 0, 0)
		inner_color = (255, 255, 255)

	pygame.draw.circle(screen, border_color, (posX, posY), 12) 
	pygame.draw.circle(screen, inner_color, (posX, posY), 10) 

	# draw king
	if king == True:
		pygame.draw.circle(screen, border_color, (posX+3, posY-3), 12)
		pygame.draw.circle(screen, inner_color, (posX+3, posY-3), 10)

def show_message(message):
	text = font.render(' '+message+' ', True, (255, 255, 255), (120, 195, 46)) 
	textRect = text.get_rect() 
	textRect.centerx = screen.get_rect().centerx
	textRect.centery = screen.get_rect().centery
	screen.blit(text, textRect)

def show_countdown(i):
	while i >= 0:
		tim = font_big.render(' '+repr(i)+' ', True, (255, 255, 255), (20, 160, 210)) 
		timRect = tim.get_rect()
		timRect.centerx = screen.get_rect().centerx
		timRect.centery = screen.get_rect().centery +50
		screen.blit(tim, timRect) 
		pygame.display.flip()
		i-=1
		pygame.time.wait(1000) # pause game for a second


def show_winner(winner):
	global board
	if winner == 'draw': show_message("draw")
	else: show_message(winner+" wins")
	pygame.display.flip() # display scene from buffer
	show_countdown(pause)
	board = init_board() #start a new game

def mouse_click(pos):
	global selected, move_limit 
	if (turn != 'black' and white.type != 'cpu') or (turn != 'white' and black.type != 'cpu'):
		column = pos[0]/(window_size[0]/board_size)
		row = pos[1]/(window_size[1]/board_size)

		if board[row][column] != 0 and board[row][column].color == turn:
			selected = row, column
		else:
			moves = avail_moves(board, turn)
			for i in range(len(moves)):
				if selected[0] == moves[i][0] and selected[1] == moves[i][1]:
					if row == moves[i][2] and column == moves[i][3]:
						make_move(selected, (row, column), board) 
						move_limit[1] += 1 
						end_turn() 

######################## START OF GAME ########################

pygame.init()

black = init_player('cpu', 'black', 1)
white = init_player('human', 'white', 1) 
board = init_board() 

ply_check() 

screen = pygame.display.set_mode(window_size) # set window size
pygame.display.set_caption(title) # set title of the window
clock = pygame.time.Clock() # setting clock so that the board doesn't refresh often

background = pygame.image.load(background_image_filename).convert() # load background
font = pygame.font.Font('freesansbold.ttf', 11) # font for the messages
font_big = pygame.font.Font('freesansbold.ttf', 13) # font for the countdown

while True: # main game loop
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit() 
		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == left:
			mouse_click(event.pos)

	screen.blit(background, (0, 0)) 

	if (turn != 'black' and white.type == 'human') or (turn != 'white' and black.type == 'human'): show_message('YOUR TURN')
	else: show_message('CPU THINKING...')

	# draw pieces on board
	for m in range(8):
		for n in range(8):
			if board[m][n] != 0:
				draw_piece(m+1, n+1, board[m][n].color, board[m][n].king)

	if start == True:
		show_message('Welcome to '+title)
		start = False

	end = end_game(board)
	if end[1] == 0:	show_winner("black")
	elif end[0] == 0: show_winner("white")

	elif move_limit[0] == move_limit[1]: show_winner("draw")

	else: pygame.display.flip()

	if turn != 'black' and white.type == 'cpu': cpu_play(white) # white cpu turn
	elif turn != 'white' and black.type == 'cpu': cpu_play(black) # black cpu turn

	clock.tick(fps) # saves cpu time

"""REFERENCES : https://www.ocf.berkeley.edu/~yosenl/extras/alphabeta/alphabeta.html
				http://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
				https://www.youtube.com/watch?v=xBXHtz4Gbdo
				https://www.pygame.org/docs/tut/newbieguide.html
				https://www.blog.pythonlibrary.org/2010/04/04/wxpython-grid-tips-and-tricks/
"""
