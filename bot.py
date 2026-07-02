import logging
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
from io import BytesIO

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 BOT SETUP (CODENAME: DOMINIC IM2IMG ART ENGINE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 START COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 **Welcome to Dominic AI Art Bot!**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📸 **အသုံးပြုပုံ:**\n"
        "၁။ Bot ထံသို့ ဓာတ်ပုံတစ်ပုံ ပို့လိုက်ပါ။\n"
        "၂။ ဓာတ်ပုံပို့သည့်အချိန်တွင် **Caption (စာသား)** နေရာ၌ ပုံဖော်လိုသည့် ပုံစံကို ရိုက်ထည့်ပေးပါ\n"
        "*(ဥပမာ: `oil painting, D&D fantasy, intricate, highly detailed, anime style`)*\n\n"
        "✨ RapidAPI မလိုဘဲ High-Speed နဲ့ အလုပ်လုပ်ပေးမှာ ဖြစ်ပါတယ်ဗျာ။"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 MAIN ENGINE: IMAGE-TO-IMAGE (IM2IMG) HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(content_types=['photo'])
async def handle_image_to_image(message: types.Message):
    # User ပို့လိုက်တဲ့ ပုံထဲမှာ Caption စာသား (Prompt) ပါမပါ စစ်ဆေးခြင်း
    user_prompt = message.caption
    
    if not user_prompt:
        await message.reply(
            "⚠️ **Prompt လိုအပ်နေပါသည်။**\n"
            "💡 ပုံပို့တဲ့အချိန်မှာ အောက်က စာရိုက်တဲ့နေရာ (Add a caption) မှာ "
            "ပြောင်းလဲချင်တဲ့ AI ပုံစံစာသားကို တစ်ပါတည်း ရိုက်ထည့်ပေးပါဗျာ။\n"
            "*(ဥပမာ caption: `beautiful oil painting, warm colors, artstation`)*"
        )
        return

    init_msg = await message.reply("⚡ **DOMINIC ENGINE: PROCESSING YOUR IMAGE WITH AI...**")

    try:
        # ၁။ Telegram Server ပေါ်က မူရင်းပုံကို Bot ကနေ Download ဆွဲယူခြင်း
        photo = message.photo[-1]  # အကြည်ဆုံး Size ကို ယူသည်
        file_info = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"

        # ၂။ Pollinations AI Image-to-Image API သို့ လှမ်းပို့ရန် URL တည်ဆောက်ခြင်း
        # Prompt စာသားထဲက Space များကို URL Format (%20) သို့ ပြောင်းလဲသည်
        formatted_prompt = user_prompt.replace(" ", "%20")
        
        # မူရင်းပုံ URL ကို သတ်မှတ်ချက်အတိုင်း တိုက်ရိုက် ချိတ်ဆက်ခြင်း
        ai_gateway_url = (
            f"https://image.pollinations.ai/p/{formatted_prompt}"
            f"?width=768&height=1024&model=flux"
            f"&enhance=true&seed=9999"
            f"&image={file_url}"  # Image-to-Image ရဲ့ အဓိက လျှို့ဝှက်ချက် Parameter
        )

        # ၃။ AI Server ဆီမှ ပုံအသစ်ကို Binary ဒေတာအဖြစ် လှမ်းယူခြင်း
        async with aiohttp.ClientSession() as session:
            async with session.get(ai_gateway_url, timeout=45) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # Memory ပေါ်မှာတင် ပုံကို BytesIO အဖြစ် အသွင်ပြောင်းခြင်း
                    photo_file = BytesIO(image_data)
                    photo_file.name = 'dominic_ai_art.jpg'
                    
                    # ၄။ User ထံသို့ AI ပြောင်းလဲပြီးသား ပုံလှလှလေးကို ပြန်လည်ပေးပို့ခြင်း
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=photo_file,
                        caption=(
                            f"🟢 **AI ART COMPLETED CLEANLY**\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🎨 **Style:** `{user_prompt}`\n"
                            f"🌌 *Engine: Flux Im2Img Tuan by Dominic*"
                        ),
                        reply_to_message_id=message.message_id
                    )
                    await bot.delete_message(message.chat.id, init_msg.message_id)
                else:
                    await bot.edit_message_text(
                        f"⚠️ **AI SERVER REJECTED:** Gateway returned HTTP `{response.status}`", 
                        message.chat.id, init_msg.message_id
                    )

    except Exception as e:
        await bot.edit_message_text(
            f"🛑 **CORE ENGINE EXCEPTION:**\n`{str(e)}`", 
            message.chat.id, init_msg.message_id
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏁 RUN BOT POLLING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
