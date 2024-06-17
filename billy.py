from telegram import Update, BotCommandScopeAllGroupChats,\
    BotCommandScopeAllPrivateChats, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler,\
    MessageHandler, filters, CallbackQueryHandler
from telegram import constants
from sys import platform
from os import path, makedirs
from logging import getLogger, DEBUG, INFO, WARNING, StreamHandler,\
    FileHandler, Formatter
from sqlite3 import connect, OperationalError
from databases import Database
import config
from language import Language, Ukraine, Russian
from random import randrange


class Users:

    def __init__(self, update: Update):
        self.__update = update
        self.__user = self.__update.effective_user

    # Перевірка на наявність нікнейма у користувача
    async def check_username(self) -> str:
        logger.debug(f"Початок перевірки нікнейма. Користувач: {self.__user}")
        if not self.__user.username:
            logger.debug("Нікнейм не існує. Ставлю ім'я. Користувач: "
                         f"{self.__user}")
            username = self.__user.first_name
        else:
            logger.debug("Нікнейм існує. Ставлю нікнейм. Нікнейм: "
                         f"{self.__user.username}. Користувач: {self.__user}")
            username = self.__user.username
        return username

    async def check_user(self):
        await db.connect()
        username = await self.check_username()
        db_id = await db.fetch_all("SELECT id FROM users")
        db_users = await db.fetch_all("SELECT username FROM users")
        data = {"username": username, "user_id": self.__user.id}
        if not any(db_users):
            logger.info(f"В датабазі {st.filename}.db, в таблиці users пусто. "
                        f"Починаю додавати дані. Дані: {data}")
            await db.execute("INSERT INTO users (username, id) VALUES "
                             "(:username, :user_id)", data)
        elif (self.__user.id,) not in db_id:
            logger.info(f"В датабазі {st.filename}.db, в таблиці users "
                        f"користувача {username} не існує. Починаю додавати "
                        f"дані. Дані: {data}")
            await db.execute("INSERT INTO users (username, id) VALUES "
                             "(:username, :user_id)", data)
        elif (username,) not in db_users:
            logger.info(f"В датабазі {st.filename}.db, в таблиці users "
                        f"користувач {username} існує, але під іншим "
                        "нікнеймом. Починаю оновлювати нікнейм")
            await db.execute("UPDATE users SET username=:username WHERE "
                             "id=:user_id", data)
        else:
            logger.debug(f"В датабазі {st.filename}.db, в таблиці users "
                         f"користувач {username} знайдений")
        await db.disconnect()


