from telegram import User, Update, ChatMember, BotCommandScopeAllGroupChats
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler,\
    MessageHandler, filters
from sys import platform
from os import path, makedirs
from logging import getLogger, DEBUG, INFO, WARNING, StreamHandler,\
    FileHandler, Formatter
from sqlite3 import connect, OperationalError
from databases import Database
import config
from language import Russian, Ukraine


async def get_db_id(user: User) -> int:
    await st.db.connect()
    query = "SELECT db_id FROM users WHERE id=:user_id"
    id_dict = {"user_id": user.id}
    db_id = await st.db.fetch_one(query, id_dict)
    db_id = db_id[0]
    await st.db.disconnect()
    return db_id


# Перевірка на наявність нікнейма у користувача
async def check_username(user: User) -> str:
    st.logger.debug(f"Початок перевірки нікнейма. Користувач: {user}")
    if user.username is None:
        st.logger.debug("Нікнейм не існує. Ставлю ім'я. Користувач: "
                        f"{user}")
        username = user.first_name
    else:
        st.logger.debug("Нікнейм існує. Ставлю нікнейм. Нікнейм: "
                        f"{user.username}. Користувач: {user}")
        username = user.username
    return username


# Проверка языка у пользователя
async def check_language(
        update: Update,
        _,
        user: User = None,
        member: ChatMember = None,
        lvl: int | float = None
) -> Ukraine or Russian:
    if update.effective_user.language_code == "uk":
        return Ukraine(user, member, lvl)
    else:
        return Russian(user, member, lvl)


