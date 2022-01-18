import time
from tkinter import *
import itertools
import random
import sys, os

# Класс для управления ходами (отдельные объекты)
# Получает объекты очков и игроков и может обращяться к ним, а так же экран для вывода информации
# Выводит информационную строку и подсказки
class Steps:
    def __init__(self, scores, players, root):
        self.scores = scores
        self.players = players
        self.root = root
        self.info_string_label = Label(root, text='Строка', font=f'Helvetica 25', width=40, anchor="w")
        self.info_string_label.place(x=450, y=470)
        self.history = []  # Список объектов ходов
        self.current_step = 0  # Текущий ход
        self.current_step_obj = 0 # Ссылка на текущий объект хода
        self.create_step()

    # Создание нового хода
    def create_step(self):
        # Если ход добавляется не в конец истории (она отмотана) то вся последующая история сначала удаляется
        if len(self.history) > self.current_step:
            del (self.history[self.current_step:])
        self.current_step += 1
        self.current_step_obj = self.Step(self.players.next_player(), self.current_step)
        self.history.append(self.current_step_obj) # Создаем шаг
        self.info_string() # Выводим информацию о ходе

    # Вывод информационной строки о ходе. Игрок, № хода, сколько очков осталось
    def info_string(self):
        self.info_string_label['text'] = self.current_step_obj.player.get_name() \
        + '      Ход ' + str(self.current_step) \
        + '      Очков в игре ' + str(self.scores.get_points_left())
        self.scores.for_cute()

    # Рассчет и вывод подсказки (сектора, которые нужно выбить на пути к лучшему результату)
    # def clue(self):
        # Для начала вычисляем минимальную и максимальную суммы которые можно выбить на данном этапе
        # min_summa = sum(self.current_step_obj.trys[:self.try_number-1]) + (4-self.try_number)
        # max_summa = sum(self.current_step_obj.trys[:self.try_number - 1]) + (4 - self.try_number) * 20

    class Step:
        # Информация о каждом ходе и методы ее изменения
        # Получает игрока и номер хода
        def __init__(self, player, step):
            # Создаем новый ход для переданного игрока
            self.number_step = step # Номер хода
            self.try_number = 1 # Какая текущая попытка
            self.trys = [0, 0, 0] # Очки за бросоки (выбитый сектор)
            self.summa = 0 # Выбитая сумма. Если в эту попытку сумма зачислилась игроку, то тут та тумма иначе 0
            self.player = player # Ссылка на объект игрока чей ход



    # @classmethod

class Scores:
    # Класс ведет счет очков, создает таблицу сумм и баллов и управляет ей через вложенный подкласс
    # Получает ссылку на поле подсказок и обновляет их
    class ButtonScore:
        # Вложенный класс создает кнопки сумм рисует их и управляет ими
        def __init__(self, root, x, y, summa, score):
            self.activ = True  # Активна ли кнопка, False когда очки уже забрали
            self.show = True # Временно скрыть при False, когда в текущий момент сумма не доступна
            self.x = x
            self.y = y
            self.summa = summa # Суммы бросков дротиков
            self.score = score # Очки за суммы
            self.root = root
            self.btn = Button(root, text=summa, font="Arial 10", width=5, relief=RIDGE)
            self.btn.place(x=x, y=y)

        # Убираем сумму из таблицы и запрещаем ее показ. Возвращяет очки за нее
        def delete_summ(self):
            if self.activ:
                self.btn.place_forget()
                self.activ = False
                self.show = False
                return self.score
            else:
                return 0

        # Возвращяем сумму в таблицу и разрешаем ее показ. Возвращяет очки за нее
        def return_summ(self):
            self.activ = True
            self.show = True
            self.btn.place(x=self.x, y=self.y)
            return self.score

        # Временно прячем сумму из таблицы
        def hide_summ(self):
            if self.activ:
                self.btn.place_forget()
                self.show = False

        # Возвращяем сумму в таблицу (временно спрятанную), если она активна
        def show_summ(self):
            if self.activ:
                self.btn.place(x=self.x, y=self.y)
                self.show = True

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

    # Посчитать сколько очков еще осталось не выбитых
    def get_points_left(self):
        return sum(i.score for i in self.all_summ.values() if i.activ)

    # Возвращяет список секторов которые нужно выбить на данном этапе для достижения лучшего результата
    # Принимает за какое количество бросков
    def for_cute(self):
        best_result = max(key for key, summ in self.all_summ.items())
        print(self.all_summ)
    # На каждом этапе доступны только те суммы которые игрок еще может выбить,
    # находим те, которые дают большее количество очков
    # и находим сектора