class Level:

    def __init__(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        self.__update = update
        self.__ctx = ctx
        self.__users = Users(self.__update)
        self.__check = Check(self.__update)
        self.__lang = Language(self.__update)
        self.__user = self.__update.effective_user
        self.__chat = self.__update.effective_chat

    # Проверка на наличие и берет уже существующий опыт
    async def __get_exp(self) -> int:
        await db.connect()
        username = await self.__users.check_username()
        logger.debug(f"Отримую рівень. Користувач: {username}")
        id_dict = {"user_id": self.__user.id}
        id_levels = await db.fetch_all("SELECT id FROM levels")
        if not any(id_levels):
            logger.info(f"Створення. В датабазі {st.filename}.db, в таблиці "
                        "levels немає користувачів")
            entry = "INSERT INTO levels (id, exp) VALUES (:user_id, 1)"
            await db.execute(entry, id_dict)
            exp = 1
        elif (self.__user.id,) not in id_levels:
            logger.info("Данные не найдены. Создаю и добавляю данные в "
                        f"датабазу {st.filename}.sqlite, в таблицу levels. "
                        f"Користувач: {username}")
            entry = "INSERT INTO levels (id, exp) VALUES (:user_id, 1)"
            await db.execute(entry, id_dict)
            exp = 1
        else:
            logger.debug("Данные найдены. Начинаю получать опыт. Користувач: "
                         f"{username}")
            query = "SELECT exp FROM levels WHERE id=:user_id"
            exp = await db.fetch_one(query, id_dict)
            exp = exp[0]
        await db.disconnect()
        return exp

    # Система уровней
    async def __get_lvl(self) -> float:
        await db.connect()
        username = await self.__users.check_username()
        logger.debug(f"Начинаю проверку уровня. Користувач: {username}")
        exp = await self.__get_exp()
        logger.debug(f"Добавляю +1 к {exp}. Користувач: {username}")
        data = {"exp": exp, "user_id": self.__user.id}
        await db.execute("UPDATE levels SET exp=:exp+1 WHERE id=:user_id",
                         data)
        logger.debug("Начинаю повторную проверку уровня. Користувач: "
                     f"{username}")
        exp = await self.__get_exp()
        lvl = exp / 5
        await db.disconnect()
        return lvl

    # Перевірка на "круглу цифру" в рівні користувача
    async def lvl_system(self):
        username = await self.__users.check_username()
        logger.debug("Новое сообщение. Начинаю проверку уровня. Користувач: "
                     f"{username}")
        if self.__chat.type != constants.ChatType.PRIVATE:
            if not self.__user.is_bot:
                raw_lvl = await self.__get_lvl()
                lvl = round(raw_lvl)
                if raw_lvl in (5, 10, 20, 35, 50, 100):
                    logger.debug(f"У пользователя {self.__user.first_name}"
                                 f" {lvl} уровень")
                    lang = self.__lang(lvl=raw_lvl)
                    await self.__ctx.bot.send_message(self.__chat.id, lang.lvl)
            else:
                # todo logger
                pass
        else:
            # todo logger
            pass


class Check:

    def __init__(self, update: Update):
        self.__update = update
        self.__user = self.__update.effective_user
        self.__chat = self.__update.effective_chat

    # Перевірка існування налаштувань в датабазі
    async def check_options(self):
        await db.connect()
        id_dict = {"chat_id": self.__chat.id}
        chat_ids = await db.fetch_all("SELECT chat_id FROM options")
        if not any(chat_ids):
            logger.info(f"В датабазі {st.filename}.db, в таблиці options "
                        "пусто. Починаю додавати дані. Дані: "
                        f"({self.__chat.id}, 1, 1, 1, 1)")
            entry = "INSERT INTO options VALUES (:chat_id, 1, 1, 1, 1)"
            await db.execute(entry, id_dict)
        elif (self.__chat.id,) not in chat_ids:
            logger.info(f"В датабазі {st.filename}.db, в таблиці options чата "
                        f"під ID {self.__chat.id} не існує. Починаю додавати "
                        f"дані. Дані: ({self.__chat.id}, 1, 1, 1, 1)")
            entry = "INSERT INTO options VALUES (:chat_id, 1, 1, 1, 1)"
            await db.execute(entry, id_dict)
        await db.disconnect()


# Если команды не существует
async def command_error(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    users = Users(update)
    lang = Language(update)
    chat = update.effective_chat
    username = await users.check_username()
    logger.debug(f"Користувач {username} ввів невідому команду. Відправляю "
                 "повідомлення про помилку")
    await ctx.bot.send_message(chat.id, lang().idk_cmd_error)


async def message_sys(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user != ctx.bot:
        users = Users(update)
        lvl = Level(update, ctx)
        await users.check_user()
        await lvl.lvl_system()


# Шаблон для команд
async def template(
        update: Update,
        ctx: ContextTypes.DEFAULT_TYPE,
        message: str = None,
        sticker: str = None
):
    await message_sys(update, ctx)
    await db.connect()
    users = Users(update)
    lang = Language(update)()
    chat = update.effective_chat
    username = await users.check_username()
    logger.debug("Вызван шаблон команд. Начинаю получать пользователей этого "
                 "чата/группы/канала. Користувач, который вызвал команду: "
                 f"{username}")
    usernames = await db.fetch_all("SELECT username FROM users")
    if not any(ctx.args):
        logger.debug("В вызванной команде нету аргументов. Отправляю сообщение"
                     " об ошибке. Користувач: {username}")
        await ctx.bot.send_message(chat.id, lang.empty)
    elif len(ctx.args) >= 2:  # Проверка на лишние аргументы
        logger.debug("В вызванной команде два или больше аргументов. Отправляю"
                     f" сообщение об ошибке. Користувач: {username}")
        await ctx.bot.send_message(chat.id, lang.so_many_args)
    else:
        target = ctx.args[0].replace("@", "")
        if target == ctx.bot.username:
            logger.debug("В вызванной команде аргументом является сам бот. "
                         "Пишу сообщение. Користувач, который вызвал команду: "
                         f"{username}")
            await ctx.bot.send_message(chat.id, "♂That turns me on♂")
            await ctx.bot.send_sticker(chat.id, "CAACAgIAAxkBAAIDmWPLpB7o_dbLh"
                                                "aC2mTmJzUMgrTmjAAIPEQACiMXRSy"
                                                "79YsevxWPOLQQ")
        elif target == username:
            logger.debug("В вызванной команде аргументом является сам "
                         f"користувач. Пишу сообщение. Користувач: {username}")
            if update.message.text.startswith("/warm"):
                await ctx.bot.send_message(chat.id, message + lang.self_alt)
            else:
                await ctx.bot.send_message(chat.id, message + lang.self)
            await ctx.bot.send_sticker(chat.id, sticker)
        else:
            target_dict = {"target": target}
            if (target,) in usernames:
                logger.debug("В вызванной команде введено все правильно. "
                             f"Отправляю сообщение. Користувач: {username}")
                query = "SELECT id FROM users WHERE username=:target"
                user_id = await db.fetch_one(query, target_dict)
                member = await chat.get_member(user_id[0])
                await ctx.bot.send_message(chat.id, message + " "
                                           + member.user.first_name)
                await ctx.bot.send_sticker(chat.id, sticker)
            else:
                logger.debug("В вызванной команде несуществующий користувач. "
                             "Отправляю сообщение об ошибке. Несуществующий "
                             f"користувач: {ctx.args[0]}. Користувач, который "
                             f"вызвал команду: {username}")
                await ctx.bot.send_message(chat.id,
                                           lang.not_correct_args_error)
    await db.disconnect()


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    users = Users(update)
    lang = Language(update)()
    nickname = await users.check_username()
    logger.debug("Вызвана команда /start. Проверяю команду. Користувач: "
                 f"{nickname}")
    chat = update.effective_chat
    if chat.type == constants.ChatType.PRIVATE:
        logger.debug("Команда вызвана в личных сообщениях. Отправляю "
                     "сообщение")
        await ctx.bot.send_message(chat.id, lang.start)
    else:
        logger.debug("Команда вызвана не в личных сообщениях. Пропускаю")


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    users = Users(update)
    lang = Language(update)()
    nickname = await users.check_username()
    logger.debug("Вызвана команда /help. Отправляю список команд. Користувач: "
                 f"{nickname}")
    chat = update.effective_chat
    if chat.type == constants.ChatType.PRIVATE:
        await ctx.bot.send_message(chat.id, "\n".join(lang.pm_help))
    else:
        await ctx.bot.send_message(chat.id, "\n".join(lang.help))


async def profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    lang = Language(update)()
    chat = update.effective_chat
    if chat.type == constants.ChatType.PRIVATE:
        await ctx.bot.send_message(chat.id, lang.not_here_cmd)
    else:
        await db.connect()
        users = Users(update)
        user = update.effective_user
        username = await users.check_username()
        logger.debug("Вызвана команда /profile. Отправляю данные об "
                     f"пользователе. Користувач: {username}")
        id_dict = {"id": user.id}
        usernames = await db.fetch_all("SELECT username FROM users")
        if not any(ctx.args):
            logger.debug("В вызванной команде нету аргументов. Отправляю "
                         f"сообщение об ошибке. Користувач: {username}")
            await ctx.bot.send_message(chat.id, lang.empty)
        elif len(ctx.args) >= 2:  # Проверка на лишние аргументы
            logger.debug("В вызванной команде два или больше аргументов. "
                         "Отправляю сообщение об ошибке. Користувач: "
                         f"{username}")
            await ctx.bot.send_message(chat.id, lang.so_many_args)
        else:
            target = ctx.args[0].replace("@", "")
            query = "SELECT exp FROM levels WHERE id=:id"
            exp = await db.fetch_one(query, id_dict)
            exp = exp[0]
            lvl = exp / 5
            if (target,) not in usernames:
                logger.debug("В вызванной команде несуществующий "
                             "пользователь. Отправляю сообщение об ошибке."
                             f" Несуществующий користувач: {ctx.args[0]}. "
                             "Користувач, который вызвал команду: "
                             f"{username}")
                await ctx.bot.send_message(chat.id,
                                           lang.not_correct_args_error)
            else:
                logger.debug("В вызванной команде введено все правильно. "
                             "Отправляю сообщение. Користувач: "
                             f"{username}")
                target_dict = {"target": target}
                query = "SELECT id FROM users WHERE username=:target"
                target_id = await db.fetch_one(query, target_dict)
                member = await chat.get_member(target_id[0])
                text = (f"Профиль {member.user.first_name}'а\n"
                        f"Количество написаних сообщений: {exp}\n"
                        f"Уровень: {lvl}\n")
                if lvl < 5:
                    text += f"Осталось до следующие уровня: {25 - exp}"
                elif 5 <= lvl < 10:
                    text += f"Осталось до следующие уровня: {50 - exp}"
                elif 10 <= lvl < 20:
                    text += f"Осталось до следующие уровня: {100 - exp}"
                elif 20 <= lvl < 35:
                    text += f"Осталось до следующие уровня: {175 - exp}"
                elif 35 <= lvl < 50:
                    text += f"Осталось до следующие уровня: {250 - exp}"
                elif 50 <= lvl < 100:
                    text += f"Осталось до следующие уровня: {500 - exp}"
                else:
                    text += "У тебя максимальный уровень"
                await ctx.bot.send_message(chat.id, text)
        await db.disconnect()


async def cards(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await db.connect()
    check = Check(update)
    chat = update.effective_chat
    lang = Language(update)()
    id_dict = {"chat_id": chat.id}
    entry = "SELECT cards FROM options WHERE chat_id=:chat_id"
    switch = await db.fetch_one(entry, id_dict)
    if not switch:
        await check.check_options()
        switch = await db.fetch_one(entry, id_dict)
    switch = switch[0]
    if switch != 1:
        await ctx.bot.send_message(chat.id, lang.turn_off_cmd)
    else:
        await message_sys(update, ctx)
        random_numb = randrange(3)
        if type(lang) is Ukraine:
            file_lang = f"billy_data/billy_cards/{random_numb}_ukr.png"
        elif type(lang) is Russian:
            file_lang = f"billy_data/billy_cards/{random_numb}_rus.png"
        else:
            file_lang = f"billy_data/billy_cards/{random_numb}_eng.png"
        with open(file_lang, "rb") as image:
            await ctx.bot.send_photo(update.effective_chat.id, image.read())
    await db.disconnect()


async def fisting(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await db.connect()
    check = Check(update)
    lang = Language(update)()
    chat = update.effective_chat
    id_dict = {"chat_id": chat.id}
    entry = "SELECT fisting FROM options WHERE chat_id=:chat_id"
    switch = await db.fetch_one(entry, id_dict)
    if not switch:
        await check.check_options()
        switch = await db.fetch_one(entry, id_dict)
    if switch[0] != 1:
        await ctx.bot.send_message(chat.id, lang.turn_off_cmd)
    else:
        users = Users(update)
        nickname = await users.check_username()
        logger.debug("Вызвана команда /fisting. Проверяю команду. Користувач: "
                     f"{nickname}")
        if chat.type == constants.ChatType.PRIVATE:
            await ctx.bot.send_message(chat.id, lang.not_here_cmd)
        else:
            message = lang.fisting
            sticker = ("CAACAgIAAxkBAAPNY8VZ8vZJwhn2GlF4AV-wlAJUXLYAAswUAAIK18"
                       "lLGuxoKB7NTf8tBA")
            await template(update, ctx, message, sticker)
    await db.disconnect()


async def deep(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await db.connect()
    check = Check(update)
    lang = Language(update)()
    chat = update.effective_chat
    id_dict = {"chat_id": chat.id}
    entry = "SELECT deep FROM options WHERE chat_id=:chat_id"
    switch = await db.fetch_one(entry, id_dict)
    if not switch:
        await check.check_options()
        switch = await db.fetch_one(entry, id_dict)
    switch = switch[0]
    if switch != 1:
        await ctx.bot.send_message(chat.id, lang.turn_off_cmd)
    else:
        users = Users(update)
        nickname = await users.check_username()
        chat = update.effective_chat
        logger.debug("Вызвана команда /deep. Проверяю команду. Користувач: "
                     f"{nickname}")
        if chat.type == constants.ChatType.PRIVATE:
            await ctx.bot.send_message(chat.id, lang.not_here_cmd)
        else:
            message = lang.deep
            sticker = ("CAACAgIAAxkBAAPcY8V976B2uJgTgKsYU4aU_UdEmXQAAq0SAAJCrc"
                       "lLV-Gg6SoCxPktBA")
            await template(update, ctx, message, sticker)
    await db.disconnect()


async def warm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await db.connect()
    check = Check(update)
    lang = Language(update)()
    chat = update.effective_chat
    id_dict = {"chat_id": chat.id}
    entry = "SELECT warm FROM options WHERE chat_id=:chat_id"
    switch = await db.fetch_one(entry, id_dict)
    if not switch:
        await check.check_options()
        switch = await db.fetch_one(entry, id_dict)
    switch = switch[0]
    if switch != 1:
        await ctx.bot.send_message(chat.id, lang.turn_off_cmd)
    else:
        users = Users(update)
        nickname = await users.check_username()
        chat = update.effective_chat
        logger.debug("Вызвана команда /warm. Проверяю команду. Користувач: "
                     f"{nickname}")
        if chat.type == constants.ChatType.PRIVATE:
            await ctx.bot.send_message(chat.id, lang.not_here_cmd)
        else:
            message = lang.warm
            sticker = ("CAACAgIAAxkBAAPnY8V-KUYPoww3mzj53kFxwU43PMMAArsSAAJHIs"
                       "hLmXzom_gcydQtBA")
            await template(update, ctx, message, sticker)
    await db.disconnect()


async def lvl_state(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    lang = Language(update)
    chat = update.effective_chat
    if chat.type == constants.ChatType.PRIVATE:
        await ctx.bot.send_message(chat.id, lang().not_here_cmd)
    else:
        await db.connect()
        users = Users(update)
        nickname = await users.check_username()
        logger.debug("Вызвана команда /lvl. Проверяю команду. Користувач, "
                     f"который вызвал команду: {nickname}")
        if not any(ctx.args):
            logger.debug("Аргументов не существует. Отправляю сообщение об "
                         f"отсутствие аргументов. Користувач: {nickname}")
            await ctx.bot.send_message(chat.id, lang().empty)
        else:
            logger.debug("Аргументы существуют. Проверяю правильность "
                         f"аргументов. Користувач: {nickname}")
            db_users = await db.fetch_all("SELECT username FROM users")
            target = ctx.args[0].replace("@", "")
            db_target = (target,)
            if db_target not in db_users:
                logger.debug("Користувач в аргументе не существует. Отправляю "
                             "сообщение об несуществующем пользователе. "
                             f"Несуществующий користувач: {target}. "
                             f"Користувач, который вызвал команду: {nickname}")
                await ctx.bot.send_message(chat.id, lang().no_user_in_db)
            else:
                logger.debug("Користувач в аргументе существует. Отправляю "
                             "уровень этого пользователя. Користувач: "
                             f"{nickname}")
                sql_target = {"target": target}
                query = "SELECT id FROM users WHERE username=:target"
                user_id = await db.fetch_one(query, sql_target)
                member = await chat.get_member(user_id[0])
                id_dict = {"user_id": member.user.id}
                query = "SELECT exp FROM levels WHERE id=:user_id"
                exp = await db.fetch_one(query, id_dict)
                lvl = round(exp[0] / 5)
                await ctx.bot.send_message(chat.id, lang(member.user,
                                                         lvl).lvl_cmd)
        await db.disconnect()


async def options(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await db.connect()
    # todo кнопку "Застосувати"
    # todo класи для кожної груп та функції для кожної кнопки
    check = Check(update)
    chat = update.effective_chat
    user = update.effective_user
    chat_member = await ctx.bot.get_chat_member(chat.id, user.id)
    lang = Language(update)()
    if chat.type == constants.ChatType.PRIVATE:
        await ctx.bot.send_message(chat.id, lang.not_here_cmd)
    elif chat_member.status not in (constants.ChatMemberStatus.OWNER,
                                    constants.ChatMemberStatus.ADMINISTRATOR):
        await ctx.bot.send_message(chat.id, lang.admin_options_only)
    else:
        id_dict = {"chat_id": chat.id}
        entry = ("SELECT fisting, deep, warm, cards FROM options WHERE "
                 "chat_id=:chat_id")
        db_options = await db.fetch_one(entry, id_dict)
        if not db_options:
            await check.check_options()
            db_options = await db.fetch_one(entry, id_dict)
        text_list = ["Fisting \U0000274E", "Deep \U0000274E",
                     "Warm \U0000274E", "Cards \U0000274E"]
        for n, _ in enumerate(text_list):
            if db_options[n] == 1:
                text_list[n] = text_list[n].replace("\U0000274E", "\U00002705")
        fisting_button = InlineKeyboardButton(text_list[0],
                                              callback_data="option1")
        deep_button = InlineKeyboardButton(text_list[1],
                                           callback_data="option2")
        warm_button = InlineKeyboardButton(text_list[2],
                                           callback_data="option3")
        cards_button = InlineKeyboardButton(text_list[3],
                                            callback_data="option4")
        markup = InlineKeyboardMarkup(((fisting_button, deep_button),
                                       (warm_button, cards_button)))
        await ctx.bot.send_message(chat.id, lang.switch, reply_markup=markup)
    await db.disconnect()


async def change_option(update: Update, _):
    await db.connect()
    chat = update.effective_chat
    call_query = update.callback_query
    options_dict = {"option1": "fisting", "option2": "deep",
                    "option3": "warm", "option4": "cards"}
    option = options_dict[call_query.data]
    sql_options_dict = {"chat_id": chat.id}
    entry = f"SELECT {option} FROM options WHERE chat_id=:chat_id"
    switch = await db.fetch_one(entry, sql_options_dict)
    sql_options_dict["switch"] = 0
    if 0 in switch:
        sql_options_dict["switch"] = 1
    query = f"UPDATE options SET {option}=:switch WHERE chat_id=:chat_id"
    await db.execute(query, sql_options_dict)
    old_inline = call_query.message.reply_markup.inline_keyboard
    buttons = {
        "fisting": old_inline[0][0].text,
        "deep": old_inline[0][1].text,
        "warm": old_inline[1][0].text,
        "cards": old_inline[1][1].text
    }
    switch_symbols = "\U00002705", "\U0000274E"
    if sql_options_dict["switch"] == 1:
        switch_symbols = "\U0000274E", "\U00002705"
    buttons[option] = buttons[option].replace(switch_symbols[0],
                                              switch_symbols[1])
    fisting_button = InlineKeyboardButton(buttons["fisting"],
                                          callback_data="option1")
    deep_button = InlineKeyboardButton(buttons["deep"],
                                       callback_data="option2")
    warm_button = InlineKeyboardButton(buttons["warm"],
                                       callback_data="option3")
    cards_button = InlineKeyboardButton(buttons["cards"],
                                        callback_data="option4")
    markup = InlineKeyboardMarkup(((fisting_button, deep_button),
                                   (warm_button, cards_button)))
    await call_query.edit_message_reply_markup(markup)
    await db.disconnect()
    await call_query.answer("Done!")


# Пишет заданий текст в чат
async def repeat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = Users(update)
    lang = Language(update)()
    user = update.effective_user
    nickname = await users.check_username()
    logger.debug("Вызвана команда /repeat. Проверяю команду. Користувач: "
                 f"{nickname}")
    chat = update.effective_chat
    if user.id in (config.roli.user_id, config.polinya.user_id):
        if user.id == config.roli.user_id:
            logger.info("Хеллоу, роли. Отправляю текст")
        else:
            logger.info("Хеллоу, Поля. Отправляю текст")
        await update.message.delete()
        text = " ".join(ctx.args)
        await ctx.bot.send_message(chat.id, text)
    else:
        logger.debug("У пользователя нет доступа к команде /repeat. Отправляю "
                     "сообщение, что у пользователя нет доступа к команде. "
                     f"Користувач: {nickname}")
        await ctx.bot.send_message(chat.id, lang.no_access)


# Проверка на наличие меню с командами
async def check_cmds(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = Users(update)
    lang = Language(update)()
    nickname = await users.check_username()
    logger.debug("Вызвана команда /hascmds. Проверяю команду. Користувач: "
                 f"{nickname}")
    user = update.effective_user
    chat = update.effective_chat
    if user.id == config.roli.user_id:
        logger.info("Хеллоу, роли. Проверяю меню с командами")
        pm_cmds = await \
            ctx.bot.get_my_commands(BotCommandScopeAllPrivateChats())
        group_cmds = await \
            ctx.bot.get_my_commands(BotCommandScopeAllGroupChats())
        if not any(pm_cmds) or not any(group_cmds):
            logger.debug("Меню с командами не существует. Создаю новое меню с "
                         "командами")
            await ctx.bot.send_message(chat.id, lang.no_cmd_menu)
            await ctx.bot.set_my_commands(
                [
                    ["help", lang.cmds_menu[0]],
                    ["cards", lang.cmds_menu[3]]
                ],
                scope=BotCommandScopeAllPrivateChats()
            )
            await ctx.bot.set_my_commands(
                [
                    ["help", lang.cmds_menu[0]],
                    ["profile", lang.cmds_menu[1]],
                    ["lvl", lang.cmds_menu[2]],
                    ["cards", lang.cmds_menu[3]],
                    ["fisting", lang.cmds_menu[4]],
                    ["deep", lang.cmds_menu[5]],
                    ["warm", lang.cmds_menu[6]],
                    ["options", lang.cmds_menu[7]]
                ],
                scope=BotCommandScopeAllGroupChats()
            )
        else:
            logger.debug("Меню с командами существует. Пишу сообщение, что все"
                         " в норме")
            await ctx.bot.send_message(chat.id, lang.ok)
    else:
        logger.debug("У пользователя нет доступа к команде /hascmds. Отправляю"
                     " сообщение, что у пользователя нет доступа к команде. "
                     f"Користувач: {nickname}")
        await ctx.bot.send_message(chat.id, lang.no_access)


# Сброс датабаз
async def db_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = Users(update)
    lang = Language(update)()
    user = update.effective_user
    chat = update.effective_chat
    username = await users.check_username()
    logger.info(f"Попытка сбросить таблицы. Користувач: {username}")
    if user.id == config.roli.user_id:
        if not any(ctx.args):
            logger.debug("Таблица не введена. Отправляю сообщение. Користувач:"
                         f" {username}")
            await ctx.bot.send_message(chat.id, lang.no_table_in_args)
        else:
            if ctx.args[0] == "users":
                logger.warning("Сбрасываю таблицу users")
                await db.execute("DROP TABLE users")
            elif ctx.args[0] == "levels":
                logger.warning("Сбрасываю таблицу levels")
                await db.execute("DROP TABLE levels")
            elif ctx.args[0] == "options":
                logger.warning("Сбрасываю таблицу options")
                await db.execute("DROP TABLE options")
            st.create_tables()
            logger.info("Хеллоу, роли. Таблицы сброшены")
            await ctx.bot.send_message(chat.id, lang.done)
    else:
        logger.debug(f"Не удалось, нету доступа. Користувач: {username}")
        await ctx.bot.send_message(chat.id, lang.no_access)


# Тест команда
async def test(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    logger.debug("Вызвана /test команда. Ничего интересного...zzz")
    lang = Language(update)()
    user = update.effective_user
    chat = update.effective_chat
    if user.id == config.roli.user_id:
        await ctx.bot.send_message(chat.id, "Тест")
    else:
        await ctx.bot.send_message(chat.id, lang.no_access)


# Класс для более удобного и простого запуска
class Start:
    if not path.exists("billy_data"):
        makedirs("billy_data")
    if platform == "linux":
        __filename = "billy_data/billy_telegram"
    elif platform == ("win32" or "darwin"):
        __filename = "billy_data\\billy_telegram"
    else:
        __filename = "billy_data/billy_telegram"
    __logger = getLogger("billy_telegram")
    __logger.setLevel(DEBUG)
    __console = StreamHandler()
    __console.setLevel(INFO)
    __file = FileHandler(__filename + ".log", "w", "utf-8")
    __file.setLevel(DEBUG)
    __impt_file = FileHandler("billy_data/important.log", "w", "utf-8")
    __impt_file.setLevel(WARNING)
    __formatter = Formatter("%(asctime)s | %(funcName)s (%(levelname)s): "
                            "%(message)s", "%d.%m.%y %H:%M:%S")
    __console.setFormatter(__formatter)
    __file.setFormatter(__formatter)
    __impt_file.setFormatter(__formatter)
    __logger.addHandler(__console)
    __logger.addHandler(__file)
    __logger.addHandler(__impt_file)
    __db = Database(f"sqlite+aiosqlite:///{__filename}.db")
    # Replace "config.billy.token" to your
    __app = ApplicationBuilder().token(config.billy.token).build()
    __start_cmd_handler = CommandHandler("start", start)
    __help_cmd_handler = CommandHandler("help", help_cmd)
    __profile_cmd_handler = CommandHandler("profile", profile)
    __lvl_cmd_handler = CommandHandler("lvl", lvl_state)
    __cards_cmd_handler = CommandHandler("cards", cards)
    __fisting_cmd_handler = CommandHandler("fisting", fisting)
    __deep_cmd_handler = CommandHandler("deep", deep)
    __warm_cmd_handler = CommandHandler("warm", warm)
    __options_cmd_handler = CommandHandler("options", options)
    __options_call_handler = CallbackQueryHandler(change_option, "option[\d]+")
    __temp_cmd_handler = CommandHandler("repeat", repeat)
    __check_cmds_cmd_handler = CommandHandler("hascmds", check_cmds)
    __db_reset_cmd_handler = CommandHandler("db_reset", db_reset)
    __test_cmd_handler = CommandHandler("test", test)
    __cmd_err_handler = MessageHandler(filters.COMMAND, command_error)
    __level_handler = MessageHandler(filters.ALL, message_sys)

    def create_tables(self):
        con = connect(self.__filename + ".db")
        cur = con.cursor()
        try:
            cur.execute("SELECT * FROM users")
            cur.execute("SELECT * FROM levels")
            cur.execute("SELECT * FROM options")
        except OperationalError:
            self.__logger.info(f"Створення. Таблиць в {self.__filename}.db не "
                               "існувало")
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            db_id INTEGER PRIMARY KEY,
                            username TEXT,
                            id INTEGER
                        )
                        """)
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS levels (
                            db_id INTEGER PRIMARY KEY,
                            exp INTEGER
                        )
                        """)
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS options(
                            chat_id INTEGER,
                            fisting INTEGER,
                            deep INTEGER,
                            warm INTEGER,
                            cards INTEGER
                        )
                        """)
        else:
            self.__logger.debug(f"Ігнорування. Таблиці в {self.__filename}.db "
                                "вже існують")
        finally:
            con.close()

    @property
    def filename(self):
        return self.__filename

    @property
    def logger(self):
        return self.__logger

    @property
    def db(self):
        return self.__db

    def __add_public_handlers(self):
        self.__logger.debug("Добавляю публичные обработчики")
        self.__app.add_handlers(
            [
                self.__start_cmd_handler,
                self.__help_cmd_handler,
                self.__profile_cmd_handler,
                self.__lvl_cmd_handler,
                self.__cards_cmd_handler,
                self.__fisting_cmd_handler,
                self.__deep_cmd_handler,
                self.__warm_cmd_handler,
                self.__options_cmd_handler,
                self.__options_call_handler
            ]
        )
        self.__logger.debug("Добавляю публичные обработчики")

    def __add_private_handlers(self):
        self.__logger.debug("Добавляю приватные обработчики")
        self.__app.add_handlers(
            [
                self.__temp_cmd_handler,
                self.__check_cmds_cmd_handler,
                self.__db_reset_cmd_handler,
                self.__test_cmd_handler
            ]
        )

    def __add_message_handlers(self):
        self.__logger.debug("Добавляю обработчики сообщений")
        self.__app.add_handlers(
            [
                self.__cmd_err_handler,
                self.__level_handler
            ]
        )

    # Создание таблиц (если их нет)
    def start(self):
        self.__logger.debug("Запускаю")
        self.create_tables()
        self.__add_public_handlers()
        self.__add_private_handlers()
        self.__add_message_handlers()
        all_update_types = [constant for constant in constants.UpdateType]
        print("Готовий до роботи!")
        self.__app.run_polling(allowed_updates=all_update_types)


if __name__ == "__main__":
    st = Start()
    db = st.db
    logger = st.logger
    st.start()
