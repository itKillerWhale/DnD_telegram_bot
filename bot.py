from tocen import BOT_TOCEN
import requests

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

    name = State()
    race = State()
    background = State()
    alignment = State()
    level = State()
    skils = State()
    stats = State()


stats_dict = {0: "Strength", 1: "Dexterity", 2: "Constitution", 3: "Intelligence", 4: "Wisdom", 5: "Charisma"}


# ---- KEYBOARDS ----
def get_keyboard_for_create() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="1", callback_data="slot_1"),
                                                 InlineKeyboardButton(text="2", callback_data="slot_2"),
                                                 InlineKeyboardButton(text="3", callback_data="slot_3")]])
    return ikb


def get_keyboard_for_menu() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Имя", callback_data="name"),
                                                 InlineKeyboardButton(text="Раса", callback_data="race")],
                                                [InlineKeyboardButton(text="Предистория", callback_data="background"),
                                                 InlineKeyboardButton(text="Мировозрение", callback_data="alignment")],
                                                [InlineKeyboardButton(text="Уровень", callback_data="level"),
                                                 InlineKeyboardButton(text="Характеристики", callback_data="stats")],
                                                [InlineKeyboardButton(text="Навыки", callback_data="skils"),
                                                 InlineKeyboardButton(text="_", callback_data="_")],
                                                [InlineKeyboardButton(text="Показать информацию",
                                                                      callback_data="info")],
                                                [InlineKeyboardButton(text="Отмена", callback_data="menu_cancel")]])

    return ikb


def get_keyboard_for_races() -> InlineKeyboardMarkup:
    url = 'https://www.dnd5eapi.co/api/races'
    response = requests.get(url).json()

    races_list = list(map(lambda x: str(x["name"]), response["results"]))

    race = ""
    if len(races_list) % 2 == 1:
        race = races_list.pop(-1)

    ikb = InlineKeyboardMarkup()

    for i in range(len(races_list) // 2):
        ikb.add(*[InlineKeyboardButton(text=races_list[i], callback_data=f"races_{races_list[i].lower()}"),
                  InlineKeyboardButton(text=races_list[len(races_list) - 1 - i],
                                       callback_data=f"races_{races_list[len(races_list) - 1 - i].lower()}")])

    ikb.add(*[InlineKeyboardButton(text=race, callback_data=f"races_{race.lower()}"),
              InlineKeyboardButton(text="Своя раса", callback_data="races_other")])

    ikb.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))

    return ikb


def get_keyboard_for_background() -> InlineKeyboardMarkup:
    url = 'https://www.dnd5eapi.co/api/backgrounds'
    response = requests.get(url).json()

    background_list = list(map(lambda x: str(x["name"]), response["results"]))

    background = ""
    if len(background_list) % 2 == 1:
        background = background_list.pop(-1)

    ikb = InlineKeyboardMarkup()

    for i in range(len(background_list) // 2):
        ikb.add(
            *[InlineKeyboardButton(text=background_list[i], callback_data=f"backgrounds_{background_list[i].lower()}"),
              InlineKeyboardButton(text=background_list[len(background_list) - 1 - i],
                                   callback_data=f"backgrounds_{background_list[len(background_list) - 1 - i].lower()}")])

    ikb.add(*[InlineKeyboardButton(text=background, callback_data=f"backgrounds_{background.lower()}"),
              InlineKeyboardButton(text="Своя предистория", callback_data="backgrounds_other")])

    ikb.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))

    return ikb


def get_keyboard_for_alignment() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    evil_good_list = [("Добро", "good"), ("Нейтрал", "neutral"), ("Зло", "evil")]
    chaotic_lawful_list = [("Закон", "lawful"), ("Нейтрал", "neutral"), ("Хаоc", "chaotic")]
    for chaotic_lawful in chaotic_lawful_list:
        ibtn_list = []
        for evil_good in evil_good_list:
            ibtn_list.append(InlineKeyboardButton(text=f"{chaotic_lawful[0]} - {evil_good[0]}",
                                                  callback_data=f"{chaotic_lawful[1]} - {evil_good[1]}"))
        ikb.add(*ibtn_list[:])
        ibtn_list.clear()
    return ikb


def get_keyboard_for_our_states() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="/back"))

    return kb


# ---- MESSAGE ----

@dp.message_handler(commands=["cancel"], state="*")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await message.answer("Отменнено", reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=["back"], state="*")
async def cancel(message: types.Message, state: FSMContext):
    await message.delete()
    await CreateStatesGroup.menu.set()


@dp.message_handler(commands=["create"])
async def create(message: types.Message, state: FSMContext) -> None:
    print(get_keyboard_for_create())
    async with state.proxy() as data:
        data["delete_list"] = []

    await message.answer(text="Выберите слот для создания персонажа", reply_markup=get_keyboard_for_create())


