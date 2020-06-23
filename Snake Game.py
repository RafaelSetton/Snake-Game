from tkinter import Tk, Label
from random import randint
from time import sleep
from colored import fg
from keyboard import read_key
from threading import Thread, Event


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

    def pixel(self, x, y, color):
        try:
            self.pixels[x][y]['bg'] = color
        except IndexError:
            raise CollisionError


class Snake:
    def __init__(self):
        self.snake = {'cabeca': [0, 4], 'vertices': dict(), 'rabo': [0, 0], 'tamanho': 5}
        self.rmove = lambda: self.right('rabo')
        self.fmove = lambda: self.right('cabeca')
        self.move = self.right
        self.aumentar = False
        self.cells = [[0, 3], [0, 2], [0, 1], [0, 0]]

        self.render()

    def aumentar_handler(self):
        if self.snake['cabeca'] in game.fruits:
            self.aumentar = True
            game.fruits = []
        else:
            self.aumentar = False

    def collision_handler(self):

        collisions = [
            self.snake['cabeca'][0] > game.win_size-1,
            self.snake['cabeca'][0] < 0,
            self.snake['cabeca'][1] > game.win_size-1,
            self.snake['cabeca'][1] < 0,
            self.snake['cabeca'] in self.cells[:-1],
        ]

        if any(collisions):
            raise CollisionError
        self.cells.append(self.snake['cabeca'].copy())
        if len(self.cells) > self.snake['tamanho']:
            self.cells.pop(0)

    def draw(self):
        game.pixel(self.snake['rabo'][0], self.snake['rabo'][1], '#111144')
        game.pixel(self.snake['cabeca'][0], self.snake['cabeca'][1], '#cccccc')

        self.fmove()
        if self.aumentar:
            self.snake['tamanho'] += 1
        else:
            self.rmove()

        game.pixel(self.snake['cabeca'][0], self.snake['cabeca'][1], '#777777')

    def render(self):

        self.collision_handler()
        self.aumentar_handler()

        self.draw()

        if str(self.snake['rabo']) in self.snake['vertices'].keys():
            self.rmove = self.snake['vertices'][str(self.snake['rabo'])]
            del self.snake['vertices'][str(self.snake['rabo'])]

    def up(self, parte):
        self.snake[parte][0] -= 1

    def left(self, parte):
        self.snake[parte][1] -= 1

    def down(self, parte):
        self.snake[parte][0] += 1

    def right(self, parte):
        self.snake[parte][1] += 1

    def chg_direction(self, new_direction):
        oposites = ((self.up, self.down), (self.right, self.left))
        for pair in oposites:
            if self.move in pair and new_direction in pair:
                return
        self.move = new_direction
        self.fmove = lambda: self.move('cabeca')
        self.snake['vertices'][str(self.snake['cabeca'])] = lambda: new_direction('rabo')


class Fruit:
    def __init__(self):
        self.coords = []

        self.new()
        self.draw()

    def new(self):
        self.coords = [randint(1, game.win_size-1), randint(1, game.win_size-1)]
        if self.coords in snake.cells:
            self.new()

    def draw(self):
        game.pixel(self.coords[0], self.coords[1], '#00ff00')


class StoppableThread(Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, target, kwargs):
        super(StoppableThread, self).__init__(target=target, kwargs=kwargs)
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


game = Game()
snake = Snake()


def run():
    try:
        while True:

            snake.render()

            if len(game.fruits) == 0:
                game.fruits.append(Fruit().coords)

            game.window.update()

            sleep(0.1-0.001*snake.snake['tamanho'])
    except CollisionError:
        game.window.destroy()
        print("Ops, você perdeu :(")
        print(f"Sua pontuação foi de {fg('yellow')}{snake.snake['tamanho']} pontos.")
        with open('snake_points.txt', 'r+') as pts:
            arq = pts.read()
            top = arq.split('\n')
            nome = input(f"{fg('red')}Digite seu nome: ")
            top.append(f"{nome:15} {str(snake.snake['tamanho']).zfill(2)}".replace(' ', '-'))
            top.sort(key=lambda x: int(x[-2:]), reverse=True)
            print(f"{fg('blue')}Maiores pontuações:")
            for pt in top[:10]:
                print(pt)
            pts.seek(0)
            pts.write('\n'.join(top))


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


Thread(target=listen).start()
run()
