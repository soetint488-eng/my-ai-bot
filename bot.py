import sys
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Token သတ်မှတ်ခြင်း
TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

# =====================================================================
# ၁။ /start Command ပို့လာလျှင် အသက်စစ်ဆေးမည့် ခလုတ်ပြခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Inline Buttons (နှိပ်လို့ရမယ့် ခလုတ်များ) ဆောက်ခြင်း
    keyboard = [
        [
            InlineKeyboardButton("✅ ဟုတ်ကဲ့၊ ၁၈ နှစ်ပြည့်ပါပြီ", callback_data='age_verified'),
            InlineKeyboardButton("❌ မပြည့်သေးပါ", callback_data='age_failed')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    warning_text = (
        "⚠️ **သတိပေးချက် / WARNING** ⚠️\n\n"
        "ဒီ Bot တွင် အသက် ၁၈ နှစ်အထက်သာ ကြည့်ရှုခွင့်ရှိသော အကြောင်းအရာများ ပါဝင်နိုင်ပါသည်။\n"
        "အသက် ၁၈ နှစ်မပြည့်သေးသူများ အသုံးမပြုရပါ။\n\n"
        "သင်သည် အသက် ၁၈ နှစ်ပြည့်ပြီးသူ ဖြစ်ပါသလား။"
    )
    
    await update.message.reply_text(text=warning_text, reply_markup=reply_markup, parse_mode="Markdown")

# =====================================================================
# ၂။ ခလုတ်များနှိပ်လိုက်သည့်အခါ အလုပ်လုပ်မည့် Function
# =====================================================================
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() # ခလုတ်နှိပ်တာ တုံ့ပြန်မှုရသွားအောင် အရင်လုပ်ခြင်း
    
    if query.data == 'age_failed':
        await query.edit_message_text(text="❌ စည်းကမ်းချက်အရ အသက်မပြည့်သေးသဖြင့် ဤ Bot ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    if query.data == 'age_verified':
        await query.edit_message_text(text="⏳ အတည်ပြုချက် အောင်မြင်သည်။ API သို့ ချိတ်ဆက်ပြီး ဓာတ်ပုံတောင်းဆိုနေပါသည်...")
        
        # --- API ချိတ်ဆက်သည့်အပိုင်း ---
        API_URL = "https://nodress.p.rapidapi.com/image"
        query_params = {'DeepStrip': 'Image'}
        headers = {
            'Content-Type': 'application/json',
            'x-rapidapi-host': 'nodress.p.rapidapi.com',
            'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
        }
        
        try:
            response = requests.get(API_URL, headers=headers, params=query_params)
            
            if response.status_code == 200:
                result = response.json()
                
                # တကယ်လို့ API က JSON ထဲမှာ 'url' ဆိုတဲ့ Key နဲ့ ပုံလင့်ခ် ပြန်ပေးတယ်ဆိုရင် -
                if "url" in result:
                    image_url = result["url"]
                    # User ဆီသို့ ဓာတ်ပုံတိုက်ရိုက်ပို့ပေးခြင်း
                    await query.message.reply_photo(photo=image_url, caption="📸 API မှ ရရှိလာသော ဓာတ်ပုံ ဖြစ်ပါသည်။")
                else:
                    # ပုံလင့်ခ်တိုက်ရိုက်မပါဘဲ text ပဲပါလာရင် ပြပေးဖို့
                    await query.message.reply_text(f"API Response: {str(result)}")
                    
            else:
                await query.message.reply_text(f"❌ API Error တက်သွားသည်။ Status Code: {response.status_code}")
                
        except Exception as e:
            await query.message.reply_text(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

# =====================================================================
# ၃။ Bot စတင်ပတ်မည့် ပင်မနေရာ
# =====================================================================
def main() -> None:
    # Application ဆောက်ခြင်း
    application = Application.builder().token(TOKEN).build()

    # Handler များ ထည့်သွင်းခြင်း
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    # Bot ကို စတင် Run ခြင်း
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
