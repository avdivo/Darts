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
        self.info_string_label = Label(root, text='', font=f'Helvetica 25', width=40, anchor="w")
        self.info_string_label.place(x=450, y=470)
        self.labl1 = Label(root, text='Лучшие сектора:', font=f'Helvetica 20', width=80, anchor="w")
        self.labl1.place(x=450, y=650)
        self.cute_string_label = Label(root, text='', font=f'Helvetica 20', width=80, anchor="w")
        self.cute_string_label.place(x=450, y=690)
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
        self.for_show_hide_score() # Изменение таблицы очков
        self.info_string() # Выводим информацию о ходе
        self.print_cute() # Выводим подсказку

    # Вывод информационной строки о ходе. Игрок, № хода, сколько очков осталось и подсказки
    def info_string(self):
        self.info_string_label['text'] = self.current_step_obj.player.get_name() \
        + '      Ход ' + str(self.current_step) \
        + '      Очков в игре ' + str(self.scores.get_points_left())

    # Вывод подсказки, ее запрашиваем в классе Score
    def print_cute(self):
        score = sum(self.current_step_obj.trys[:self.current_step_obj.try_number-1]) # Сколько очков уже набрано
        trys = 4 - self.current_step_obj.try_number # Сколько попыток осталось
        string = [str(i) for i in self.scores.for_cute(trys, score)]
        self.cute_string_label['text'] = ', '.join(string)

    # Подготовка к вызову функции скрывающей недоступные на данном этапе суммы в таблице и показывающей доступные
    def for_show_hide_score(self):
        # Вычисляем минимальную и максимальную суммы которые можно выбить, с учетом уже выбитого
        min_summa = sum(self.current_step_obj.trys[:self.current_step_obj.try_number-1]) + (4-self.current_step_obj.try_number)
        max_summa = sum(self.current_step_obj.trys[:self.current_step_obj.try_number - 1]) + (4 - self.current_step_obj.try_number) * 20
        self.scores.show_hide_score(min_summa, max_summa) # Вызываем метод

    # Смена попытки. Аргументы - сколько записать очков на текущую попытку, номер попытки который нужно установить
    def try_change(self, score, num):
        self.current_step_obj.trys[self.current_step_obj.try_number-1] = score
        if self.current_step_obj.try_number == num:
            print('Hf,jnftn')
            return
        # Это выполняется если меняется этап (попытка)
        self.current_step_obj.try_number = num
        self.print_cute()  # Выводим подсказку
        self.for_show_hide_score()  # Изменение таблицы очков

    # Вернуть номер этапа (попытки)
    def try_number(self):
        return self.current_step_obj.try_number

    # Набранная сумма
    def summa(self):
        return sum(self.current_step_obj.trys)

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
        self.light_summ = 0 # Объект который подсвечен (клеточка суммы выделена красным)
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
    # получает за какое количество бросков и сколько очков уже выбито
    def for_cute(self, shot, score_now):
        # Находим список видимых сумм с лучшим результатом по очкам
        # но не полных сумм, а уменьшиных на уже набранную сумму
        max_score = 0
        list_sum = []
        for key, button in self.all_summ.items():
            if button.show:
                if max_score == button.score:
                    list_sum.append(key - score_now)
                elif max_score < button.score:
                    list_sum.clear()
                    list_sum.append(key - score_now)
                    max_score = button.score
        # Для каждой суммы находим все комбинации ее получения 1, 2 или 3 бросками в зависимости от этапа
        # В комбинациях нас интересуют только сектора (очки за 1 бросок)
        # составляем список из этих цифр, каждая по 1 разу
        best_sectors = set()
        # Получаем список кортежей, каждый длиной от 1 до 3 элементов, в зависимости от количества ходов
        all_sectors = list(range(1, 21))
        for res in list_sum:
            that = [i for i in itertools.combinations_with_replacement(all_sectors, shot) if sum(i) == res]
            for i in that:
                # Записываем каждый кортеж в set чтобы убрать повторы
                best_sectors = best_sectors | set(i)
        return list(best_sectors)

    # Скрывает недоступные суммы в таблице и отображаем доступные
    # Все что меньше минимальной и больше максимальной скрываем
    def show_hide_score(self, min_summa, max_summa):
        for button in self.all_summ.values():
            if button.activ:
                if button.summa < min_summa or button.summa > max_summa:
                    button.hide_summ()
                else:
                    button.show_summ()

    # Включает подсветкой суммы
    def light_on(self, summ):
        if self.all_summ[summ].show:
            self.light_summ = self.all_summ[summ]
            self.light_summ.light_summ()

    # Гасит подсветкой суммы
    def light_off(self):
        if self.light_summ != 0:
            # Гасим засвеченную сумму
            self.light_summ.normal_summ()
            self.light_summ = 0

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

# # Нажатие клавишь в полях ввода
# def word1_press(event):
#     word2.focus()
#     word2.select_range(0, END)
#
# def word2_press(event):
#     word3.focus()
#     word3.select_range(0, END)
#
# def word3_press(event):
#     global who_step
#     sc = int(score1.get()) + int(score2.get()) + int(score3.get())
#     if sc > 2 and sc < 61:
#         new = all_obj[sc].get_score()
#         if who_step == 0:
#             sc1['text'] = int(sc1['text']) + new
#         else:
#             sc2['text'] = int(sc2['text']) + new
#     who_step = not who_step
#     who['text'] = players[who_step]
#     score1.set(0)
#     score2.set(0)
#     score3.set(0)
#     word1.focus()
#     word1.select_range(0, END)
#
# def clear(event):
#     global who_step
#     who_step = not who_step
#     who['text'] = players[who_step]
#     score1.set(0)
#     score2.set(0)
#     score3.set(0)
#     word1.focus()
#     word1.select_range(0, END)

