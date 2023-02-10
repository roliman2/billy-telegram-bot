from telegram import User, Update
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

if path.exists("billy_data"):
    if platform == "linux":
        filename = "billy_data/billy_telegram"
    elif platform == ("win32" or "darwin"):
        filename = "billy_data\\billy_telegram"
    else:
        filename = "billy_data/billy_telegram"
else:
    makedirs("billy_data")
    if platform == "linux":
        filename = "billy_data/billy_telegram"
    elif platform == ("win32" or "darwin"):
        filename = "billy_data\\billy_telegram"
    else:
        filename = "billy_data/billy_telegram"

logger = getLogger("billy_telegram")
logger.setLevel(DEBUG)

console = StreamHandler()
console.setLevel(INFO)

file = FileHandler(filename + ".log", "w", "utf-8")
file.setLevel(DEBUG)

file2 = FileHandler("billy_data/important.log", "w", "utf-8")
file2.setLevel(WARNING)

formatter = Formatter("%(asctime)s | %(funcName)s (%(levelname)s): "
                      "%(message)s", "%d.%m.%y %H:%M:%S")

console.setFormatter(formatter)
file.setFormatter(formatter)
file2.setFormatter(formatter)

logger.addHandler(console)
logger.addHandler(file)
logger.addHandler(file2)

db = Database(f"sqlite+aiosqlite:///{filename}.sqlite")


