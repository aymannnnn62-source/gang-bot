import os
import random
import telebot
from telebot import types

# جلب توكن البوت من متغيرات البيئة أو وضعه مباشرة
TOKEN = os.getenv("BOT_TOKEN", "حط_التوكن_حقك_هنا_اذا_ما_استخدمت_البيئة")
bot = telebot.TeleBot(TOKEN)

# قاعدة بيانات مؤقتة لتخزين بيانات اللاعبين
# المفتاح هو (user_id)
players = {}

def get_player(user_id, username):
    if user_id not in players:
        players[user_id] = {
            "name": username or "مجهول",
            "money": 1000,
            "respect": 10,
            "gang": "بدون عصابة",
            "weapons": [],
            "cars": [],
            "last_crime": 0,
            "last_daily": 0,
            "last_work": 0
        }
    return players[user_id]

# 1. أمر البداية /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    p = get_player(user.id, user.first_name)
    text = (
        f"🔥 أهلاً بك يا أسطورة {p['name']} في عالم حرب العصابات السحابية!\n\n"
        "البوت الحين شغال 24 ساعة ويدعم المجموعات واللعب الجماعي.\n"
        "📜 **الأوامر المتاحة:**\n"
        "• /profile - عرض ملفك الشخصي وعطادك\n"
        "• /crime - تنفيذ جريمة وسرقات لكسب المال\n"
        "• /shop - فتح السوق السوداء للأسلحة والسيارات\n"
        "• /buy [الرقم] - شراء سلاح أو سيارة\n"
        "• /leaderboard - قائمة أزعماء العصابات وأغناهم\n"
        "• /rob [@معرف] - محاولة سرقة لاعب آخر بالجروب\n"
        "• /daily - استلام الراتب والمكافأة اليومية\n"
        "• /work - إرسال أعضاء عصابتك لأعمال حرة\n"
        "• /gang [اسم العصابة] - إنشاء أو الانضمام لعصابة"
    )
    bot.reply_to(message, text)

# 2. الملف الشخصي /profile
@bot.message_handler(commands=['profile'])
def show_profile(message):
    user = message.from_user
    p = get_player(user.id, user.first_name)
    weapons_list = ", ".join(p["weapons"]) if p["weapons"] else "لا يوجد"
    cars_list = ", ".join(p["cars"]) if p["cars"] else "لا يوجد"
    
    text = (
        f"👤 **الملف الشخصي الإجرامي:**\n"
        f"• الاسم: {p['name']}\n"
        f"• الفلوس: ${p['money']}\n"
        f"• الاحترام: {p['respect']}\n"
        f"• العصابة: {p['gang']}\n"
        f"• الأسلحة: {weapons_list}\n"
        f"• السيارات: {cars_list}"
    )
    bot.reply_to(message, text)

# 3. تنفيذ جريمة /crime
@bot.message_handler(commands=['crime'])
def do_crime(message):
    user = message.from_user
    p = get_player(user.id, user.first_name)
    
    success = random.choice([True, True, False]) # نسبة نجاح 66%
    if success:
        earned = random.randint(300, 900)
        p["money"] += earned
        p["respect"] += 2
        bot.reply_to(message, f"💰 نجحت العملية ورجعت بغينمة دسمة! +${earned}")
    else:
        lost = random.randint(150, 400)
        p["money"] = max(0, p["money"] - lost)
        bot.reply_to(message, f"🚨 فشلت العملية وقبضت عليك الشرطة! خسرت -${lost}")

# 4. السوق السوداء /shop
@bot.message_handler(commands=['shop'])
def show_shop(message):
    shop_text = (
        "🛒 **السوق السوداء لتطوير العتاد:**\n\n"
        "🔫 **الأسلحة:**\n"
        "1. مسدس بيريتا - السعر: $1500 (أمر: `/buy 1`)\n"
        "2. رشاش كلاشنكوف - السعر: $4000 (أمر: `/buy 2`)\n\n"
        "🚗 **السيارات:**\n"
        "3. سيارة ددسن غمارة - السعر: $3000 (أمر: `/buy 3`)\n"
        "4. هيلكات رياضية - السعر: $10000 (أمر: `/buy 4`)"
    )
    bot.reply_to(message, shop_text)

