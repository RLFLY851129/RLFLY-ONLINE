from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import html
import json
import os
import sqlite3
import threading
import time
import sys
import subprocess

# Install missing dependencies automatically
def install_package(package, module=None):
    module = module or package
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package
        ])

install_package("requests")
install_package("pyTelegramBotAPI", "telebot")

import requests
import telebot
from telebot import types

# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN", "8861694651:AAHbPNcvoAbOfqPK0X9X4iw5kyd4_QAnZ7g"
).strip()

if not BOT_TOKEN:
  raise RuntimeError(
      "BOT_TOKEN missing. Hosting Environment Variables me BOT_TOKEN set karo."
  )

ADMIN_ID = 6228720365
DEFAULT_SECOND_ADMIN = 2687964335

DAILY_CREDITS = 5

SUPPORT_USERNAME = "@DEVILRAHUL_OP"
TELEGRAM_CHANNEL = "@RLFLY_OFFICIAL"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ============================================================
# PRIVACY 
# ============================================================
PROTECTED_NUMBERS = {
    "7631629772",
    "6200633714",
    "9279646142",
    "6290194954",
    "8877029235"
}

PROTECTED_TG_IDS = {
    "6228720365",
    "5144696186",
    "6359967173"
}

# ============================================================
# CHANNELS & OFFICIAL GROUP
# ============================================================

CHANNELS = [
    "@RLFLY_OFFICIAL",
    -1004365897296,
    -1003636558668,
]

CHANNEL_LINKS = [
    "https://t.me/RLFLY_OFFICIAL",
    "https://t.me/+L7mMEIMtzdxiNmU1",
    "https://t.me/+mtsPKbT2YW1jMTJi",
]

OFFICIAL_GROUP_LINK = "https://t.me/+rpX-PK5VOb83YzJl"
WARNINGS_FILE = "warnings.json"

# ============================================================
# PUBLIC API (Updated)
# ============================================================
MOBILE_API = "https://api.trxedition.shop/api.php?number="

AADHAAR_API = "https://api.trxedition.shop/aadhaar?value="

VEHICLE_API = "https://devilswillrise.kotakmahindrabank9090.workers.dev/vahan?key=ALPHA_UNLIMITED&vechile="

VEHICLE2_API = "https://api.trxedition.shop/vehiclenum?number="

TG2NUM_API = "https://devilswillrise.kotakmahindrabank9090.workers.dev/tg-lookup?key=ALPHA_UNLIMITED&id="

PAN_API_BASE = "https://orissosint-pan.antideploy.app/pan?pan="
PAN_API_KEY = "WKM"

GST_API = "https://veerulookup.onrender.com/search_gst?gst="
IFSC_API = "https://ifsc.razorpay.com/"
PINCODE_API = "https://pincode-ng.vercel.app/lookup?pincode="

# ============================================================
# AUTO DELETE WORKER THREAD
# ============================================================


def schedule_message_deletion(chat_id, message_ids, delay=120):
  """Background thread jo 2 mins (120 secs) baad messages delete kar deta hai"""

  def delete_job():
    time.sleep(delay)
    for msg_id in message_ids:
      try:
        bot.delete_message(chat_id, msg_id)
      except Exception:
        pass

  threading.Thread(target=delete_job, daemon=True).start()
# ============================================================
# HELPER / JSON FORMATTING FUNCTIONS & WARNINGS
# ============================================================


def load_warnings():
  if not os.path.exists(WARNINGS_FILE):
    return {}
  try:
    with open(WARNINGS_FILE, "r") as f:
      return json.load(f)
  except:
    return {}


def save_warnings(data):
  with open(WARNINGS_FILE, "w") as f:
    json.dump(data, f, indent=4)
def sanitize_json(obj):
    # Faltu keys aur branding ko remove karne ke liye
    remove_keys = {
        "_brand",
        "api",
        "_powered_by",
        "developer",
        "developer_message",
        "developer_tag",
        "author",
        "made_by",
        "creator",
        "credits",
        "credit",
        "powered_by",
        "owner",
        "dev",
        "plan",
        "cost",
        "usage",
        "source",
        "join",
        "support",
        "note",
        "pricing_info",
        "pricing",
        "contact",
        "api_provider",
        "data_source",
        "service",
        "valid_from",
        "expires_at",
        "normalized",
        "mobile_norm",
        "brand",
        "channel",
        "_top_branding",
        "_meta",
        "_middle_branding",
        "_info",
        "rate_limit",
        "_watermark",
        "_sig",
        "success",
        "found",
        "count",
        "_b"
    }

    if isinstance(obj, dict):
        clean = {}

        for k, v in obj.items():
            if str(k).lower() in remove_keys:
                continue

            cleaned_val = sanitize_json(v)
            if cleaned_val is not None:
                clean[k] = cleaned_val

        return clean

    elif isinstance(obj, list):
        return [sanitize_json(i) for i in obj if sanitize_json(i) is not None]

    return obj



def pretty_json_html(obj):
  try:
    data = sanitize_json(obj)
    s = json.dumps(data, indent=4, ensure_ascii=False)
  except Exception:
    s = str(obj)
  return f'<pre><code class="language-json">{html.escape(s)}</code></pre>'


def send_long_message(chat_id, text, reply_to=None, mode="HTML"):
  MAX = 3800
  parts = [text[i : i + MAX] for i in range(0, len(text), MAX)]
  sent_ids = []
  for i, part in enumerate(parts):
    try:
      if i == 0 and reply_to:
        msg = bot.send_message(
            chat_id, part, parse_mode=mode, reply_to_message_id=reply_to
        )
      else:
        msg = bot.send_message(chat_id, part, parse_mode=mode)
      sent_ids.append(msg.message_id)
    except Exception:
      break
  return sent_ids


# ============================================================
# DATABASE & SETTINGS
# ============================================================

DB_FILE = "bot.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    credits INTEGER DEFAULT 5,
    premium INTEGER DEFAULT 0,
    allowed_private INTEGER DEFAULT 0,
    joined_at INTEGER,
    last_reset TEXT,
    premium_expires INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)
""")

db.commit()

# Ensure default admins exist in DB
try:
  cursor.execute(
      "INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (ADMIN_ID,)
  )
  cursor.execute(
      "INSERT OR IGNORE INTO admins (user_id) VALUES (?)",
      (DEFAULT_SECOND_ADMIN,),
  )
  db.commit()
except Exception:
  pass

try:
  cursor.execute(
      "ALTER TABLE users ADD COLUMN premium_expires INTEGER DEFAULT 0"
  )
  db.commit()
except Exception:
  pass


def is_admin(user_id):
  if user_id == ADMIN_ID or user_id == DEFAULT_SECOND_ADMIN:
    return True
  cursor.execute("SELECT user_id FROM admins WHERE user_id=?", (user_id,))
  return cursor.fetchone() is not None


# Maintenance Helpers
def is_maintenance_mode():
  cursor.execute("SELECT value FROM settings WHERE key='maintenance'")
  row = cursor.fetchone()
  return row is not None and row[0] == "1"


def set_maintenance_mode(status: bool):
  val = "1" if status else "0"
  cursor.execute(
      "INSERT OR REPLACE INTO settings (key, value) VALUES ('maintenance', ?)",
      (val,),
  )
  db.commit()


# ============================================================
# DATE / DAILY RESET — INDIA TIME
# ============================================================

IST = ZoneInfo("Asia/Kolkata")


def today_date():
    return datetime.now(IST).strftime("%Y-%m-%d")


def reset_daily_credits(user_id):
    today = today_date()

    try:
        cursor.execute(
            "SELECT last_reset FROM users WHERE user_id=?",
            (user_id,)
        )

        row = cursor.fetchone()

        if not row:
            return

        last_reset = row[0]

        if last_reset != today:
            cursor.execute(
                """
                UPDATE users
                SET credits=?, last_reset=?
                WHERE user_id=?
                """,
                (DAILY_CREDITS, today, user_id)
            )

            db.commit()

    except Exception as e:
        print("[USER CREDIT RESET ERROR]", e)


# ============================================================
# AUTOMATIC DAILY CREDIT RESET WORKER
# ============================================================

def reset_all_daily_credits():
    today = today_date()

    try:
        with sqlite3.connect(DB_FILE, timeout=30) as conn:
            cur = conn.cursor()

            cur.execute(
                """
                UPDATE users
                SET credits=?, last_reset=?
                WHERE last_reset IS NULL
                   OR last_reset != ?
                """,
                (
                    DAILY_CREDITS,
                    today,
                    today
                )
            )

            changed = cur.rowcount
            conn.commit()

        return changed

    except Exception as e:
        print("[ALL USERS CREDIT RESET ERROR]", e)
        return 0


def daily_credit_reset_worker():

    print("[CREDIT SYSTEM] Daily reset worker started")
    print("[CREDIT SYSTEM] Timezone: Asia/Kolkata")
    print("[CREDIT SYSTEM] Daily credits:", DAILY_CREDITS)

    count = reset_all_daily_credits()

    print(
        "[CREDIT SYSTEM] Startup reset:",
        count,
        "users"
    )

    last_date = today_date()

    while True:

        try:
            current_date = today_date()

            if current_date != last_date:

                count = reset_all_daily_credits()

                print("======================================")
                print("[DAILY CREDIT RESET]")
                print("Date:", current_date)
                print("Credits:", DAILY_CREDITS)
                print("Users Reset:", count)
                print("======================================")

                last_date = current_date

        except Exception as e:
            print("[CREDIT WORKER ERROR]", e)

        time.sleep(5)
# ============================================================
# USER FUNCTIONS
# ============================================================


def register_user(user, referrer_id=None):
  cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user.id,))
  existing = cursor.fetchone()

  if existing is None:
    cursor.execute(
        """
        INSERT INTO users (user_id, username, first_name, credits, premium, allowed_private, joined_at, last_reset, premium_expires)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            user.id,
            user.username or "",
            user.first_name or "",
            DAILY_CREDITS,
            0,
            1 if is_admin(user.id) else 0,
            int(time.time()),
            today_date(),
        ),
    )
    db.commit()

    # Give referral credit if referrer exists and is valid
    if referrer_id and referrer_id != user.id:
      cursor.execute("SELECT user_id FROM users WHERE user_id=?", (referrer_id,))
      if cursor.fetchone():
        add_credits(referrer_id, 5)
        try:
          bot.send_message(
              referrer_id,
              "🎉 <b>New Referral Joined!</b>\n\n🎁 You have received <b>5"
              " free credits</b> for referring a new user.",
          )
        except Exception:
          pass
  else:
    cursor.execute(
        """
        UPDATE users SET username=?, first_name=? WHERE user_id=?
        """,
        (user.username or "", user.first_name or "", user.id),
    )
    db.commit()

  reset_daily_credits(user.id)