class Player():
    # Игрок
    def __init__(self, num, name):
        self.number = num
        self.name = name
        self.score = 0

    # Вернуть имя игрока
    def get_name(self):
        return self.name

    # Вернуть очки игрока
    def get_score(self):
        return self.score

    def __str__(self):
        return f'Номер: {self.number}\nИмя: {self.name}\nОчки: {self.score}'

class Players():
    # Класс для управления игроками и их очками
    def __init__(self, root):
        # Читаем файл Players.txt с именами игроков
        try:
            PATH = os.path.join(sys.path[0], 'Players.txt')  # Путь к файлу с именами
            with open(PATH, 'r', encoding='utf8') as f:
                names = f.read().split('\n')
        except:
            names = ['Игрок 1', 'Игрок 2']
        random.shuffle(names)  # Перемешиваем игроков
        self.players = [] # Все игроки
        font_size = 45 - len(names) * 2
        spase_y = 400 // len(names)
        space_x = 600 - len(names) * 15
        self.string_table = [] # Список кортежей, номера строк таблицы (метка имени, метка очков)
        for i, name in enumerate(names):
            # Создаем игроков и готовим турнирную таблицу
            self.players.append(Player(i, name)) # Номер игрока, имя, очки
            n = Label(root, text='', font=f'Helvetica {font_size}', width=20, anchor="w")
            s = Label(root, text='0', font=f'Helvetica {font_size}', width=4, anchor="e")
            n.place(x=space_x//8+450, y=50+i*spase_y)
            s.place(x=500+space_x, y=50+i*spase_y)
            self.string_table.append((n, s)) # В каждой строке имя и очки
        self.current_player = len(self.players) - 1 # Текущий игрок, ставим последнего, чтоб при первом запросе получить 1
        self.print_table()

    # Сделать текущим следующего игрока и вернуть его
    def next_player(self):
        self.current_player += 1
        if self.current_player == len(self.players):
            self.current_player = 0
        return self.players[self.current_player]

    # Вывод турнирной таблицы
    def print_table(self):
        self.players.sort(key=lambda x: x.score, reverse=True) # Сортируем массив игроков по очкам
        for i, st in enumerate(self.string_table):
            st[0]['text'] = self.players[i].get_name()
            st[1]['text'] = self.players[i].get_score()

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

scores = Scores() # Создаем объект управляющий очками, таблицей и подсказкой

players = Players(root) # Создаем объекты игроков и турнирную таблицу

step = Steps(scores, players, root) # создаем первый ход, передаем ему объекты очков и игроков и объект экрана



# pl1 = Label(root, text=players[who_step], font=f'Helvetica 30', width=10)
# pl2 = Label(root, text=players[not who_step], font=f'Helvetica 30', width=10)
# pl1.place(x=600, y=100)
# pl2.place(x=900, y=100)
#
# sc1 = Label(root, text=0, font=f'Helvetica 50', width=10)
# sc2 = Label(root, text=0, font=f'Helvetica 50', width=10)
# sc1.place(x=530, y=200)
# sc2.place(x=830, y=200)

score1 = StringVar() # Переменная для поля ввода
score2 = StringVar()
score3 = StringVar()

word1 = Entry(root, width=3, font="Helvetica 30", textvariable=score1)
word2 = Entry(root, width=3, font="Helvetica 30", textvariable=score2)
word3 = Entry(root, width=3, font="Helvetica 30", textvariable=score3)
word1.place(x=700, y=550)
word2.place(x=800, y=550)
word3.place(x=900, y=550)
word1.bind('<Return>', word1_press)
word2.bind('<Return>', word2_press)
word3.bind('<Return>', word3_press)
root.bind("<Escape>", clear)

score1.set(0)
score2.set(0)
score3.set(0)
word1.focus()
word1.select_range(0, END)

# who = Label(root, text=players[who_step], font=f'Helvetica 30', width=10)
# who.place(x=700, y=400)



root.mainloop()