class Level:

    # Проверка на наличие и берет уже существующий опыт
    @staticmethod
    async def get_exp(user: User) -> int:
        await st.db.connect()
        name = await check_username(user)
        st.logger.debug(f"Отримую рівень. Користувач: {name}")
        sql_id = user.id,
        sql_id_dict = {"id": user.id}
        id_levels = await st.db.fetch_all("SELECT id FROM levels")
        if not any(id_levels):
            st.logger.info(f"Створення. В датабазі {st.filename}.db, в таблиці"
                           " levels немає користувачів")
            await st.db.execute("INSERT INTO levels (id, exp) VALUES (:id, 1)",
                                sql_id_dict)
            exp = 1
            await st.db.disconnect()
            return exp
        elif sql_id not in id_levels:
            st.logger.info("Данные не найдены. Создаю и добавляю данные в "
                           f"датабазу {st.filename}.sqlite, в таблицу levels. "
                           f"Користувач: {name}")
            await st.db.execute("INSERT INTO levels (id, exp) VALUES (:id, 1)",
                                sql_id_dict)
            exp = 1
            await st.db.disconnect()
            return exp
        else:
            st.logger.debug("Данные найдены. Начинаю получать опыт. "
                            f"Користувач: {name}")
            query = "SELECT exp FROM levels WHERE id=:id"
            exp = await st.db.fetch_one(query, sql_id_dict)
            await st.db.disconnect()
            return exp[0]

    # Система уровней
    @classmethod
    async def get_lvl(cls, user: User) -> float:
        await st.db.connect()
        name = await check_username(user)
        st.logger.debug(f"Начинаю проверку уровня. Користувач: {name}")
        exp = await cls.get_exp(user)
        st.logger.debug(f"Добавляю +1 к {exp}. Користувач: {name}")
        data = {"exp": exp, "id": user.id}
        await st.db.execute("UPDATE levels SET exp=:exp+1 WHERE id=:id", data)
        st.logger.debug("Начинаю повторную проверку уровня. Користувач: "
                        f"{name}")
        exp = await cls.get_exp(user)
        lvl = exp / 5
        await st.db.disconnect()
        return lvl

    # Проверка на "круглую цифру" в уровне
    @classmethod
    async def lvl_system(cls, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        username = await check_username(user)
        st.logger.debug("Новое сообщение. Начинаю проверку уровня. "
                        f"Пользователя: {username}")
        chat = update.effective_chat
        if chat.type != "private":
            if ctx.bot.id != update.effective_user.id:
                if not update.effective_user.is_bot:
                    raw_lvl = await cls.get_lvl(user)
                    lvl = round(raw_lvl)
                    lang = await check_language(update, ctx, user, lvl=raw_lvl)
                    if raw_lvl == 5:
                        st.logger.debug(f"У пользователя {user.first_name} "
                                        f"{lvl} уровень")
                        await ctx.bot.send_message(chat.id, lang.lvl_text)
                    elif raw_lvl == 10:
                        st.logger.debug(f"У пользователя {user.first_name} "
                                        f"{lvl} уровень")
                        await ctx.bot.send_message(chat.id, lang.lvl_text)
                    elif raw_lvl == 20:
                        st.logger.debug(f"У пользователя {user.first_name} "
                                        f"{lvl} уровень")
                        await ctx.bot.send_message(chat.id, lang.lvl_text)
                    elif raw_lvl == 35:
                        st.logger.debug(f"У пользователя {user.first_name} "
                                        f"{lvl} уровень")
                        await ctx.bot.send_message(chat.id, lang.lvl_text)
                    elif raw_lvl == 50:
                        st.logger.debug(f"У пользователя {user.first_name} "
                                        f"{lvl} уровень")
                        await ctx.bot.send_message(chat.id, lang.lvl_text)
                    elif raw_lvl == 100:
                        st.logger.debug(f"У пользователя {user.first_name} "
                                        f"{lvl} уровень")
                        await ctx.bot.send_message(chat.id, lang.lvl_text)


async def check_user(update: Update, _):
    await st.db.connect()
    user = update.effective_user
    username = await check_username(user)
    db_name = username,
    db_id = await st.db.fetch_all("SELECT id FROM users")
    db_users = await st.db.fetch_all("SELECT username FROM users")
    data = {"username": username, "user_id": user.id}
    if not any(db_users):
        st.logger.info(f"В датабазе {st.filename}.sqlite, в таблице users "
                       f"пусто. Начинаю добавлять данные. Данные: {data}")
        await st.db.execute("INSERT INTO users (username, id) VALUES "
                            "(:username, :user_id)", data)
    elif user.id not in db_id:
        await st.db.execute("INSERT INTO users (username, id) VALUES "
                            "(:username, :user_id)", data)
    elif db_name not in db_users:
        st.logger.info(f"В датабазе {st.filename}.sqlite, в таблице users "
                       f"пользователя {username} нет. Начинаю добавлять "
                       f"данные. Данные: {data}")
        await st.db.execute("UPDATE users SET username=:username WHERE "
                            "id=:user_id", data)
    else:
        st.logger.debug(f"В датабазе {st.filename}.sqlite, в таблице users "
                        f"користувач {username} найден. Беру опыт")
    await st.db.disconnect()


# Если команды не существует
async def command_error(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    user = update.effective_user
    chat = update.effective_chat
    username = await check_username(user)
    lang = await check_language(update, ctx)
    st.logger.debug(f"Користувач {username} ввел неизвестную команду. "
                    "Отправляю сообщение об ошибке")
    await ctx.bot.send_message(chat.id, lang.idk_command_text)


async def message_sys(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user != ctx.bot:
        lvl = Level()
        await check_user(update, ctx)
        await lvl.lvl_system(update, ctx)


# Шаблон для команд
async def template(
        update: Update,
        ctx: ContextTypes.DEFAULT_TYPE,
        message: str = None,
        sticker: str = None
):
    await message_sys(update, ctx)
    await st.db.connect()
    user = update.effective_user
    chat = update.effective_chat
    username = await check_username(user)
    lang = await check_language(update, ctx)
    st.logger.debug("Вызван шаблон команд. Начинаю получать пользователей э"
                    "того чата/группы/канала. Користувач, который вызвал "
                    f"команду: {username}")
    db_usernames = await st.db.fetch_all("SELECT username FROM users")
    if not any(ctx.args):
        st.logger.debug("В вызванной команде нету аргументов. Отправляю "
                        f"сообщение об ошибке. Користувач: {username}")
        await ctx.bot.send_message(chat.id, lang.empty_text)
    elif len(ctx.args) >= 2:  # Проверка на лишние аргументы
        st.logger.debug("В вызванной команде два или больше аргументов. "
                        "Отправляю сообщение об ошибке. Користувач: "
                        f"{username}")
        await ctx.bot.send_message(chat.id, lang.more_args_text)
    else:
        target = ctx.args[0].replace("@", "")
        if target == ctx.bot.username:
            st.logger.debug("В вызванной команде аргументом является сам бот. "
                            "Пишу сообщение. Користувач, который вызвал "
                            f"команду: {username}")
            await ctx.bot.send_message(chat.id, "♂That turns me on♂")
            await ctx.bot.send_sticker(chat.id, "CAACAgIAAxkBAAIDmWPLpB7o_dbLh"
                                                "aC2mTmJzUMgrTmjAAIPEQACiMXRSy"
                                                "79YsevxWPOLQQ")
        elif target == username:
            st.logger.debug("В вызванной команде аргументом является сам "
                            "користувач. Пишу сообщение. Користувач: "
                            f"{username}")
            if update.message.text.startswith("/warm"):
                await ctx.bot.send_message(chat.id, message + lang.self2_text)
            else:
                await ctx.bot.send_message(chat.id, message + lang.self1_text)
            await ctx.bot.send_sticker(chat.id, sticker)
        else:
            db_target = target,
            target_dict = {"target": target}
            if db_target in db_usernames:
                st.logger.debug("В вызванной команде введено все правильно. "
                                "Отправляю сообщение. Користувач: "
                                f"{username}")
                query = "SELECT id FROM users WHERE username=:target"
                user_id = await st.db.fetch_one(query, target_dict)
                user_id = user_id[0]
                member = await chat.get_member(user_id)
                await ctx.bot.send_message(chat.id, message + " "
                                           + member.user.first_name)
                await ctx.bot.send_sticker(chat.id, sticker)
            else:
                st.logger.debug("В вызванной команде несуществующий "
                                "користувач. Отправляю сообщение об ошибке. "
                                f"Несуществующий користувач: {ctx.args[0]}. "
                                "Користувач, который вызвал команду: "
                                f"{username}")
                await ctx.bot.send_message(chat.id, lang.error_args_text)
    await st.db.disconnect()


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    user = update.effective_user
    nickname = await check_username(user)
    st.logger.debug("Вызвана команда /start. Проверяю команду. Користувач: "
                    f"{nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    if chat.type == "private":
        st.logger.debug("Команда вызвана в личных сообщениях. Отправляю "
                        "сообщение")
        await ctx.bot.send_message(chat.id, lang.start_text)
    else:
        st.logger.debug("Команда вызвана не в личных сообщениях. Пропускаю")


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    user = update.effective_user
    nickname = await check_username(user)
    st.logger.debug("Вызвана команда /help. Отправляю список команд. "
                    f"Користувач: {nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    if chat.type == "private":
        await ctx.bot.send_message(chat.id, lang.no_here_text)
    else:
        await ctx.bot.send_message(chat.id, lang.get_cmds_text())


async def profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    if chat.type == "private":
        await ctx.bot.send_message(chat.id, lang.no_cmd_access_text)
    else:
        await st.db.connect()
        user = update.effective_user
        username = await check_username(user)
        st.logger.debug("Вызвана команда /profile. Отправляю данные об "
                        f"пользователе. Користувач: {username}")
        sql_id_dict = {"id": user.id}
        users = await st.db.fetch_all("SELECT username FROM users")
        db_name = username,
        if not any(ctx.args):
            st.logger.debug("В вызванной команде нету аргументов. Отправляю "
                            f"сообщение об ошибке. Користувач: {username}")
            await ctx.bot.send_message(chat.id, lang.empty_text)
        elif len(ctx.args) >= 2:  # Проверка на лишние аргументы
            st.logger.debug("В вызванной команде два или больше аргументов. "
                            "Отправляю сообщение об ошибке. Користувач: "
                            f"{username}")
            await ctx.bot.send_message(chat.id, lang.more_args_text)
        else:
            target = ctx.args[0].replace("@", "")
            if db_name in users:
                query = "SELECT exp FROM levels WHERE id=:id"
                exp = await st.db.fetch_one(query, sql_id_dict)
                exp = exp[0]
                lvl = exp / 5
                db_target = target,
                if db_target not in users:
                    st.logger.debug("В вызванной команде несуществующий "
                                    "пользователь. Отправляю сообщение об "
                                    "ошибке. Несуществующий користувач: "
                                    f"{ctx.args[0]}. Користувач, который "
                                    f"вызвал команду: {username}")
                    await ctx.bot.send_message(chat.id, lang.error_args_text)
                else:
                    st.logger.debug("В вызванной команде введено все "
                                    "правильно. Отправляю сообщение. "
                                    "Користувач: {username}")
                    sql_target = {"target": target}
                    query = "SELECT id FROM users WHERE username=:target"
                    db_id = await st.db.fetch_one(query, sql_target)
                    db_id = db_id[0]
                    member = await chat.get_member(db_id)
                    if lvl < 5:
                        text = (f"Профиль {member.user.first_name}'а\n"
                                f"Количество написаних сообщений: {exp}\n"
                                f"Уровень: {lvl}\n"
                                f"Осталось до следующие уровня: {25 - exp}")
                    elif 5 <= lvl < 10:
                        text = (f"Профиль {member.user.first_name}'а\n"
                                f"Количество написаних сообщений: {exp}\n"
                                f"Уровень: {lvl}\n"
                                f"Осталось до следующие уровня: {50 - exp}")
                    elif 10 <= lvl < 20:
                        text = (f"Профиль {member.user.first_name}'а\n"
                                f"Количество написаних сообщений: {exp}\n"
                                f"Уровень: {lvl}\n"
                                f"Осталось до следующие уровня: {100 - exp}")
                    elif 20 <= lvl < 35:
                        text = (f"Профиль {member.user.first_name}'а\n"
                                f"Количество написаних сообщений: {exp}\n"
                                f"Уровень: {lvl}\n"
                                f"Осталось до следующие уровня: {175 - exp}")
                    elif 35 <= lvl < 50:
                        text = (f"Профиль {member.user.first_name}'а\n"
                                f"Количество написаних сообщений: {exp}\n"
                                f"Уровень: {lvl}\n"
                                f"Осталось до следующие уровня: {250 - exp}")
                    elif 50 <= lvl < 100:
                        text = (f"Профиль {member.user.first_name}'а\n"
                                f"Количество написаних сообщений: {exp}\n"
                                f"Уровень: {lvl}\n"
                                f"Осталось до следующие уровня: {500 - exp}")
                    else:
                        text = (f"Профиль {member.user.first_name}'а\n"
                                f"Количество написаних сообщений: {exp}\n"
                                f"Уровень: {lvl}\n"
                                f"У тебя максимальный уровень")
                    await ctx.bot.send_message(chat.id, text)
        await st.db.disconnect()


async def fisting(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    chat = update.effective_chat
    st.logger.debug("Вызвана команда /fisting. Проверяю команду. Користувач:"
                    f" {nickname}")
    lang = await check_language(update, ctx, user)
    if chat.type == "private":
        await ctx.bot.send_message(chat.id, lang.no_cmd_access_text)
    else:
        message = lang.fisting_text
        sticker = ("CAACAgIAAxkBAAPNY8VZ8vZJwhn2GlF4AV-wlAJUXLYAAswUAAIK18lLGu"
                   "xoKB7NTf8tBA")
        await template(update, ctx, message, sticker)


async def deep(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    chat = update.effective_chat
    st.logger.debug("Вызвана команда /deep. Проверяю команду. Користувач: "
                    f"{nickname}")
    lang = await check_language(update, ctx, user)
    if chat.type == "private":
        await ctx.bot.send_message(chat.id, lang.no_cmd_access_text)
    else:
        message = lang.deep_text
        sticker = ("CAACAgIAAxkBAAPcY8V976B2uJgTgKsYU4aU_UdEmXQAAq0SAAJCrclLV-"
                   "Gg6SoCxPktBA")
        await template(update, ctx, message, sticker)


async def warm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    chat = update.effective_chat
    st.logger.debug("Вызвана команда /warm. Проверяю команду. Користувач: "
                    f"{nickname}")
    lang = await check_language(update, ctx, user)
    if chat.type == "private":
        await ctx.bot.send_message(chat.id, lang.no_cmd_access_text)
    else:
        message = lang.warm_text
        sticker = ("CAACAgIAAxkBAAPnY8V-KUYPoww3mzj53kFxwU43PMMAArsSAAJHIshLmX"
                   "zom_gcydQtBA")
        await template(update, ctx, message, sticker)


async def lvl_state(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await message_sys(update, ctx)
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    if chat.type == "private":
        await ctx.bot.send_message(chat.id, lang.no_cmd_access_text)
    else:
        await st.db.connect()
        user = update.effective_user
        nickname = await check_username(user)
        st.logger.debug("Вызвана команда /lvl. Проверяю команду. Користувач, "
                        f"который вызвал команду: {nickname}")
        if not any(ctx.args):
            st.logger.debug("Аргументов не существует. Отправляю сообщение об "
                            f"отсутствие аргументов. Користувач: {nickname}")
            await ctx.bot.send_message(chat.id, lang.empty_text)
        else:
            st.logger.debug("Аргументы существуют. Проверяю правильность "
                            f"аргументов. Користувач: {nickname}")
            users = await st.db.fetch_all("SELECT username FROM users")
            target = ctx.args[0].replace("@", "")
            db_target = (target,)
            if db_target not in users:
                st.logger.debug("Користувач в аргументе не существует. "
                                "Отправляю сообщение об несуществующем "
                                "пользователе. Несуществующий користувач: "
                                f"{target}. Користувач, который вызвал команду"
                                f": {nickname}")
                await ctx.bot.send_message(chat.id, lang.no_db_user_text)
            else:
                st.logger.debug("Користувач в аргументе существует. Отправляю "
                                "уровень этого пользователя. Користувач: "
                                f"{nickname}")
                sql_target = {"target": target}
                query = "SELECT id FROM users WHERE username=:target"
                user_id = await st.db.fetch_one(query, sql_target)
                user_id = user_id[0]
                member = await chat.get_member(user_id)
                sql_id_dict = {"id": user.id}
                query = "SELECT exp FROM levels WHERE id=:id"
                exp = await st.db.fetch_one(query, sql_id_dict)
                exp = exp[0]
                lvl = round(exp / 5)
                lang = await check_language(update, ctx, member=member,
                                            lvl=lvl)
                await ctx.bot.send_message(chat.id, lang.lvl_cmd_text)
        await st.db.disconnect()


# Пишет заданий текст в чат
async def repeat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    st.logger.debug("Вызвана команда /repeat. Проверяю команду. Користувач: "
                    f"{nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    roli_id = 865151826
    polya_id = 853872563
    if user.id == roli_id or user.id == polya_id:
        if user.id == roli_id:
            st.logger.info("Хеллоу, роли. Отправляю текст")
        else:
            st.logger.info("Хеллоу, Поля. Отправляю текст")
        await update.message.delete()
        text = " ".join(ctx.args)
        await ctx.bot.send_message(chat.id, text)
    else:
        st.logger.debug("У пользователя нет доступа к команде /repeat. "
                        "Отправляю сообщение, что у пользователя нет доступа к"
                        f" команде. Користувач: {nickname}")
        await ctx.bot.send_message(chat.id, lang.no_access_text)


# Проверка на наличие меню с командами
async def check_cmds(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    st.logger.debug("Вызвана команда /hascmds. Проверяю команду. Користувач:"
                    f" {nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    roli_id = 865151826
    if user.id == roli_id:
        st.logger.info("Хеллоу, роли. Проверяю меню с командами")
        cmds = await ctx.bot.get_my_commands()
        if not any(cmds):
            st.logger.debug("Меню с командами не существует. Создаю новое меню"
                            " с командами")
            await ctx.bot.send_message(chat.id, lang.check_cmd_text)
            await ctx.bot.set_my_commands(
                [
                    ["help", lang.for_check_menu_text[0]]
                ]
            )
            await ctx.bot.set_my_commands(
                [
                    ["help", lang.for_check_menu_text[0]],
                    ["profile", lang.for_check_menu_text[1]],
                    ["lvl", lang.for_check_menu_text[2]],
                    ["fisting", lang.for_check_menu_text[3]],
                    ["deep", lang.for_check_menu_text[4]],
                    ["warm", lang.for_check_menu_text[5]]
                ],
                scope=BotCommandScopeAllGroupChats()
            )
        else:
            st.logger.debug("Меню с командами существует. Пишу сообщение, что "
                            "все в норме")
            await ctx.bot.send_message(chat.id, lang.ok_text)
    else:
        st.logger.debug("У пользователя нет доступа к команде /hascmds. "
                        "Отправляю сообщение, что у пользователя нет доступа к"
                        f" команде. Користувач: {nickname}")
        await ctx.bot.send_message(chat.id, lang.no_access_text)


# Сброс датабаз
async def db_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    username = await check_username(user)
    lang = await check_language(update, ctx)
    st.logger.info(f"Попытка сбросить таблицы. Користувач: {username}")
    if not any(ctx.args):
        st.logger.debug("Таблица не введена. Отправляю сообщение. "
                        f"Користувач: {username}")
        await ctx.bot.send_message(chat.id, lang.no_arg_table_text)
    else:
        if user.id == 865151826:
            try:
                if ctx.args[0] == "users":
                    st.logger.warning("Сбрасываю таблицу users")
                    await st.db.execute("DROP TABLE users")
                elif ctx.args[0] == "levels":
                    st.logger.warning("Сбрасываю таблицу levels")
                    await st.db.execute("DROP TABLE levels")
            except IndexError:
                pass
            st.create_tables()
            await ctx.bot.send_message(chat.id, lang.done_text)
            st.logger.info("Хеллоу, роли. Таблицы сброшены")
        else:
            st.logger.debug("Не удалось, нету доступа. Користувач: "
                            f"{username}")
            await ctx.bot.send_message(chat.id, lang.no_access_text)


# Тест команда
async def test(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    st.logger.debug("Вызвана /test команда. Ничего интересного...zzz")
    user = update.effective_user
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    if user.id == 865151826:
        await ctx.bot.send_message(update.effective_chat.id, update.message)
    else:
        await ctx.bot.send_message(chat.id, lang.no_access_text)


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
    __app = ApplicationBuilder().token(config.billy_test.token).build()
    __start_cmd_handler = CommandHandler("start", start)
    __help_cmd_handler = CommandHandler("help", help_cmd)
    __profile_cmd_handler = CommandHandler("profile", profile)
    __fisting_cmd_handler = CommandHandler("fisting", fisting)
    __deep_cmd_handler = CommandHandler("deep", deep)
    __warm_cmd_handler = CommandHandler("warm", warm)
    __lvl_cmd_handler = CommandHandler("lvl", lvl_state)
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
        except OperationalError:
            self.__logger.info(f"Создание. Таблиц в {self.__filename}.db не "
                               "существует")
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
        else:
            self.__logger.debug(f"Игнорирование. Таблицы в {self.__filename} "
                                "уже существуют")
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
                self.__fisting_cmd_handler,
                self.__deep_cmd_handler,
                self.__warm_cmd_handler,
                self.__lvl_cmd_handler
            ]
        )

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
        self.__add_public_handlers()
        self.__add_private_handlers()
        self.__add_message_handlers()
        print("Готов к работе!")
        self.__app.run_polling()


if __name__ == "__main__":
    st = Start()
    st.start()