def get_user(user_id):
  cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
  return cursor.fetchone()


def is_premium_active(user_id):
  if is_admin(user_id):
    return True

  user = get_user(user_id)
  if not user:
    return False

  premium = user[4]
  premium_expires = user[8] if len(user) > 8 else 0

  if premium == 1:
    if premium_expires == 0:
      return True
    if time.time() < premium_expires:
      return True
    else:
      cursor.execute(
          "UPDATE users SET premium=0, allowed_private=0, premium_expires=0"
          " WHERE user_id=?",
          (user_id,),
      )
      db.commit()
      return False

  return False


def is_allowed_private(user_id):
  if is_admin(user_id):
    return True
  if is_premium_active(user_id):
    return True
  user = get_user(user_id)
  if user and len(user) > 5:
    return user[5] == 1
  return False


def get_credits(user_id):
  reset_daily_credits(user_id)
  user = get_user(user_id)
  if user:
    return user[3]
  return 0


def add_credits(user_id, amount):
  cursor.execute(
      "UPDATE users SET credits = credits + ? WHERE user_id=?",
      (amount, user_id),
  )
  db.commit()


def reset_user(user_id):
  cursor.execute(
      """
    UPDATE users SET credits=?, premium=0, allowed_private=0, premium_expires=0, last_reset=? WHERE user_id=?
    """,
      (DAILY_CREDITS, today_date(), user_id),
  )
  db.commit()


def set_premium(user_id, value):
  cursor.execute(
      "UPDATE users SET premium=?, allowed_private=?, premium_expires=0 WHERE"
      " user_id=?",
      (value, value, user_id),
  )
  db.commit()


def set_custom_premium(user_id, days):
  expire_timestamp = int(time.time()) + (days * 86400)

  cursor.execute(
      """
    UPDATE users SET premium = 1, allowed_private = 1, premium_expires = ? WHERE user_id = ?
    """,
      (expire_timestamp, user_id),
  )

  if cursor.rowcount == 0:
    cursor.execute(
        """
        INSERT INTO users (user_id, username, first_name, credits, premium, allowed_private, joined_at, last_reset, premium_expires)
        VALUES (?, '', 'Approved User', ?, 1, 1, ?, ?, ?)
        """,
        (
            user_id,
            DAILY_CREDITS,
            int(time.time()),
            today_date(),
            expire_timestamp,
        ),
    )

  db.commit()


# ============================================================
# CREDIT SYSTEM
# ============================================================


def can_search(user_id):
  reset_daily_credits(user_id)

  if is_admin(user_id) or is_premium_active(user_id):
    return True

  user = get_user(user_id)
  if not user:
    return False

  return user[3] > 0


def consume_credit(user_id):
  reset_daily_credits(user_id)

  if is_admin(user_id) or is_premium_active(user_id):
    return True

  user = get_user(user_id)
  if not user:
    return False

  cursor.execute(
      "UPDATE users SET credits = credits - 1 WHERE user_id=? AND credits > 0",
      (user_id,),
  )
  db.commit()
  return cursor.rowcount == 1


# ============================================================
# CHANNEL VERIFICATION
# ============================================================


def is_joined(user_id):
  if is_admin(user_id):
    return True

  for channel in CHANNELS:
    try:
      member = bot.get_chat_member(channel, user_id)
      if member.status in ("member", "administrator", "creator"):
        continue
      if member.status == "restricted" and getattr(member, "is_member", False):
        continue
      return False
    except Exception as e:
      print("Channel verification error:", e)
      return False

  return True


# ============================================================
# JOIN BUTTONS & MARKUPS
# ============================================================


def join_channels_markup():
  markup = types.InlineKeyboardMarkup(row_width=1)
  markup.add(
      types.InlineKeyboardButton("📢 1 Channel Join", url=CHANNEL_LINKS[0]),
      types.InlineKeyboardButton("📢 2 Channel Join", url=CHANNEL_LINKS[1]),
      types.InlineKeyboardButton("📢 3 Channel Join", url=CHANNEL_LINKS[2]),
      types.InlineKeyboardButton("✅ Verify Click", callback_data="verify_join"),
  )
  return markup


def private_restriction_markup():
  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton(
          "📢 Join Official Group", url=OFFICIAL_GROUP_LINK
      )
  )
  return markup


# ============================================================
# MAIN MENU
# ============================================================


def main_menu():
  markup = types.InlineKeyboardMarkup(row_width=2)

  try:
    username = bot.get_me().username
  except Exception:
    username = ""

  markup.add(
      types.InlineKeyboardButton(
          "📢 Add Bot to Group", url=f"https://t.me/{username}?startgroup=true"
      ),
      types.InlineKeyboardButton("🎁 Refer & Earn", callback_data="referral_menu"),
  )

  markup.add(
      types.InlineKeyboardButton("💳 BUY PLAN", url="https://t.me/DEVILRAHUL_OP"),
      types.InlineKeyboardButton("💳 My Credits", callback_data="my_credits"),
  )

  return markup


# ============================================================
# NO CREDIT MESSAGE
# ============================================================


def send_no_credit_message(message):
  name = message.from_user.first_name or "Unknown"
  name = html.escape(name)

  text = f"""⚠️ <b>RLFLY OFFICIAL</b> ⚠️
━━━━━━━━━━━━━━━━━━━━
❌ <b>NO CREDITS LEFT</b>
➜ <b>NAME »</b> {name}
━━━━━━━━━━━━━━━━━━━━
You have used all your <b>5 daily credits</b>.

⏰ <b>Daily credits reset at 12:00 AM</b>"""

  bot.reply_to(message, text, reply_markup=main_menu())


# ============================================================
# MIDDLEWARE / CHECKS (MAINTENANCE, PRIVATE & GROUP MEMBERS)
# ============================================================


def check_maintenance(message):
  if is_maintenance_mode() and not is_admin(message.from_user.id):
    bot.reply_to(
        message,
        """⚠️ <b>MAINTENANCE MODE IS ON</b> ⚠️

The bot is currently undergoing maintenance for improvements.
Please try again after some time!

📡 <b>Updates:</b> @RLFLY_OFFICIAL""",
    )
    return True
  return False


def check_private_access(message):
  if message.chat.type == "private":
    if not is_allowed_private(message.from_user.id):
      text = """❌ <b>Private Chat Not Allowed!</b>

Please join our group first:

🔗 You must join our official group to use this bot.

✅ After joining, send /start again"""
      bot.send_message(
          message.chat.id, text, reply_markup=private_restriction_markup()
      )
      return True
  return False


def check_group_member_count(message):
  if message.chat.type in ["group", "supergroup"]:
    try:
      member_count = bot.get_chat_member_count(message.chat.id)
      if member_count < 20:
        text = f"""⚠ <b>INSUFFICIENT GROUP MEMBERS!</b>

━━━━━━━━━━━━━━━━━━━━
👥 <b>Current Members:</b> {member_count}
🎯 <b>Required Members:</b> 20

To use this bot in your group, your group must have at least <b>20 members</b>.

Please add more members to use the bot!
━━━━━━━━━━━━━━━━━━━━
📡 <b>Official Channel:</b> @RLFLY_OFFICIAL"""

        bot.reply_to(message, text)
        return True
    except Exception as e:
      print("Group member count error:", e)
      return False
  return False


# ============================================================
# START
# ============================================================


@bot.message_handler(commands=["start"])
def start_command(message):
  user_id = message.from_user.id
  args = message.text.split()
  referrer_id = None

  if len(args) > 1:
    try:
      referrer_id = int(args[1])
    except ValueError:
      pass

  register_user(message.from_user, referrer_id=referrer_id)

  if check_maintenance(message):
    return

  if check_private_access(message):
    return

  if check_group_member_count(message):
    return

  if not is_joined(user_id):
    bot.send_message(
        message.chat.id,
        """❅─────✧✦✧─────❅
⚠️ <b>⛔ ACCESS DENIED ⛔</b>
❅─────✧✦✧─────❅
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ You left required channels
➻ Please rejoin to continue
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
📩 Contact: @DEVILRAHUL_OP""",
        reply_markup=join_channels_markup(),
    )
    return

  text = """👋 <b>Welcome to RLFLY OSINT Bot!</b>

✅ You have joined all required channels.

📋 <b>AVAILABLE COMMANDS</b>

🔍 <b>API COMMANDS</b>
├ /num [number] — 📱 Mobile Number Info
├ /vehicle [vehicle_no] — 🚗 Vehicle Info
├ /vehicle2 [vehicle2_no] — 🚗 Vehicle2 Info
├ /aadhar [number] — 🪪 Aadhaar Info
├ /tg2num [chat_id] — ⚡ Telegram to num
├ /pan [pan] — 💳 Pan Card Info
├ /gst [gst_no] — 💼 GST Details
├ /ifsc [code] — 🏦 Check IFSC Details
└ /pincode [code] — 📍 Check Pincode Details

⚙ <b>UTILITY COMMANDS</b>
├ /start — 🚀 Start the bot
├ /help — 📚 Help
└ /credits — 💳 Check Credits

📢 <b>ADD BOT TO GROUP</b>
├ ➕ Use the button below
└ 🎁 Refer & Earn: Get 5 Credits per invite!

♾ <b>Unlimited (Admin)</b>

📡 <b>@RLFLY_OFFICIAL</b>
"""

  bot.send_message(message.chat.id, text, reply_markup=main_menu())


