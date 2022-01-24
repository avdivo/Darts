import time
from tkinter import *
import tkinter.messagebox as mb
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
        self.info_string_label = Label(root, text='', font=f'Helvetica 25', width=40, anchor="w", fg='red4')
        self.info_string_label.place(x=450, y=470)
        self.labl1 = Label(root, text='Лучшие сектора:', font=f'Helvetica 20', width=80, anchor="w", fg='red4')
        self.labl1.place(x=450, y=670)
        self.cute_string_label = Label(root, text='', font=f'Helvetica 20', width=80, anchor="w", fg='red4')
        self.cute_string_label.place(x=450, y=710)
        self.history = []  # Список объектов ходов
        self.current_step = 0  # Текущий ход
        self.current_step_obj = 0 # Ссылка на текущий объект хода
        self.create_step()

    class Step:
        # Информация о каждом ходе и методы ее изменения
        # Получает игрока и номер хода
        def __init__(self, player, step):
            # Создаем новый ход для переданного игрока
            self.number_step = step # Номер хода
            self.try_number = 0 # Какая текущая попытка
            self.trys = [0, 0, 0] # Очки за бросоки (выбитый сектор)
            self.summa = 0 # Выбитая сумма. Если в эту попытку сумма зачислилась игроку, то тут та тумма иначе 0
            self.player = player # Ссылка на объект игрока чей ход

    # Передача хода следующему игроку
    def next_step(self):
        result = self.scores.get_result() # Получаем результаты бросков сделанных игроком (объект ButtonScore)
        if result:
            self.current_step_obj.summa = result.summa # Запоминаем выбитую сумму
            self.current_step_obj.player.score += result.score # Записываем очки игроку
        else:
            self.current_step_obj.summa = 0 # Запоминаем выбитую сумму
        self.create_step() # Создаем новый ход

    # Запись пустого хода, пропуск хода (при промахе, по клавише esc)
    def null_step(self):
        self.current_step_obj.trys = [0, 0, 0]  # Запоминаем выбитую сумму
        self.for_show_hide_score()  # Изменение таблицы очков

    # Перемотка истории назад
    def history_previous(self):
        if self.current_step == 1:
            return False # Переход не выполнен
        self.current_step -= 1
        self.current_step_obj = self.history[self.current_step-1] # Делаем предидущий шаг текущим
        if self.current_step_obj.summa:
            # Если сумма не 0 нужно ее восстановить и отнять
            result = self.scores.cancel_result(self.current_step_obj.summa) # Получаем объект суммы (ButtonScore)
            self.current_step_obj.player.score -= result.score # Отнимаем очки у игрока
        self.players.set_current_player(self.current_step_obj.player) # Делаем игрока текущим и обновляем таблицу
        self.current_step_obj.try_number = 2 if self.current_step_obj.trys[2] else 0 # Устанавливаем текущую попытку
        self.for_show_hide_score() # Изменение таблицы очков
        self.info_string() # Выводим информацию о ходе
        self.print_cute() # Выводим подсказку
        return self.current_step_obj

    # Перемотка истории вперед
    def history_next(self):
        if self.current_step == len(self.history):
            return False # Переход не выполнен, дошли до конца истории
        if self.step_change():
            mb.showwarning('Внимание', 'Результаты хода быле изменены. Необходимо сохранить ход, '
                    'в этом случае дальнейшая история будет утеряна. Или вернуть старые результаты.')
            return False  # Результаты были изменены, поэтому дальнейшая история должна быть удалена
        if self.current_step_obj.summa:
            # Если сумма не 0 нужно ее удалить из таблицы и прибавить игроку
            result = self.scores.cancel_result(self.current_step_obj.summa) # Получаем объект суммы (ButtonScore)
            self.current_step_obj.player.score += result.delete_summ() # Добавляем очки игроку и удаляем сумму из таблицы
        self.current_step += 1
        self.current_step_obj = self.history[self.current_step-1] # Делаем следующий шаг текущим
        self.players.set_current_player(self.current_step_obj.player) # Делаем игрока текущим и обновляем таблицу
        self.current_step_obj.try_number = 2 if self.current_step_obj.trys[2] else 0 # Устанавливаем текущую попытку
        self.for_show_hide_score() # Изменение таблицы очков
        self.info_string() # Выводим информацию о ходе
        self.print_cute() # Выводим подсказку
        return self.current_step_obj

    # Если ход добавляется не в конец истории (она отмотана) вернет True
    def step_end(self):
        return len(self.history) > self.current_step

    # Если результаты хода были изменены вернет True
    def step_change(self):
        summ = self.summa()
        if summ != self.current_step_obj.summa:
            # Данные были изменены или сумма не была записана, поскольку уже ранее была выбита (тогда там 0)
            if self.current_step_obj.summa == 0:
                # Если сумма и была 0, то возможно сейчас внесены изменения и сумму можно записать
                return self.scores.available_summ(summ) # Сумма стала доступна для записи, значит считаем что ход был изменен
            else:
                return True
        return False

    # Создание нового хода
    def create_step(self):
        # Если ход добавляется не в конец истории (она отмотана) то вся последующая история сначала удаляется
        if self.step_end():
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
        score = sum(self.current_step_obj.trys[:self.current_step_obj.try_number]) # Сколько очков уже набрано
        trys = 3 - self.current_step_obj.try_number # Сколько попыток осталось
        string = [str(i) for i in self.scores.for_cute(trys, score)]
        self.cute_string_label['text'] = ', '.join(string)

    # Подготовка к вызову функции скрывающей недоступные на данном этапе суммы в таблице и показывающей доступные
    def for_show_hide_score(self):
        if self.current_step_obj.try_number == 2 and self.current_step_obj.trys[2] > 0:
            # Для третьей попытки в таблице оставляем одну выбитую цифру, когда начат ввод данных
            min_summa = max_summa = sum(self.current_step_obj.trys)
        else:
            # Вычисляем минимальную и максимальную суммы которые можно выбить, с учетом уже выбитого
            min_summa = sum(self.current_step_obj.trys[:self.current_step_obj.try_number]) + (3-self.current_step_obj.try_number)
            max_summa = sum(self.current_step_obj.trys[:self.current_step_obj.try_number]) + (3 - self.current_step_obj.try_number) * 20
        self.scores.show_hide_score(min_summa, max_summa) # Вызываем метод

    # Запись очков в текущую попытку
    def set_try_score(self, score):
        self.current_step_obj.trys[self.current_step_obj.try_number] = score
        self.for_show_hide_score()  # Изменение таблицы очков
        self.print_cute()

    # Смена попытки. Аргумент - номер попытки который нужно установить. Обновляет таблицу очков
    def try_change(self, num):
        self.current_step_obj.try_number = num
        self.for_show_hide_score()  # Изменение таблицы очков
        self.print_cute()  # Выводим подсказку

    # Вернуть номер этапа (попытки)
    def get_try_number(self):
        return self.current_step_obj.try_number

    # Вернуть Очки на текущей попытке
    def get_try_summa(self):
        return self.current_step_obj.trys[self.current_step_obj.try_number]

    # Набранная сумма
    def summa(self):
        return sum(self.current_step_obj.trys)


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
            btn = Button(root, text=key, font="Arial 10", width=5, relief=RIDGE, fg='blue')
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

    # Находит сумму которая не скрыта и возвращяет этот объект, если его нет вернет 0
    def get_result(self):
        counter = result = 0
        for button in self.all_summ.values():
            if button.show:
                counter += 1
                if counter > 1:
                    return 0
                result = button
        if result:
            result.delete_summ() # Сумма выбита, убираем ее из таблицы
        return result

    # Доступна ли сумма для записи True, если да
    def available_summ(self, summ):
        return self.all_summ[summ].activ

    # Восстанавливаем удаленную из таблицы сумму и возвращяем этот объект
    def cancel_result(self, summ):
        self.all_summ[summ].return_summ() # Восстанавливаем
        return self.all_summ[summ]

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


