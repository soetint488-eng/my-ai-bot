import logging
import requests
import io
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ၁။ Setup
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
REMOVE_BG_API_KEY = 'NJqyHZ2Du9oAhnNiiTazFPpo' # ကိုကိုပေးတဲ့ Key ထည့်ထားပါတယ်

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ခလုတ်များ တည်ဆောက်ခြင်း
def get_bg_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✂️ ဖြတ်ထုတ်ရုံပဲ", callback_data="bg_transparent"),
        InlineKeyboardButton("🔵 အပြာရောင်ပြောင်း", callback_data="bg_blue"),
        InlineKeyboardButton("⚪ အဖြူရောင်ပြောင်း", callback_data="bg_white")
    )
    return kb

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "👤 **AI Background Remover မှ ကြိုဆိုပါတယ်!**\n\n"
        "ပြုပြင်ချင်တဲ့ လူပုံ (သို့) ပစ္စည်းပုံကို ပို့ပေးလိုက်ပါဗျ။",
        parse_mode="Markdown"
    )

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    await message.reply("ပုံရပါပြီ။ ဘာလုပ်ချင်လဲ ရွေးပေးပါဗျ-", reply_markup=get_bg_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith('bg_'))
async def process_background(callback_query: types.CallbackQuery):
    action = callback_query.data
    message = callback_query.message
    
    # User ပို့ခဲ့တဲ့ပုံကို ပြန်ယူမယ်
    photo = await message.reply_to_message.photo[-1].get_file()
    photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{photo.file_path}"
    
    await bot.edit_message_text("⏳ Processing... ခဏစောင့်ပေးပါဗျ။", 
                               chat_id=callback_query.message.chat.id, 
                               message_id=callback_query.message.message_id)

    # API Parameters သတ်မှတ်ခြင်း
    data = {
        'image_url': photo_url,
        'size': 'auto'
    }
    
    if action == "bg_blue":
        data['bg_color'] = 'blue'
    elif action == "bg_white":
        data['bg_color'] = 'white'
    # bg_transparent ဆိုရင် ဘာမှထပ်ထည့်စရာမလိုပါ (အကြည်ရမှာမို့လို့)

    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            data=data,
            headers={'X-API-Key': REMOVE_BG_API_KEY},
        )

        if response.status_code == requests.codes.ok:
            output_io = io.BytesIO(response.content)
            output_io.name = 'processed_image.png'
            
            await bot.send_document(
                callback_query.from_user.id, 
                document=output_io, 
                caption="✅ အောင်မြင်စွာ ပြုပြင်ပြီးပါပြီ!"
            )
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        else:
            error_msg = response.json().get('errors', [{}])[0].get('title', 'API Error')
            await bot.send_message(callback_query.from_user.id, f"❌ Error: {error_msg}")

    except Exception as e:
        logging.error(e)
        await bot.send_message(callback_query.from_user.id, "❌ တစ်ခုခုမှားယွင်းနေပါတယ်။ ခဏနေမှ ပြန်စမ်းကြည့်ပါဗျ။")

    await bot.answer_callback_query(callback_query.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