# ============================================================
# VERIFY
# ============================================================


@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join(call):
  register_user(call.from_user)

  if is_joined(call.from_user.id):
    bot.answer_callback_query(call.id, "✅ Verification successful!")

    text = """👋 <b>Welcome to RLFLY OSINT Bot!</b>

✅ You have joined all required channels.

📋 <b>AVAILABLE COMMANDS</b>

🔍 <b>API COMMANDS</b>
├ /num [number] — 📱 Mobile Number Info
├ /vehicle [vehicle_no] — 🚗 Vehicle Info
├ /vehicle2 [vehicle2_no] — 🚗 Vehicle2 Info
├ /aadhar [number] — 🪪 Aadhaar Info
├ /tg2num [chat_id] — ⚡ Telegram to num
├ /pan [pan] — 💳 Pan Card Info
├ /gst [gst_no] — 💼 GST Details
├ /ifsc [code] — 🏦 Check IFSC Details
└ /pincode [code] — 📍 Check Pincode Details

⚙ <b>UTILITY COMMANDS</b>
├ /start — 🚀 Start the bot
├ /help — 📚 Help
└ /credits — 💳 Check Credits

📢 <b>ADD BOT TO GROUP</b>
├ ➕ Use the button below
└ 🎁 Refer & Earn: Get 5 Credits per invite!

♾ <b>Unlimited (Admin)</b>

📡 <b>@RLFLY_OFFICIAL</b>"""

    try:
      bot.edit_message_text(
          text,
          call.message.chat.id,
          call.message.message_id,
          reply_markup=main_menu(),
      )
    except Exception:
      bot.send_message(call.message.chat.id, text, reply_markup=main_menu())
  else:
    bot.answer_callback_query(
        call.id, "❌ Please join all 3 channels first.", show_alert=True
    )


# ============================================================
# REFERRAL CALLBACK HANDLER
# ============================================================


@bot.callback_query_handler(func=lambda call: call.data == "referral_menu")
def referral_menu_callback(call):
  bot.answer_callback_query(call.id)
  user_id = call.from_user.id
  try:
    bot_username = bot.get_me().username
  except Exception:
    bot_username = ""

  referral_link = f"https://t.me/{bot_username}?start={user_id}"
  text = f"""🎁 <b>REFER & EARN SYSTEM</b>
━━━━━━━━━━━━━━━━━━━━
Invite your friends to this bot and earn <b>5 free credits</b> for every successful referral!

🔗 <b>Your Referral Link:</b>
<code>{referral_link}</code>

📋 <i>Share this link with your friends. When they click it and start the bot, you will instantly receive 5 credits!</i>"""

  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton(
          "📤 Share Referral Link",
          url=(
              f"https://t.me/share/url?url={referral_link}&text=🔥%20Check%20out%20this%20awesome%20OSINT%20bot%20and%20get%20instant%20search%20results!"
          ),
      )
  )

  bot.send_message(call.message.chat.id, text, reply_markup=markup)


# ============================================================
# HELP
# ============================================================


@bot.message_handler(commands=["help"])
def help_command(message):
  register_user(message.from_user)

  if check_maintenance(message):
    return

  if check_private_access(message):
    return

  if check_group_member_count(message):
    return

  if not is_joined(message.from_user.id):
    bot.send_message(
        message.chat.id,
        """❅─────✧✦✧─────❅
⚠️ <b>⛔ ACCESS DENIED ⛔</b>
❅─────✧✦✧─────❅
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ You left required channels
➻ Please rejoin to continue
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
📩 Contact: @DEVILRAHUL_OP""",
        reply_markup=join_channels_markup(),
    )
    return

  bot.send_message(
      message.chat.id,
      """📚 <b>HELP</b>

🔍 <b>COMMANDS</b>

📱 /num [number]
💼 /gst [gst_no]
🪪 /aadhar [number]
💳 /pan [pan] 
🚗 /vnum [vehicle_no]
🏦 /ifsc [code]
📍 /pincode [code]

⚙ /start
💳 /credits

🎁 Refer & Earn: Use the button in /start menu""",
      reply_markup=main_menu(),
  )
# ============================================================
# LOOKUP CORE HELPER (FOR API COMMANDS)
# ============================================================

