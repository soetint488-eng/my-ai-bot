import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from aiohttp import web

# --- CONFIG ---
# သင့် Bot Token ကို ဒီမှာ ထည့်ပါ
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# လက်ရှိ Folder ထဲမှာပဲ Captcha ပုံကို သိမ်းပါမယ်
current_dir = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_PATH = os.path.join(current_dir, "captcha.png")

logging.basicConfig(level=logging.INFO)

# Global Driver Variable
driver = None

class BotStates(StatesGroup):
    waiting_for_captcha = State()

# --- RENDER WEB SERVER ---
async def handle(request):
    return web.Response(text="Zefoy Captcha Bot is Live!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- SELENIUM BROWSER INIT ---
def init_browser():
    global driver
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Render မှာ Screen မရှိလို့ သုံးရမည်
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Render ပေါ်မှာ Chrome လမ်းကြောင်းကို ရှာရန်
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin:
        chrome_options.binary_location = chrome_bin

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# --- BOT HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Zefoy Automation Bot** မှ ကြိုဆိုပါတယ်!\n\n"
        "စတင်ရန် /get_captcha ကို နှိပ်ပါဗျ။\n"
        "ပုံရလာရင် စာလုံးကို ရိုက်ထည့်ပေးရမှာ ဖြစ်ပါတယ်။",
        parse_mode="Markdown"
    )

@dp.message(Command("get_captcha"))
async def get_captcha(message: types.Message, state: FSMContext):
    global driver
    wait_msg = await message.answer("⏳ Zefoy ကို ဖွင့်နေပါတယ်... (၅ စက္ကန့်ခန့် စောင့်ပါ)")
    
    try:
        if driver is None:
            init_browser()
        
        driver.get("https://zefoy.com/")
        await asyncio.sleep(5) # Page Load ဖြစ်အောင် စောင့်ခြင်း
        
        # Screenshot ရိုက်ခြင်း
        driver.save_screenshot(SCREENSHOT_PATH)
        
        # ပုံကို Telegram သို့ ပို့ခြင်း
        if os.path.exists(SCREENSHOT_PATH):
            photo = types.FSInputFile(SCREENSHOT_PATH)
            await bot.send_photo(
                message.chat.id, 
                photo, 
                caption="📸 Captcha ပုံ ရပါပြီ။ စာလုံးကို ရိုက်ထည့်ပေးပါဗျ။"
            )
            await state.set_state(BotStates.waiting_for_captcha)
        else:
            await message.answer("❌ Screenshot ရိုက်လို့ မရပါဘူးဗျ။")
            
        await wait_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer(f"❌ Error တက်သွားပါတယ်: {str(e)}")

@dp.message(BotStates.waiting_for_captcha)
async def solve_captcha(message: types.Message, state: FSMContext):
    global driver
    captcha_text = message.text
    
    try:
        # Zefoy ၏ Captcha Input Box ကို ရှာပြီး စာရိုက်ထည့်ခြင်း
        # Zefoy structure အရ ပထမဆုံးတွေ့တဲ့ input သည် captcha input ဖြစ်တတ်ပါသည်
        input_box = driver.find_element(By.TAG_NAME, "input")
        input_box.clear()
        input_box.send_keys(captcha_text)
        
        # Submit Button ကို နှိပ်ခြင်း (Zefoy တွင် Enter ခေါက်ရပါသည်)
        from selenium.webdriver.common.keys import Keys
        input_box.send_keys(Keys.ENTER)
        
        await asyncio.sleep(3)
        
        # အောင်မြင်မှု ရှိမရှိ စစ်ဆေးရန် SS တစ်ချက် ထပ်ရိုက်ပြခြင်း
        driver.save_screenshot(SCREENSHOT_PATH)
        photo = types.FSInputFile(SCREENSHOT_PATH)
        await bot.send_photo(message.chat.id, photo, caption=f"✅ '{captcha_text}' ကို ထည့်ပြီးပါပြီ။ Result ကို ကြည့်ပါဗျ။")
        
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ အမှားတက်သွားပါတယ်: {str(e)}")

async def main():
    init_db_dummy = True # Database မလိုသေးသဖြင့် dummy ထည့်ထားသည်
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
