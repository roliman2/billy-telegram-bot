import telegram
from telegram import ext as tg_ext
import logging
import sqlite3

logging.basicConfig(filename="\\billy_data\\billy_telegram.log", filemode="w", encoding="utf-8",
                    level=logging.DEBUG, format="%(asctime)s | %(funcName)s: "
                                                "%(levelname)s: %(message)s",
                    datefmt="%d.%m.%Y %H:%M:%S")

con = sqlite3.connect("\\billy_data\\billy_telegram.sqlite")
cur = con.cursor()


def create_tables():
    # Проверка на существование таблиц путем блока try-except
    try:
        cur.execute("SELECT * FROM users")  # если ошибка = нету таблиц
    except sqlite3.OperationalError:
        logging.info("создание, таблиц нету в database: users")
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        db_id INTEGER PRIMARY KEY,
                        chat_id INTEGER,
                        username TEXT,
                        id INTEGER
                    )
                    """)
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS levels (
                        lvlid INTEGER PRIMARY KEY,
                        name TEXT,
                        exp INTEGER
                    )
                    """)
    else:
        logging.info("игнорирование, таблицы уже существуют")


async def check_username(source):
    logging.info(f"Начало проверки никнейма пользователя {source}")
    # if isinstance(source, telegram.User):  # если это будет бот
    #     username = source.first_name
    if source.username is None:
        logging.info("username не существует. Ставлю first_name. Пользователь:"
                     f" {source}")
        username = source.first_name
    else:
        logging.info("username существует. Ставлю username. Username: "
                     f"{source.username}. Пользователь: {source}")
        username = source.username
    return username


# async def exist(guild, user):
#     members = guild.members
#     names = []
#     for i in members:
#         names.append(i.mention)
#     try:
#         if names.index(user):
#             nick = members[names.index(user)]
#             ment = await check_username(nick)
#     except ValueError:
#         logging.info("mention_member: пользователя не существует")
#         ment = "error"
#     return ment


async def check_lvl_param(name):
    logging.info(f"Получаю уровень пользователя {name}")
    db = (str(name),)
    sel_name = cur.execute("SELECT name FROM levels")
    corr_user = sel_name.fetchall()
    if not any(corr_user):
        logging.info("создание, в database: levels нету ни одного пользователя")
        cur.execute("INSERT INTO levels (name, exp) VALUES (?, 1)", db)
        con.commit()
        exp_user = 1
        return exp_user
    # Проверка на присутствие пользователя в списке путем try-except
    try:
        if corr_user.index(db):  # .index, как сигнал о том, что в
            # списке есть или нету этого
            pass
    except ValueError:  # если в списке пользователя нету
        logging.info("Данные не найдены. Создаю и добавляю в database: levels."
                     f" Пользователь: {name}")
        cur.execute("INSERT INTO levels (name, exp) VALUES (?, 1)", db)
        con.commit()
        exp_user = 1
        return exp_user
    else:
        logging.info("Данные найдены. Начинаю получать exp. Пользователь: "
                     f"{name}")
        sel_exp = cur.execute("SELECT exp FROM levels WHERE name=?", db)
        exp_user = sel_exp.fetchone()[0]
        return exp_user


async def lvls_system(user):
    logging.info(f"Начинаю проверку уровня. Пользователь: {user}")
    exp = await check_lvl_param(user)
    check_db = (exp, str(user))
    logging.info(f"Добавляю +1 к {exp}. Пользователь: {user}")
    cur.execute("""
                UPDATE levels SET exp=?+1 WHERE name=?
                """, check_db)
    con.commit()
    logging.info(f"Начинаю повторную проверку уровня. Пользователь: {user}")
    exp = await check_lvl_param(user)
    lvl = exp / 2
    return lvl