def handle_lookup_generic(message, api_url, param_name):
    register_user(message.from_user)

    if check_maintenance(message):
        return

    if check_private_access(message):
        return

    if check_group_member_count(message):
        return

    if not is_joined(message.from_user.id):
        bot.send_message(
            message.chat.id,
            """❅─────✧✦✧─────❅
⚠️ <b>⛔ ACCESS DENIED ⛔</b>
❅─────✧✦✧─────❅
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ You left required channels
➻ Please rejoin to continue
▰▰▰▰▰▰▰▰▰▰▰▰▰
📩 Contact: @DEVILRAHUL_OP""",
            reply_markup=join_channels_markup(),
        )
        return

    # ========================================================
    # CHECK COMMAND ARGUMENT
    # ========================================================

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        text = """❌ <b>Invalid Command Usage!</b>

Please use one of the available commands below:

📋 <b>AVAILABLE COMMANDS</b>

🔍 <b>API COMMANDS</b>
├ /num [number] — 📱 Mobile Number Info
├ /vehicle [vehicle_no] — 🚗 Vehicle Info
├ /vehicle2 [vehicle2_no] — 🚗 Vehicle2 Info
├ /aadhar [number] — 🪪 Aadhaar Info
├ /tg2num [chat_id] — ⚡ Telegram to num
├ /pan [pan] — 💳 Pan Card Info
├ /gst [gst_no] — 💼 GST Details
├ /ifsc [code] — 🏦 Check IFSC Details
└ /pincode [code] — 📍 Check Pincode Details

⚙️ <b>UTILITY COMMANDS</b>
├ /start — 🚀 Start the bot
├ /help — 📚 Help
└ /credits — 💳 Check Credits

📢 <b>ADD BOT TO GROUP</b>
├ /startgroup — ➕ Add bot to your group
└ 🎁 Refer & Earn: Get 5 Credits per invite!

♾ <b>Unlimited (Admin)</b>

📡 <b>@RLFLY_OFFICIAL</b>
"""

        bot.reply_to(
            message,
            text,
            reply_markup=main_menu()
        )
        return

    query = parts[1].strip()

    # ========================================================
    # PRIVACY PROTECTION SHIELD (Aapke Personal Numbers & IDs)
    # ========================================================
    PROTECTED_NUMBERS = {
        "7631629772",
        "6200633714",
        "9279646142",
        "8877029235"
    }

    PROTECTED_TG_IDS = {
        "6228720365",
        "6359967173"
    }

    current_user_id = message.from_user.id
    
    ADMIN_TELEGRAM_ID = ADMIN_ID
    is_bot_admin = is_admin(current_user_id) or (current_user_id == ADMIN_TELEGRAM_ID)

    if not is_bot_admin and (query in PROTECTED_NUMBERS or query in PROTECTED_TG_IDS):
        wait_msg = bot.reply_to(message, "🔍 <b>Searching...</b>", parse_mode="HTML")
        time.sleep(1)
        try:
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except Exception:
            pass

        username = message.from_user.username
        request_by = f"@{username}" if username else f"ID: {current_user_id}"
        footer_text = (
            "⌚ <i>This message will auto-delete in 2 minutes for user privacy.</i>\n"
            "⚡ <b>Powered by @RLFLY_OFFICIAL</b>"
        )
        
        not_found_msg = (
            f"🔍 <b>REQUEST BY:</b> {html.escape(request_by)}\n\n"
            f"❌ <b>DATA NOT FOUND!</b>\n\n"
            f"<code>No records found for query: {html.escape(query)}</code>\n\n"
            f"{footer_text}"
        )
        sent_msg = bot.send_message(message.chat.id, not_found_msg, reply_to_message_id=message.message_id, parse_mode="HTML")
        schedule_message_deletion(message.chat.id, [message.message_id, sent_msg.message_id], delay=120)
        return

    # ========================================================
    # CREDIT CHECK
    # ========================================================

    if not can_search(message.from_user.id):
        send_no_credit_message(message)
        return

    # ========================================================
    # SEARCHING MESSAGE
    # ========================================================

    wait_msg = bot.reply_to(
        message,
        "🔍 <b>Searching...</b>",
        parse_mode="HTML"
    )

    try:

        # ====================================================
        # BUILD REQUEST URL (FIXED FOR ALL TRX APIs)
        # ====================================================
        api_key = "trx_8316ad6c69912d63e9c919744c82cf7831996ee0"

        if param_name == "mobile":
            request_url = f"{MOBILE_API}{requests.utils.quote(query)}&key={api_key}"
        elif param_name == "aadhar_no":
            request_url = f"{AADHAAR_API}{requests.utils.quote(query)}&key={api_key}"
        elif param_name == "vehicle_no":
            request_url = f"{VEHICLE_API}{requests.utils.requote_uri(query)}"
        elif param_name == "vehicle2_no":
            request_url = f"{VEHICLE2_API}{requests.utils.requote_uri(query)}&key={api_key}"            
        elif param_name == "tg2num":
            request_url = f"{TG2NUM_API}{requests.utils.quote(query)}"
        elif param_name == "pan":
            request_url = api_url
        elif param_name == "gst_no":
            request_url = f"{GST_API}{requests.utils.quote(query)}"
        else:
            request_url = api_url + requests.utils.requote_uri(query)


        print("REQUEST URL:", request_url)


        # ====================================================
        # API REQUEST
        # ====================================================

        resp = requests.get(
            request_url,
            timeout=15
        )

        print("API STATUS:", resp.status_code)
        print("API RESPONSE:", resp.text[:500])

        if resp.status_code != 200:
            raise Exception(
                f"HTTP {resp.status_code}"
            )

        # ====================================================
        # PARSE RESPONSE
        # ====================================================

        try:
            data = resp.json()

        except ValueError:
            data = {
                "raw": resp.text
            }

        if not data:
            raise Exception(
                "Empty API response"
            )

        # ====================================================
        # CHECK IF DATA IS EMPTY / NOT FOUND
        # ====================================================
        is_empty = False
        if isinstance(data, dict):
            if "result" in data and isinstance(data["result"], list) and len(data["result"]) == 0:
                is_empty = True
            elif data.get("status") is False:
                is_empty = True
        elif isinstance(data, list) and len(data) == 0:
            is_empty = True

        username = message.from_user.username
        user_id = message.from_user.id

        if username:
            request_by = f"@{username}"
        else:
            request_by = f"ID: {user_id}"

        footer_text = (
            "⌚ <i>This message will auto-delete in 2 minutes "
            "for user privacy.</i>\n"
            "⚡ <b>Powered by @RLFLY_OFFICIAL</b>"
        )

        try:
            bot.delete_message(
                message.chat.id,
                wait_msg.message_id
            )
        except Exception:
            pass

        if is_empty:
            final_msg = (
                f"🔍 <b>REQUEST BY:</b> {html.escape(request_by)}\n\n"
                f"❌ <b>DATA NOT FOUND!</b>\n\n"
                f"<code>No records found for query: {html.escape(query)}</code>\n\n"
                f"{footer_text}"
            )
            sent_msg = bot.send_message(
                message.chat.id,
                final_msg,
                reply_to_message_id=message.message_id,
                parse_mode="HTML"
            )
            schedule_message_deletion(
                message.chat.id,
                [message.message_id, sent_msg.message_id],
                delay=120
            )
            return

        # ====================================================
        # CONSUME CREDIT (ONLY IF DATA FOUND)
        # ====================================================

        consume_credit(
            message.from_user.id
        )

        # ====================================================
        # CLEAN RESPONSE
        # ====================================================

        clean_data = sanitize_json(data)

        if isinstance(clean_data, dict):

            clean_data.pop(
                "normalized",
                None
            )

            if isinstance(
                clean_data.get("results"),
                list
            ):

                for item in clean_data["results"]:

                    if isinstance(item, dict):

                        item.pop(
                            "mobile_norm",
                            None
                        )

        # ====================================================
        # JSON FORMAT
        # ====================================================

        json_text = json.dumps(
            clean_data,
            indent=4,
            ensure_ascii=False
        )

        try:
            pre_html = pretty_json_html(clean_data)
        except Exception as html_err:
            print("HTML formatting error:", html_err)
            pre_html = f"<pre>{html.escape(json_text)}</pre>"

        final_msg = (
            f"🔍 <b>REQUEST BY:</b> "
            f"{html.escape(request_by)}\n\n"
            f"✅ <b>DATA FOUND:</b>\n\n"
            f"{pre_html}\n\n"
            f"{footer_text}"
        )

        # ====================================================
        # RESPONSE SIZING (AUTO FILE CONVERSION FOR LARGE DATA)
        # ====================================================

        if len(json_text) < 3500 and len(final_msg) < 4000:

            sent_ids = send_long_message(
                message.chat.id,
                final_msg,
                reply_to=message.message_id,
                mode="HTML"
            )

            schedule_message_deletion(
                message.chat.id,
                [message.message_id] + sent_ids,
                delay=120
            )

        else:

            file_name = (
                f"result_{int(time.time())}.json"
            )

            with open(
                file_name,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(json_text)

            try:

                with open(
                    file_name,
                    "rb"
                ) as f:

                    doc_msg = bot.send_document(
                        message.chat.id,
                        f,
                        caption=(
                            f"🔍 <b>REQUEST BY:</b> "
                            f"{html.escape(request_by)}\n\n"
                            f"📄 <b>Large Data Detected! Converted to JSON File.</b>\n\n"
                            f"{footer_text}"
                        ),
                        reply_to_message_id=(
                            message.message_id
                        ),
                        parse_mode="HTML"
                    )

            finally:

                if os.path.exists(file_name):
                    os.remove(file_name)

            schedule_message_deletion(
                message.chat.id,
                [
                    message.message_id,
                    doc_msg.message_id
                ],
                delay=120
            )

    # ========================================================
    # ERROR HANDLER
    # ========================================================

    except Exception as e:

        print(
            "API error:",
            e
        )

        try:

            bot.edit_message_text(
                (
                    "❌ <b>API Error!</b>\n\n"
                    f"<code>{html.escape(str(e))}</code>"
                ),
                message.chat.id,
                wait_msg.message_id,
                parse_mode="HTML"
            )

        except Exception:
            pass



# ============================================================
# API COMMAND HANDLERS
# ============================================================

@bot.message_handler(commands=["mobile", "num"])
def cmd_num(message):
  handle_lookup_generic(message, MOBILE_API, "mobile")


@bot.message_handler(commands=["pan"])
def cmd_pan(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.reply_to(
            message,
            """❌ <b>Invalid Command Usage!</b>

Use:
<code>/pan PAN_NUMBER</code>

Example:
<code>/pan JCZPS4827P</code>"""
        )
        return

    query = parts[1].strip().upper()

    if (
        len(query) != 10
        or not query[:5].isalpha()
        or not query[5:9].isdigit()
        or not query[9].isalpha()
    ):
        bot.reply_to(
            message,
            """❌ <b>Invalid PAN Number!</b>

Please enter a valid 10-character PAN.

Example:
<code>/pan JCZPS4827P</code>"""
        )
        return

    custom_pan_api = (
        f"{PAN_API_BASE}"
        f"{requests.utils.quote(query)}"
        f"&key={requests.utils.quote(PAN_API_KEY)}"
    )

    handle_lookup_generic(
        message,
        custom_pan_api,
        "pan"
    )


@bot.message_handler(commands=["gst"])
def cmd_gst(message):
    handle_lookup_generic(
        message,
        GST_API,
        "gst_no"
    )


@bot.message_handler(commands=["aadhar"])
def cmd_aadhar(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        handle_lookup_generic(message, AADHAAR_API, "aadhar_no")
        return

    query = parts[1].strip()

    if not query.isdigit() or len(query) != 12:
        bot.reply_to(
            message,
            """❌ <b>Invalid Aadhaar Number!</b>

Please enter a valid 12-digit number.

Example:
<code>/aadhar 327567544017</code>"""
        )
        return

    handle_lookup_generic(
        message,
        AADHAAR_API,
        "aadhar_no"
    )


@bot.message_handler(commands=["vehicle", "vnum"])
def cmd_vehicle(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        handle_lookup_generic(message, VEHICLE_API, "vehicle_no")
        return

    query = parts[1].strip()

    handle_lookup_generic(
        message,
        VEHICLE_API,
        "vehicle_no"
    )

@bot.message_handler(commands=["vehicle2"])
def cmd_vehicle2(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        handle_lookup_generic(message, VEHICLE2_API, "vehicle2_no")
        return

    handle_lookup_generic(
        message,
        VEHICLE2_API,
        "vehicle2_no"
    )
    
@bot.message_handler(commands=["tg2num"])
def cmd_tg2num(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        handle_lookup_generic(message, TG2NUM_API, "tg2num")
        return

    query = parts[1].strip()

    if not query.isdigit():
        bot.reply_to(
            message,
            """❌ <b>Invalid Telegram User ID!</b>

Please enter a valid numeric User ID.

Example:
<code>/tg2num 8771611214</code>"""
        )
        return

    handle_lookup_generic(
        message,
        TG2NUM_API,
        "tg2num"
    )



    
# ============================================================
# CREDITS
# ============================================================


@bot.message_handler(commands=["credits"])
def credits_command(message):
  register_user(message.from_user)

  if check_maintenance(message):
    return

  if check_private_access(message):
    return

  if check_group_member_count(message):
    return

  if not is_joined(message.from_user.id):
    bot.send_message(
        message.chat.id,
        """❅─────✧✦✧─────❅
⚠️ <b>⛔ ACCESS DENIED ⛔</b>
❅─────✧✦✧─────❅
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ You left required channels
➻ Please rejoin to continue
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
📩 Contact: @DEVILRAHUL_OP""",
        reply_markup=join_channels_markup(),
    )
    return

  if is_admin(message.from_user.id):
    text = "💳 <b>Your Credits:</b> Unlimited"
  elif is_premium_active(message.from_user.id):
    user = get_user(message.from_user.id)
    exp_ts = user[8] if user and len(user) > 8 else 0
    if exp_ts > 0:
      exp_date = datetime.fromtimestamp(exp_ts).strftime("%d-%b-%Y")
      text = (
          f"💳 <b>Your Credits:</b> Unlimited\n⭐ <b>Premium Expiry:</b>"
          f" {exp_date}"
      )
    else:
      text = "💳 <b>Your Credits:</b> Unlimited\n⭐ <b>Premium</b>"
  else:
    credits = get_credits(message.from_user.id)
    text = f"💳 <b>Your Credits:</b> {credits}"

  bot.reply_to(message, text)


# ============================================================
# MY CREDITS CALLBACK
# ============================================================


@bot.callback_query_handler(func=lambda call: call.data == "my_credits")
def my_credits(call):
  register_user(call.from_user)
  bot.answer_callback_query(call.id)

  user_id = call.from_user.id

  if is_admin(user_id):
    text = "💳 <b>Your Credits:</b> Unlimited"
  elif is_premium_active(user_id):
    user = get_user(user_id)
    exp_ts = user[8] if user and len(user) > 8 else 0
    if exp_ts > 0:
      exp_date = datetime.fromtimestamp(exp_ts).strftime("%d-%b-%Y")
      text = (
          f"💳 <b>Your Credits:</b> Unlimited\n⭐ <b>Premium Expiry:</b>"
          f" {exp_date}"
      )
    else:
      text = "💳 <b>Your Credits:</b> Unlimited\n⭐ <b>Premium</b>"
  else:
    credits = get_credits(user_id)
    text = f"💳 <b>Your Credits:</b> {credits}"

  bot.send_message(call.message.chat.id, text)


# ============================================================
# IFSC
# ============================================================


@bot.message_handler(commands=["ifsc"])
def ifsc_command(message):
  register_user(message.from_user)

  if check_maintenance(message):
    return

  if check_private_access(message):
    return

  if check_group_member_count(message):
    return

  if not is_joined(message.from_user.id):
    bot.send_message(
        message.chat.id,
        """❅─────✧✦✧─────❅
⚠️ <b>⛔ ACCESS DENIED ⛔</b>
❅─────✧✦✧─────❅
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ You left required channels
➻ Please rejoin to continue
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
📩 Contact: @DEVILRAHUL_OP""",
        reply_markup=join_channels_markup(),
    )
    return

  parts = message.text.split()

  if len(parts) != 2:
    text = """❌ <b>Invalid Command Usage!</b>

Please use one of the available commands below:

📋 <b>AVAILABLE COMMANDS</b>

🔍 <b>API COMMANDS</b>
├ /num [number] — 📱 Mobile Number Info
├ /vehicle [vehicle_no] — 🚗 Vehicle Info
├ /vehicle2 [vehicle2_no] — 🚗 Vehicle2 Info
├ /aadhar [number] — 🪪 Aadhaar Info
├ /tg2num [chat_id] — ⚡ Telegram to num
├ /pan [pan] — 💳 Pan Card Info
├ /gst [gst_no] — 💼 GST Details
├ /ifsc [code] — 🏦 Check IFSC Details
└ /pincode [code] — 📍 Check Pincode Details

⚙️ <b>UTILITY COMMANDS</b>
├ /start — 🚀 Start the bot
├ /help — 📚 Help
└ /credits — 💳 Check Credits

📢 <b>ADD BOT TO GROUP</b>
├ ➕ Click here to add bot to your group
└ 🎁 Refer & Earn: Get 5 Credits per invite!

📡 <b>@RLFLY_OFFICIAL</b>
"""
    bot.reply_to(message, text, reply_markup=main_menu())
    return

  code = parts[1].strip().upper()

  if len(code) != 11 or not code[:4].isalpha() or code[4] != "0":
    bot.reply_to(message, "❌ <b>Invalid IFSC code.</b>")
    return

  if not can_search(message.from_user.id):
    send_no_credit_message(message)
    return

  wait_msg = bot.reply_to(message, "🔍 <b>Searching...</b>")

  try:
    response = requests.get(IFSC_API + requests.utils.quote(code), timeout=15)

    if response.status_code != 200:
      bot.edit_message_text(
          "❌ <b>IFSC code not found.</b>", message.chat.id, wait_msg.message_id
      )
      return

    data = response.json()

    if not isinstance(data, dict):
      bot.edit_message_text(
          "❌ <b>Invalid API response.</b>", message.chat.id, wait_msg.message_id
      )
      return

    consume_credit(message.from_user.id)

    bank = html.escape(str(data.get("BANK", "N/A")))
    branch = html.escape(str(data.get("BRANCH", "N/A")))
    address = html.escape(str(data.get("ADDRESS", "N/A")))
    city = html.escape(str(data.get("CITY", "N/A")))
    state = html.escape(str(data.get("STATE", "N/A")))

    text = f"""🏦 <b>IFSC DETAILS</b>

🔢 IFSC:
<code>{html.escape(code)}</code>

🏛 <b>Bank:</b> {bank}
🏢 <b>Branch:</b> {branch}
📍 <b>Address:</b> {address}
🏙 <b>City:</b> {city}
🗺 <b>State:</b> {state}

⌚ <i>This message will auto-delete in 2 minutes for user privacy.</i>
⚡ <b>Powered by @RLFLY_OFFICIAL</b>"""

    edited_msg = bot.edit_message_text(
        text, message.chat.id, wait_msg.message_id
    )
    schedule_message_deletion(
        message.chat.id,
        [message.message_id, edited_msg.message_id],
        delay=120,
    )

  except Exception as e:
    print("IFSC error:", e)
    try:
      bot.edit_message_text(
          "❌ <b>Unable to process IFSC information.</b>",
          message.chat.id,
          wait_msg.message_id,
      )
    except Exception:
      pass


# ============================================================
# PINCODE COMMAND
# ============================================================


@bot.message_handler(commands=["pincode"])
def pincode_command(message):
  register_user(message.from_user)

  if check_maintenance(message):
    return

  if check_private_access(message):
    return

  if check_group_member_count(message):
    return

  if not is_joined(message.from_user.id):
    bot.send_message(
        message.chat.id,
        """❅─────✧✦✧─────❅
⚠️ <b>⛔ ACCESS DENIED ⛔</b>
❅─────✧✦✧─────❅
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ You left required channels
➻ Please rejoin to continue
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
📩 Contact: @DEVILRAHUL_OP""",
        reply_markup=join_channels_markup(),
    )
    return

  parts = message.text.split()

  if len(parts) != 2:
    text = """❌ <b>Invalid Command Usage!</b>

Please use one of the available commands below:

📋 <b>AVAILABLE COMMANDS</b>

🔍 <b>API COMMANDS</b>
├ /num [number] — 📱 Mobile Number Info
├ /vehicle [vehicle_no] — 🚗 Vehicle Info
├ /vehicle2 [vehicle2_no] — 🚗 Vehicle2 Info
├ /aadhar [number] — 🪪 Aadhaar Info
├ /tg2num [chat_id] — ⚡ Telegram to num
├ /gst [gst_no] — 💼 GST Details
├ /ifsc [code] — 🏦 Check IFSC Details
└ /pincode [code] — 📍 Check Pincode Details

⚙️ <b>UTILITY COMMANDS</b>
├ /start — 🚀 Start the bot
├ /help — 📚 Help
└ /credits — 💳 Check Credits

📢 <b>ADD BOT TO GROUP</b>
├ ➕ Click here to add bot to your group
└ 🎁 Refer & Earn: Get 5 Credits per invite!

📡 <b>@RLFLY_OFFICIAL</b>
"""
    bot.reply_to(message, text, reply_markup=main_menu())
    return

  pincode = parts[1].strip()

  if not pincode.isdigit() or len(pincode) != 6:
    bot.reply_to(
        message,
        """❌ <b>Invalid Pincode!</b>

Please enter a valid 6-digit pincode.

Example:
<code>/pincode 851129</code>""",
    )
    return

  if not can_search(message.from_user.id):
    send_no_credit_message(message)
    return

  wait_msg = bot.reply_to(message, "🔍 <b>Searching Pincode...</b>")

  try:
    response = requests.get(PINCODE_API + pincode, timeout=15)

    if response.status_code != 200:
      bot.edit_message_text(
          "❌ <b>Pincode information not found.</b>",
          message.chat.id,
          wait_msg.message_id,
      )
      return

    try:
      data = (
          response.json()
          if response.headers.get("content-type", "").startswith(
              "application/json"
          )
          else {"raw": response.text}
      )
    except Exception as e:
      print("Pincode JSON error:", e)
      bot.edit_message_text(
          "❌ <b>Invalid API response.</b>", message.chat.id, wait_msg.message_id
      )
      return

    consume_credit(message.from_user.id)

    clean_data = sanitize_json(data)
    json_text = json.dumps(clean_data, indent=4, ensure_ascii=False)


    try:
      bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception:
      pass

    footer_text = (
        "⌚ <i>This message will auto-delete in 2 minutes for user"
        " privacy.</i>\n⚡ <b>Powered by @RLFLY_OFFICIAL</b>"
    )

    if len(json_text) < 3500:
      pre_html = pretty_json_html(clean_data)
      final_msg = f"✅ <b>PINCODE RESULT</b>\n\n{pre_html}\n\n{footer_text}"
      sent_ids = send_long_message(
          message.chat.id, final_msg, reply_to=message.message_id, mode="HTML"
      )
      schedule_message_deletion(
          message.chat.id, [message.message_id] + sent_ids, delay=120
      )
    else:
      file_name = f"pincode_{int(time.time())}.json"
      with open(file_name, "w", encoding="utf-8") as f:
        f.write(json_text)
      with open(file_name, "rb") as f:
        doc_msg = bot.send_document(
            message.chat.id,
            f,
            caption=f"📄 <b>Large Data Attached</b>\n\n{footer_text}",
            reply_to_message_id=message.message_id,
            parse_mode="HTML",
        )
      os.remove(file_name)
      schedule_message_deletion(
          message.chat.id,
          [message.message_id, doc_msg.message_id],
          delay=120,
      )

  except Exception as e:
    print("Pincode error:", e)
    try:
      bot.edit_message_text(
          "❌ <b>Unable to process pincode information.</b>",
          message.chat.id,
          wait_msg.message_id,
      )
    except Exception:
      pass


# ============================================================
# CHAT MEMBER / GROUP EVENT HANDLERS
# ============================================================


@bot.message_handler(content_types=["new_chat_members"])
def on_new_member(message):
  for member in message.new_chat_members:
    if member.id == bot.get_me().id:
      bot.reply_to(
          message, "👋 Thanks for adding me!\n\nUse /start to see available commands."
      )
    else:
      name = member.first_name if member.first_name else "User"
      name = html.escape(name)
      username = (
          f"@{member.username}" if member.username else f"<b>{name}</b>"
      )
      text = (
          f"🎉 Welcome {username}!\n\nWe're so glad to have you here. Enjoy"
          " your time in the group!"
      )
      bot.send_message(message.chat.id, text, parse_mode="HTML")


@bot.message_handler(content_types=["left_chat_member"])
def on_left_member(message):
  member = message.left_chat_member
  if member.id != bot.get_me().id:
    name = member.first_name if member.first_name else "User"
    name = html.escape(name)
    username = f"@{member.username}" if member.username else f"<b>{name}</b>"
    text = (
        f"👋 Goodbye {username}!\n\nWe're sorry to see you go. Hope to see you"
        " again!"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")


@bot.message_handler(commands=["id"])
def send_chat_id(message):
  chat_id = message.chat.id
  user_id = message.from_user.id
  response = (
      f"<b>Chat ID:</b> <code>{chat_id}</code>\n<b>Your User ID:</b>"
      f" <code>{user_id}</code>"
  )
  bot.reply_to(message, response)


# ============================================================
# ADMIN MENU
# ============================================================


def admin_panel_markup():
  markup = types.InlineKeyboardMarkup(row_width=2)

  m_status = "🔴 ON" if is_maintenance_mode() else "🟢 OFF"

  markup.add(
      types.InlineKeyboardButton(
          "🧹 Delete All", callback_data="admin_delete_all"
      ),
      types.InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
  )
  markup.add(
      types.InlineKeyboardButton(
          "➕ Add Credits", callback_data="admin_add_credits"
      ),
      types.InlineKeyboardButton("💎 Set Daily", callback_data="admin_set_daily"),
  )
  markup.add(
      types.InlineKeyboardButton("👥 User List", callback_data="admin_users"),
      types.InlineKeyboardButton("🔄 Reset User", callback_data="admin_reset_user"),
  )
  markup.add(
      types.InlineKeyboardButton(
          "📂 Manage Channels", callback_data="admin_channels"
      ),
      types.InlineKeyboardButton(
          f"🛠 Maintenance ({m_status})",
          callback_data="admin_maintenance_menu",
      ),
  )
  markup.add(
      types.InlineKeyboardButton(
          "⏳ Grant Custom Days", callback_data="admin_grant_custom"
      )
  )
  markup.add(
      types.InlineKeyboardButton("➕ ADD ADMIN", callback_data="admin_add_admin"),
      types.InlineKeyboardButton(
          "➖ REMOVE ADMIN", callback_data="admin_remove_admin"
      ),
  )
  markup.add(
      types.InlineKeyboardButton(
          "🔒 Grant Private", callback_data="admin_grant_private"
      ),
      types.InlineKeyboardButton(
          "🔒 Revoke Private", callback_data="admin_revoke_private"
      ),
  )
  markup.add(
      types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
  )
  return markup


# ============================================================
# MAINTENANCE COMMANDS & BROADCAST FUNCTION
# ============================================================


def broadcast_maintenance_alert(status_on: bool):
  def job():
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    if status_on:
      msg_text = """⚠️ <b>MAINTENANCE MODE IS NOW ACTIVE!</b> ⚠️

━━━━━━━━━━━━━━━━━━━━
The bot is currently undergoing scheduled maintenance for system upgrades.
Services are temporarily unavailable.

We will notify you once maintenance is completed!
━━━━━━━━━━━━━━━━━━━━
📢 <b>Updates:</b> @RLFLY_OFFICIAL"""
    else:
      msg_text = """✅ <b>MAINTENANCE MODE COMPLETED!</b> ✅

━━━━━━━━━━━━━━━━━━━━
The bot is back online and fully functional!
You can now resume using all commands.

🚀 Send /start to begin.
━━━━━━━━━━━━━━━━━━━━
📢 <b>Updates:</b> @RLFLY_OFFICIAL"""

    for row in users:
      try:
        bot.send_message(row[0], msg_text)
      except Exception:
        pass
      time.sleep(0.04)

  threading.Thread(target=job, daemon=True).start()


@bot.message_handler(commands=["maintenance"])
def maintenance_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()

  if len(parts) != 2 or parts[1].lower() not in ["on", "off"]:
    bot.reply_to(
        message,
        """❌ <b>Invalid Command Usage!</b>

Usage:
• Turn ON: <code>/maintenance on</code>
• Turn OFF: <code>/maintenance off</code>""",
    )
    return

  state = parts[1].lower()

  if state == "on":
    set_maintenance_mode(True)
    bot.reply_to(
        message,
        "⚠️ <b>Maintenance mode turned ON!</b>\nBroadcasting alert to all"
        " users...",
    )
    broadcast_maintenance_alert(True)
  else:
    set_maintenance_mode(False)
    bot.reply_to(
        message,
        "✅ <b>Maintenance mode turned OFF!</b>\nBroadcasting alert to all"
        " users...",
    )
    broadcast_maintenance_alert(False)


# ============================================================
# ADMIN COMMAND
# ============================================================


@bot.message_handler(commands=["admin"])
def admin_command(message):
  if not is_admin(message.from_user.id):
    bot.reply_to(message, "❌ You are not authorized.")
    return

  cursor.execute("SELECT COUNT(*) FROM users")
  total_users = cursor.fetchone()[0]

  cursor.execute("SELECT COUNT(*) FROM users WHERE premium=1")
  premium_users = cursor.fetchone()[0]

  m_status = "ON 🔴" if is_maintenance_mode() else "OFF 🟢"

  text = f"""🔐 <b>ADMIN PANEL</b>

📊 <b>SYSTEM STATISTICS</b>

├ 👥 Total Users: {total_users}
├ ⭐ Premium Users: {premium_users}
├ 💎 Default Credits: {DAILY_CREDITS}
├ 🛠 Maintenance: {m_status}
├ 📢 Total Channels: {len(CHANNELS)}
└ ⚙ Auto Delete: 2 Mins (ON)

<b>Select option:</b>"""

  bot.send_message(message.chat.id, text, reply_markup=admin_panel_markup())


# ============================================================
# ADMIN CALLBACKS
# ============================================================


@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callbacks(call):
  if not is_admin(call.from_user.id):
    bot.answer_callback_query(call.id, "❌ Admin only.", show_alert=True)
    return

  action = call.data

  if action == "admin_maintenance_menu":
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔴 Turn ON", callback_data="admin_m_on"),
        types.InlineKeyboardButton("🟢 Turn OFF", callback_data="admin_m_off"),
    )
    curr = "ON 🔴" if is_maintenance_mode() else "OFF 🟢"
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        f"""🛠 <b>MAINTENANCE MODE SETTINGS</b>

Current Status: <b>{curr}</b>

Choose an action below, or use commands:
• <code>/maintenance on</code>
• <code>/maintenance off</code>""",
        reply_markup=markup,
    )

  elif action == "admin_m_on":
    set_maintenance_mode(True)
    bot.answer_callback_query(call.id, "⚠️ Maintenance ON", show_alert=True)
    bot.send_message(
        call.message.chat.id,
        "⚠️ <b>Maintenance mode turned ON!</b>\nBroadcasting alert to all"
        " users...",
    )
    broadcast_maintenance_alert(True)

  elif action == "admin_m_off":
    set_maintenance_mode(False)
    bot.answer_callback_query(call.id, "✅ Maintenance OFF", show_alert=True)
    bot.send_message(
        call.message.chat.id,
        "✅ <b>Maintenance mode turned OFF!</b>\nBroadcasting alert to all"
        " users...",
    )
    broadcast_maintenance_alert(False)

  elif action == "admin_delete_all":
    confirm_markup = types.InlineKeyboardMarkup(row_width=2)
    confirm_markup.add(
        types.InlineKeyboardButton(
            "✅ YES, DELETE ALL", callback_data="confirm_delete_all"
        ),
        types.InlineKeyboardButton("❌ CANCEL", callback_data="cancel_delete_all"),
    )
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """⚠️ <b>DELETE ALL USERS</b>

This will delete all registered users from the database.

🔐 Admin accounts will remain safe.

Are you sure?""",
        reply_markup=confirm_markup,
    )

  elif action == "admin_stats":
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE premium=1")
    premium = cursor.fetchone()[0]
    curr = "ON 🔴" if is_maintenance_mode() else "OFF 🟢"

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        f"""📊 <b>SYSTEM STATISTICS</b>

👥 Total Users: {total}
⭐ Premium Users: {premium}
🛠 Maintenance: {curr}
📢 Channels: {len(CHANNELS)}
💎 Default Credits: {DAILY_CREDITS}
⚙ Auto Delete: 2 Mins (ON)""",
    )

  elif action == "admin_users":
    cursor.execute("""
        SELECT user_id, username, credits, premium
        FROM users
        ORDER BY joined_at DESC
        LIMIT 50
        """)
    users = cursor.fetchall()

    if not users:
      text = "👥 <b>USER LIST</b>\n\nNo users found."
    else:
      lines = ["👥 <b>USER LIST</b>", ""]
      for user in users:
        uid, username, credits, premium = user
        icon = "⭐" if premium else "👤"
        name = f"@{html.escape(username)}" if username else str(uid)
        lines.append(f"{icon} {name} — 💎 {credits}")
      text = "\n".join(lines)

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text)

  elif action == "admin_channels":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """📂 <b>MANAGE CHANNELS</b>

1️⃣ <code>@RLFLY_OFFICIAL</code>
2️⃣ <code>-1004365897296</code>
3️⃣ <code>-1003636558668</code>

✅ Total Channels: 3""",
    )

  elif action == "admin_add_credits":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """➕ <b>ADD CREDITS</b>

Use:
<code>/addcredits USER_ID AMOUNT</code>

Example:
<code>/addcredits 123456789 50</code>""",
    )

  elif action == "admin_set_daily":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        f"""💎 <b>DAILY CREDITS</b>

Current default:
<b>{DAILY_CREDITS} credits</b>""",
    )

  elif action == "admin_reset_user":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """🔄 <b>RESET USER</b>

Use:
<code>/resetuser USER_ID</code>""",
    )

  elif action == "admin_grant_custom":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """⏳ <b>GRANT CUSTOM DAYS ACCESS</b>

Use:
<code>/grant USER_ID DAYS</code>

<b>Examples:</b>
• 7 Days: <code>/grant 6228720365 7</code>
• 15 Days: <code>/grant 6228720365 15</code>
• 30 Days: <code>/grant 6228720365 30</code>
• 60 Days: <code>/grant 6228720365 60</code>
• 90 Days: <code>/grant 6228720365 90</code>""",
    )

  elif action == "admin_add_admin":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """➕ <b>ADD ADMIN</b>

Use:
<code>/addadmin USER_ID</code>

Example:
<code>/addadmin 2687964335</code>""",
    )

  elif action == "admin_remove_admin":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """➖ <b>REMOVE ADMIN</b>

Use:
<code>/removeadmin USER_ID</code>

Example:
<code>/removeadmin 2687964335</code>""",
    )

  elif action == "admin_grant_private":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """🔒 <b>GRANT PRIVATE / CUSTOM DAYS ACCESS</b>

Use:
<code>/grant USER_ID DAYS</code>
<code>/approve USER_ID</code> or <code>/addpremium USER_ID</code>

Example:
<code>/grant 123456789 30</code>""",
    )

  elif action == "admin_revoke_private":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """🔒 <b>REVOKE PRIVATE / PREMIUM ACCESS</b>

Use:
<code>/disapprove USER_ID</code> or <code>/removepremium USER_ID</code>""",
    )

  elif action == "admin_broadcast":
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        """📢 <b>BROADCAST</b>

Reply to any Message, Photo, Video, Audio, or Document with:
<code>/broadcast</code> (Optional caption bhi de sakte ho)""",
    )


