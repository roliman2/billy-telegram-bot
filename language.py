from telegram import Update, User, ChatMember


class Russian:
    so_many_args = "Слишком много аргументов. Попробуй убрать лишние"
    idk_cmd_error = "Неизвестная команда. Попробуй написать команду /help"
    self = " сам себе"
    self_alt = " самого себя"
    no_args = "Нет аргументов"
    no_user_in_db = "Нет в датабазе пользователя"
    no_cmd_menu = "Команд не существовало. Создал новое меню с командами"
    ok = "Все в норме"
    no_access = "У тебя нет доступа к команде, slave"
    not_here_cmd = ("Команда в этом чате недоступна. Попробуйте добавить меня "
                    "в группу или канал.")
    no_table_in_args = "Какую таблицу?"
    done = "Готово, boy"
    admin_options_only = "Настройки доступны только для администраторов"
    not_correct_args_error = ("Неправильно введена команда. Попробуй проверить"
                              " данные на ошибки")
    turn_off_cmd = "Данная команда выключена в этом чате"
    switch = "Включить/Выключить:"
    no_args_error = "Пользователь не введён. Попробуй добавить пользователя"
    start = ("Привет, ♂slave♂\n"
             "Видимо, ты здесь новенький, давай сам Billy тебя проведёт в "
             "♂deep dark fantasies♂\n"
             "Напиши /help для списка команд с которыми ты сможешь "
             "использовать силы настоящего ♂full master♂\n"
             "И самое главное, ♂slave♂, что сила в мужской дружбе")
    help = (
        "/help - Показать это сообщение",
        "/profile - Посмотреть статистику ♂slave♂'а",
        "/lvl - Посмотреть уровень ♂slave♂'а",
        "/cards - Получить случайную картку",
        "/fisting - Сделать ♂fisting♂ ♂slave♂'у",
        "/deep - Проверить глубину ♂slave♂'а",
        "/warm - Почувствовать тепло ♂slave♂'а",
        "/options - Настроить бота в группе/канале"
    )
    pm_help = (
        help[0],
        help[3],
        "Для полного списка команд, добавь меня в группу или канал"
    )
    cmds_menu = (
        "Список команд",
        "Посмотреть статистику ♂slave♂'а",
        "Посмотреть уровень ♂slave♂'а",
        "Получить случайную картку",
        "Сделать ♂fisting♂ ♂slave♂'у",
        "Проверить глубину ♂slave♂'а",
        "Почувствовать тепло ♂slave♂'а",
        "Настроить бота в группе/канале"
    )

    def __init__(self, user: User = None, target: User = None,
                 lvl: int | float = None):
        if user:
            self.fisting = f"{user.first_name} делает жесткий ♂fisting♂"
            self.deep = (f"♂It's so fucking deep♂ - сказал {user.first_name} "
                         "boy'ю")
            self.warm = f"{user.first_name} почувствовал тепло"
            if lvl is not None:
                self.lvl = (f"Welcome to the club, {user.first_name}\n"
                            f"Теперь у тебя {lvl} уровень!")
        if target:
            if lvl:
                self.lvl_cmd = f"У {target.first_name} {lvl} уровень"


class Ukraine:
    so_many_args = "Занадто багато аргументів. Спробуй видалити зайві"
    idk_cmd_error = "Невідома команда. Спробуй написати команду /help"
    self = " сам собі"
    self_alt = " самого себе"
    no_args = "Немає аргументів"
    no_user_in_db = "Немає в датабазі користувача"
    no_cmd_menu = "Команд не існувало. Створив нове меню із командами"
    ok = "Все в нормі"
    no_access = "У тебе немає доступу до команди, slave"
    not_here_cmd = ("Команда в цьому чаті недоступна. Спробуйте додати мене в "
                    "групу чи канал.")
    no_table_in_args = "Яку таблицю?"
    done = "Готово, boy"
    admin_options_only = "Налаштування доступні тільки для адміністраторів"
    not_correct_args_error = ("Неправильно введено команду. Спробуй перевірити"
                              " дані на помилки")
    turn_off_cmd = "Данна команда вимкнена в цьому чаті"
    switch = "Ввімкнути/Вимкнути:"
    empty = "Користувач не введений. Спробуй додати користувача"
    start = ("Привіт, ♂slave♂\n"
             "Мабуть, ти тут новенький, давай сам Billy тебе проведе в ♂deep "
             "dark fantasies♂\n"
             "Напиши /help для списку команд з якими ти зможеш використовувати"
             " сили справжнього ♂full master♂\n"
             "І саме головне, ♂slave♂, що сила в чоловічій дружбі")
    help = (
        "/help - Показати це повідомлення",
        "/profile - Подивитися статистику ♂slave♂'а",
        "/lvl - Переглянути рівень ♂slave♂'а",
        "/cards - Отримати випадкову картку",
        "/fisting - Зробити ♂fisting♂ ♂slave♂'у",
        "/deep - Перевірити глибину ♂slave♂'а",
        "/warm - Відчути тепло ♂slave♂'а",
        "/options - Налаштувати бота в групі/каналі"
    )
    pm_help = (
        help[0],
        help[3],
        "Для повного списку команд, добав мене в групу чи канал"
    )
    cmds_menu = (
        "Список команд",
        "Подивитися статистику ♂slave♂'а",
        "Переглянути рівень ♂slave♂'а",
        "Отримати випадкову картку",
        "Зробити ♂fisting♂ ♂slave♂'у",
        "Перевірити глибину ♂slave♂'а",
        "Відчути тепло ♂slave♂'а",
        "Налаштувати бота в групі/каналі"
    )

    def __init__(self, user: User = None, target: User = None,
                 lvl: int | float = None):
        if user:
            self.fisting = f"{user.first_name} робить жорсткий ♂fisting♂"
            self.deep = (f"♂It's so fucking deep♂ - сказав {user.first_name} "
                         f"boy'ю")
            self.warm = f"{user.first_name} відчув тепло"
            if not lvl:
                self.lvl = (f"Welcome to the club, {user.first_name}\n"
                            f"Тепер у тебе {lvl} рівень!")
        if target:
            if lvl:
                self.lvl_cmd = f"У {target.first_name} {lvl} рiвень"


class Language:

    def __init__(self, update: Update):
        self.__user = update.effective_user

    def __call__(self, target: User = None, lvl: int | float = None,
                 *args, **kwargs):
        if self.__user.language_code == "uk":
            self.__lang = Ukraine(self.__user, target, lvl)
        else:
            self.__lang = Russian(self.__user, target, lvl)
        return self.__lang
