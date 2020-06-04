# импортируем все нужные библиотеки
import codecs    # потому что слетала кодировка
import json    # потому что словарь в формате json
import telebot    # непосредственно библиотека для работы с ботом
from telebot import *
from collections import deque   # очередь для сообщений

bot = telebot.TeleBot('1152483061:AAEb3U5qdlkuh_6oV9oplfCctZK6ERpvczE')    # это и есть наш бот, его токен

# открываем json файл и вытаскиваем оттуда всю информацию
f = codecs.open("game.json", "r", "utf_8")
js = f.read()
f.close()
game = json.loads(js)

# тема - название раздела, который будет изучаться
# блок - какое-то количество вопросов, объединённых одним заданием
# задание - то, что нужно сделать (выбрать, написать, вставить пропуск и т.д.)
# вопрос - то, на что пользователю нужно каким-то образом ответить

messages = {}    # словарь вида id - очередь от этого пользователя, чтобы развести потоки сообщений
steps = {}    # словарь вида id - тема - [номер блока, номер вопроса], чтобы сохранять прогресс пользователя

# записываем все названия тем в список
names = []                       # 0 - Артикли, 1 - Существительные, 2- Степени сравнения прилагательных, 3 - Предлоги,
for name in game["themes"]:      # 4 - Использование времён, 5 - Пассивный залог, 6 - Инфинитивы, 7 - Причастие,
    n = game["themes"][name]["name"]     # 8- Герундий, 9 - Сложное дополнение, 10 - Сложное подлежащее,
    names.append(n)      # 11 - Условные предложения, 12 - Модальные глаголы

# записываем все отклики на нажатие кнопок в список
call_backs = []
for call_back in game["themes"]:
    c = game["themes"][call_back]["call_back"]
    call_backs.append(c)


# обработка команды /start, кнопки с выбором темы
@bot.message_handler(commands=['start'])
def themes(m):
    cid = m.chat.id
    steps[cid] = {}   # создаём словарь для хранения прогресса каждого пользователя
    messages[cid] = deque()
    for back in game["themes"]:    # в каждой теме ставим 0 номер блока и 0 номер вопроса по умолчанию
        call = game["themes"][back]["call_back"]
        steps[cid][call] = [0, 0]
    keyboard = types.InlineKeyboardMarkup()  # формируем выпадающие кнопки
    for i in range(13):
        key = types.InlineKeyboardButton(text=names[i], callback_data=call_backs[i])
        keyboard.add(key)
    bot.send_message(cid, text='Выберите раздел, который хотите отточить:', reply_markup=keyboard)


# те же кнопки с выбором темы, но уже для использования внутри основного цикла, потому что там другой тип объекта
def for_themes(m):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(13):
        key = types.InlineKeyboardButton(text=names[i], callback_data=call_backs[i])
        keyboard.add(key)
    bot.send_message(m.message.chat.id, text='Выберите раздел, который хотите отточить:',
                     reply_markup=keyboard)


# что происходит, когда получаем какое-либо сообщение
@bot.message_handler(content_types=['text'])
def message_in(m):
    print(m)
    a = m.text  # берём текст этого сообщения
    print("Text", a)
    ci = m.chat.id
    queue = deque()
    messages[ci] = queue
    messages[ci].append(a)
    print(messages)
    bot.send_message(ci, a)  # добавляем текст в очередь первым (единственным, а значит, последним) элементом


# извлекаем последний (он же первый) текст и возвращаем его
def message_out(m):
    cid = m.message.chat.id
    while len(messages[cid]) == 0:    # ждём ответа пользователя
        time.sleep(1)
    k = messages[cid].popleft()    # извлекаем последний (он же первый) текст и обрабатываем
    return k


# обработка команды /help
@bot.message_handler(commands=['help'])
def help1(message):
    bot.send_message(message.chat.id, 'Напиши "/start"')


