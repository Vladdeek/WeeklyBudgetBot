import telebot
from telebot import types
import mysql.connector

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        port="8889",
        password="root",
        database="my-costs",
        charset="utf8",
        use_unicode=True
    )

bot = telebot.TeleBot('5057799665:AAFIb7hDGqx45-KzGtqV2_b0WRmv9A_m65U')
mybd = connect_to_database()
cursor = mybd.cursor()

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Приветствую, я телеграм бот который поможет тебе контролировать свои расходы немного иначе."
                                      "\nЯ помогу распределять твои деньги на неделю."
                                      "\nЕсть у тебя 12000 руб на месяц, "
                                      "ты вводишь сколько ты хочешь растянуть денег на неделю"
                                      ", а я в то же время посчетаю твой дневной лимит(сколько тебе желательно тратить в день что бы"
                                      " в конце месяца не сдохнуть с голоду потому что нет денег), далее ты сможешь записывать каждую свою трату"
                                      "будь то это продукты, транспорт(маршрутка или такси) и разное(все не сьедобное), так же ты сможешь"
                                      "посмотреть сколько у тебя осталось на сегодня, вышел или не вышел ли ты за лимит. "
                                      "\n\nВсе мы любим покупать"
                                      " что нибудь дорогое на что большенству людей нужно копить, я могу если у тебя в конце дня остались деньги "
                                      "выбрать что с ним сделать "
                                      "\n\nоставить(ваш остаток будет внесен в следующий день, то есть предположим твой лимит 500"
                                      "потратил ты 200 и у тебя осталось в конце дня 300, на следующий день ты сможешь потратить 800) "
                                      "\n\nотложить(тут все и так понятно)"
                                      "\nсовет для вас 'не вызывайте такси если не знаете сколько у вас денег с собой' я бот для контроля твоих денег"
                                      ", не ванга я не знаю сколько у тебя в кармане денег, хотя пару условий во мне прописаны, но они этому "
                                      "не поспособствую)"
                                      "\n\n Туториал "
                                      "\n/start - полный перезапуск бота и базы данных ваш счет и все остальное будет 0"
                                      "\n/restart - если бот где-то завис эта команда перезапускает его, без сброса данных"
                                      "\nПеред тем как потратить деньги и посчитать лимит нужно пополнить баланс"
                                      "\n'Дополнительно'->'Пополнить'"
                                      "\nЖелательно перед тем как тратить задать недельный лимит"
                                      "\n'Дополнительно'->'Обновить лимит'"
                                      "\nИформация о балансе, дневном лимите и остатке"
                                      "\n'Дополнительно'->'Баланс'"
                                      "\nНачать новый день, обновить свой сегодняшний лимит(желательно не тыкать просто так без предназначения"
                                      " ведь если из-за этого я посчитаю что то не правильно это уже будут твои проблеммы потому что я всего лишь"
                                      "набор команд из букв, цифр и символов)"
                                      "\n'Дополнительно'->'Новый день'"
                                      "\nКак тратить все мы занем)"
                                      "\n\nНадеюсь буду полезен")
    start_command(message)
    cursor.execute("INSERT INTO global(bank, day_lim, remainder, telegram_id) VALUES (%s, %s, %s, %s)", (0, 0, 0, user_id))
    cursor.execute("INSERT INTO week_limit(week_lim, telegram_id) VALUES (%s, %s)", (0, user_id))
    cursor.execute("INSERT INTO remainder(remainder, telegram_id) VALUES (%s, %s)", (0, user_id))
    mybd.commit()
