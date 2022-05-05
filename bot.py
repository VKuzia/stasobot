from abc import ABC, abstractmethod

from aiogram import Bot, types

from model import Model
from storage import Storage, Registry


class BotApi(ABC):

    @abstractmethod
    async def handle_temperature(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def handle_length(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def handle_default(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def handle_params(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def handle_message(self, message: types.Message) -> None:
        pass


class BotApiImpl(BotApi):

    def __init__(self, bot: Bot, storage: Storage, model: Model):
        self.bot = bot
        self.storage = storage
        self.model = model

    async def handle_temperature(self, message: types.Message) -> None:
        args = message.get_args()
        try:
            float(args)
        except ValueError:
            await message.reply('/temperature принимает только вещественный тип [float]')
            return
        temperature = float(args)
        if temperature < 0.01 or temperature > 100:
            await message.reply(
                'на всякий случай устанавливайте температуру в промежутке от 0.01 до 100')
            return
        self.storage.checkout(message.chat.id)
        self.storage.set_temperature(message.chat.id, temperature)
        await message.reply(f'Температура установлена на {temperature}')

    async def handle_length(self, message: types.Message) -> None:
        args = message.get_args()
        try:
            int(args)
        except ValueError:
            await message.reply('/length принимает только целочисленный тип [int]')
            return
        length = int(args)
        if length < 10 or length > 1000:
            await message.reply(
                'на всякий случай устанавливайте длину ответа в промежутке от 10 до 1000')
            return
        self.storage.checkout(message.chat.id)
        self.storage.set_length(message.chat.id, length)
        await message.reply(f'Длина ответа установлена на {length}')

    async def handle_default(self, message: types.Message) -> None:
        self.storage.checkout(message.chat.id)
        self.storage.set_temperature(message.chat.id, Registry().temperature)
        self.storage.set_length(message.chat.id, Registry().length)
        await message.reply(
            f'Температура установлена на {Registry().temperature}\n'
            f'Длина ответа установлена на {Registry().length}')

    async def handle_params(self, message: types.Message) -> None:
        self.storage.checkout(message.chat.id)
        await message.reply(
            f'Температура: {self.storage.get_temperature(message.chat.id)}\n'
            f'Длина ответа: {self.storage.get_length(message.chat.id)}'
        )

    async def handle_message(self, message: types.Message) -> None:
        if len(message.text) < 7:
            await message.reply('я отвечаю только на сообщения, в которых есть хотя бы 7 символов')
            return
        if len(message.text) > 100:
            await message.reply('я не отвечаю на сообщения, в которых больше 100 символов')
            return
        filtered = self.model.filter(message.text)
        if len(filtered) < 7:
            await message.reply(f'После чистки сообщения в нём оказалось меньше 7 символов. '
                                f'Я на такое отвечать не буду:\n\n"{filtered}"')
            return
        self.storage.checkout(message.chat.id)
        result = self.model.generate(filtered, self.storage.get_length(message.chat.id),
                                     self.storage.get_temperature(message.chat.id))
        messages = result.split(self.model.special)
        for item in messages:
            await message.answer(item)
