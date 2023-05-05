class TelegramConfig:

    def __init__(self, token: str):
        self.__token = token

    @property
    def token(self):
        return self.__token


billy = TelegramConfig("6142604213:AAHOfdX--XxT6TF1xZQuHlHAl9-73wteGws")
billy_test = TelegramConfig("5930487248:AAHlFY3sgDj8BRN2npbhLEZWv-RLdIu5Ykk")
