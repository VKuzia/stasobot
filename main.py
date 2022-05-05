import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv

from bot import BotApiImpl, BotApi
from model import Model
from storage import Storage

load_dotenv()

bot = Bot(token=os.environ['TELEGRAM_API_KEY'])
dp = Dispatcher(bot)
cuda: bool = True if int(os.environ['CUDA']) != 0 else False
storage: Storage = Storage()
model: Model = Model(os.environ['PATH_TO_MODEL'], cuda=cuda)
core: BotApi = BotApiImpl(bot, storage, model)


@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    print(f'{message.chat.id}: start')
    await message.answer('Здравствуй, напиши мне что-нибудь, а я продолжу.'
                         'Если тебе нужна помощь, используй /help')


@dp.message_handler(commands=['help'])
async def handle_help(message: types.Message):
    print(f'{message.chat.id}: help')
    await message.answer('Для продолжения фразы в авторском стиле, просто напиши мне что-нибудь.'
                         'Принимаются строчные и прописные русские буквы, '
                         'а также некоторые знаки препинания.\n '
                         'Можешь настроить меня парой сеттеров:\n'
                         '/temperature [float] степень подрожания, '
                         'чем выше, тем вероятнее однозначный ответ\n'
                         '/length [int] длина продолжения\n'
                         '/params покажет текущие настройки бота\n'
                         '/default для восстановления параметров бота по умолчанию (1.0, 100)\n\n'
                         'Развлекайся.')


@dp.message_handler(commands=['temperature'])
async def handle_search(message: types.Message):
    print(f'{message.chat.id}: temperature -> {message.get_args()}')
    await core.handle_temperature(message)


@dp.message_handler(commands=['length'])
async def handle_stats(message: types.Message):
    print(f'{message.chat.id}: length -> {message.get_args()}')
    await core.handle_length(message)


@dp.message_handler(commands=['params'])
async def handle_stats(message: types.Message):
    print(f'{message.chat.id}: params')
    await core.handle_params(message)


@dp.message_handler(commands=['default'])
async def handle_stats(message: types.Message):
    print(f'{message.chat.id}: default')
    await core.handle_default(message)


@dp.message_handler()
async def handle_unknown(message: types.Message):
    print(f'{message.chat.id}: message -> {message.text}')
    await core.handle_message(message)


if __name__ == '__main__':
    print(os.environ['MODEL_NAME'])
    executor.start_polling(dp, skip_updates=False, reset_webhook=True)