# 5. الشراء /buy
@bot.message_handler(commands=['buy'])
def buy_item(message):
    user = message.from_user
    p = get_player(user.id, user.first_name)
    args = message.text.split()
    
    if len(args) < 2:
        bot.reply_to(message, "⚠️ يا أسطورة حدد رقم السلعة. مثال: `/buy 1`")
        return
    
    item = args[1]
    items_data = {
        "1": {"name": "مسدس بيريتا", "type": "weapon", "price": 1500},
        "2": {"name": "رشاش كلاشنكوف", "type": "weapon", "price": 4000},
        "3": {"name": "ددسن غمارة", "type": "car", "price": 3000},
        "4": {"name": "هيلكات رياضية", "type": "car", "price": 10000},
    }
    
    if item not in items_data:
        bot.reply_to(message, "❌ هذه السلعة غير موجودة في السوق السوداء.")
        return
        
    target = items_data[item]
    if p["money"] < target["price"]:
        bot.reply_to(message, f"❌ فلوسك ما تكفي! تحتاج ${target['price']} لشراء {target['name']}.")
        return
        
    p["money"] -= target["price"]
    if target["type"] == "weapon":
        p["weapons"].append(target["name"])
    else:
        p["cars"].append(target["name"])
        
    bot.reply_to(message, f"🎉 مبروك! تم شراء {target['name']} بنجاح وانضافت لعزبتك.")

# 6. قائمة الزعماء /leaderboard
@bot.message_handler(commands=['leaderboard'])
def leaderboard(message):
    if not players:
        bot.reply_to(message, "📊 مافي لاعبين مسجلين للحين.")
        return
        
    sorted_players = sorted(players.values(), key=lambda x: x["money"], reverse=True)
    text = "🏆 **قائمة زعماء العصابات (الأثرياء):**\n\n"
    for idx, pl in enumerate(sorted_players[:5], 1):
        text += f"{idx}. {pl['name']} - 💰 ${pl['money']} (احترام: {pl['respect']})\n"
        
    bot.reply_to(message, text)

# 7. سرقة لاعب آخر /rob
@bot.message_handler(commands=['rob'])
def rob_player(message):
    bot.reply_to(message, "⚠️ ميزة السرقة بين الأعضاء قيد التحديث الكبير، انتظرها قريباً!")

# 8. الراتب اليومي /daily
@bot.message_handler(commands=['daily'])
def daily_reward(message):
    user = message.from_user
    p = get_player(user.id, user.first_name)
    p["money"] += 1000
    bot.reply_to(message, "🎁 استلمت راتب العصابة اليومي بنجاح: +$1000!")

# 9. العمل /work
@bot.message_handler(commands=['work'])
def work_job(message):
    user = message.from_user
    p = get_player(user.id, user.first_name)
    earned = random.randint(100, 350)
    p["money"] += earned
    bot.reply_to(message, f"🛠️ اشتغلت في أعمال العصابة ورجعت بمبلغ: +${earned}")

# 10. العصابة /gang
@bot.message_handler(commands=['gang'])
def manage_gang(message):
    args = message.text.split(maxsplit=1)
    user = message.from_user
    p = get_player(user.id, user.first_name)
    
    if len(args) < 2:
        bot.reply_to(message, f"🏷️ عصابتك الحالية: {p['gang']}\nللإنشاء أو الانضمام اكتب: `/gang اسم_العصابة`")
        return
        
    gang_name = args[1]
    p["gang"] = gang_name
    bot.reply_to(message, f"🔥 يا أسطورة! صرت الآن منسوباً لعصابة: **{gang_name}**")

print("Bot is running...")
bot.infinity_polling()