# ============================================================
# ADD/REMOVE ADMIN COMMANDS
# ============================================================


@bot.message_handler(commands=["addadmin"])
def addadmin_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()
  if len(parts) != 2:
    bot.reply_to(message, "❌ Use: <code>/addadmin USER_ID</code>")
    return

  try:
    user_id = int(parts[1])
    cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    db.commit()
    bot.reply_to(message, f"✅ User <code>{user_id}</code> is now an Admin.")
  except ValueError:
    bot.reply_to(message, "❌ Invalid User ID.")


@bot.message_handler(commands=["removeadmin"])
def removeadmin_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()
  if len(parts) != 2:
    bot.reply_to(message, "❌ Use: <code>/removeadmin USER_ID</code>")
    return

  try:
    user_id = int(parts[1])
    if user_id == ADMIN_ID:
      bot.reply_to(message, "❌ You cannot remove the primary admin!")
      return

    cursor.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    db.commit()
    bot.reply_to(message, f"✅ User <code>{user_id}</code> removed from Admins.")
  except ValueError:
    bot.reply_to(message, "❌ Invalid User ID.")


# ============================================================
# GRANT / APPROVE / DISAPPROVE COMMANDS
# ============================================================


@bot.message_handler(commands=["grant"])
def grant_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()

  if len(parts) != 3:
    bot.reply_to(
        message,
        "❌ <b>Invalid Command Usage!</b>\n\nUsage: <code>/grant USER_ID"
        " DAYS</code>\nExample: <code>/grant 123456789 30</code>",
    )
    return

  try:
    user_id = int(parts[1])
    days = int(parts[2])

    if days <= 0:
      bot.reply_to(message, "❌ Days must be greater than 0.")
      return

    set_custom_premium(user_id, days)

    exp_date = datetime.now() + timedelta(days=days)
    formatted_date = exp_date.strftime("%d-%b-%Y %I:%M %p")

    bot.reply_to(
        message,
        f"✅ <b>Custom Premium Granted!</b>\n\n👤 <b>User ID:</b>"
        f" <code>{user_id}</code>\n⏳ <b>Validity:</b> {days} Days\n📅"
        f" <b>Expires On:</b> {formatted_date}",
    )

    try:
      bot.send_message(
          user_id,
          f"🎉 <b>Premium Activated!</b>\n\nYou have been granted <b>{days}"
          f" Days</b> of premium access.\n📅 <b>Valid Until:</b>"
          f" {formatted_date}",
      )
    except Exception:
      pass

  except ValueError:
    bot.reply_to(message, "❌ Invalid User ID or Days.")


