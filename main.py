from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from kb_client import kb_client, kb_fsm_cancel
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from db import db_start, edit_profile, create_profile

storage = MemoryStorage()
TOKEN = "YOUR TOKEN"

bot = Bot(TOKEN)
dp = Dispatcher(bot=bot,
                storage=storage)

async def on_startup(_):
    await db_start()

class ProfState(StatesGroup):

    name = State()
    desc = State()
    price = State()
    photo = State()

class SupState(StatesGroup):

    sup_mes = State()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Welcome!",
                           reply_markup=kb_client())
    await create_profile(user_id=message.from_user.id)

@dp.message_handler(Text(equals="Restaurants near 🥰", ignore_case=True))
async def cmd_near(message: types.Message):
    await bot.send_location(chat_id=message.from_user.id,
                            latitude=40,
                            longitude=40,
                            reply_markup=kb_client())

@dp.message_handler(Text(equals="Menu 🔥", ignore_case=True))
async def cmd_menu(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='menu')

@dp.message_handler(Text(equals="Support 😐", ignore_case=True))
async def cmd_sup(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Write your letter')
    await SupState.sup_mes.set()


@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
async def cmd_cancel(message:types.Message, state: FSMContext):
    await message.answer("Stopped",
                         reply_markup=kb_client())
    return await state.finish()


@dp.message_handler(Text(equals="Add Food", ignore_case=True))
async def cmd_admin(message:types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Send name your Food!",
                           reply_markup=kb_fsm_cancel())
    await ProfState.name.set()

@dp.message_handler(state=SupState.sup_mes)
async def sup_letter_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['support_letter'] = message.text
        await message.answer("We take your letter. Thank You!")


@dp.message_handler(state=ProfState.name)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply('Now send description',
                        reply_markup=kb_fsm_cancel())
    await ProfState.next()



@dp.message_handler(state=ProfState.desc)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await message.reply('Now send price',
                        reply_markup=kb_fsm_cancel())
    await ProfState.next()

@dp.message_handler(lambda message: not message.text.isdigit(),state=ProfState.price)
async def check_price(message: types.Message):
    await message.answer('This is not your price in $')

@dp.message_handler(state=ProfState.price)
async def load_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await message.reply('Now send photo',
                        reply_markup=kb_fsm_cancel())
    await ProfState.next()

@dp.message_handler(lambda message: not message.photo, state=ProfState.photo)
async def check_photo(message: types.Message):
    await message.reply('This is no photo')


@dp.message_handler(content_types=['photo'], state=ProfState.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await message.reply('Succesfull')
    HELP_cd = f'''
    {data['name']}, {data['price']}$
    {data['desc']}
    '''
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=data['photo'],
                         caption=HELP_cd)
    await edit_profile(state, user_id=message.from_user.id)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)