# Создание таблиц (если их нет)
def create_tables():
    con = connect(filename + ".sqlite")
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM users")
        cur.execute("SELECT * FROM levels")
    except OperationalError:
        logger.info(f"Создание. Таблиц в {filename}.sqlite не существует")
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
                        username TEXT,
                        id INTEGER,
                        exp INTEGER
                    )
                    """)
    else:
        logger.debug(f"Игнорирование. Таблицы в {filename} уже существуют")
    finally:
        con.close()


# Проверка на наличие никнейма у пользователя
async def check_username(user: User) -> str:
    logger.debug(f"Начало проверки никнейма. Пользователь: {user}")
    if user.username is None:
        logger.debug("Никнейма не существует. Ставлю имя. Пользователь: "
                     f"{user}")
        username = user.first_name
    else:
        logger.debug("Никнейм существует. Ставлю никнейм. Никнейм: "
                     f"{user.username}. Пользователь: {user}")
        username = user.username
    return username


# Проверка языка у пользователя
async def check_language(
        update: Update,
        ctx: ContextTypes.DEFAULT_TYPE,
        user=None,
        member=None,
        lvl=None
) -> Ukraine or Russian:
    user_ok = update.effective_user
    if user_ok.language_code == "uk":
        return Ukraine(user, member, lvl)
    else:
        return Russian(user, member, lvl)


# Проверка на наличие и берет уже существующий опыт
async def check_exp(user: User) -> int:
    await db.connect()
    name = await check_username(user)
    logger.debug(f"Получаю уровень. Пользователь: {name}")
    db_name = (name,)
    data = {"name": name, "user_id": user.id}
    db_users = await db.fetch_all("SELECT username FROM levels")
    if not any(db_users):
        logger.info(f"Создание. В датабазе {filename}.sqlite, в таблице levels"
                    " нет ни одного пользователя")
        await db.execute("INSERT INTO levels (username, id, exp) VALUES "
                         "(?, ?, 1)", data)
        exp = 1
        return exp
    elif db_name in db_users:
        logger.debug("Данные найдены. Начинаю получать опыт. Пользователь: "
                     f"{name}")
        data = {"name": name}
        query = "SELECT exp FROM levels WHERE username=:name"
        exp = await db.fetch_one(query, data)
        return exp[0]
    else:
        logger.info(f"Данные не найдены. Создаю и добавляю данные в датабазу "
                    f"{filename}.sqlite, в таблицу levels. Пользователь: "
                    f"{name}")
        await db.execute("INSERT INTO levels (username, id, exp) VALUES "
                         "(:name, :user_id, 1)", data)
        exp = 1
        return exp


# Система уровней
async def lvl_system(user: User) -> float:
    name = await check_username(user)
    logger.debug(f"Начинаю проверку уровня. Пользователь: {name}")
    exp = await check_exp(user)
    data = {"exp": exp, "name": name}
    logger.debug(f"Добавляю +1 к {exp}. Пользователь: {name}")
    await db.execute("UPDATE levels SET exp=:exp+1 WHERE username=:name", data)
    logger.debug(f"Начинаю повторную проверку уровня. Пользователь: {name}")
    exp = await check_exp(user)
    lvl = exp / 5
    return lvl


# Если команды не существует
async def command_error(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    username = await check_username(user)
    lang = await check_language(update, ctx)
    logger.debug(f"Пользователь {username} ввел неизвестную команду. Отправляю"
                 " сообщение об ошибке")
    await ctx.bot.send_message(chat.id, lang.idk_command_text)


# Проверка на "круглой цифры" в уровне
async def level(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await db.connect()
    if update.effective_user != ctx.bot:
        user = update.effective_user
        chat = update.effective_chat
        username = await check_username(user)
        lang = await check_language(update, ctx)
        logger.debug("Новое сообщение. Начинаю проверку уровня. Пользователя: "
                     f"{username}")
        db_users = await db.fetch_all("SELECT username FROM users")
        db_name = (username,)
        data = {"username": username, "user_id": user.id}
        if not any(db_users):
            logger.info(f"В датабазе {filename}.sqlite, в таблице users пусто."
                        f" Начинаю добавлять данные. Данные: {data}")
            await db.execute("INSERT INTO users (username, id) VALUES "
                             "(:username, :user_id)", data)
        elif db_name in db_users:
            logger.debug(f"В датабазе {filename}.sqlite, в таблице users "
                         f"пользователь {username} найден. Беру опыт")
        else:
            logger.info(f"В датабазе {filename}.sqlite, в таблице users "
                        f"пользователя {username} нет. Начинаю добавлять "
                        f"данные. Данные: {data}")
            await db.execute("INSERT INTO users (username, id) VALUES "
                             "(:username, :user_id)", data)
        if ctx.bot.id != update.effective_user.id:
            if not update.effective_user.is_bot:
                lvl = await lvl_system(user)
                if lvl == 5:
                    logger.debug(f"У пользователя {username} {lvl} "
                                 "уровень")
                    await ctx.bot.send_message(chat.id, lang.lvl_text)
                elif lvl == 10:
                    logger.debug(f"У пользователя {username} {lvl} "
                                 "уровень")
                    await ctx.bot.send_message(chat.id, lang.lvl_text)
                elif lvl == 20:
                    logger.debug(f"У пользователя {username} {lvl} "
                                 "уровень")
                    await ctx.bot.send_message(chat.id, lang.lvl_text)
                elif lvl == 35:
                    logger.debug(f"У пользователя {username} {lvl} "
                                 "уровень")
                    await ctx.bot.send_message(chat.id, lang.lvl_text)
                elif lvl == 50:
                    logger.debug(f"У пользователя {username} {lvl} "
                                 "уровень")
                    await ctx.bot.send_message(chat.id, lang.lvl_text)
                elif lvl == 100:
                    logger.debug(f"У пользователя {username} {lvl} "
                                 "уровень")
                    await ctx.bot.send_message(chat.id, lang.lvl_text)
    await db.disconnect()


# Шаблон для команд
async def template(
        update: Update,
        ctx: ContextTypes.DEFAULT_TYPE,
        message=None,
        sticker=None
):
    user = update.effective_user
    chat = update.effective_chat
    username = await check_username(user)
    lang = await check_language(update, ctx)
    logger.debug("Вызван шаблон команд. Начинаю получать пользователей этого "
                 "чата/группы/канала. Пользователь, который вызвал команду: "
                 f"{username}")
    users = await db.fetch_all("SELECT username FROM users")
    if not any(ctx.args):
        logger.debug("В вызванной команде нету аргументов. Отправляю сообщение"
                     f" об ошибке. Пользователь: {username}")
        await ctx.bot.send_message(chat.id, lang.empty_text)
    elif len(ctx.args) >= 2:  # Проверка на лишние аргументы
        logger.debug("В вызванной команде два или больше аргументов. Отправляю"
                     f" сообщение об ошибке. Пользователь: {username}")
        await ctx.bot.send_message(chat.id, lang.more_args_text)
    else:
        target = ctx.args[0].replace("@", "")
        if target == ctx.bot.username:
            logger.debug("В вызванной команде аргументом является сам бот. "
                         "Пишу сообщение. Пользователь, который вызвал "
                         f"команду: {username}")
            await ctx.bot.send_message(chat.id, "♂That turns me on♂")
            await ctx.bot.send_sticker(chat.id, "CAACAgIAAxkBAAIDmWPLpB7o_dbLh"
                                                "aC2mTmJzUMgrTmjAAIPEQACiMXRSy"
                                                "79YsevxWPOLQQ")
        elif target == username:
            logger.debug("В вызванной команде аргументом является сам "
                         "пользователь. Пишу сообщение. Пользователь: "
                         f"{username}")
            if update.message.text.startswith("/warm"):
                await ctx.bot.send_message(chat.id, message
                                           + Russian.self2_text)
            else:
                await ctx.bot.send_message(chat.id, message
                                           + Russian.self1_text)
            await ctx.bot.send_sticker(chat.id, sticker)
        else:
            db_target = target,
            sql_target = {"target": target}
            if db_target in users:
                logger.debug("В вызванной команде введено все правильно. "
                             f"Отправляю сообщение. Пользователь: {username}")
                query = "SELECT id FROM users WHERE username=:target"
                db_id = await db.fetch_one(query, sql_target)
                db_id = db_id[0]
                member = await chat.get_member(db_id)
                await ctx.bot.send_message(chat.id, message + " "
                                           + member.user.first_name)
                await ctx.bot.send_sticker(chat.id, sticker)
            else:
                logger.debug("В вызванной команде несуществующий пользователь."
                             " Отправляю сообщение об ошибке. Несуществующий "
                             f"пользователь: {ctx.args[0]}. Пользователь, "
                             f"который вызвал команду: {username}")
                await ctx.bot.send_message(chat.id, lang.error_args_text)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    logger.debug("Вызвана команда /start. Проверяю команду. Пользователь: "
                 f"{nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    if chat.type == "private":
        logger.debug("Команда вызвана в личных сообщениях. Отправляю "
                     "сообщение")
        await ctx.bot.send_message(chat.id, lang.start_text)
    else:
        logger.debug("Команда вызвана не в личных сообщениях. Пропускаю")


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    logger.debug("Вызвана команда /help. Отправляю список команд. "
                 f"Пользователь: {nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    await ctx.bot.send_message(chat.id, lang.get_cmds_text())


async def profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = await check_username(user)
    logger.debug("Вызвана команда /profile. Отправляю данные об пользователе. "
                 f"Пользователь: {username}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    users = await db.fetch_all("SELECT username FROM users")
    db_name = username,
    if not any(ctx.args):
        logger.debug("В вызванной команде нету аргументов. Отправляю сообщение"
                     f" об ошибке. Пользователь: {username}")
        await ctx.bot.send_message(chat.id, lang.empty_text)
    elif len(ctx.args) >= 2:  # Проверка на лишние аргументы
        logger.debug("В вызванной команде два или больше аргументов. Отправляю"
                     f" сообщение об ошибке. Пользователь: {username}")
        await ctx.bot.send_message(chat.id, lang.more_args_text)
    else:
        target = ctx.args[0].replace("@", "")
        sql_username = {"username": username}
        if db_name in users:
            query = "SELECT exp FROM levels WHERE username=:username"
            exp = await db.fetch_one(query, sql_username)
            exp = exp[0]
            lvl = exp / 5
            db_target = (target,)
            if db_target not in users:
                logger.debug("В вызванной команде несуществующий пользователь."
                             " Отправляю сообщение об ошибке. Несуществующий "
                             f"пользователь: {ctx.args[0]}. Пользователь, "
                             f"который вызвал команду: {username}")
                await ctx.bot.send_message(chat.id, lang.error_args_text)
            else:
                logger.debug("В вызванной команде введено все правильно. "
                             f"Отправляю сообщение. Пользователь: {username}")
                sql_target = {"target": target}
                query = "SELECT id FROM users WHERE username=:target"
                db_id = await db.fetch_one(query, sql_target)
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


async def fisting(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    logger.debug("Вызвана команда /fisting. Проверяю команду. Пользователь:"
                 f" {nickname}")
    lang = await check_language(update, ctx, user,
                                lvl=await check_exp(user) / 5)
    message = lang.fisting_text
    sticker = ("CAACAgIAAxkBAAPNY8VZ8vZJwhn2GlF4AV-wlAJUXLYAAswUAAIK18lLGuxoKB"
               "7NTf8tBA")
    await template(update, ctx, message, sticker)


async def deep(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    logger.debug("Вызвана команда /deep. Проверяю команду. Пользователь: "
                 f"{nickname}")
    lang = await check_language(update, ctx, user,
                                lvl=await check_exp(user) / 5)
    message = lang.deep_text
    sticker = ("CAACAgIAAxkBAAPcY8V976B2uJgTgKsYU4aU_UdEmXQAAq0SAAJCrclLV-Gg6S"
               "oCxPktBA")
    await template(update, ctx, message, sticker)


async def warm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    logger.debug("Вызвана команда /warm. Проверяю команду. Пользователь: "
                 f"{nickname}")
    lang = await check_language(update, ctx, user,
                                lvl=await check_exp(user) / 5)
    message = lang.warm_text
    sticker = ("CAACAgIAAxkBAAPnY8V-KUYPoww3mzj53kFxwU43PMMAArsSAAJHIshLmXzom_"
               "gcydQtBA")
    await template(update, ctx, message, sticker)


async def lvl_state(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    logger.debug("Вызвана команда /lvl. Проверяю команду. Пользователь, "
                 f"который вызвал команду: {nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    if not any(ctx.args):
        logger.debug("Аргументов не существует. Отправляю сообщение об "
                     f"отсутствие аргументов. Пользователь: {nickname}")
        await ctx.bot.send_message(chat.id, lang.empty_text)
    else:
        logger.debug("Аргументы существуют. Проверяю правильность аргументов. "
                     f"Пользователь: {nickname}")
        users = await db.fetch_all("SELECT username FROM users")
        target = ctx.args[0].replace("@", "")
        db_target = (target,)
        if db_target not in users:
            logger.debug("Пользователь в аргументе не существует. Отправляю "
                         "сообщение об несуществующем пользователе. "
                         f"Несуществующий пользователь: {target}. "
                         f"Пользователь, который вызвал команду: {nickname}")
            await ctx.bot.send_message(chat.id, lang.no_db_user_text)
        else:
            logger.debug("Пользователь в аргументе существует. Отправляю "
                         "уровень этого пользователя. Пользователь: "
                         f"{nickname}")
            sql_target = {"target": target}
            query = "SELECT id FROM users WHERE username=:target"
            db_id = await db.fetch_one(query, sql_target)
            db_id = db_id[0]
            member = await chat.get_member(db_id)
            query = "SELECT exp FROM levels WHERE username=:target"
            exp = await db.fetch_one(query, sql_target)
            exp = exp[0]
            lvl = exp / 5
            lang = await check_language(update, ctx, member=member, lvl=lvl)
            await ctx.bot.send_message(chat.id, lang.lvl_cmd_text)


# Пишет заданий текст в чат
async def repeat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    logger.debug("Вызвана команда /repeat. Проверяю команду. Пользователь: "
                 f"{nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    roli_id = 865151826
    polya_id = 853872563
    if user.id == roli_id or user.id == polya_id:
        if user.id == roli_id:
            logger.info("Хеллоу, роли. Отправляю текст")
        else:
            logger.info("Хеллоу, Поля. Отправляю текст")
        await update.message.delete()
        text = " ".join(ctx.args)
        await ctx.bot.send_message(chat.id, text)
    else:
        logger.debug("У пользователя нет доступа к команде /repeat. Отправляю "
                     "сообщение, что у пользователя нет доступа к команде. "
                     f"Пользователь: {nickname}")
        await ctx.bot.send_message(chat.id, lang.no_access_text)


# Проверка на наличие меню с командами
async def check_cmds(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    nickname = await check_username(user)
    logger.debug("Вызвана команда /hascmds. Проверяю команду. Пользователь: "
                 f"{nickname}")
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    roli_id = 865151826
    if user.id == roli_id:
        logger.info("Хеллоу, роли. Проверяю меню с командами")
        cmds = await ctx.bot.get_my_commands()
        if not any(cmds):
            logger.debug("Меню с командами не существует. Создаю новое меню с "
                         "командами")
            await ctx.bot.set_my_commands(
                [
                    ["help", lang.for_check_menu_text[0]],
                    ["fisting", lang.for_check_menu_text[1]],
                    ["deep", lang.for_check_menu_text[2]],
                    ["warm", lang.for_check_menu_text[3]],
                    ["lvl", lang.for_check_menu_text[4]]
                ]
            )
            await ctx.bot.send_message(chat.id, lang.check_cmd_text)
        else:
            logger.debug("Меню с командами существует. Пишу сообщение, что все"
                         " в норме")
            await ctx.bot.send_message(chat.id, lang.ok_text)
    else:
        logger.debug("У пользователя нет доступа к команде /hascmds. Отправляю"
                     " сообщение, что у пользователя нет доступа к команде. "
                     f"Пользователь: {nickname}")
        await ctx.bot.send_message(chat.id, lang.no_access_text)


# Сброс датабаз
async def db_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    username = await check_username(user)
    lang = await check_language(update, ctx)
    logger.info(f"Попытка сбросить таблицы. Пользователь: {username}")
    if not any(ctx.args):
        logger.debug("Таблица не введена. Отправляю сообщение. Пользователь: "
                     f"{username}")
        await ctx.bot.send_message(chat.id, lang.no_arg_table_text)
    else:
        if user.id == 865151826:
            try:
                if ctx.args[0] == "users":
                    logger.warning("Сбрасываю таблицу users")
                    await db.execute("DROP TABLE users")
                elif ctx.args[0] == "levels":
                    logger.warning("Сбрасываю таблицу levels")
                    await db.execute("DROP TABLE levels")
            except IndexError:
                pass
            create_tables()
            await ctx.bot.send_message(chat.id, lang.done_text)
            logger.info("Хеллоу, роли. Таблицы сброшены")
        else:
            logger.debug("Не удалось, нету доступа. Пользователь: "
                         f"{username}")
            await ctx.bot.send_message(chat.id, lang.no_access_text)


# Тест команда
async def test(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    logger.debug("Вызвана /test команда. Ничего интересного...zzz")
    user = update.effective_user
    chat = update.effective_chat
    lang = await check_language(update, ctx)
    if user.id == 865151826:
        await ctx.bot.send_message(update.effective_chat.id, update.message)
    else:
        await ctx.bot.send_message(chat.id, lang.no_access_text)


# Класс для более удобного и простого запуска
class Main:

    def __init__(self):
        logger.debug("Создаю Application")
        self.__app = ApplicationBuilder().token(config.billy.token).build()
        logger.debug("Создаю обработчики")
        self.__start_cmd_handler = CommandHandler("start", start)
        self.__help_cmd_handler = CommandHandler("help", help_cmd)
        self.__profile_cmd_handler = CommandHandler("profile", profile)
        self.__fisting_cmd_handler = CommandHandler("fisting", fisting)
        self.__deep_cmd_handler = CommandHandler("deep", deep)
        self.__warm_cmd_handler = CommandHandler("warm", warm)
        self.__lvl_cmd_handler = CommandHandler("lvl", lvl_state)
        self.__temp_cmd_handler = CommandHandler("repeat", repeat)
        self.__check_cmds_cmd_handler = CommandHandler("hascmds", check_cmds)
        self.__db_reset_cmd_handler = CommandHandler("db_reset", db_reset)
        self.__test_cmd_handler = CommandHandler("test", test)
        self.__level_handler = MessageHandler(filters.ALL, level)
        self.__cmd_err_handler = MessageHandler(filters.COMMAND, command_error)

    def add_public_handlers(self):
        logger.debug("Добавляю публичные обработчики")
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

    def add_private_handlers(self):
        logger.debug("Добавляю приватные обработчики")
        self.__app.add_handlers(
            [
                self.__temp_cmd_handler,
                self.__check_cmds_cmd_handler,
                self.__db_reset_cmd_handler,
                self.__test_cmd_handler
            ]
        )

    def add_message_handlers(self):
        logger.debug("Добавляю обработчики сообщений")
        self.__app.add_handlers(
            [
                self.__level_handler,
                self.__cmd_err_handler
            ]
        )

    def start(self):
        logger.debug("Запускаю")
        print("Готов к работе!")
        self.__app.run_polling()


if __name__ == "__main__":
    m = Main()
    logger.debug("Проверяю таблицы")
    create_tables()
    m.add_public_handlers()
    m.add_private_handlers()
    m.add_message_handlers()
    m.start()
