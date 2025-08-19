from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from os import getenv
from core import get_response, get_weather

load_dotenv()
token = getenv('TELEGRAM_BOT_KEY')
channel_id = getenv('CHANNEL_ID')
model = None

dp = Dispatcher()

class Form(StatesGroup):
    prompt = State()
    city = State()

@dp.message(CommandStart())
async def start_bot(message: Message):

    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Gemini 1.5 Flash', callback_data='gemini-1.5-flash'),
        InlineKeyboardButton(text='Gemini 2.0 Flash', callback_data='gemini-2.0-flash-001'),
        InlineKeyboardButton(text='Gemini 2.5 Flash', callback_data='gemini-2.5-flash')
    ]])

    await message.answer('Hello, call me <code>LumiBot</code>', parse_mode='html', reply_markup=markup)

@dp.callback_query(F.data.startswith('gemini'))
async def callback_data(call: CallbackQuery):

    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Generate text', callback_data='gen-text'),
        InlineKeyboardButton(text='Get weather', callback_data='gen-weather')
    ]])

    await call.message.answer(f"Okay, i'm gonna use <code>{call.data.title()}</code> to answer you.\nPlease choose what i need to do", parse_mode='html', reply_markup=markup)
    
    global model
    model = call.data

@dp.callback_query(lambda call: call.data == 'gen-text')
async def get_message(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.prompt)

    await call.message.answer('Okay, please enter your message')

@dp.message(Form.prompt)
async def generate_text(message: Message, state: FSMContext):
    global model
    response = await get_response(message.text, model)

    await message.bot.send_message(channel_id, f'Prompt: <i>{message.text}</i>\n\nResponse: <i>{response[0]}</i>\n\nGenerated with <code>{response[1]}</code>', parse_mode='html')
    
    model = None
    await state.clear()

@dp.callback_query(lambda call: call.data == 'gen-weather')
async def generate_text(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.city)

    await call.message.answer('Okay, please enter your city')

@dp.message(Form.city)
async def generate_weather(message: Message, state: FSMContext):
    global model
    response = await get_weather(message.text, model)

    await message.answer(f'{response[0]}\n\nGenerated with <code>{response[1]}</code>', parse_mode='html')
    
    model = None
    await state.clear()

async def main():
    bot = Bot(token=token)
    await dp.start_polling(bot)