# что происходит после того, как пользователь выбрал одну из тем
def theme(m, tema):
    cid = m.message.chat.id
    choose_new_theme = False    # флаг для того, чтобы смотреть, не хочет ли пользователь сменить тему
    keyboard = types.ReplyKeyboardMarkup(False, True)    # создаём кастомную клавиатуру
    keyboard.row('Нужна помощь.')    # добавляем в неё кнопки
    keyboard.row("Я не знаю. Покажи ответ.")
    keyboard.row("Выбрать другую тему.")
    keyboard_end = types.InlineKeyboardMarkup()   # кнопка, которая появляется после решения всех заданий блока
    key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
    keyboard_end.add(key_end)
    print(messages)
    bl = steps[cid][tema][0]    # номер блока, в котором был задан последний вопрос
    for block in range(bl, len(game['themes'][tema]['questions'])):
        if choose_new_theme is True:    # а не сменить ли нам тему
            break
        qu = steps[cid][tema][1]    # номер последнего вопроса
        for question in range(qu, len(game['themes'][tema]['questions'][block]['question'])):
            if choose_new_theme is True:    # может, всё-таки сменить?
                break
            steps[cid][tema][0] = block    # получаем новый номер блока
            steps[cid][tema][1] = question    # получаем новй номер вопроса
            bot.send_message(cid, game['themes'][tema]['questions'][block]['task'] + '\n\n' +
                             game['themes'][tema]['questions'][block]['question'][question], reply_markup=keyboard)
            b = message_out(m)    # ждём ответ
            while b.lower().rstrip('.') != (game['themes'][tema]['questions'][block]['answer']
                                            [question].lower().rstrip('.')):
                # проверяем на соответствие, не обращая внимание на регистр
                if b == "Нужна помощь.":    # проверям на соответствие надписям на кнопках
                    bot.send_message(cid, game['themes'][tema]['questions'][block]['help'])
                    bot.send_message(cid,
                                     "Попробуйте ещё раз." + "\n" + game['themes'][tema]['questions'][block]
                                     ['task'] + '\n\n' + game['themes'][tema]['questions'][block]['question']
                                     [question], reply_markup=keyboard)
                    b = message_out(m)
                elif b == "Я не знаю. Покажи ответ.":
                    bot.send_message(cid,
                                     'Правильный ответ:' + '\n\n' + game['themes'][tema]['questions'][block]['answer']
                                     [question])
                    break    # нужен, чтобы бот не спамил сообщениями и переходил к следующему вопросу
                elif b == "Выбрать другую тему.":
                    choose_new_theme = True  # меняем состояние флага
                    for_themes(m)
                    break
                else:
                    bot.send_message(cid,
                                     'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes'][tema]
                                     ['questions'][block]['task'] + '\n\n' + game['themes'][tema]['questions'][block]
                                     ['question'][question], reply_markup=keyboard)
                    b = message_out(m)

    if choose_new_theme is False:    # закончили всю тему - получите печеньку
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)


# основной цикл
@bot.callback_query_handler(func=lambda call: True)
def optionals(m):

    # если нажали кнопку "Артикли", здесь не используется функция т.к. нужны дополнительные кнопки на клавиатуре
    if m.data == 'articles':
       theme(m, 'articles')

    # сюда будут приходить отклики после окончания любой из тем
    elif m.data == "end":
        for_themes(m)

    # если нажали кнопку "Существительные"
    elif m.data == 'nouns':
        theme(m, 'nouns')

    # если нажали кнопку "Степени сравнения прилагательных"
    elif m.data == 'comparison':
        theme(m, 'comparison')

    # если нажали кнопку "Предлоги"
    elif m.data == 'prepositions':
        theme(m, 'prepositions')

    # если нажали кнопку "Использование времён"
    elif m.data == 'tenses':
        theme(m, 'tenses')

    # если нажали кнопку "Пассивный залог"
    elif m.data == 'passive':
        theme(m, 'passive')

    # если нажали кнопку "Инфинитивы"
    elif m.data == 'infinitive':
        theme(m, 'infinitive')

    # если нажали кнопку "Причастие"
    elif m.data == 'participle':
        theme(m, 'participle')

    # если нажали кнопку "Герундий"
    elif m.data == 'gerund':
        theme(m, 'gerund')

    # если нажали кнопку "Сложное дополнение"
    elif m.data == 'complex object':
        theme(m, 'complex object')

    # если нажали на кнопку "Сложное подлежащее"
    elif m.data == 'complex subject':
        theme(m, 'complex subject')

    # если нажали на кнопку "Условные предложения"
    elif m.data == 'conditional':
        theme(m, 'conditional')

    # если нажали на кнопку "Модальные глаголы"
    elif m.data == 'modal':
        theme(m, 'modal')


bot.polling(none_stop=True, interval=0)