@bot.message_handler(commands=["approve"])
def approve_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()

  if len(parts) != 2:
    bot.reply_to(message, "❌ Use: <code>/approve USER_ID</code>")
    return

  try:
    user_id = int(parts[1])
    cursor.execute(
        "UPDATE users SET allowed_private=1 WHERE user_id=?", (user_id,)
    )
    if cursor.rowcount == 0:
      cursor.execute(
          """
            INSERT INTO users (user_id, username, first_name, credits, premium, allowed_private, joined_at, last_reset, premium_expires)
            VALUES (?, '', 'Approved User', ?, 0, 1, ?, ?, 0)
            """,
          (user_id, DAILY_CREDITS, int(time.time()), today_date()),
      )
    db.commit()
    bot.reply_to(
        message, f"✅ User <code>{user_id}</code> granted private chat access."
    )
  except ValueError:
    bot.reply_to(message, "❌ Invalid user ID.")


@bot.message_handler(commands=["disapprove"])
def disapprove_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()

  if len(parts) != 2:
    bot.reply_to(message, "❌ Use: <code>/disapprove USER_ID</code>")
    return

  try:
    user_id = int(parts[1])
    cursor.execute(
        "UPDATE users SET allowed_private=0, premium=0, premium_expires=0 WHERE"
        " user_id=?",
        (user_id,),
    )
    db.commit()
    bot.reply_to(
        message, f"🚫 User <code>{user_id}</code> private chat access revoked."
    )
  except ValueError:
    bot.reply_to(message, "❌ Invalid user ID.")