async def command_error(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Неизвестная команда")


async def level(update, context):
    user = update.message.from_user
    username = await check_username(user)
    db = (username,)
    data = (username, user.id)
    users = cur.execute("SELECT username FROM users").fetchall()
    if not any(users):
        cur.execute("INSERT INTO users (username, id) VALUES (?, ?)", data)
    # Проверка на присутствие пользователя в списке путем блока try-except
    try:
        if users.index(db):
            pass
    except ValueError:
        cur.execute("INSERT INTO users (username, id) VALUES (?, ?)", data)
    finally:
        if context.bot.id != update.message.from_user.id:
            if not update.message.from_user.is_bot:
                lvl = await lvls_system(username)
                if lvl == 5:
                    logging.info(f"У пользователя {username} {lvl} уровень.")
                    await context.bot.send_message(update.effective_chat.id,
                                                   "Welcome to the club, "
                                                   f"{user.first_name}\nТеперь"
                                                   f" у тебя 5 левел!")
                elif lvl == 10:
                    logging.info(f"У пользователя {username} {lvl} уровень.")
                    await context.bot.send_message(update.effective_chat.id,
                                                   "Welcome to the club, "
                                                   f"{user.first_name}\nТеперь"
                                                   f" у тебя 10 левел!")
                elif lvl == 20:
                    logging.info(f"У пользователя {username} {lvl} уровень.")
                    await context.bot.send_message(update.effective_chat.id,
                                                   "Welcome to the club, "
                                                   f"{user.first_name}\nТеперь"
                                                   f" у тебя 20 левел!")
                elif lvl == 35:
                    logging.info(f"У пользователя {username} {lvl} уровень.")
                    await context.bot.send_message(update.effective_chat.id,
                                                   "Welcome to the club, "
                                                   f"{user.first_name}\nТеперь"
                                                   f" у тебя 35 левел!")
                elif lvl == 50:
                    logging.info(f"У пользователя {username} {lvl} уровень.")
                    await context.bot.send_message(update.effective_chat.id,
                                                   "Welcome to the club, "
                                                   f"{user.first_name}\nТеперь"
                                                   f" у тебя 50 левел!")
                elif lvl == 100:
                    logging.info(f"У пользователя {username} {lvl} уровень.")
                    await context.bot.send_message(update.effective_chat.id,
                                                   "Welcome to the club, "
                                                   f"{user.first_name}\nТеперь"
                                                   f" у тебя 100 левел!")


async def fisting(update, context):
    user = update.message.from_user
    users = cur.execute("SELECT username FROM users").fetchall()
    username = await check_username(user)
    try:
        if not any(context.args):  # если нету аргументов
            await context.bot.send_message(update.effective_chat.id,
                                           "Пользователь не введён. Попробуйте"
                                           " добавить таким образом: /fisting "
                                           "@[пользователь]")
        elif context.args[1]:  # если аргумент один - кидает в блок try-except
            await context.bot.send_message(update.effective_chat.id,
                                           "Слишком много аргументов. Попробуйте у"
                                           "брать лишные")
    except IndexError:
        try:
            db_user = users[users.index((context.args[0].replace("@", ""),))]
        except ValueError:
            await context.bot.send_message(update.effective_chat.id,
                                           "Неправильно введена команда. Попро"
                                           "буйте проверить данные на ошибки")
        else:
            await context.bot.send_message(update.effective_chat.id,
                                           f"{username} делает жесткий фистинг"
                                           f" {db_user[0]}")


async def deep(update, context):
    user = update.message.from_user
    users = cur.execute("SELECT username FROM users").fetchall()
    username = await check_username(user)
    try:
        if not any(context.args):
            await context.bot.send_message(update.effective_chat.id,
                                           "Пользователь не введён. Попробуйте"
                                           " добавить таким образом: /fisting "
                                           "@[пользователь]")
        elif context.args[1]:
            await context.bot.send_message(update.effective_chat.id,
                                           "Слишком много аргументов. Попробуй"
                                           "те убрать лишные")
    except IndexError:
        try:
            db_user = users[users.index((context.args[0].replace("@", ""),))]
        except ValueError:
            await context.bot.send_message(update.effective_chat.id,
                                           "Неправильно введена команда. Попро"
                                           "буйте проверить данные на ошибки")
        else:
            await context.bot.send_message(update.effective_chat.id,
                                           f"{username} проверил глубину "
                                           f"{db_user[0]}")


async def warm(update, context):
    user = update.message.from_user
    users = cur.execute("SELECT username FROM users").fetchall()
    username = await check_username(user)
    try:
        if not any(context.args):
            await context.bot.send_message(update.effective_chat.id,
                                           "Пользователь не введён. Попробуйте"
                                           " добавить таким образом: /fisting "
                                           "@[пользователь]")
        elif context.args[1]:
            await context.bot.send_message(update.effective_chat.id,
                                           "Слишком много аргументов. Попробуй"
                                           "те убрать лишные")
    except IndexError:
        try:
            db_user = users[users.index((context.args[0].replace("@", ""),))]
        except ValueError:
            await context.bot.send_message(update.effective_chat.id,
                                           "Неправильно введена команда. Попро"
                                           "буйте проверить данные на ошибки")
        else:
            await context.bot.send_message(update.effective_chat.id,
                                           f"{username} почувствовал тепло "
                                           f"{db_user[0]}")


async def test(update, context):
    await context.bot.send_message(update.effective_chat.id, "ok")


async def db_reset(update, context):
    logging.info("Попытка сбросить таблицы")
    if update.message.from_user.id == 865151826:
        logging.warning("Сбрасываю таблицы")
        cur.execute("DROP TABLE users")
        cur.execute("DROP TABLE levels")
        create_tables()
        await context.bot.send_message(update.effective_chat.id, "Done")
        logging.info("Таблицы сброшены")
    else:
        logging.info(f"Не удалось, нету доступа. Пользователь: "
                     f"{await check_username(update.message.from_user)}")
        await context.bot.send_message(update.effective_chat.id, "No permission")


if __name__ == "__main__":
    create_tables()
    logging.info("Создаю Application")
    app = tg_ext.ApplicationBuilder().token("5800885688:AAHN3XMozPxBPbbkguDZVI"
                                            "Pqtj4T0c1vowk").build()
    logging.info("Создаю обработчики")
    fisting_cmd_handler = tg_ext.CommandHandler("fisting", fisting)
    deep_cmd_handler = tg_ext.CommandHandler("deep", deep)
    warm_cmd_handler = tg_ext.CommandHandler("warm", warm)
    test_cmd_handler = tg_ext.CommandHandler("test", test)
    dbdrop_cmd_handler = tg_ext.CommandHandler("db_reset", db_reset)
    level_handler = tg_ext.MessageHandler(tg_ext.filters.ALL, level)
    cmd_err_handler = tg_ext.MessageHandler(tg_ext.filters.COMMAND,
                                            command_error)
    logging.info("Добавляю обработчики")
    app.add_handlers([fisting_cmd_handler, deep_cmd_handler, warm_cmd_handler])
    app.add_handlers([test_cmd_handler, dbdrop_cmd_handler])
    app.add_handler(level_handler)
    app.add_handler(cmd_err_handler)
    logging.info("Запускаю")
    app.run_polling()
