import requests
import time
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from telegraph import Telegraph

def getAllData():
	data = requests.get(
		'https://milab.s3.yandex.net/2020/covid19-stat/data/v10/default_data.json',
		params = {'v': str(int(time.time() * 1000))}
	).json()['world_stat_struct']['data']

	return [data[c]['info'] for c in data]

def getAllVaccine():
	data = requests.get(
		'https://milab.s3.yandex.net/2020/covid19-stat/data/v10/default_data.json',
		params = {'v': str(int(time.time() * 1000))}
	).json()['vaccination_struct']

	return [data[c] for c in data]

def getAllRegions():
	data = requests.get(
		'https://milab.s3.yandex.net/2020/covid19-stat/data/v10/default_data.json',
		params = {'v': str(int(time.time() * 1000))}
	).json()['russia_stat_struct']['data']
	
	return [data[c]['info'] for c in data]

def createPage(title, html):
	telegraph = Telegraph()
	telegraph.create_account(short_name = 'CoronaStat')

	response = telegraph.create_page(
		title,
		html_content = html
	)

	return 'https://telegra.ph/' + response['path']

bot = Bot(token = open('token.txt', 'r').readlines()[0].strip(), parse_mode = 'HTML')
dp = Dispatcher(bot)

@dp.message_handler(commands = ['start'])
async def main(message: types.Message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
	itembtn1 = types.KeyboardButton('🦠 Коронавирус')
	itembtn2 = types.KeyboardButton('💉 Вакцинация')
	itembtn3 = types.KeyboardButton('🦠 Регионы')
	markup.add(itembtn1, itembtn2, itembtn3)
	await bot.send_message(message.from_user.id, 'Привет!\nЯ бот, который умеет парсить статистику по коронавирусу и вакцинации!', reply_markup = markup)
 
@dp.message_handler(content_types = ['text'])
async def covid(message: types.Message):
	if message.text == '🦠 Коронавирус':
		lst = list()
		for country in getAllData():
			lst.append(f'<p>{country["name"]}: ☣ {country["cases"]} (+{country["cases_delta"]}) 💀 {country["deaths"]} (+{country["deaths_delta"]}) 💊 {country["cured"]} (+{country["cured_delta"]})</p>')
		lst = '\n'.join(lst)
		page = createPage('CoronaStatAll', lst)
		await bot.send_message(message.from_user.id, f'Ваша страница готова:\n{page}')

	elif message.text == '💉 Вакцинация':
		lst = list()
		for country in getAllVaccine():
			if 'peop_full_vac' in country:
				lst.append(f'<p>{country["name_ru"]}: 💉 {"{0:,}".format(int(country["peop_full_vac"])).replace(",", " ")}</p>')
		lst = '\n'.join(lst)
		page = createPage('VaccineStatAll', lst)
		await bot.send_message(message.from_user.id, f'Ваша страница готова:\n{page}')

	elif message.text == '🦠 Регионы':
		lst = list()
		for country in getAllRegions():
			lst.append(f'<p>{country["name"]}: ☣ {country["cases"]} (+{country["cases_delta"]}) 💀 {country["deaths"]} (+{country["deaths_delta"]})</p>')
		lst = '\n'.join(lst)
		page = createPage('RegionStat', lst)
		await bot.send_message(message.from_user.id, f'Ваша страница готова:\n{page}')

if __name__ == '__main__':
	executor.start_polling(dp)
