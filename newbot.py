#импортируем все нужные библиотека
import codecs    #потому что слетала кодировка
import json    #потому что словарь в формате json
import telebot    #непосредственно библиотека для работы с ботом
from telebot import *
from collections import deque    #очередь для сообщений

bot = telebot.TeleBot('1152483061:AAEb3U5qdlkuh_6oV9oplfCctZK6ERpvczE')    #это и есть наш бот


#открываем json файл и вытаскиваем оттуда всю информацию
f = codecs.open("game.json", "r", "utf_8_sig")
js = f.read()
f.close()
game = json.loads(js)

#тема - название раздела, который будет изучаться
#блок - какое-то количество вопросов, объединённых одним заданием
#задание - то, что нужно сделать (выбрать, написать, вставить пропуск и т.д.)
#вопрос - то, на что пользователю нужно каким-то образом ответить


#записываем все названия тем в список
names = []                       #0 - Артикли, 1 - Существительные, 2- Степени сравнения прилагательных, 3 - Предлоги,
for name in game["themes"]:      #4 - Использование времён, 5 - Пассивный залог, 6 - Инфинитивы, 7 - Причастие,
    n = game["themes"][name]["name"]  #8- Герундий, 9 - Сложное дополнение, 10 - Сложное подлежащее, 11 - Условные предложения,
    names.append(n)                   #12- Конструкция 'I wish', 13 - Модальные глаголы

#записываем все отклики в список
call_backs = []
for call_back in game["themes"]:
    c = game["themes"][call_back]["call_back"]
    call_backs.append(c)


#обработка команды /start, кнопки с выбором темы
@bot.message_handler(commands=['start'])
def themes(m):
    ci = m.chat.id
    keyboard = types.InlineKeyboardMarkup()
    for i in range(14):
        key = types.InlineKeyboardButton(text=names[i], callback_data=call_backs[i])
        keyboard.add(key)
    bot.send_message(ci, text='Выберите раздел, который хотите отточить:',
                     reply_markup=keyboard)


#те же кнопки с выбором темы, но уже для использования внутри основного цикла
def for_themes(m):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(14):
        key = types.InlineKeyboardButton(text=names[i], callback_data=call_backs[i])
        keyboard.add(key)
    bot.send_message(m.message.chat.id, text='Выберите раздел, который хотите отточить:',
                     reply_markup=keyboard)


#создаём очередь
queue = deque()


#текст каждого нового полученного сообщения записываем в эту очередь первым элементом
@bot.message_handler(content_types=['text'])
def message_in(m):
    a = m.text
    queue.append(a)
    print(queue)


#извлекаем последний (оно же первый) текст и возвращаем его
def message_out():
    while len(queue) == 0:
        time.sleep(1)
    m = queue.popleft()
    return m


#обработка команды /help
@bot.message_handler(commands=['help'])
def help1(message):
    bot.send_message(message.chat.id, 'Напиши "/start"')


