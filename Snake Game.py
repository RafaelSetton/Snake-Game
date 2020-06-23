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
        self.move = self.right
        self.aumentar = False
        self.cells = [[0, 3], [0, 2], [0, 1], [0, 0]]
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
        game.pixel(*self.cells[0], '#111144')
        game.pixel(*self.cells[-1], '#cccccc')
        game.pixel(*self.cells[-2], '#777777')

    def render(self):

        self.collision_handler()
        self.aumentar_handler()

        self.draw()
        self.tamanho = len(self.cells)

    def up(self):
        cabeca = self.cells[0]
        cabeca[0] -= 1
        self.cells.append(cabeca)
        if not self.aumentar:
            self.cells.pop(0)

    def left(self):
        cabeca = self.cells[0]
        cabeca[1] -= 1
        self.cells.append(cabeca)
        if not self.aumentar:
            self.cells.pop(0)

    def down(self):
        cabeca = self.cells[0]
        cabeca[0] += 1
        self.cells.append(cabeca)
        if not self.aumentar:
            self.cells.pop(0)

    def right(self):
        cabeca = self.cells[0]
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
            sleep(0.1-0.001*snake.tamanho)
    except CollisionError:
        game.window.destroy()
        print("Ops, você perdeu :(")
        print(f"Sua pontuação foi de {fg('yellow')}{snake.tamanho} pontos.")
        with open('snake_points.txt', 'r+') as pts:
            nome = input(f"{fg('red')}Digite seu nome: ")

            arq = pts.read()
            top = arq.split('\n')
            top.append(f"{nome:15} {str(snake.tamanho).zfill(2)}".replace(' ', '-'))
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
