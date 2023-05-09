class Russian:
    more_args_text = "Слишком много аргументов. Попробуй убрать лишние"
    idk_command_text = "Неизвестная команда. Попробуй написать команду /help"
    self1_text = " сам себе"
    self2_text = " самого себя"
    no_args_text = "Нет аргументов"
    no_db_user_text = "Нет в датабазе пользователя"
    check_cmd_text = "Команд не существовало. Создал новое меню с командами"
    ok_text = "Все в норме"
    no_access_text = "У тебя нет доступа к команде, slave"
    no_cmd_access_text = ("Команда в этом чате недоступна. Попробуйте добавить"
                          " меня в группу или канал.")
    no_arg_table_text = "Какую таблицу?"
    done_text = "Готово, boy"
    error_args_text = ("Неправильно введена команда. Попробуй проверить данные"
                       " на ошибки")
    empty_text = "Пользователь не введён. Попробуй добавить пользователя"
    start_text = ("Привет, ♂slave♂\n"
                  "Видимо, ты здесь новенький, давай сам Billy тебя проведёт в"
                  " ♂deep dark fantasies♂\n"
                  "Напиши /help для списка команд с которыми ты сможешь "
                  "использовать силы настоящего ♂full master♂\n"
                  "И самое главное, ♂slave♂, что сила в мужской дружбе")
    no_here_text = ("Добавь меня в группу или канал для начала моей грязной "
                    "работы ;)")
    cmds_text = (
        # "/help - Вывести все команды бота",
        "/profile - Посмотреть статистику ♂slave♂'а",
        "/lvl - Посмотреть уровень ♂slave♂'а",
        "/fisting - Сделать ♂fisting♂ ♂slave♂'у",
        "/deep - Проверить глубину ♂slave♂'а",
        "/warm - Почувствовать тепло ♂slave♂'а"
    )
    for_check_menu_text = (
        "Список команд",
        "Посмотреть статистику ♂slave♂'а",
        "Посмотреть уровень ♂slave♂'а",
        "Сделать ♂fisting♂ ♂slave♂'у",
        "Проверить глубину ♂slave♂'а",
        "Почувствовать тепло ♂slave♂'а"
    )

    def __init__(self, user=None, member=None, lvl=None):
        if user is not None:
            self.fisting_text = f"{user.first_name} делает жесткий ♂fisting♂"
            self.deep_text = (f"♂It's so fucking deep♂ - сказал "
                              f"{user.first_name} boy'ю")
            self.warm_text = f"{user.first_name} почувствовал тепло"
            if lvl is not None:
                self.lvl_text = (f"Welcome to the club, {user.first_name}\n"
                                 f"Теперь у тебя {lvl} уровень!")
        if member is not None:
            if lvl is not None:
                self.lvl_cmd_text = f"У {member.user.first_name} {lvl} уровень"

    @classmethod
    def get_cmds_text(cls):
        output = ""
        for t in cls.cmds_text:
            output += t + "\n"
        return output


class Ukraine:
    more_args_text = "Занадто багато аргументів. Спробуй видалити зайві"
    idk_command_text = "Невідома команда. Спробуй написати команду /help"
    self1_text = " сам собі"
    self2_text = " самого себе"
    no_args_text = "Немає аргументів"
    no_db_user_text = "Немає в датабазі користувача"
    check_cmd_text = "Команд не існувало. Створив нове меню із командами"
    ok_text = "Все в нормі"
    no_access_text = "У тебе немає доступу до команди, slave"
    no_cmd_access_text = ("Команда в цьому чаті недоступна. Спробуйте додати "
                          "мене в групу чи канал.")
    no_arg_table_text = "Яку таблицю?"
    done_text = "Готово, boy"
    error_args_text = ("Неправильно введено команду. Спробуй перевірити дані "
                       "на помилки")
    empty_text = "Користувач не введений. Спробуй додати користувача"
    start_text = ("Привіт, ♂slave♂\n"
                  "Мабуть, ти тут новенький, давай сам Billy тебе проведе в "
                  "♂deep dark fantasies♂\n"
                  "Напиши /help для списку команд з якими ти зможеш "
                  "використовувати сили справжнього ♂full master♂\n"
                  "І саме головне, ♂slave♂, що сила в чоловічій дружбі")
    no_here_text = ("Добав мене в групу чи канал для початку моєї брудної "
                    "праці ;)")
    cmds_text = (
        # "/help - Вивести всі команди бота",
        "/profile - Подивитися статистику ♂slave♂'а",
        "/lvl - Переглянути рівень ♂slave♂'а",
        "/fisting - Зробити ♂fisting♂ ♂slave♂'у",
        "/deep - Перевірити глибину ♂slave♂'а",
        "/warm - Відчути тепло ♂slave♂'а"

    )
    for_check_menu_text = (
        "Список команд",
        "Подивитися статистику ♂slave♂'а",
        "Зробити ♂fisting♂ ♂slave♂'у",
        "Перевірити глибину ♂slave♂'а",
        "Відчути тепло ♂slave♂'а",
        "Переглянути рівень ♂slave♂'а"
    )

    def __init__(self, user=None, member=None, lvl=None):
        if user is not None:
            self.fisting_text = f"{user.first_name} робить жорсткий ♂fisting♂"
            self.deep_text = (
                f"♂It's so fucking deep♂ - сказав {user.first_name} "
                f"boy'ю")
            self.warm_text = f"{user.first_name} відчув тепло"
            if lvl is not None:
                self.lvl_text = (f"Welcome to the club, {user.first_name}\n"
                                 f"Тепер у тебе {lvl} рівень!")
        if lvl is not None:
            if member is not None:
                self.lvl_cmd_text = f"У {member.user.first_name} {lvl} рiвень"

    @classmethod
    def get_cmds_text(cls):
        output = ""
        for t in cls.cmds_text:
            output += t + "\n"
        return output
