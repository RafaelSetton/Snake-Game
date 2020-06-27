from tkinter import Tk, Label
from random import randint
from time import sleep
from keyboard import read_key
from threading import Thread


class CollisionError(IndexError):
    pass


class Game:
    def __init__(self):
        self.fruits = []

        self.window = Tk(screenName='Snake Game')
        self.window.title = 'Snake Game'
        self.window['bg'] = "#111144"
        self.win_size = 30

        self.pixels = [
            [Label(self.window, height=1, width=2, background='#111144') for _ in range(self.win_size)]
            for _ in range(self.win_size)
        ]

        for i in range(self.win_size):
            for j in range(self.win_size):
                self.pixels[i][j].grid(row=i, column=j)

    def pixel(self, coords, color):
        x, y = coords
        try:
            self.pixels[x][y]['bg'] = color
        except IndexError:
            raise CollisionError


class Snake:
    def __init__(self):
        self.move = self.right
        self.aumentar = False
        self.cells = [[0, 0], [0, 1], [0, 2], [0, 3]]
        self.tamanho = len(self.cells)

    def aumentar_handler(self):
        if self.cells[-1] in game.fruits:
            self.aumentar = True
            game.fruits = []
        else:
            self.aumentar = False

    def collision_handler(self):

        collisions = [
            self.cells[-1][0] > game.win_size-1,
            self.cells[-1][0] < 0,
            self.cells[-1][1] > game.win_size-1,
            self.cells[-1][1] < 0,
            self.cells[-1] in self.cells[:-1],
        ]

        if any(collisions):
            raise CollisionError

    def draw(self):
        self.move()
        game.pixel(self.cells[0], '#111144')
        game.pixel(self.cells[-1], '#777777')
        game.pixel(self.cells[-2], '#cccccc')

    def render(self):
        self.collision_handler()
        self.aumentar_handler()

        self.draw()
        self.tamanho = len(self.cells)

    def up(self):
        cabeca = self.cells[-1][:]
        cabeca[0] -= 1
        self.cells.append(cabeca)
        if not self.aumentar:
            self.cells.pop(0)

    def left(self):
        cabeca = self.cells[-1][:]
        cabeca[1] -= 1
        self.cells.append(cabeca)
        if not self.aumentar:
            self.cells.pop(0)

    def down(self):
        cabeca = self.cells[-1][:]
        cabeca[0] += 1
        self.cells.append(cabeca)
        if not self.aumentar:
            self.cells.pop(0)

    def right(self):
        cabeca = self.cells[-1][:]
        cabeca[1] += 1
        self.cells.append(cabeca)
        if not self.aumentar:
            self.cells.pop(0)

    def chg_direction(self, new_direction):
        oposites = ((self.up, self.down), (self.right, self.left))
        for pair in oposites:
            if self.move in pair and new_direction in pair:
                return
        self.move = new_direction


class Fruit:
    def __init__(self):
        self.coords = [randint(1, game.win_size-1), randint(1, game.win_size-1)]
        while self.coords in snake.cells:
            self.coords = [randint(1, game.win_size-1), randint(1, game.win_size-1)]
        game.pixel(self.coords, '#00ff00')


game = Game()
snake = Snake()


def run():
    try:
        while True:
            snake.render()

            if len(game.fruits) == 0:
                game.fruits.append(Fruit().coords)

            game.window.update()
            sleep(0.1-0.001*snake.tamanho)
    except CollisionError:
        game.window.destroy()
        input("Pressione enter para sair")


def listen():
    dic_funcs = {
        'w': lambda: snake.chg_direction(snake.up),
        'a': lambda: snake.chg_direction(snake.left),
        's': lambda: snake.chg_direction(snake.down),
        'd': lambda: snake.chg_direction(snake.right),
        'enter': "break"
    }

    while True:
        key = read_key()
        func = dic_funcs.get(key)
        if func == "break":
            break
        elif func:
            func()
            sleep(0.1 - 0.001 * snake.tamanho)


Thread(target=listen).start()
run()
