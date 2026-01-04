import telebot
from telebot import types
import requests
import httpx
from io import BytesIO
from groq import Groq
import re
import random
import json

# ========= التوكنات =========
TOKEN = OKEN = "8587570928:AAH91rHjGR11vCyp5LXSjx3G15n_ZAbKk4o"
GROQ_API_KEY = "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"
REMOVEBG_API_KEY = "u2CvqkZJkjEzD8GAjFXTfqbh"

bot = telebot.TeleBot(TOKEN)
http_client = httpx.Client(timeout=60)
client = Groq(api_key=GROQ_API_KEY, http_client=http_client)

user_mode = {}
user_histories = {}

# ========= الاشتراك الإجباري =========
FORCED_CHANNELS = {}  # {chat_id: link} - يضاف من المطور

DEV_ID = 8428121812  # ايدي المطور

# ========= ملف الزخارف =========
DECORATIONS_FILE = "/storage/emulated/0/Download/Telegram/hh.json"

def load_fonts():
    try:
        with open(DECORATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [str(item) for item in data if str(item).strip()]
    except:
        return ["أُخِـٌـٍْـٍِبِـِْـٍْـٌـٍُـٍٍبُ"]

fonts = load_fonts()

def stylize(text, font):
    base_letters = "abcdefghijklmnopqrstuvwxyz"
    table = str.maketrans(
        base_letters + base_letters.upper(),
        font + font.upper()
    )
    return text.translate(table)

def check_subscription(user_id):
    if not FORCED_CHANNELS:
        return True
    for channel_id in FORCED_CHANNELS.keys():
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked", "banned"]:
                return False
        except:
            return False
    return True

def subscription_keyboard():
    markup = types.InlineKeyboardMarkup()
    for link in FORCED_CHANNELS.values():
        markup.add(types.InlineKeyboardButton("اشترك في القناة", url=link))
    markup.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub"))
    return markup

# ========= Start =========
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    if user_id == DEV_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            "💬 تحدث مع الذكاء",
            "🖼️ إنشاء صورة",
            "🧼 إزالة خلفية",
            "✨ زخرف لي الاسم"
        )
        dev_markup = types.InlineKeyboardMarkup()
        dev_markup.add(types.InlineKeyboardButton("إضافة قناة اشتراك إجباري ➕", callback_data="add_channel"))
        bot.send_message(message.chat.id, "مرحباً يا مطور 👨‍💻\nاختار من القائمة:", reply_markup=markup)
        bot.send_message(message.chat.id, "إدارة الاشتراك الإجباري:", reply_markup=dev_markup)
        return

    if not check_subscription(user_id):
        bot.send_message(message.chat.id, 
            "❌ عذراً عزيزي، يلزمك الاشتراك في القنوات التالية لاستخدام البوت:\n\n"
            "بعد الاشتراك اضغط على 'تحقق من الاشتراك'", 
            reply_markup=subscription_keyboard())
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        "💬 تحدث مع الذكاء",
        "🖼️ إنشاء صورة",
        "🧼 إزالة خلفية",
        "✨ زخرف لي الاسم"
    )
    bot.send_message(message.chat.id, "🎉 مرحباً بك!\nاختار من القائمة:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data == "add_channel")
def add_channel(call):
    if call.from_user.id != DEV_ID:
        bot.answer_callback_query(call.id, "غير مسموح لك")
        return
    
    msg = bot.send_message(call.message.chat.id, "🔗 ارسل رابط القناة أو المجموعة اللي عايز تضيفها للاشتراك الإجباري:")
    bot.register_next_step_handler(msg, process_new_channel)

def process_new_channel(message):
    if message.from_user.id != DEV_ID:
        return
    
    link = message.text.strip()
    if "t.me" not in link:
        bot.send_message(message.chat.id, "❌ الرابط غير صحيح، لازم يكون t.me/... ")
        return
    
    # استخراج chat_id
    try:
        if link.startswith("https://t.me/"):
            username = link.split("https://t.me/")[1].split("?")[0]
        else:
            username = link.split("t.me/")[1].split("?")[0]
        chat_id = f"@{username}"
    except:
        bot.send_message(message.chat.id, "❌ فشل استخراج الرابط")
        return
    
    FORCED_CHANNELS[chat_id] = link
    bot.send_message(message.chat.id, f"✅ تم إضافة القناة بنجاح:\n{link}\n\nالآن كل مستخدم لازم يشترك فيها.")

    bot.send_message(message.chat.id, "⚠️ تأكد إنك رفعت البوت أدمن في القناة عشان يقدر يتحقق من الاشتراك.")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.edit_message_text("✅ تم التحقق من اشتراكك بنجاح!\nالآن تقدر تستخدم البوت.", call.message.chat.id, call.message.message_id)
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(
            "💬 تحدث مع الذكاء",
            "🖼️ إنشاء صورة",
            "🧼 إزالة خلفية",
            "✨ زخرف لي الاسم"
        )
        bot.send_message(call.message.chat.id, "اختار من القائمة:", reply_markup=kb)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد في جميع القنوات", show_alert=True)

# ========= اختيار =========
@bot.message_handler(func=lambda m: m.text in [
    "💬 تحدث مع الذكاء",
    "🖼️ إنشاء صورة",
    "🧼 إزالة خلفية",
    "✨ زخرف لي الاسم"
])
def choose_mode(message):
    if message.from_user.id != DEV_ID and not check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, "❌ يلزمك الاشتراك أولاً", reply_markup=subscription_keyboard())
        return

    modes = {
        "💬 تحدث مع الذكاء": "chat",
        "🖼️ إنشاء صورة": "image",
        "🧼 إزالة خلفية": "removebg",
        "✨ زخرف لي الاسم": "decorate"
    }
    user_mode[message.from_user.id] = modes[message.text]
    bot.send_message(message.chat.id, "⬇️ ارسل المطلوب")

