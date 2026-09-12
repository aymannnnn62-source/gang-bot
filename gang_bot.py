import sqlite3
import time
import requests

# إعداد قاعدة البيانات وتخزين معلومات اللاعبين والعصابات
def init_db():
    conn = sqlite3.connect('gangs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            money INTEGER DEFAULT 1000,
            gang TEXT DEFAULT 'بدون عصابة',
            respect INTEGER DEFAULT 10
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# دالة لتسجيل أو جلب اللاعب
def get_player(user_id, username):
    conn = sqlite3.connect('gangs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    player = cursor.fetchone()
    if not player:
        cursor.execute('INSERT INTO players (user_id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
        player = cursor.fetchone()
    conn.close()
    return player

# التوكن الخاص ببوتك
TOKEN = "8301495628:AAFCmIlBJ5mPQ6-FsheRsOEfWf-iy940CPs"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def send_message(chat_id, text):
    url = URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def main():
    print("Bot is running and listening for updates...")
    last_update_id = 0
    while True:
        try:
            response = requests.get(URL + "getUpdates", params={"offset": last_update_id + 1, "timeout": 30})
            data = response.json()
            if "result" in data:
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_id = update["message"]["from"]["id"]
                        username = update["message"]["from"].get("first_name", "User")
                        text = update["message"]["text"]

                        # الأوامر الأساسية للبوت
                        if text == "/start":
                            get_player(user_id, username)
                            send_message(chat_id, f"🔥 أهلاً بك يا أسطورة {username} في لعبة حرب العصابات السحابية!\n\nاكتب /profile لعرض ملفك الشخصي أو /crime لتنفيذ عملية.")
                        
                        elif text == "/profile":
                            p = get_player(user_id, username)
                            send_message(chat_id, f"👤 الملف الشخصي:\n- الاسم: {p[1]}\n- الفلوس: ${p[2]}\n- العصابة: {p[3]}\n- الاحترام: {p[4]}")

                        elif text == "/crime":
                            p = get_player(user_id, username)
                            conn = sqlite3.connect('gangs.db')
                            cursor = conn.cursor()
                            cursor.execute('UPDATE players SET money = money + 500, respect = respect + 2 WHERE user_id = ?', (user_id,))
                            conn.commit()
                            conn.close()
                            send_message(chat_id, "💰 نجحت العملية ورجعت بغنيمة دسمة! +$500")

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
