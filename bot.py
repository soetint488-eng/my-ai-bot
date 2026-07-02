import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, executor, types

# 📝 Logging စနစ်ဖွင့်ခြင်း (Render Log စစ်ဆေးရလွယ်ကူစေရန်)
logging.basicConfig(level=logging.INFO)

# 🔑 ကိုကိုပေးထားသည့် Bot Token အသစ်ကို တိုက်ရိုက်သတ်မှတ်ခြင်း
BOT_TOKEN = "8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 ၁။ START & HELP COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "🎨 **DOMINIC AI ANIME ART GENERATOR**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **Developer:** `Dominic`\n"
        "🟢 **Core Status:** `READY`\n\n"
        "📝 **အသုံးပြုနည်းလမ်း:**\n"
        "ရိုက်ရန် -> `/generate [ပုံဖော်လိုသည့် စာသား]`\n"
        "✨ **ဥပမာ:** `/generate cyberpunk neon cat girl`\n\n"
        "📊 *Stable Diffusion Meinamix V9 Engine တပ်ဆင်ထားသည်။*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🌌 *System fully localized under Shine thu ya aung.*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 ၂။ AI IMAGE GENERATION ENGINE (OMNIINFER API)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['generate'])
async def generate_ai_image(message: types.Message):
    # User ရိုက်လိုက်သည့် Prompt ကို ဖတ်ယူခြင်း
    user_prompt = message.get_args()
    if not user_prompt:
        await message.answer(
            "💡 **Format မှားယွင်းနေပါသည်။**\n"
            "📝 အသုံးပြုပုံ: `/generate [ပုံဖော်လိုသည့် အကြောင်းအရာ]`\n"
            "🔍 ဥပမာ: `/generate cute anime girl laughing`"
        )
        return
        
    init_msg = await message.answer("🎨 **AI IS PAINTING YOUR IMAGINATION... PLEASE WAIT...**")
    
    # Omniinfer API Setup
    url = "https://omniinfer.p.rapidapi.com/v2/txt2img"
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'omniinfer.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da' # ကိုကို့ RapidAPI Key
    }
    
    # ကိုကိုပေးထားသည့် CURL parameters များကို Payload အဖြစ် တည်ဆောက်ခြင်း
    payload = {
        "prompt": f"{user_prompt}, (Studio ghibli), nekopara, highly detailed, modern anime, detailed portrait, vibrant, kyoto animation, elegant highly detailed, digital painting, artstation pixiv cyberpunk, sharp focus, japan anime",
        "negative_prompt": "nsfw, watermark, facial distortion, lip deformity, redundant background, extra fingers, Abnormal eyesight, ((multiple faces)), ((Tongue protruding)), ((extra arm)), extra hands, extra fingers, deformity, missing legs, missing toes, missin hand, missin fingers, (painting by bad-artist-anime:0.9), (painting by bad-artist:0.9), watermark, text, error, blurry, jpeg artifacts, cropped, worst quality, low quality, normal quality, signature, username, artist name, bad anatomy",
        "sampler_name": "Euler a",
        "batch_size": 1,
        "n_iter": 1,
        "steps": 20,
        "cfg_scale": 7,
        "seed": -1,
        "height": 1024,
        "width": 768,
        "model_name": "meinamix_meinaV9.safetensors"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=45) as response:
                if response.status == 200:
                    res_data = await response.json()
                    
                    # Note: RapidAPI အချို့သည် Task ID ပြန်ပေးတတ်ပြီး အချို့က Image URL တန်းပေးတတ်ပါသည်။
                    # ဤနေရာတွင် ရလဒ်ထဲမှ URL သို့မဟုတ် Base64 ဆွဲထုတ်ရန် ကြိုးစားခြင်း
                    status_code = res_data.get("code")
                    data_body = res_data.get("data", {})
                    
                    # ပုံထွက်လာသည့် သော့ချက်ကို စစ်ဆေးခြင်း
                    image_url = data_body.get("url") or data_body.get("image") or res_data.get("url")
                    
                    if image_url:
                        await bot.send_photo(
                            chat_id=message.chat.id, 
                            photo=image_url, 
                            caption=f"🟢 **AI ART COMPLETED**\n━━━━━━━━━━━━━━━━━━━━\n🎯 **Prompt:** `{user_prompt}`\n🌌 *Engine: Meinamix V9 by Dominic*"
                        )
                        await bot.delete_message(message.chat.id, init_msg.message_id)
                    else:
                        # ပုံတန်းမကျဘဲ Task Queued ဖြစ်သွားပါက Response ကို စာဖြင့်ပြရန်
                        await bot.edit_message_text(f"📥 **API Response (No Direct Image):**\n`{str(res_data)}`", message.chat.id, init_msg.message_id)
                else:
                    await bot.edit_message_text(f"⚠️ **SERVER REJECTED:** RapidAPI returned HTTP `{response.status}`", message.chat.id, init_msg.message_id)
                    
    except Exception as e:
        await bot.edit_message_text(f"🛑 **CORE ENGINE EXCEPTION:**\n`{str(e)}`", message.chat.id, init_msg.message_id)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ BOT PROCESS TRIGGER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    print("--- Dominic AI Image Bot Engine Online ---")
    executor.start_polling(dp, skip_updates=True)