#основной цикл
@bot.callback_query_handler(func=lambda call: True)
def optionals(m):
    cid = m.message.chat.id   #id того чата, в котором сейчас находимся
    choose_new_theme = False    #флаг для выбора новой темы
    # если нажали кнопку "Артикли"
    if m.data == 'articles':
        markup_articles = types.ReplyKeyboardMarkup(False, True)    #создаём кастомную клавиатуру
        markup_articles.row('a', 'an', 'the', '_')    #первый ряд кнопок
        markup_articles.row('Нужна помощь.')    #второй ряд кнопок
        markup_articles.row("Выбрать другую тему.")    #третий ряд кнопок
        keyboard_end = types.InlineKeyboardMarkup()    #кнопка, которая показывается при окончании темы
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['articles']['questions'])):    #перебираем блоки заданий
            for a in range(len(game['themes']['articles']['questions'][z]['question'])):
                if choose_new_theme is True:     #проверяем, не выбрана ли другая тема соответствующей кнопкой
                    break
                bot.send_message(cid, game['themes']['articles']['questions'][z]['task'] + '\n\n' +    #выводим вопросы
                                 game['themes']['articles']['questions'][z]['question'][a],
                                 reply_markup=markup_articles)
                b = message_out()    #получаем ответ и обрабатываем его
                if b == "Выбрать другую тему.":
                    choose_new_theme = True   #меняем состояние флага
                    for_themes(m)
                elif b == "Нужна помощь.":
                    bot.send_message(cid, game['themes']['articles']['questions'][z]['help'])
                    bot.send_message(cid,
                                     "Попробуйте ещё раз" + "\n" + game['themes']['articles']['questions'][z]
                                     ['task'] + '\n\n' + game['themes']['articles']['questions'][z]['question']
                                     [a], reply_markup=markup_articles)
                    b = message_out()
                else:
                    while b != game['themes']['articles']['questions'][z]['answer'][a]:   #до тех пор, пока ответ неправильный, вопрос повторяется
                        bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.'+'\n' + game['themes']
                                         ['articles']['questions'][z]['task'] + '\n\n' + game['themes']['articles']
                                         ['questions'][z]['question'][a], reply_markup=markup_articles)

                        b = message_out()
                        if b == "Нужна помощь.":    #попросить грамматическую справку можно как прочитав задание, так и неправильно ответив несколько раз
                            bot.send_message(cid, game['themes']['articles']['questions'][z]['help'])
                            bot.send_message(cid,
                                             "Попробуйте ещё раз" + "\n" + game['themes']['articles']['questions'][z]
                                             ['task'] + '\n\n' + game['themes']['articles']['questions'][z]['question']
                                             [a], reply_markup=markup_articles)
                            b = message_out()
        if not choose_new_theme:
            bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)    #появлется после того, как закончились все блоки и вопросы в них

    #сюда будут приходить отклики после окончания любой из тем
    elif m.data == "end":
        for_themes(m)

    #если нажали кнопку "Существительные"
    elif m.data == 'nouns':
        keyboard_nouns = types.InlineKeyboardMarkup()
        key_nouns_help = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="nouns_help")
        keyboard_nouns.add(key_nouns_help)
        key_nouns_answer = types.InlineKeyboardButton(text="Я не знаю. Покажи ответ.", callback_data="nouns_answer")
        keyboard_nouns.add(key_nouns_answer)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['nouns']['questions'])):
            for a in range(len(game['themes']['nouns']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['nouns']['questions'][z]['task'] + '\n\n' +
                                 game['themes']['nouns']['questions'][z]['question'][a], reply_markup=keyboard_nouns)
                b = message_out()
                while b.lower() != game['themes']['nouns']['questions'][z]['answer'][a]:
                    bot.send_message(cid,
                                     'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['nouns']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['nouns']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_nouns)
                    b = message_out()
        bot.send_message(cid,
                         "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали кнопку "Степени сравнения прилагательных"
    elif m.data == 'comparison':
        keyboard_comparison = types.InlineKeyboardMarkup()
        key_comparison = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="comparison_help")
        keyboard_comparison.add(key_comparison)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['comparison']['questions'])):
            for a in range(len(game['themes']['comparison']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['comparison']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['comparison']['questions'][z]['question'][a], reply_markup=keyboard_comparison)
                b = message_out()
                while b.lower() != game['themes']['comparison']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['comparison']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['comparison']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_comparison)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали кнопку "Предлоги"
    elif m.data == 'prepositions':
        keyboard_prepositions = types.InlineKeyboardMarkup()
        key_prepositions = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="prepositions_help")
        keyboard_prepositions.add(key_prepositions)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['prepositions']['questions'])):
            for a in range(len(game['themes']['prepositions']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['prepositions']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['prepositions']['questions'][z]['question'][a], reply_markup=keyboard_prepositions)
                b = message_out()
                while b.lower() != game['themes']['prepositions']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['prepositions']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['prepositions']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_prepositions)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали кнопку "Использование времён"
    elif m.data == 'tenses':
        keyboard_tenses = types.InlineKeyboardMarkup()
        key_tenses = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="tenses_help")
        keyboard_tenses.add(key_tenses)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['tenses']['questions'])):
            for a in range(len(game['themes']['tenses']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['tenses']['questions'][z]['task'] + '\n\n' + game['themes']
                                ['tenses']['questions'][z]['question'][a], reply_markup=keyboard_tenses)
                b = message_out()
                while b.lower() != game['themes']['tenses']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['comparison']
                                     ['tenses'][z]['task'] + '\n\n' + game['themes']['tenses']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_tenses)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали кнопку "Пассивный залог"
    elif m.data == 'passive':
        keyboard_passive = types.InlineKeyboardMarkup()
        key_passive = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="passive_help")
        keyboard_passive.add(key_passive)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['passive']['questions'])):
            for a in range(len(game['themes']['passive']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['passive']['questions'][z]['task'] + '\n\n' + game['themes']
                                ['passive']['questions'][z]['question'][a], reply_markup=keyboard_passive)
                b = message_out()
                while b.lower() != game['themes']['passive']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['passive']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['passive']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_passive)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали кнопку "Инфинитивы"
    elif m.data == 'infinitive':
        keyboard_infinitive = types.InlineKeyboardMarkup()
        key_infinitive = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="infinitive_help")
        keyboard_infinitive.add(key_infinitive)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['infinitive']['questions'])):
            for a in range(len(game['themes']['infinitive']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['infinitive']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['infinitive']['questions'][z]['question'][a], reply_markup=keyboard_infinitive)
                b = message_out()
                while b.lower() != game['themes']['infinitive']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['infinitive']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['infinitive']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_infinitive)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали кнопку "Причастие"
    elif m.data == 'participle':
        keyboard_participle = types.InlineKeyboardMarkup()
        key_participle = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="participle_help")
        keyboard_participle.add(key_participle)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['participle']['questions'])):
            for a in range(len(game['themes']['participle']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['participle']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['participle']['questions'][z]['question'][a], reply_markup=keyboard_participle)
                b = message_out()
                while b.lower() != game['themes']['participle']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['participle']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['participle']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_participle)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали кнопку "Герундий"
    elif m.data == 'gerund':
        keyboard_gerund = types.InlineKeyboardMarkup()
        key_gerund = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="gerund_help")
        keyboard_gerund.add(key_gerund)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['gerund']['questions'])):
            for a in range(len(game['themes']['gerund']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['gerund']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['gerund']['questions'][z]['question'][a], reply_markup=keyboard_gerund)
                b = message_out()
                while b.lower() != game['themes']['gerund']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['gerund']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['comparison']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_gerund)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали кнопку "Сложное дополнение"
    elif m.data == 'complex object':
        keyboard_cmplxobj = types.InlineKeyboardMarkup()
        key_cmplxobj = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="cmplxobj_help")
        keyboard_cmplxobj.add(key_cmplxobj)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['complex object']['questions'])):
            for a in range(len(game['themes']['complex object']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['complex object']['questions'][z]['task'] + '\n\n' + game['themes']
                                ['complex object']['questions'][z]['question'][a], reply_markup=keyboard_cmplxobj)
                b = message_out()
                while b.lower() != game['themes']['complex object']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['complex object']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['complex object']['questions']
                                     [z]['question'][a], reply_markup=keyboard_cmplxobj)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали на кнопку "Сложное подлежащее"
    elif m.data == 'complex subject':
        keyboard_cmplxsubj = types.InlineKeyboardMarkup()
        key_cmplxsubj = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="cmplxsubj_help")
        keyboard_cmplxsubj.add(key_cmplxsubj)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['complex subject']['questions'])):
            for a in range(len(game['themes']['complex subject']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['complex subject']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['complex subject']['questions'][z]['question'][a], reply_markup=keyboard_cmplxsubj)
                b = message_out()
                while b.lower() != game['themes']['complex subject']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['complex subject']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['complex subject']['questions']
                                     [z]['question'][a], reply_markup=keyboard_cmplxsubj)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали на кнопку "Условные предложения"
    elif m.data == 'conditional':
        keyboard_conditional = types.InlineKeyboardMarkup()
        key_conditional = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="conditional_help")
        keyboard_conditional.add(key_conditional)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['conditional']['questions'])):
            for a in range(len(game['themes']['conditional']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['conditional']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['conditional']['questions'][z]['question'][a], reply_markup=keyboard_conditional)
                b = message_out()
                while b.lower() != game['themes']['conditional']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['conditional']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['conditional']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_conditional)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали на кнопку "Конструкция 'I wish'"
    elif m.data == 'wish':
        keyboard_wish = types.InlineKeyboardMarkup()
        key_wish = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="wish_help")
        keyboard_wish.add(key_wish)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['wish']['questions'])):
            for a in range(len(game['themes']['wish']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['wish']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['wish']['questions'][z]['question'][a], reply_markup=keyboard_wish)
                b = message_out()
                while b.lower() != game['themes']['wish']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['wish']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['wish']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_wish)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)

    #если нажали на кнопку "Модальные глаголы"
    elif m.data == 'modal':
        keyboard_modal = types.InlineKeyboardMarkup()
        key_modal = types.InlineKeyboardButton(text="Нужна помощь.", callback_data="modal_help")
        keyboard_modal.add(key_modal)
        keyboard_end = types.InlineKeyboardMarkup()
        key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
        keyboard_end.add(key_end)
        for z in range(len(game['themes']['modal']['questions'])):
            for a in range(len(game['themes']['modal']['questions'][z]['question'])):
                bot.send_message(cid, game['themes']['modal']['questions'][z]['task'] + '\n\n' + game['themes']
                                 ['modal']['questions'][z]['question'][a], reply_markup=keyboard_modal)
                b = message_out()
                while b.lower() != game['themes']['modal']['questions'][z]['answer'][a]:
                    bot.send_message(cid, 'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes']['modal']
                                     ['questions'][z]['task'] + '\n\n' + game['themes']['modal']['questions'][z]
                                     ['question'][a], reply_markup=keyboard_modal)
                    b = message_out()
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)


bot.polling(none_stop=True, interval=0)