def start_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Дополнительно")
    button2 = types.KeyboardButton("Потратить")
    markup.row(button2, button1)
    bot.send_message(message.chat.id, "Выберите операцию", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Дополнительно")
def settings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Пополнить")
    button2 = types.KeyboardButton("Обновить лимит")
    button3 = types.KeyboardButton("Новый день")
    button4 = types.KeyboardButton("Баланс")
    button5 = types.KeyboardButton("Назад")
    markup.add(button3)
    markup.add(button1, button4, button2)
    markup.add(button5)
    bot.send_message(message.chat.id, "Дополнительно", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Назад")
def back(message):
    start_command(message)

@bot.message_handler(commands=["restart"])
def restart(message):
    start_command(message)

@bot.message_handler(func=lambda message: message.text == "Пополнить")
def handle_deposit(message):
    bot.send_message(message.chat.id, "Сколько хотите пополнить")
    bot.register_next_step_handler(message, insert_deposit)
def insert_deposit(message):
    user_id = message.from_user.id
    if message.text.isdigit():
        deposit = int(message.text)
        cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        result = cursor.fetchone()  # Получаем результат запроса
        cursor.execute("SELECT day_lim FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        day_lim = cursor.fetchone()
        remainder = int(day_lim[0])
        if result:
            bank = result[0]  # Первый элемент кортежа
        else:
            bank = 0  # Устанавливаем значение по умолчанию
        new_bank = bank + deposit
        cursor.execute("INSERT INTO global(bank, day_lim, remainder, telegram_id) VALUES (%s, %s, %s, %s)", (new_bank, int(day_lim[0]), remainder, user_id))
        mybd.commit()
        bot.send_message(message.chat.id, "Данные были успешно добавлены!")
    else:
        bot.send_message(message.chat.id, "Введено некорректное число. Пожалуйста, введите число.")


@bot.message_handler(func=lambda message: message.text == "Потратить")
def handle_typespend(message):
    user_id = message.from_user.id
    cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    bank = cursor.fetchone()
    cursor.execute("SELECT day_lim FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    day_lim = cursor.fetchone()
    if int(bank[0]) <= 0:
        bot.send_message(message.chat.id, "Ваш кошелек пустой")
    elif int(day_lim[0]) <= 0:
        bot.send_message(message.chat.id, "(Ваш лимит не задан)"
                                          "\nИзвините, но я создан не только для записи ваших расходов,"
                                          " но и для их контроля, по этому сначала нажмите на кнопку 'Обновить лимит'"
                                          " и введите сумму которую хотите потратить за период 7 дней,"
                                          " а только потом начинайте тратить свои деньги")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Транспорт")
        button2 = types.KeyboardButton("Продукты")
        button3 = types.KeyboardButton("Разное")
        markup.add(button1, button2)
        markup.add(button3)
        bot.send_message(message.chat.id, "Выбери тип траты", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Транспорт")
def handle_trans(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Маршрутка")
    button2 = types.KeyboardButton("Такси")
    markup.add(button1, button2)
    bot.send_message(message.chat.id, "Вид транспорта", reply_markup=markup)
    bot.register_next_step_handler(message, spend_trans)
def spend_trans(message):
    user_id = message.from_user.id
    if (message.text == "Маршрутка"):
        spend = 25
        cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id, ))
        bank = cursor.fetchone()
        cursor.execute("SELECT day_lim FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1 ", (user_id,))
        day_lim = cursor.fetchone()
        cursor.execute("SELECT remainder FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1 ", (user_id,))
        remainder = cursor.fetchone()
        if int(bank[0]) < spend:
            bot.send_message(message.chat.id, "У вас на счету - " + str(bank[0]) + " руб\nЭто последние деньги!")
        else:
            new_bank = int(bank[0]) - spend
            new_remainder = int(remainder[0]) - spend
            day_lim = int(day_lim[0])
            cursor.execute("INSERT INTO global(bank, day_lim, remainder, spend, type_id, telegram_id) VALUES (%s, %s, %s, %s, 1, %s)",
                           (int(new_bank), int(day_lim), int(new_remainder), (int(spend)), user_id))
            mybd.commit()
            bot.send_message(message.chat.id, "У вас осталось: " +str(new_remainder) + " руб")
            start_command(message)
    elif message.text == "Такси":
        handle_spend(message)

@bot.message_handler(func=lambda message: message.text in ["Продукты", "Разное", "Такси"])
def handle_spend(message):
    global type
    type = message.text
    print(type)
    bot.send_message(message.chat.id, "Сколько потратил?")
    bot.register_next_step_handler(message, spend_bank)
def spend_bank(message):
    user_id = message.from_user.id
    if message.text.isdigit():
        spend = int(message.text)
        cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        bank = cursor.fetchone()
        cursor.execute("SELECT day_lim FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1 ", (user_id,))
        day_lim = cursor.fetchone()
        cursor.execute("SELECT remainder FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1 ", (user_id,))
        remainder = cursor.fetchone()
        new_remainder = 0
        if type == "Продукты":
            if int(bank[0]) < spend:
                bot.send_message(message.chat.id, "У вас на счету - " + str(bank[0]) + " руб\nЭто последние деньги!")
            else:
                new_bank = int(bank[0]) - spend
                new_remainder = int(remainder[0]) - spend
                day_lim = int(day_lim[0])
                cursor.execute(
                    "INSERT INTO global(bank, day_lim, remainder, spend, type_id, telegram_id) VALUES (%s, %s, %s, %s, 2, %s)",
                    (int(new_bank), int(day_lim), int(new_remainder), (int(spend)), user_id))
                mybd.commit()
        elif type == "Разное":
            if int(bank[0]) < spend:
                bot.send_message(message.chat.id, "У вас на счету - " + str(bank[0]) + " руб\nЭто последние деньги!")
            else:
                new_bank = int(bank[0]) - spend
                new_remainder = int(remainder[0]) - spend
                day_lim = int(day_lim[0])
                cursor.execute(
                    "INSERT INTO global(bank, day_lim, remainder, spend, type_id, telegram_id) VALUES (%s, %s, %s, %s, 3, %s)",
                    (int(new_bank), int(day_lim), int(new_remainder), (int(spend)), user_id))
                mybd.commit()
        elif type == "Такси":
            if int(bank[0]) < spend:
                bot.send_message(message.chat.id, "У вас на счету - " + str(bank[0]) + " руб\nЭто последние деньги!")
            else:
                new_bank = int(bank[0]) - spend
                new_remainder = int(remainder[0]) - spend
                day_lim = int(day_lim[0])
                cursor.execute(
                    "INSERT INTO global(bank, day_lim, remainder, spend, type_id, telegram_id) VALUES (%s, %s, %s, %s, 1, %s)",
                    (int(new_bank), int(day_lim), int(new_remainder), (int(spend)), user_id))
                mybd.commit()
        bot.send_message(message.chat.id, "У вас осталось: " +str(new_remainder) + " руб")
        start_command(message)
    else:
        bot.send_message(message.chat.id, "Введено некорректное число. Пожалуйста, введите число.")

@bot.message_handler(func=lambda message: message.text == "Обновить лимит")
def new_lim(message):
    user_id = message.from_user.id
    cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    bank = cursor.fetchone()
    bot.send_message(message.chat.id, "У вас на счету - " + str(bank[0]) + "\nСколько хотите выделить денег на неделю?")
    bot.register_next_step_handler(message, week_lim)
def week_lim(message):
    user_id = message.from_user.id
    if message.text.isdigit():
        lim = int(message.text)
        cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        bank = cursor.fetchone()
        mybd.commit()
        if bank[0] >= lim:
            week_lim = lim / 7
            day_lim = week_lim
            remainder = week_lim
            cursor.execute("INSERT INTO week_limit(week_lim, telegram_id) VALUES (%s, %s)", (week_lim, user_id))
            cursor.execute("INSERT INTO global(bank, day_lim, remainder, telegram_id) VALUES (%s, %s, %s, %s)", (int(bank[0]) ,day_lim, remainder, user_id))
            mybd.commit()
            bot.send_message(message.chat.id, "Ваш дневной лимитт: " +str(day_lim) + " руб")
            start_command(message)
        else:
            bot.send_message(message.chat.id, "Как ты собрался выделить на неделю больше чем у тебя вообще есть")
    else:
        bot.send_message(message.chat.id, "Введено некорректное число. Пожалуйста, введите число.")

@bot.message_handler(func=lambda message: message.text == "Новый день")
def next_day(message):
    user_id = message.from_user.id
    cursor.execute("SELECT remainder FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    remainder = cursor.fetchone()
    cursor.execute("SELECT week_lim FROM week_limit WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    week_lim = cursor.fetchone()

    if remainder and int(remainder[0]) > 0:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Отложить")
        button2 = types.KeyboardButton("Оставить")
        markup.add(button1, button2)
        bot.send_message(message.chat.id, "Ваш остаток: " + str(remainder[0]) + ""
                                      "\nЧто хотите сделать с остатком?", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: invest_or_next_day(msg, week_lim, remainder))
    else:
        next_day_with_remainder(message, week_lim, remainder)
def invest_or_next_day(message, week_lim, remainder):
    if message.text == "Отложить":
        invest(message, week_lim)
    elif message.text == "Оставить":
        next_day_with_remainder(message, week_lim, remainder)
def next_day_with_remainder(message, week_lim, remainder):
    user_id = message.from_user.id
    cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    bank = cursor.fetchone()
    day_lim = int(week_lim[0]) + int(remainder[0])
    if day_lim > int(week_lim[0]):
        bot.send_message(message.chat.id, "Новый день, новые траты"
                                          "\nСегодня ты можешь потратить больше, чем обычно"
                                          "\nЛимит на сегодняшний день: " + str(day_lim))
    elif day_lim < int(week_lim[0]):
        bot.send_message(message.chat.id, "Новый день, новые траты"
                                          "\nК сожалению, сегодня ты можешь потратить меньше, чем обычно"
                                          "\nЛимит на сегодняшний день: " + str(day_lim))
    else:
        bot.send_message(message.chat.id,
                         "Новый день, новые траты"
                         "\nЛимит на сегодняшний день: " + str(day_lim) + " руб")
    remainder = day_lim
    cursor.execute("INSERT INTO global(bank, day_lim, remainder, telegram_id) VALUES (%s, %s, %s, %s)",
                       (int(bank[0]), day_lim, remainder, user_id))
    start_command(message)
def invest(message, week_lim):
    user_id = message.from_user.id
    cursor.execute("SELECT remainder FROM remainder WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    invest = cursor.fetchone()
    cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    bank = cursor.fetchone()
    cursor.execute("SELECT remainder FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    rem = cursor.fetchone()
    new_invest = int(invest[0]) + int(rem[0])
    day_lim = int(week_lim[0])
    bot.send_message(message.chat.id,
                     "Новый день, новые траты"
                     "\nЛимит на сегодняшний день: " + str(day_lim)+ " руб")
    remainder = day_lim
    cursor.execute("INSERT INTO global(bank, day_lim, remainder, telegram_id) VALUES (%s, %s, %s, %s)",
                   (int(bank[0]), day_lim, remainder, user_id))
    cursor.execute("INSERT INTO remainder(remainder, telegram_id) VALUES (%s, %s)",
                   (new_invest, user_id))
    start_command(message)

@bot.message_handler(func=lambda message: message.text == "Баланс")
def deposit_command(message):
    user_id = message.from_user.id
    cursor.execute("SELECT bank FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id, ))
    bank = cursor.fetchone()
    cursor.execute("SELECT week_lim FROM week_limit WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    week_lim = cursor.fetchone()
    cursor.execute("SELECT remainder FROM global WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    remainder = cursor.fetchone()
    cursor.execute("SELECT remainder FROM remainder WHERE telegram_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    invest = cursor.fetchone()
    if bank:
        bot.send_message(message.chat.id, "Баланс: {} руб\n"
                                          "Ежедневный лимит на неделю: {} руб\n"
                                          "Остаток: {} руб\n"
                                          "Накоплено: {} руб".format(bank[0], week_lim[0], remainder[0], invest[0]))
    else:
        bot.send_message(message.chat.id, "Нет данных о банке.")

bot.polling(none_stop=True)