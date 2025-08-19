from google import genai
from google.genai import types
from dotenv import load_dotenv
from os import getenv
import aiohttp
from json import dumps

load_dotenv()
bot_api_key = getenv('GEMINI_API_KEY')
weather_api_key = getenv('WEATHER_API_KEY')

client = genai.Client(api_key=bot_api_key)

async def get_response(message: str, model: str) -> tuple:
    response = client.models.generate_content(
        model=model,
        contents=message
    )

    return response.text, model

async def weather_func(city: str) -> dict:
    params = {
        'q': city,
        'appid': weather_api_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.openweathermap.org/data/2.5/weather', params=params) as response:
            data = await response.json()
    
    return {
        'city': city,
        'weather': data['weather'][0]['description'],
        'temp': f'{int(data['main']['temp']) - 273.15:.2f} celcius',
        'humd': f'{data['main']['humidity']}%'
    }

async def get_weather(city: str, model: str) -> tuple:
    weather = await weather_func(city)

    response = client.models.generate_content(
        model=model,
        contents=f'Weather in {city}: {weather}'
    )

    return response.text, model