class Players():
    # Класс для управления игроками и их очками
    def __init__(self, root, scores):
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
            s = Label(root, text='0', font=f'Helvetica {font_size}', width=4, anchor="e", fg='blue')
            n.place(x=space_x//8+450, y=50+i*spase_y)
            s.place(x=500+space_x, y=50+i*spase_y)
            self.string_table.append((n, s)) # В каждой строке имя и очки
        self.current_player = len(self.players) - 1 # Текущий игрок, ставим последнего, чтоб при первом запросе получить 1
        self.scores = scores

    # Сделать текущим следующего игрока и вернуть его
    def next_player(self):
        self.current_player += 1
        if self.current_player == len(self.players):
            self.current_player = 0
        self.print_table() # Обновляем турнирную таблицу
        return self.players[self.current_player]

    # Сделать текущим переданного игрока и обновить турнирную таблицу
    def set_current_player(self, player):
        self.current_player = player.number
        self.print_table() # Обновляем турнирную таблицу

    # Вывод турнирной таблицы
    def print_table(self):
        players = self.players.copy()
        players.sort(key=lambda x: x.score, reverse=True) # Сортируем массив игроков по очкам
        for i, st in enumerate(self.string_table):
            st[0]['text'] = players[i].get_name()
            st[1]['text'] = players[i].get_score()
        # Если очки первого игрока больше чем сумма очков второго игрока и оставшихся в игре очков
        # Значит его уже нельзя догнать, окрашиваем его имя красным или черным если это не так
        if players[0].get_score() > (players[1].get_score() + self.scores.get_points_left()):
            self.string_table[0][0]['fg'] = 'red'
        else:
            self.string_table[0][0]['fg'] = 'black'

# Получение фокуса полями ввода, запрещает перемещение вправо, если слева остается нулевое поле
# При удачном переходе запрашивает изменение попытки и таблицы очков
def focus_in_word(event, num):
    if num > 0:
        if int(score[num-1].get()) == 0:
            word[num-1].focus()
            return
        elif num == 2:
            if int(score[0].get()) == 0:
                word[0].focus()
                return
    # Переход одобрен
    word[num].select_range(0, END) # Выделяем данные в поле
    step.try_change(num) # Меняем попытку

# Нажатие клавишь в полях ввода
def word_press(event, num):
    if (event.state & 0x4) != 0:
        return # Не допускаем обработку клавишь с нажатым CTRL
    if event.keycode == 8:
        if step.get_try_summa() != 0:
            score[num].delete(0, "end")
            score[num].insert(0, '0')
            word[num].select_range(0, END)
        else:
            score[num].delete(0, "end")
            score[num].insert(0, '0')
            previous_try()
            return
    if event.keycode == 39:
        # Стрелка вправо
        next_try()
        return
    if event.keycode == 37:
        # Стрелка влево
        previous_try()
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
    step.set_try_score(text) # Записываем очки хода
    all_score_labl['text'] = f'Итого: {step.summa()}' # Показываем выбитую сумму
    if num < 2:
        # В старшем разряде не может быть цифры больше 2, поэтому переходим к следующему полю
        if text > 2:
            next_try()
    # Enter
    if event.keycode == 13:
        enter()
        return

# Нажатие графических кнопок
def button_digit(sector):
    num = step.get_try_number() # Номер поля которое заполняется
    score[num].delete(0, "end")
    score[num].insert(0, sector)
    step.set_try_score(int(sector))  # Записываем очки хода
    all_score_labl['text'] = f'Итого: {step.summa()}'  # Показываем выбитую сумму
    next_try()


# Переход на правое поле (1 или 2), когда левое (0 или 1) правильно заполнено
def next_try():
    num = step.get_try_number() # Узнаем номер текущей попытки
    if num < 2:
        word[num + 1].focus()

# Переход на левое поле (1 или 2)
def previous_try():
    num = step.get_try_number() # Узнаем номер текущей попытки
    if num > 0:
        word[num - 1].focus()

# Нажатие Enter или кнопки Ок
def enter():
    num = step.get_try_number()  # Номер поля на котором нажат Enter
    if num < 2:
        next_try() # Переход к следующему полю
    else:
        if int(score[num].get()) == 0:
            return
        enter_or_esc()

# Одинаковая часть для Enter и ESC
def enter_or_esc():
    if step.step_end():
        # Ход сохраняется не в конец истории
        if step.step_change():
            # Результаты хода были изменены, спросим Будем ли сохранять, теряя историю
            if not mb.askyesno('Внимание', 'Результаты хода были изменены. Сохранение хода приведет к потере дальнейшей '
                                    'истории. Сохранить ход?' ):
                return
        else:
            # Ход не был изменен поэтому совершается просто переход вперед по истории
            history_next(0)
            return
    # Завершение хода игрока, переход к следующему
    # Очищаем поля ввода
    score[0].delete(0, "end")
    score[0].insert(0, '0')
    score[1].delete(0, "end")
    score[1].insert(0, '0')
    score[2].delete(0, "end")
    score[2].insert(0, '0')
    all_score_labl['text'] = f'Итого: 0'  # Обнуляем выбитую сумму
    step.next_step() # Создаем новый ход
    score[0].focus() # Фокус на первое поле ввода

# Перемотка истории назад
def history_previous(event=0):
    step_old = step.history_previous()
    if not step_old:
        return
    # Устанавливаем поля ввода
    score[0].delete(0, "end")
    score[0].insert(0, step_old.trys[0])
    score[1].delete(0, "end")
    score[1].insert(0, step_old.trys[1])
    score[2].delete(0, "end")
    score[2].insert(0, step_old.trys[2])
    all_score_labl['text'] = f'Итого: {step.summa()}'  # Показываем выбитую сумму
    score[step_old.try_number].focus() # Фокус на последнее поле ввода
    word[step_old.try_number].select_range(0, END) # Выделяем данные в поле

# Перемотка истории вперед
def history_next(event=0):
    step_next = step.history_next()
    if not step_next:
        return
    # Устанавливаем поля ввода
    score[0].delete(0, "end")
    score[0].insert(0, step_next.trys[0])
    score[1].delete(0, "end")
    score[1].insert(0, step_next.trys[1])
    score[2].delete(0, "end")
    score[2].insert(0, step_next.trys[2])
    all_score_labl['text'] = f'Итого: {step.summa()}'  # Показываем выбитую сумму
    score[step_next.try_number].focus() # Фокус на последнее поле ввода
    word[step_next.try_number].select_range(0, END) # Выделяем данные в поле

# Нажата клавиша esc
def esc(event=0):
    step.null_step()
    enter_or_esc()

root = Tk()
root.attributes("-fullscreen", True)

scores = Scores() # Создаем объект управляющий очками, таблицей и подсказкой

players = Players(root, scores) # Создаем объекты игроков и турнирную таблицу, передаем ему экран и объект очков

step = Steps(scores, players, root) # создаем первый ход, передаем ему объекты очков и игроков и объект экрана



score = word = [0, 0, 0]
score[0] = StringVar() # Переменная для поля ввода
score[1] = StringVar()
score[2] = StringVar()
word[0] = Entry(root, width=2, font="Helvetica 40", textvariable=score[0])
word[1] = Entry(root, width=2, font="Helvetica 40", textvariable=score[1])
word[2] = Entry(root, width=2, font="Helvetica 40", textvariable=score[2])
word[0].place(x=450, y=535)
word[1].place(x=530, y=535)
word[2].place(x=610, y=535)
word[0].bind('<FocusIn>', lambda event, x=0: focus_in_word(event, x))
word[1].bind('<FocusIn>', lambda event, x=1: focus_in_word(event, x))
word[2].bind('<FocusIn>', lambda event, x=2: focus_in_word(event, x))
word[0].bind('<KeyRelease>', lambda event, x=0: word_press(event, x))
word[1].bind('<KeyRelease>', lambda event, x=1: word_press(event, x))
word[2].bind('<KeyRelease>', lambda event, x=2: word_press(event, x))
all_score_labl = Label(root, text='Итого: 0', font=f'Helvetica 20', width=8, anchor="w", fg='blue')
all_score_labl.place(x=450, y=605)
root.bind("<Escape>", esc)
root.bind("<Control-Right>", history_next)
root.bind("<Control-Left>", history_previous)

Button(text='< Исория', command=history_previous, font="Helvetica 12").place(x=865, y=640)
Button(text='Исория >', command=history_next, font="Helvetica 12").place(x=955, y=640)
Button(text='Пропуск', command=esc, font="Helvetica 12").place(x=1063, y=640)


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


