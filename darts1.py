from tkinter import *
import itertools
import random
import sys, os

class History():
    # Класс управляет историей ходов
    def __init__(self):
        self.history = [] # Список объектов ходов
        self.current_step = 0 # Текущий ход

    def new_step(self, player):
        # Создаем новый ход для переданного игрока
        # Если ход добавляется не в конец истории (она отмотана) то вся последующая история сначала удаляется
        if len(self.history) > self.current_step:
            del(self.history[self.current_step:])
        self.current_step += 1
        self.history.append(Step(player, self.current_step))

class Step():
    # Информация о каждом ходе и методы ее изменения
    def __init__(self, player, number_step):
        self.number_step = number_step # Номер хода
        self.try_number = 1 # Какая текущая попытка
        self.try1 = 0 # Очки за бросок (выбитый сектор)
        self.try2 = 0
        self.try3 = 0
        self.summa = 0 # Выбитая сумма. Если в эту попытку сумма зачислилась игроку, то тут та тумма иначе 0
        self.player = player # Ссылка на объект игрока чей ход

class Scores():
    # Класс ведет счет очков, создает таблицу сумм и баллов и управляет ей через вложенный подкласс
    # Получает ссылку на поле подсказок и обновляет их
    class ButtonScore():
        # Вложенный класс создает кнопки сумм рисует их и управляет ими
        def __init__(self, root, x, y, summa, score):
            self.activ = True  # Активна ли кнопка
            self.x = x
            self.y = y
            self.summa = summa
            self.score = score
            self.root = root
            self.btn = Button(root, text=summa, font="Arial 10", width=5, relief=RIDGE)
            self.btn.place(x=x, y=y)

        # Убираем сумму из таблицы и запрещаем ее показ. Возвращяет очки за нее
        def delete_summ(self):
            if self.activ:
                self.btn.place_forget()
                self.activ = False
                return self.score
            else:
                return 0

        # Возвращяем сумму в таблицу и разрешаем ее показ. Возвращяет очки за нее
        def return_summ(self):
            self.activ = True
            self.btn.place(x=self.x, y=self.y)
            return self.score

        # Временно прячем сумму из таблицы
        def hide_summ(self):
            if self.activ:
                self.btn.place_forget()

        # Возвращяем сумму в таблицу (временно спрятанную), если она активна
        def show_summ(self):
            if self.activ:
                self.btn.place(x=self.x, y=self.y)

        # Подсвечиваем сумму
        def light_summ(self):
            if self.activ:
                self.btn['background'] = 'red'

        # Убираем подсветку с суммы
        def normal_summ(self):
            if self.activ:
                self.btn['background'] = root['background']

    # Методы класса Scores
    def __init__(self):
        all_sectors = list(range(1, 21))
        all_res_dict = dict()
        for res in range(3, 61):
            # Считаем. сколько есть способов выбить по секторам каждую сумму от 1 до 60
            that = [i for i in itertools.combinations_with_replacement(all_sectors, 3) if sum(i) == res]
            # Группируем в словарь с key - количество очков за выбивание суммы
            # value - какие суммы нужно выбить за эти очки
            if 56 - len(that) in all_res_dict:
                all_res_dict[56 - len(that)].append(res)
            else:
                all_res_dict[56 - len(that)] = [res]

        # Словарь, где ключи - это суммы, а значения объекты кнопок-ячеек
        self.all_summ = dict()
        y = 10
        for key, val in all_res_dict.items():
            x = 100
            btn = Button(root, text=key, font="Arial 10", width=5, relief=RIDGE)
            btn.place(x=x, y=y)
            x += 50
            for i in val:
                x += 55
                self.all_summ[i] = self.ButtonScore(root, x, y, i, key)
            y += 28


class Player():
    # Игрок
    def __init__(self, num, name):
        self.number = num
        self.name = name
        self.score = 0

    def __str__(self):
        return f'Номер: {self.number}\nИмя: {self.name}\nОчки: {self.score}'

class Players():
    # Класс для управления игроками и их очками
    def __init__(self):
        # Читаем файл Players.txt с именами игроков
        try:
            PATH = os.path.join(sys.path[0], 'Players.txt')  # Путь к файлу с именами
            with open(PATH, 'r', encoding='utf8') as f:
                names = f.read().split()
        except:
            names = ['Игрок 1', 'Игрок 2']
        random.shuffle(names)  # Перемешиваем игроков
        self.players = [] # Все игроки
        for i, name in enumerate(names):
            self.players.append(Player(i, name)) # Номер игрока, имя, очки
        self.current_player = 0 # Текущий игрок

    # Возвращяет объект игрока
    def get_player(self):
        return self.players[self.current_player]

    # Сделать текущим следующего игрока и вернуть его
    def next_player(self):
        self.current_player += 1
        if self.current_player == len(self.players):
            self.current_player = 0
        return self.players[self.current_player]

def word1_press(event):
    print('Ok 1')
    word2.focus()
    word2.select_range(0, END)


def word2_press(event):
    word3.focus()
    word3.select_range(0, END)



def word3_press(event):
    global who_step
    sc = int(score1.get()) + int(score2.get()) + int(score3.get())
    if sc > 2 and sc < 61:
        new = all_obj[sc].get_score()
        if who_step == 0:
            sc1['text'] = int(sc1['text']) + new
        else:
            sc2['text'] = int(sc2['text']) + new
    who_step = not who_step
    who['text'] = players[who_step]
    score1.set(0)
    score2.set(0)
    score3.set(0)
    word1.focus()
    word1.select_range(0, END)

def clear(event):
    global who_step
    who_step = not who_step
    who['text'] = players[who_step]
    score1.set(0)
    score2.set(0)
    score3.set(0)
    word1.focus()
    word1.select_range(0, END)



root = Tk()
root.attributes("-fullscreen", True)

a = Players()
# Интерфейс
print(a.get_player())
print(a.next_player())

scores = Scores()


who_step = random.randint(0, 1)
players = ['Сергей', 'Алексей']


pl1 = Label(root, text=players[who_step], font=f'Helvetica 30', width=10)
pl2 = Label(root, text=players[not who_step], font=f'Helvetica 30', width=10)
pl1.place(x=600, y=100)
pl2.place(x=900, y=100)

sc1 = Label(root, text=0, font=f'Helvetica 50', width=10)
sc2 = Label(root, text=0, font=f'Helvetica 50', width=10)
sc1.place(x=530, y=200)
sc2.place(x=830, y=200)

score1 = StringVar() # Переменная для поля ввода
score2 = StringVar()
score3 = StringVar()

word1 = Entry(root, width=3, font="Helvetica 30", textvariable=score1)
word2 = Entry(root, width=3, font="Helvetica 30", textvariable=score2)
word3 = Entry(root, width=3, font="Helvetica 30", textvariable=score3)
word1.place(x=700, y=500)
word2.place(x=800, y=500)
word3.place(x=900, y=500)
word1.bind('<Return>', word1_press)
word2.bind('<Return>', word2_press)
word3.bind('<Return>', word3_press)
root.bind("<Escape>", clear)

score1.set(0)
score2.set(0)
score3.set(0)
word1.focus()
word1.select_range(0, END)

who = Label(root, text=players[who_step], font=f'Helvetica 30', width=10)
who.place(x=700, y=400)



root.mainloop()