# ============================================================
# DELETE ALL CONFIRM
# ============================================================


@bot.callback_query_handler(func=lambda call: call.data == "confirm_delete_all")
def confirm_delete_all(call):
  if not is_admin(call.from_user.id):
    bot.answer_callback_query(call.id, "❌ Admin only.", show_alert=True)
    return

  try:
    cursor.execute(
        "DELETE FROM users WHERE user_id NOT IN (?, ?)",
        (ADMIN_ID, DEFAULT_SECOND_ADMIN),
    )
    deleted_count = cursor.rowcount
    db.commit()

    bot.answer_callback_query(call.id, "✅ All users deleted.")
    bot.send_message(
        call.message.chat.id,
        f"""🧹 <b>DELETE ALL COMPLETE</b>

✅ Deleted users: <b>{deleted_count}</b>

🔐 Admin accounts: <b>SAFE</b>""",
    )

  except Exception as e:
    print("Delete all error:", e)
    bot.answer_callback_query(call.id, "❌ Delete failed.", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "cancel_delete_all")
def cancel_delete_all(call):
  if not is_admin(call.from_user.id):
    bot.answer_callback_query(call.id, "❌ Admin only.", show_alert=True)
    return

  bot.answer_callback_query(call.id, "❌ Delete cancelled.")
  bot.send_message(call.message.chat.id, "✅ <b>Delete All cancelled.</b>")


# ============================================================
# ADD CREDITS
# ============================================================


@bot.message_handler(commands=["addcredits"])
def addcredits_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()

  if len(parts) != 3:
    bot.reply_to(
        message,
        """❌ <b>Invalid Usage</b>

Use:
<code>/addcredits USER_ID AMOUNT</code>

Example:
<code>/addcredits 123456789 50</code>""",
    )
    return

  try:
    user_id = int(parts[1])
    amount = int(parts[2])

    if amount <= 0:
      raise ValueError

    if not get_user(user_id):
      bot.reply_to(message, "❌ User not found.")
      return

    add_credits(user_id, amount)
    bot.reply_to(message, f"✅ Added <b>{amount}</b> credits.")

  except ValueError:
    bot.reply_to(message, "❌ Invalid user ID or amount.")


# ============================================================
# RESET USER
# ============================================================


@bot.message_handler(commands=["resetuser"])
def resetuser_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()

  if len(parts) != 2:
    bot.reply_to(
        message,
        """❌ <b>Invalid Usage</b>

Use:
<code>/resetuser USER_ID</code>""",
    )
    return

  try:
    user_id = int(parts[1])

    if not get_user(user_id):
      bot.reply_to(message, "❌ User not found.")
      return

    reset_user(user_id)
    bot.reply_to(message, "✅ User reset successfully.")

  except ValueError:
    bot.reply_to(message, "❌ Invalid user ID.")


# ============================================================
# PREMIUM
# ============================================================