@dp.message_handler(lambda message: message.text, state=CreateStatesGroup.name)
async def get_name(message: types.Message, state: FSMContext) -> None:
    delete_list = [message.message_id]

    await CreateStatesGroup.menu.set()
    new_message = await message.answer(text=f"Теперь имя вашего персонажа: '{message.text}'")
    delete_list.append(new_message.message_id)

    async with state.proxy() as data:
        data["name"] = message.text
        data["delete_list"] += delete_list


# ---- CALLBACK QUERY ----
@dp.callback_query_handler(lambda callbeck: "slot" in callbeck.data)
async def get_slot(callbeck: types.CallbackQuery, state: FSMContext) -> None:
    n = int(callbeck.data[-1])

    async with state.proxy() as data:
        data["n_slot"] = n

    await CreateStatesGroup.menu.set()
    await callbeck.message.answer(text=f"Выбран слот {n}.\nЗаполните информацию о персонаже",
                                  reply_markup=get_keyboard_for_menu())


@dp.callback_query_handler(state=CreateStatesGroup.menu)
async def menu(callbeck: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        for id in data["delete_list"][::-1]:
            await bot.delete_message(message_id=id, chat_id=callbeck.message.chat.id)
        data["delete_list"] = []

    if callbeck.data == "info":
        async with state.proxy() as data:
            await callbeck.answer(text=str(data), show_alert=True)

    elif callbeck.data == "name":
        await CreateStatesGroup.name.set()

        async with state.proxy() as data:
            try:
                name = data["name"]
            except KeyError:
                new_message = await callbeck.message.answer(text="Введите имя персонажа",
                                                            reply_markup=get_keyboard_for_our_states())

            else:
                new_message = await callbeck.message.answer(
                    text=f"Имя вашего персонажа уже {name}. Если не хотите его менять нажмите /back")

            data["delete_list"].append(new_message.message_id)

    elif callbeck.data == "race":
        await CreateStatesGroup.race.set()

        async with state.proxy() as data:
            try:
                race = data["race"]
            except KeyError:
                pass
            else:
                await callbeck.answer(f"Раса вашего персонажа {race.capitalize()}.\n"
                                      f"Для смены нажмите на нужную расу. Для отмены нажмите /back", show_alert=True)

            await callbeck.message.answer(text="Выберите расу персонажа", reply_markup=get_keyboard_for_races())

    elif callbeck.data == "background":
        await CreateStatesGroup.background.set()

        async with state.proxy() as data:
            try:
                background = data["background"]
            except KeyError:
                pass
            else:
                await callbeck.answer(f"Предистория вашего персонажа {background.capitalize()}.\n"
                                      f"Для смены нажмите на нужную предисторию. Для отмены нажмите /back",
                                      show_alert=True)

            await callbeck.message.answer(text="Выберите предисторию персонажа",
                                          reply_markup=get_keyboard_for_background())

    elif callbeck.data == "alignment":
        await CreateStatesGroup.alignment.set()

        async with state.proxy() as data:
            try:
                alignment = data["alignment"]
            except KeyError:
                pass
            else:
                await callbeck.answer(f"Мировозрение вашего персонажа {alignment.capitalize()}.\n"
                                      f"Для смены нажмите на нужное мировозрение. Для отмены нажмите /back",
                                      show_alert=True)

            await callbeck.message.answer(text="Выберите мировозрение персонажа",
                                          reply_markup=get_keyboard_for_alignment())


@dp.callback_query_handler(lambda callbeck: callbeck.data == "cancel", state="*")
async def cancel(callbeck: types.CallbackQuery):
    await CreateStatesGroup.menu.set()
    await callbeck.message.delete()


@dp.callback_query_handler(state=CreateStatesGroup.race)
async def get_race(callbeck: types.CallbackQuery, state: FSMContext):
    race = callbeck.data.replace("races_", "")
    async with state.proxy() as data:
        data["race"] = race

    await callbeck.answer(f"Выбранна раса {race.capitalize()}", show_alert=True)
    await callbeck.message.delete()
    await CreateStatesGroup.menu.set()


@dp.callback_query_handler(state=CreateStatesGroup.background)
async def get_background(callbeck: types.CallbackQuery, state: FSMContext):
    background = callbeck.data.replace("backgrounds_", "")
    async with state.proxy() as data:
        data["background"] = background

    await callbeck.answer(f"Выбранна предистория {background.capitalize()}", show_alert=True)
    await callbeck.message.delete()
    await CreateStatesGroup.menu.set()


@dp.callback_query_handler(state=CreateStatesGroup.alignment)
async def get_background(callbeck: types.CallbackQuery, state: FSMContext):
    alignment = callbeck.data
    async with state.proxy() as data:
        data["alignment"] = alignment

    await callbeck.answer(f"Выбранно мировозрение {alignment.capitalize()}", show_alert=True)
    await callbeck.message.delete()
    await CreateStatesGroup.menu.set()


# @dp.message_handler()
# async def echo(message: types.Message) -> None:
#     await message.answer(text=message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
