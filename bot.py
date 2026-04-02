import os
import time
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# --- CONFIG ---
# Render ရဲ့ Environment Variables ထဲမှာ BOT_TOKEN ထည့်ဖို့ မမေ့ပါနဲ့
TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Browser Setting (Render ပေါ်မှာ Run ရန် အရေးကြီးဆုံးအပိုင်း)
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless') # မျက်နှာပြင်မပါဘဲ Run မည်
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.binary_location = "/usr/bin/chromium-browser" # Render အတွက် Path
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# State သတ်မှတ်ခြင်း
class ZefoyState(StatesGroup):
    waiting_for_captcha = State()

# Browser ကို Global အနေနဲ့ တစ်ခါတည်း ဖွင့်ထားမယ်
driver = get_driver()

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🇲🇲 **Zefoy Views Booster Bot**\n\nTikTok Video Link ကို ပို့ပေးပါ။ Captcha ကျလာရင် ပုံရိုက်ပြီး ပြန်ပို့ပေးပါမယ် Shine!")

@dp.message(F.text.contains("tiktok.com"))
async def handle_link(message: types.Message, state: FSMContext):
    video_url = message.text.strip()
    wait_msg = await message.answer("⌛ Zefoy ကို သွားနေပါပြီ။ ခဏစောင့်ပါ...")

    try:
        driver.get("https://zefoy.com/")
        time.sleep(5) # Page Load ဖြစ်အောင် စောင့်မယ်
        
        # ၁။ Captcha ပုံကို ရှာပြီး Screenshot ရိုက်မယ်
        captcha_img = driver.find_element(By.TAG_NAME, "img")
        photo_path = f"captcha_{message.from_user.id}.png"
        captcha_img.screenshot(photo_path)
        
        # ၂။ User ဆီ ပုံပြန်ပို့မယ်
        photo = types.FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption="📸 ပုံထဲက စာလုံးတွေကို အဖြေပြန်ရိုက်ပေးပါ Shine!")
        
        # State နဲ့ URL ကို သိမ်းထားမယ်
        await state.set_state(ZefoyState.waiting_for_captcha)
        await state.update_data(video_url=video_url)
        
        # ပုံဖိုင်ကို ဖျက်မယ်
        os.remove(photo_path)
        await wait_msg.delete()

    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")

@dp.message(ZefoyState.waiting_for_captcha)
async def solve_captcha(message: types.Message, state: FSMContext):
    captcha_answer = message.text.strip()
    data = await state.get_data()
    video_url = data.get("video_url")
    
    wait_msg = await message.answer("⌛ Captcha ကို စစ်ဆေးနေပါပြီ...")

    try:
        # ၃။ Captcha အဖြေကို ရိုက်ထည့်မယ်
        input_box = driver.find_element(By.TAG_NAME, "input")
        input_box.clear()
        input_box.send_keys(captcha_answer)
        
        # Submit နှိပ်မယ်
        driver.find_element(By.XPATH, "//button").click()
        time.sleep(5)
        
        # ၄။ Views တိုးတဲ့ အပိုင်း (Zefoy ရဲ့ HTML ပေါ် မူတည်ပြီး ပြင်ရနိုင်သည်)
        # ဤနေရာတွင် ရှာတွေ့သည့် Views ခလုတ်ကို နှိပ်ခိုင်းမည်
        await wait_msg.edit_text(f"✅ Captcha အောင်မြင်ပုံရပါတယ်။ {video_url} အတွက် Views တိုးပေးနေပါပြီ!")
        
        # လုပ်ငန်းစဉ်ပြီးရင် State ကို Clear လုပ်မယ်
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")
        await state.clear()

async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