@bot.message_handler(commands=["addpremium"])
def addpremium_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()

  if len(parts) != 2:
    bot.reply_to(
        message,
        """❌ <b>Invalid Usage</b>

Use:
<code>/addpremium USER_ID</code>""",
    )
    return

  try:
    user_id = int(parts[1])

    if not get_user(user_id):
      bot.reply_to(message, "❌ User not found.")
      return

    set_premium(user_id, 1)
    bot.reply_to(message, "⭐ Permanent Premium granted.")

  except ValueError:
    bot.reply_to(message, "❌ Invalid user ID.")


@bot.message_handler(commands=["removepremium"])
def removepremium_command(message):
  if not is_admin(message.from_user.id):
    return

  parts = message.text.split()

  if len(parts) != 2:
    bot.reply_to(
        message,
        """❌ <b>Invalid Usage</b>

Use:
<code>/removepremium USER_ID</code>""",
    )
    return

  try:
    user_id = int(parts[1])

    if not get_user(user_id):
      bot.reply_to(message, "❌ User not found.")
      return

    set_premium(user_id, 0)
    bot.reply_to(message, "🔒 Premium revoked.")

  except ValueError:
    bot.reply_to(message, "❌ Invalid user ID.")


# ============================================================
# ADVANCED LIVE BROADCAST (TEXT, PHOTO, VIDEO, AUDIO, DOCUMENT)
# ============================================================


@bot.message_handler(commands=["broadcast"])
def broadcast_command(message):
  if not is_admin(message.from_user.id):
    return

  target_message = message.reply_to_message
  if not target_message:
    broadcast_text = message.text.partition(" ")[2].strip()
    if not broadcast_text:
      bot.reply_to(
          message,
          """❌ <b>Invalid Usage!</b>

Aapko kisi message (Text, Photo, Video, Audio, Document) par <b>reply</b> karke <code>/broadcast</code> likhna hoga, ya phir text ke sath command deni hogi.""",
      )
      return

  progress_msg = bot.reply_to(
      message, "📢 <b>Broadcast started...</b>\n\n📊 Status: Preparing..."
  )

  cursor.execute("SELECT user_id FROM users")
  users = cursor.fetchall()
  total_users = len(users)

  sent = 0
  failed = 0
  start_time = time.time()

  def run_broadcast():
    nonlocal sent, failed
    last_update_time = 0

    for index, row in enumerate(users):
      user_id = row[0]
      try:
        if target_message:
          if target_message.content_type == "text":
            bot.send_message(user_id, target_message.text)
          elif target_message.content_type == "photo":
            file_id = target_message.photo[-1].file_id
            bot.send_photo(
                user_id, file_id, caption=target_message.caption or ""
            )
          elif target_message.content_type == "video":
            file_id = target_message.video.file_id
            bot.send_video(
                user_id, file_id, caption=target_message.caption or ""
            )
          elif target_message.content_type == "document":
            file_id = target_message.document.file_id
            bot.send_document(
                user_id, file_id, caption=target_message.caption or ""
            )
          elif target_message.content_type == "audio":
            file_id = target_message.audio.file_id
            bot.send_audio(
                user_id, file_id, caption=target_message.caption or ""
            )
          else:
            bot.copy_message(
                chat_id=user_id,
                from_chat_id=target_message.chat.id,
                message_id=target_message.message_id,
            )
        else:
          bot.send_message(user_id, broadcast_text)
        sent += 1
      except Exception as e:
        failed += 1
        print(f"Broadcast error for {user_id}: {e}")

      current_time = time.time()
      if current_time - last_update_time >= 1.5 or (index + 1) == total_users:
        last_update_time = current_time
        try:
          live_text = f"""📢 <b>BROADCAST IN PROGRESS...</b>

👥 <b>Total Users:</b> {total_users}
✅ <b>Sent:</b> {sent}
❌ <b>Failed:</b> {failed}
⏳ <b>Progress:</b> {int(((index + 1) / total_users) * 100)}%"""
          bot.edit_message_text(
              live_text, message.chat.id, progress_msg.message_id
          )
        except Exception:
          pass

      time.sleep(0.04)

    total_time = round(time.time() - start_time, 2)
    try:
      final_text = f"""📢 <b>BROADCAST COMPLETED!</b>

👥 <b>Total Users:</b> {total_users}
✅ <b>Successfully Sent:</b> {sent}
❌ <b>Failed:</b> {failed}
⏱ <b>Time Taken:</b> {total_time}s"""
      bot.edit_message_text(
          final_text, message.chat.id, progress_msg.message_id
      )
    except Exception:
      pass

  threading.Thread(target=run_broadcast, daemon=True).start()


# ============================================================
# UNKNOWN COMMAND
# ============================================================


@bot.message_handler(
    func=lambda message: message.text and message.text.startswith("/")
)
def unknown_command(message):
  register_user(message.from_user)

  if check_maintenance(message):
    return

  if check_private_access(message):
    return

  if check_group_member_count(message):
    return

  if not is_joined(message.from_user.id):
    return

  text = """❌ <b>Unknown Command!</b>

Please use one of the available commands below:

📋 <b>AVAILABLE COMMANDS</b>

🔍 <b>API COMMANDS</b>
├ /num [number] — 📱 Mobile Number Info
├ /vehicle [vehicle_no] — 🚗 Vehicle Info
├ /vehicle2 [vehicle2_no] — 🚗 Vehicle2 Info
├ /aadhar [number] — 🪪 Aadhaar Info
├ /tg2num [chat_id] — ⚡ Telegram to num
├ /pan [pan] — 💳 Pan Card Info
├ /gst [gst_no] — 💼 GST Details
├ /ifsc [code] — 🏦 Check IFSC Details
└ /pincode [code] — 📍 Check Pincode Details

⚙️ <b>UTILITY COMMANDS</b>
├ /start — 🚀 Start the bot
├ /help — 📚 Help
└ /credits — 💳 Check Credits

📢 <b>ADD BOT TO GROUP</b>
├ ➕ Click here to add bot to your group
└ 🎁 Refer & Earn: Get 5 Credits per invite!

📡 <b>@RLFLY_OFFICIAL</b>
"""

  bot.reply_to(message, text, reply_markup=main_menu())


# ============================================================
# ANTI-LINK PROTECTION & WARNING SYSTEM
# ============================================================


@bot.message_handler(func=lambda message: True, content_types=["text"])
def filter_links(message):
  if message.chat.type == "private":
    return

  if not message.text:
    return

  text = message.text.lower()
  has_link = False

  if message.entities:
    for entity in message.entities:
      if entity.type in ["url", "text_link"]:
        has_link = True

  if not has_link and any(
      keyword in text
      for keyword in [
          "http://",
          "https://",
          "t.me/",
          "www.",
          "joinchat",
          ".com",
          ".me",
      ]
  ):
    has_link = True

  if has_link:
    try:
      user_status = bot.get_chat_member(
          message.chat.id, message.from_user.id
      ).status
      if user_status in ["administrator", "creator"] or is_admin(
          message.from_user.id
      ):
        return

      bot.delete_message(message.chat.id, message.message_id)

      user = message.from_user
      chat_id = message.chat.id
      user_id = str(user.id)

      warnings_data = load_warnings()
      if str(chat_id) not in warnings_data:
        warnings_data[str(chat_id)] = {}

      current_warnings = warnings_data[str(chat_id)].get(user_id, 0) + 1
      warnings_data[str(chat_id)][user_id] = current_warnings
      save_warnings(warnings_data)

      MAX_WARNINGS = 3

      if current_warnings >= MAX_WARNINGS:
        mute_until = datetime.now() + timedelta(days=30)
        try:
          bot.restrict_chat_member(
              chat_id=chat_id,
              user_id=user.id,
              permissions=types.ChatPermissions(can_send_messages=False),
              until_date=int(mute_until.timestamp()),
          )
        except Exception as e:
          print(f"User mute error: {e}")

        warnings_data[str(chat_id)][user_id] = 0
        save_warnings(warnings_data)

        bot.send_message(
            chat_id,
            f"🔇 {user.first_name} ko 30 dino ke liye mute kar diya gaya hai.\n"
            f"Reason: link promotion ({MAX_WARNINGS}/{MAX_WARNINGS})",
        )
      else:
        display_name = user.first_name or "User"
        bot.send_message(
            chat_id,
            f"⚠️ Hey <b>{html.escape(display_name)}</b>, links are not allowed"
            f" in this group!\nWarnings: ({current_warnings}/3)\nReason: link"
            " promotion",
            parse_mode="HTML",
        )

    except Exception as e:
      print(f"Error handling link: {e}")


# ============================================================
# RUN BOT
# ============================================================

print("======================================")
print("        RLFLY TELEGRAM BOT")
print("======================================")
print("Bot is starting...")
print("Daily Credits:", DAILY_CREDITS)
print("Support:", SUPPORT_USERNAME)
print("Channel:", TELEGRAM_CHANNEL)
print("Pincode API: pincode-ng ONLY")
print("Auto Delete: 2 Minutes Enabled")
print("Group Members Check: Min 20 Members")
print("Anti-Link Protection & Warning System: Enabled")


# ============================================================
# START DAILY CREDIT RESET WORKER
# ============================================================

threading.Thread(
    target=daily_credit_reset_worker,
    daemon=True
).start()

print("[SYSTEM] Daily credit reset: ENABLED")
print("[SYSTEM] Reset time: 12:00 AM IST")
print("[SYSTEM] Daily credits:", DAILY_CREDITS)
print("======================================")


# ============================================================
# START TELEGRAM BOT
# ============================================================

print("Bot is running...")

while True:
    try:
        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60
        )

    except Exception as e:
        print("Polling error:", e)
        time.sleep(5)