# ========= شات =========
@bot.message_handler(func=lambda m: user_mode.get(m.from_user.id) == "chat")
def chat_ai(message):
    if message.from_user.id != DEV_ID and not check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, "❌ يلزمك الاشتراك", reply_markup=subscription_keyboard())
        return

    uid = message.from_user.id
    if uid not in user_histories:
        user_histories[uid] = [{"role": "system", "content": "رد عربي مختصر وواضح"}]
    user_histories[uid].append({"role": "user", "content": message.text})
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_histories[uid],
            max_tokens=300
        )
        reply = res.choices[0].message.content
        user_histories[uid].append({"role": "assistant", "content": reply})
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطأ Groq:\n{e}")

# ========= إنشاء صورة =========
@bot.message_handler(func=lambda m: user_mode.get(m.from_user.id) == "image")
def generate_image(message):
    if message.from_user.id != DEV_ID and not check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, "❌ يلزمك الاشتراك", reply_markup=subscription_keyboard())
        return

    prompt = message.text.strip()
    wait = bot.send_message(message.chat.id, "🎨")
    try:
        if re.search(r'[\u0600-\u06FF]', prompt):
            tr = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Translate Arabic to English image prompt only"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60
            )
            prompt = tr.choices[0].message.content.strip()
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
        r = requests.get(url, timeout=120)
        bot.send_photo(message.chat.id, BytesIO(r.content))
        bot.delete_message(message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("❌ فشل إنشاء الصورة", message.chat.id, wait.message_id)

# ========= إزالة خلفية =========
@bot.message_handler(content_types=["photo"])
def remove_bg(message):
    uid = message.from_user.id
    if user_mode.get(uid) != "removebg":
        return
    if uid != DEV_ID and not check_subscription(uid):
        bot.send_message(message.chat.id, "❌ يلزمك الاشتراك", reply_markup=subscription_keyboard())
        return

    wait = bot.send_message(message.chat.id, "⏳")
    try:
        file = bot.get_file(message.photo[-1].file_id)
        img_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        r = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            data={"image_url": img_url, "size": "auto"},
            headers={"X-Api-Key": REMOVEBG_API_KEY},
            timeout=120
        )
        bot.send_photo(message.chat.id, r.content)
        bot.delete_message(message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("❌ فشل إزالة الخلفية", message.chat.id, wait.message_id)
    user_mode[uid] = None

# ========= زخرفة =========
@bot.message_handler(func=lambda m: user_mode.get(m.from_user.id) == "decorate")
def decorate_name(message):
    if message.from_user.id != DEV_ID and not check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, "❌ يلزمك الاشتراك", reply_markup=subscription_keyboard())
        return

    name = message.text.strip()
    if not name:
        return
    styled_list = []
    fonts_copy = fonts.copy()
    random.shuffle(fonts_copy)
    for font in fonts_copy[:10]:
        styled_list.append(stylize(name, font))
    response = f"✨ {len(styled_list)} زخارف مختلفة لـ \"{name}\":\n\n"
    for styled in styled_list:
        response += f"`{styled}`\n\n"
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# ========= تشغيل =========
print("✅ البوت شغال مع اشتراك إجباري + زر إضافة قناة للمطور فقط")
bot.infinity_polling()
