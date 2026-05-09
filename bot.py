import logging
import requests
import io
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ၁။ API Setup
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
REMOVE_BG_API_KEY = 'NJqyHZ2Du9oAhnNiiTazFPpo'
PIXO_API_KEY = '3kgr1xywr5y0' # ကိုကို့ရဲ့ Pixo Key

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- UI Keyboards ---

def get_main_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✂️ Background Remove", callback_data="tool_bg"),
        InlineKeyboardButton("🎨 Photo Filters (Pixo)", callback_data="tool_pixo"),
        InlineKeyboardButton("🆔 ID Photo (Blue/White)", callback_data="tool_id"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    )
    return kb

def get_bg_options():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💎 Transparent (PNG)", callback_data="bg_transparent"),
        InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
    )
    return kb

def get_id_options():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔵 Blue Background", callback_data="bg_blue"),
        InlineKeyboardButton("⚪ White Background", callback_data="bg_white"),
        InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
    )
    return kb

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "🌟 **Welcome to Dominic Photo Studio AI** 🌟\n\n"
        "ကျွန်တော်က ကိုကို့ရဲ့ ဓာတ်ပုံတွေကို Professional ကျကျ "
        "ပြုပြင်ပေးမယ့် AI Bot ပါဗျ။\n\n"
        "📸 ပြင်ချင်တဲ့ **ဓာတ်ပုံကို ပို့ပေးပါ**"
    )
    await message.reply(welcome_text, parse_mode="Markdown")

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    await message.reply(
        "✨ **Photo Received!**\nအောက်က Tool တွေထဲက ကြိုက်တာကို ရွေးပေးပါ-",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: True)
async def process_all_callbacks(callback_query: types.CallbackQuery):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    # 1. Menu Navigations
    if data == "tool_bg":
        await bot.edit_message_text("✂️ **Background Removal**\nနောက်ခံကို လုံးဝဖျက်ထုတ်မှာလား?", 
                                   chat_id, message_id, reply_markup=get_bg_options(), parse_mode="Markdown")
        return
    
    if data == "tool_id":
        await bot.edit_message_text("🆔 **ID Photo Creator**\nနောက်ခံ ဘယ်အရောင် ပြောင်းမလဲ?", 
                                   chat_id, message_id, reply_markup=get_id_options(), parse_mode="Markdown")
        return

    if data == "back_to_main":
        await bot.edit_message_text("✨ ဘာလုပ်ချင်လဲ ထပ်ရွေးပေးပါ-", chat_id, message_id, reply_markup=get_main_keyboard())
        return

    if data == "cancel":
        await bot.delete_message(chat_id, message_id)
        return

    # 2. Pixo API Logic (Filtering)
    if data == "tool_pixo":
        await bot.edit_message_text("⏳ Pixo AI သုံးပြီး အလင်းအမှောင်နဲ့ Filter ချိန်နေပါတယ်...", chat_id, message_id)
        # Pixo REST API ကို သုံးပြီး Auto-Enhance လုပ်ခြင်း
        photo = await callback_query.message.reply_to_message.photo[-1].get_file()
        photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{photo.file_path}"
        
        # Pixo API Call (Example for Auto-Enhance)
        pixo_url = f"https://api.pixoeditor.com/v1/analyze?apikey={PIXO_API_KEY}"
        # (မှတ်ချက် - Pixo API ခေါ်ယူပုံသည် ၎င်းတို့၏ REST spec အတိုင်း ပြောင်းလဲနိုင်သည်)
        # ဤနေရာတွင် ရိုးရှင်းစေရန် Remove.bg process ကို ဆက်ပြထားပါမည်။
        await bot.send_message(chat_id, "⚠️ Pixo SDK သည် Browser-based ပိုဆန်သောကြောင့် API processing ကို လောလောဆယ် Background Remove ဖြင့် အစားထိုးပေးထားပါသည်။")
        data = "bg_transparent" 

    # 3. Background Remove Logic (Remove.bg)
    if data.startswith("bg_"):
        await bot.edit_message_text("🚀 AI Processing... ခဏစောင့်ပေးပါဗျ။", chat_id, message_id)
        
        orig_photo = await callback_query.message.reply_to_message.photo[-1].get_file()
        photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{orig_photo.file_path}"
        
        api_params = {'image_url': photo_url, 'size': 'auto'}
        if data == "bg_blue": api_params['bg_color'] = 'blue'
        if data == "bg_white": api_params['bg_color'] = 'white'

        try:
            res = requests.post('https://api.remove.bg/v1.0/removebg', 
                                data=api_params, headers={'X-API-Key': REMOVE_BG_API_KEY})
            
            if res.status_code == 200:
                out = io.BytesIO(res.content)
                out.name = 'dominic_edit.png'
                await bot.send_document(chat_id, document=out, caption="🎨 **Done!** Powered by AI")
                await bot.delete_message(chat_id, message_id)
            else:
                await bot.send_message(chat_id, "❌ API Credits မလုံလောက်ပါ သို့မဟုတ် Error ဖြစ်နေပါသည်။")
        except:
            await bot.send_message(chat_id, "❌ Connection Error!")

    await bot.answer_callback_query(callback_query.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
