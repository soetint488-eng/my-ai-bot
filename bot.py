import logging
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
from io import BytesIO

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 BOT SETUP (CODENAME: DOMINIC CARTOON LAB ENGINE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "✨ **Dominic PhotoLab AI Bot မှ ကြိုဆိုပါတယ်!**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📸 **အသုံးပြုပုံ:**\n"
        "Bot ဆီကို လူပုံ (သို့မဟုတ်) မိမိကြိုက်နှစ်သက်ရာ ဓာတ်ပုံတစ်ပုံကို ပို့ပေးလိုက်ပါ။\n"
        "စက္ကန့်ပိုင်းအတွင်းမှာ လှပတဲ့ **AI Cartoon/Anime Style** အဖြစ် အလိုအလျောက် ဖန်တီးပေးမှာ ဖြစ်ပါတယ်ဗျာ။"
    )

@dp.message_handler(content_types=['photo'])
async def handle_photolab_effect(message: types.Message):
    init_msg = await message.reply("⚡ **PROCESSING YOUR PHOTO WITH CARTOON EFFECT...**")

    try:
        # ၁။ ပုံကို Telegram Server ပေါ်ကနေ အကြည်ဆုံး Size နဲ့ ဆွဲယူခြင်း
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"

        # ၂။ PhotoLab စတိုင် 3D Pixar/Anime Cartoon ပုံစံပြောင်းလဲရန် Prompt သတ်မှတ်ခြင်း
        # (ကိုကို့ရဲ့ curl ထဲက ပုံစံမျိုးထွက်အောင် prompt အလန်းစားကို ကြိုတင် Set ထားပေးပါတယ်)
        cartoon_prompt = "3d animation style, pixar character art, highly detailed, sharp focus, vibrant colors, masterpiece"
        formatted_prompt = cartoon_prompt.replace(" ", "%20")
        
        # ၃။ AI Gateway URL တည်ဆောက်ခြင်း
        ai_gateway_url = (
            f"https://image.pollinations.ai/p/{formatted_prompt}"
            f"?width=1024&height=768&model=flux"
            f"&enhance=true&seed=12345"
            f"&image={file_url}"  # မူရင်းပုံကို base URL အနေနဲ့ ထည့်သွင်းခြင်း
        )

        # ၄။ AI က ပြောင်းလဲပေးလိုက်တဲ့ ပုံအသစ်ကို Download ဆွဲယူပြီး User ဆီ ပြန်ပို့ခြင်း
        async with aiohttp.ClientSession() as session:
            async with session.get(ai_gateway_url, timeout=45) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    photo_file = BytesIO(image_data)
                    photo_file.name = 'photolab_effect.jpg'
                    
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=photo_file,
                        caption=(
                            f"🎨 **AI CARTOON EFFECT COMPLETED**\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"✨ *Style: PhotoLab 3D Pixar / Anime Art*\n"
                            f"🌌 *Engine Tuan by Dominic*"
                        ),
                        reply_to_message_id=message.message_id
                    )
                    await bot.delete_message(message.chat.id, init_msg.message_id)
                else:
                    await bot.edit_message_text(
                        f"⚠️ **AI SERVER ERROR:** HTTP `{response.status}`", 
                        message.chat.id, init_msg.message_id
                    )

    except Exception as e:
        await bot.edit_message_text(
            f"🛑 **ENGINE ERROR:**\n`{str(e)}`", 
            message.chat.id, init_msg.message_id
        )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