# Получение фокуса полями ввода
def focus_in_word(event, num):
    # Нельзя перемещяться вправо, если левые поля еще нулевые
    if num > 0:
        if int(score[num-1].get()) == 0:
            word[num-1].focus()
            word[num-1].select_range(0, END)
            return
        elif num == 2:
            if int(score[0].get()) == 0:
                word[0].focus()
                word[0].select_range(0, END)
                return
    # Переход одобрен
    word[num].select_range(0, END) # Выделяем данные в поле
    step.try_change(int(score[step.try_number()-1].get()), num+1) # Заполняем информацию о броске и переходим к следующему
    scores.light_off() # Гасим подсветку при переходах


# Нажатие клавишь в полях ввода
def word_press(event, num):
    if event.keycode == 8:
        score[num].delete(0, "end")
        score[num].insert(0, '0')
        word[num].select_range(0, END)
        event.keycode = 37
    # Запрещяем ввод не цифр
    if event.keycode == 39:
        # Стрелка вправо, действует как Enter для 1 и 2 полей, на 3 не работает
        if num < 2:
            enter()
        return
    if event.keycode == 37:
        # Стрелка влево
        if num > 0:
            word[num - 1].focus()
            word[num - 1].select_range(0, END)
            step.try_change(int(score[num].get()), num + 1)  # Заполняем информацию о броске и переходим к следующему
        return
    try:
        # Должны быть только цифры
        text = int(score[num].get())
    except:
        score[num].delete(0, "end")
        score[num].insert(0, '0')
        word[num].select_range(0, END)
        text = 0
    if text > 20 or len(score[num].get()) > 2:
        # Максимальное значение сектора 20, длина цифры 2 символа, ограничиваем
        score[num].delete(0, "end")
        score[num].insert(0, '0')
        word[num].select_range(0, END)
        text = 0
    if num < 2:
        # В старшем разряде не может быть цифры больше 2, поэтому переходим к следующему полю
        if text > 2:
            next_try(num)
    else:
        # Сумма третьей ячейки заполняется при наборе
        step.try_change(text, num)  # Заполняем информацию о броске и остаемся
        scores.light_on(step.summa()) # Передаем набранную сумму чтобы засветить ее

    if event.keycode == 13:
        enter()
        return





def button_digit(sector):
    num = step.try_number()-1 # Номер поля которое заполняется
    score[num].delete(0, "end")
    score[num].insert(0, sector)
    if num < 2:
        next_try(num)
    else:
        # Сумма третьей ячейки заполняется при наборе
        step.try_change(sector, num)  # Заполняем информацию о броске и остаемся
        scores.light_on(step.summa())  # Передаем набранную сумму чтобы засветить ее

# Переход на правое поле (1 или 2), когда левое (0 или 1) правильно заполнено
def next_try(num):
    word[num + 1].focus()
    word[num + 1].select_range(0, END)
    step.try_change(int(score[num].get()), num + 1)  # Заполняем информацию о броске и переходим к следующему

# Нажатие Enter или кнопки Ок
def enter():
    num = step.try_number() - 1  # Номер поля на котором нажат Enter
    if num < 2:
        next_try(num) # Переход к следующему полю
    else:
        # Завершение хода игрока, переход к следующему
        pass

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
score = word = [0, 0, 0]
score[0] = StringVar() # Переменная для поля ввода
score[1] = StringVar()
score[2] = StringVar()
word[0] = Entry(root, width=2, font="Helvetica 40", textvariable=score[0])
word[1] = Entry(root, width=2, font="Helvetica 40", textvariable=score[1])
word[2] = Entry(root, width=2, font="Helvetica 40", textvariable=score[2])
word[0].place(x=450, y=550)
word[1].place(x=530, y=550)
word[2].place(x=610, y=550)
word[0].bind('<FocusIn>', lambda event, x=0: focus_in_word(event, x))
word[1].bind('<FocusIn>', lambda event, x=1: focus_in_word(event, x))
word[2].bind('<FocusIn>', lambda event, x=2: focus_in_word(event, x))
word[0].bind('<KeyRelease >', lambda event, x=0: word_press(event, x))
word[1].bind('<KeyRelease >', lambda event, x=1: word_press(event, x))
word[2].bind('<KeyRelease >', lambda event, x=2: word_press(event, x))
# root.bind("<Escape>", clear)


score[0].insert(0, '0')
score[1].insert(0, '0')
score[2].insert(0, '0')
score[0].focus()
score[0].select_range(0, END)




# Кнопки для быстрого ввода
x = 700
y = 535
for i in range(1, 11):
    Button(text=str(i), command=lambda i=i: button_digit(i), width=3, font="Helvetica 18").place(x=x, y=y)
    Button(text=str(i+10), command=lambda i=i+10: button_digit(i), width=3, font="Helvetica 18").place(x=x, y=y+54)
    x += 55
Button(text=str('Ok'), command=enter, width=6, height=3, font="Helvetica 18").place(x=x, y=y)


root.mainloop()