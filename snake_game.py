
from enum import Enum
from random import choices
import matplotlib.pyplot as plt
from  matplotlib.animation import FuncAnimation
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)

class GameState(Enum):
    kBeforeGame, kInGame, kEndGame = range(0, 3)

class MovingDirection(Enum):
    kUp, kRight, kDown, kLeft = range(0, 4)

# numerial definition depends on MovingDirection enum
class Turn(Enum):
    kRight = 1
    kLeft = -1
    kStraight = 0

class GameResult(Enum):
    kSnakeDie, kSnakeOutOfBox = range(0, 2)

class GameBoard(object):
    """game board for snake game"""

    def __init__(self, dim, snake_length):
        self.dim = dim
        self.snake_length = snake_length
        #self.board = [[False for x in range(dim)] for y in range(dim)]
        self.state = GameState.kBeforeGame

        # snake related vars
        self.moving_direction = MovingDirection.kUp
        self.snake = []

        # some stats
        self.counter = 0
        self.snake_die = False
        self.snake_out_of_box = False

    def state_change_to(self, new_state):
        self.state = new_state
        logging.info('game state changed to ' + str(new_state))

    def clear_board(self):
        for x in range(self.dim):
            for y in range(self.dim):
                self.board[x][y] = False

    def place_a_snake(self, head_row, head_col, moving_direction):
        assert(len(self.snake) == 0)
        try:
            if(moving_direction == MovingDirection.kLeft):
                for col_offset in range(self.snake_length):
                    cur_row = head_row
                    cur_col = head_col + col_offset
                    self.boundary_check(cur_row, cur_col)
                    self.snake.append([cur_row, cur_col])
            elif(moving_direction == MovingDirection.kRight):
                for col_offset in range(self.snake_length):
                    cur_row = head_row
                    cur_col = head_col - col_offset
                    self.boundary_check(cur_row, cur_col)
                    self.snake.append([cur_row, cur_col])
            elif(moving_direction == MovingDirection.kUp):
                for row_offset in range(self.snake_length):
                    cur_row = head_row + row_offset
                    cur_col = head_col
                    self.boundary_check(cur_row, cur_col)
                    self.snake.append([cur_row, cur_col])
            elif(moving_direction == MovingDirection.kDown):
                for row_offset in range(self.snake_length):
                    cur_row = head_row - row_offset
                    cur_col = head_col
                    self.boundary_check(cur_row, cur_col)
                    self.snake.append([cur_row, cur_col])
            else:
                logging.error('unexpect moving direction')
                exit(1)

            self.moving_direction = moving_direction;

        except (IndexError, AssertionError) as e:
            logging.error('can not place a snake at given position & moving direction')
            exit(1)

    def map_snake_to_board(self):
        self.clear_board()
        for [row, col] in self.snake:
            assert(self.board[row][col] == False)
            self.board[row][col] = True

    def boundary_check(self, row, col):
        if row < 0 or col < 0 or row >= self.dim or col >= self.dim:
            raise IndexError('boundary check fail!')

    def collision_check(self, new_row, new_col):
        for [row, col] in self.snake:
            assert(row != new_row or col != new_col)

    def update_moving_direction(self, turn):
        old_dir = self.moving_direction
        new_dir = MovingDirection((old_dir.value + turn.value) % 4)
        self.moving_direction = new_dir
        logging.debug(str(old_dir) + " + " + str(turn) + " -> " + str(new_dir))

    def generate_turn(self, weight = [.5, .5, .5]):
        return Turn(choices([0, -1, 1], weight)[0])

    def move_one_step(self):
        new_head_row = self.snake[0][0]
        new_head_col = self.snake[0][1]
        if self.moving_direction == MovingDirection.kUp:
            new_head_row = new_head_row - 1
        elif self.moving_direction == MovingDirection.kDown:
            new_head_row = new_head_row + 1
        elif self.moving_direction == MovingDirection.kLeft:
            new_head_col = new_head_col - 1
        elif self.moving_direction == MovingDirection.kRight:
            new_head_col = new_head_col + 1
        else:
            logging.error('unexpect moving direction')
            exit(1)

        self.boundary_check(new_head_row, new_head_col)
        self.snake.pop()  # remove tail
        self.collision_check(new_head_row, new_head_col)
        self.snake.insert(0, [new_head_row, new_head_col]) # insert new head

    def run(self, ignore_die = False):
        while(True):
            if self.state == GameState.kBeforeGame:
                self.place_a_snake(round(self.dim / 2), round(self.dim / 2), MovingDirection.kLeft)

                self.state_change_to(GameState.kInGame)
            elif self.state == GameState.kInGame:
                self.counter += 1
                turn = self.generate_turn([4, .5, .5])
                self.update_moving_direction(turn)
                try:
                    self.move_one_step()
                except IndexError as e:
                    logging.info('game end due to: ' + str(e))
                    self.snake_out_of_box = True
                    self.state_change_to(GameState.kEndGame)
                except AssertionError as e:
                    if ignore_die:
                        self.snake_die = False
                    else:
                        self.snake_die = True
                        logging.info('game end due to: ' + str(e))
                        self.state_change_to(GameState.kEndGame)

            elif self.state == GameState.kEndGame:
                if self.snake_die and not self.snake_out_of_box:
                    return [GameResult.kSnakeDie, self.counter]
                elif self.snake_out_of_box and not self.snake_die:
                    return [GameResult.kSnakeOutOfBox, self.counter]
                else:
                    logging.error('unexpect game ending')
                    exit(1)

def test_one_case():
    game = GameBoard(dim = 1000, snake_length = 30)
    [result, counter] = game.run(ignore_die = False)
    print(str(result) + ',' + str(counter))

def test_avg_out_of_box():
    test_times = 20
    avg_count = 0
    for i in range(0, test_times):
        game = GameBoard(dim = 1000, snake_length = 30)
        [result, counter] = game.run(ignore_die = True)
        print(str(result) + ',' + str(counter))
        avg_count += counter

    print('avg steps for OUT_OF_BOX: ' + str(avg_count / test_times))

def test_stats():
    test_times = 1000
    sum_steps = {'out_of_box': 0, 'die': 0}
    counts = {'out_of_box': 0, 'die': 0}
    for i in range(0, test_times):
        game = GameBoard(dim = 1000, snake_length = 30)
        [result, counter] = game.run(ignore_die = False)
        print(str(result) + ',' + str(counter))
        if result == GameResult.kSnakeOutOfBox:
            counts['out_of_box'] += 1
            sum_steps['out_of_box'] += counter
        elif result == GameResult.kSnakeDie:
            counts['die'] += 1
            sum_steps['die'] += counter
        else:
            logging.error('unexpect game result')
            exit(1)

    print('snake die: {die_count} times, out of box: {out_of_box_count} times, total: {total} times '.format(die_count = counts['die'], out_of_box_count = counts['out_of_box'], total = test_times))

    print('avg steps of snake die: {die_avg_step}, avg steps of out of box: {out_avg_step}'.format(die_avg_step = sum_steps['die'] / counts['die'], out_avg_step = sum_steps['out_of_box'] / (counts['out_of_box'] + 1)))

def main():
    #test_one_case()
    #test_avg_out_of_box()
    test_stats()

    print()

if __name__ == "__main__":
    main()
