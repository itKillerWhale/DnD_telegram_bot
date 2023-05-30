from tocen import BOT_TOCEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

storage = MemoryStorage()
bot = Bot(BOT_TOCEN)
dp = Dispatcher(bot, storage=storage)


# ----- БЛОК "СОЗДАНИЕ НОВОГО ПЕРСОНАЖА" -----
class CreateStatesGroup(StatesGroup):
    menu = State()
    stats = State()
    skills = State()


@dp.message_handler(commands=["cancel"], state="*")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await message.answer("Отменнено", reply_markup=ReplyKeyboardRemove())
    await state.finish()


stats_dict = {0: "Strength", 1: "Dexterity", 2: "Constitution", 3: "Intelligence", 4: "Wisdom", 5: "Charisma"}


def get_keyboard_for_menu() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Имя", callback_data="create_name"),
                                                 InlineKeyboardButton(text="Раса", callback_data="create_race")],
                                                [InlineKeyboardButton(text="Предистория", callback_data="background"),
                                                 InlineKeyboardButton(text="Мировозрение", callback_data="alignment")],
                                                [InlineKeyboardButton(text="Уровень", callback_data="level"),
                                                 InlineKeyboardButton(text="Характеристики", callback_data="stats")],
                                                [InlineKeyboardButton(text="Навыки", callback_data="skils"),
                                                 InlineKeyboardButton(text="", callback_data="_")],
                                                [InlineKeyboardButton(text="Отмена", callback_data="cancel")]])

    return ikb


def get_keyboard_for_create() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="1", callback_data="slot_1"),
                                                 InlineKeyboardButton(text="2", callback_data="slot_2"),
                                                 InlineKeyboardButton(text="3", callback_data="slot_3")]])
    return ikb


@dp.message_handler(commands=["create"])
async def create(message: types.Message) -> None:
    print(get_keyboard_for_create())
    await message.answer(text="Выберите слот для создания персонажа", reply_markup=get_keyboard_for_create())


@dp.callback_query_handler(lambda callbeck: "slot" in callbeck.data)
async def get_slot(callbeck: types.CallbackQuery, state: FSMContext) -> None:
    n = int(callbeck.data[-1])

    async with state.proxy() as data:
        data["n_slot"] = n

    await CreateStatesGroup.menu.set()
    await callbeck.message.answer(text=f"Выбран слот {n}.\nЗаполните информацию о персонаже",
                                  reply_markup=get_keyboard_for_menu())


# @dp.message_handler()
# async def echo(message: types.Message) -> None:
#     await message.answer(text=message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
