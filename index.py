import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import *
import random

stickers = []
words = {}

with open('stickers.txt', encoding="utf8") as f:
    stickers = f.read().splitlines()

with open('words.txt', encoding="utf8") as f:
    wordlist = f.read().splitlines()
    for word in wordlist:
        parts = word.split('-')
        meanings = parts[1].split(',')
        pronounce = parts[0].strip()
        pronounce_one = pronounce.split('(')[0].strip()
        pronounce_two = pronounce.split('(')[1].split(')')[0].strip()

        for meaning in meanings:
            words[meaning.strip()] = {'pronounce_full': pronounce, 'pronounce_one': pronounce_one, 'pronounce_two': pronounce_two}
async def words_kb(p=0):
    words_kb = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    words_only = list(words.keys())[p*10:(p*10)*2 if p!=0 else p+1*10]
    i = 0
    ii = 0
    
    words2add = []
    while ii<10:
        if len(words_only) < 10 and ii >=len(words_only):
            break
        if i<=len(words_only)-1:
            words2add.append(words_only[i])
        if i+1<=len(words_only)-1:
            words2add.append(words_only[i+1])

        if len(words2add) == 1:
            words_kb.row(InlineKeyboardButton(text=words2add[0], callback_data="w_"+str(p)+"_"+words2add[0]))
            i+=1
        if len(words2add) == 2:
            words_kb.row(InlineKeyboardButton(text=words2add[0], callback_data="w_"+str(p)+"_"+words2add[0]), InlineKeyboardButton(text=words2add[1], callback_data="w_"+str(p)+"_"+words2add[1]))
            i+=2

        ii+=len(words2add)
        words2add = []

    if ii ==0:
        raise Exception("nah")
    
    words_kb.row(InlineKeyboardButton("⬅️", callback_data=f"page_{p-1 if p-1>0 else 0}"),InlineKeyboardButton(str(p+1), callback_data="ignore"), InlineKeyboardButton("➡️", callback_data=f"page_{p+1}"))
    words_kb.add(InlineKeyboardButton("Pronunciation guide", callback_data="pronun"), InlineKeyboardButton("Contact me", url="t.me/Pomorgite"))
    
    return words_kb

async def back_kb(page):
    kb = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(InlineKeyboardButton(f"Back to page {page+1}", callback_data=f"page_{page}"))
    return kb

API_TOKEN = '6565650736:AAF92hXUGldzVlXH8yXwdHH34z0VYHeFDxg'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.callback_query_handler(text_contains="page")
async def page(call: CallbackQuery):
    await call.answer()
    page = int(call.data.split("_")[1])
    try:
        kb = await words_kb(page)
    except:
        return
    await call.message.edit_text(f"Page {page+1}")
    await call.message.edit_reply_markup(reply_markup=kb)

@dp.callback_query_handler(text_contains="w")
async def page(call: CallbackQuery):
    await call.answer()
    word = call.data.split("_")[2]
    page = int(call.data.split("_")[1])
    await call.message.edit_text(f"{word} - {words[word]['pronounce_full']}")
    await call.message.edit_reply_markup(reply_markup=await back_kb(page))

@dp.callback_query_handler(text="ignore")
async def page(call: CallbackQuery):
    await call.answer()

@dp.callback_query_handler(text="pronun")
async def pronun(call: CallbackQuery):
    await call.answer()
    await call.message.answer('''á –(a) like in the word <b>"what"</b>
a - (a:) like in the word <b>"last"</b>
e – (æ)] like in the word <b>"bed", "cat"</b>, cats don't use long (æ)
é – (e) like in the word <b>"get, generation"</b>
é: – this is a vocal similar to the previous, <b>just longer</b>
i – (i) like in the word <b>"ship"</b>, cats don't use long (i)
o – (o) like in the word <b>"hot", "box"</b>, cats don't use long (o)
ö – (ə) like in the word <b>"third"</b>, cats don't use long (ə)
u – (u) like in the word <b>"wood", "took"</b>
u: - (u:) like in the word <b>"fool"</b>''', parse_mode="html")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer_sticker(random.choice(stickers))
    await message.answer("Hi! I'm gonna help you learn cat language!\nUse buttons below to continue.\n\nPro tip: Type the word, or a part of it, and I will reply with probable meanings of it!", reply_markup=await words_kb(0))

@dp.message_handler()
async def find_meaning(message: types.message):
    word = message.text.strip()
    words2send = []
    for word1 in list(words.keys()):
        if word1.lower().count(word.lower())>0:
            words2send.append(word1)

    resp = []
    for word1 in words2send:
        resp.append(f"{word1} - {words[word1]['pronounce_full']}")
    
    await message.answer('Here are the meanings, for the word you probably meant: \n\n'+'\n'.join(resp) if len(resp)>0 else 'Nothing found.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)