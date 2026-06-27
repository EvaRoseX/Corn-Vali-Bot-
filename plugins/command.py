import datetime
import asyncio
import random
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, MediaEmpty
from Script import script
from database.users_db import db
from info import LOG_CHANNEL, PREMIUM_LOGS, FSUB, QR_CODE_IMAGE, DAILY_LIMIT, PREMIUM_DAILY_LIMIT, UPI_ID
from utils import temp, is_user_joined
from plugins.verification import verify_user_on_start
from plugins.send_file import send_requested_file
from plugins.refer import refer_on_start

# =================================================
# ⚙️ FIXED DIRECT CHANNEL SETTING
# =================================================
MY_PHOTO_CHANNEL = -1004493848925  

# =================================================
# 🖼️ MULTIPLE START IMAGES LIST
# =================================================
START_PICS_LIST = [
    "https://i.ibb.co/vv3vZ5Xg/photo-2026-06-26-12-05-20-7655674163104841744.jpg",
    "https://i.ibb.co/6cKdRWbV/photo-2026-06-26-12-05-24-7655674201759547408.jpg",
    "https://i.ibb.co/84bJ6P79/photo-2026-06-26-12-05-26-7655674223234383888.jpg",
    "https://i.ibb.co/0w6w5BW/photo-2026-06-26-12-05-29-7655674261889089552.jpg",
    "https://i.ibb.co/zHXf41Zs/photo-2026-06-26-12-05-30-7655674304838762512.jpg",
    "https://i.ibb.co/HfDpcqqk/photo-2026-06-26-12-05-33-7655674326313598980.jpg"
]

# =================================================
# 🚀 START COMMAND (CLEAN SINGLE-MESSAGE SYSTEM)
# =================================================
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user_id = message.from_user.id
    mention = message.from_user.mention
    me2 = (await client.get_me()).mention
    
    if FSUB and not await is_user_joined(client, message):
        return
        
    argument = message.command[1] if len(message.command) > 1 else None

    if argument and argument.startswith('avbotz'):
        await verify_user_on_start(client, message)
        return

    if argument == "terms":
        await send_legal_text(client, message, script.TERMS_TXT)
        return
    elif argument == "disclaimer":
        await send_legal_text(client, message, script.DISCLAIMER_TXT)
        return
    elif argument == "help":
        await send_legal_text(client, message, script.HELP_TXT)
        return
    elif argument == "about":
        await send_about_text(client, message)
        return

    if argument and argument.startswith("reff_"):
        try:
            await refer_on_start(client, message)
            return 
        except Exception as e:
            print(f"Referral Error: {e}")

    if argument:
        search_id = argument.replace("avx-", "")
        for attempt in range(5):
            try:
                await send_requested_file(client, message, user_id, search_id)
                return 
            except (MediaEmpty, Exception) as e:
                if "MEDIA_EMPTY" in str(e) or isinstance(e, MediaEmpty):
                    print(f"⚠️ Broken File ID auto-bypassed: {search_id}")
                    try:
                        pipeline = [{"$sample": {"size": 1}}]
                        cursor = db.videos.aggregate(pipeline)
                        result = await cursor.to_list(length=1)
                        if result:
                            search_id = result[0]["file_unique_id"]
                            continue 
                    except Exception as db_err:
                        print(f"Backup fetch error: {db_err}")
                        break
                else:
                    print(f"Other Error: {e}")
                    break
        return await message.reply("🍿 <b>Server busy!</b> Kripya channel se kisi doosri video par click karein.")

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        try:
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(me2, user_id, mention))
        except Exception:
            pass

    # 🔗 INLINE KEYBOARD (Ab ye direct photo ke niche set hoga bina kisi gap ke)
    inline_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Update Channel 📢", url="https://t.me/ERBotsUpdate"),
            InlineKeyboardButton("Buy Source Code 💰", url="https://t.me/EvaRoseX")
        ]
    ])

    random_pic = random.choice(START_PICS_LIST)

    # Photo aur inline buttons ek sath single message me lock ho gayi
    await message.reply_photo(
        photo=random_pic,
        caption=script.START_TXT.format(mention, temp.U_NAME, temp.U_NAME),
        reply_markup=inline_keyboard,
        has_spoiler=True
    )

# =================================================
# 🖼️ GET PHOTO HANDLER (100% FILTER FOR PHOTOS ONLY)
# =================================================
@Client.on_message((filters.regex(r"^Get Photo$") | filters.command("photo")) & filters.private)
async def send_photo_from_channel(client, message: Message):
    processing_msg = await message.reply("🔄 <b>Aapke bhandar se photo nikal raha hoon...</b>")
    
    # Jab user active photo maangega, tabhi nichla main-menu keyboard popup hoga
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Get Video"), KeyboardButton("Get Photo")],
            [KeyboardButton("Brazzers")],
            [KeyboardButton("My plan"), KeyboardButton("Subscription")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    try:
        chat_details = await client.get_chat(MY_PHOTO_CHANNEL)
        latest_id = chat_details.pinned_message.id if chat_details.pinned_message else 1500
            
        if not_id or latest_id < 2:
            latest_id = 700 
            
        for _ in range(60): 
            random_msg_id = random.randint(1, latest_id)
            try:
                target_msg = await client.get_messages(MY_PHOTO_CHANNEL, random_msg_id)
                
                if not target_msg or not target_msg.photo:
                    continue
                
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=MY_PHOTO_CHANNEL,
                    message_id=random_msg_id,
                    caption="<b>Here is your requested photo! ✨\n\nClick 'Get Photo' again for more!</b>",
                    reply_markup=reply_keyboard # Photo aate hi user ka menu keyboard open ho jayega
                )
                await processing_msg.delete()
                return 
            except Exception:
                continue 
                
        await processing_msg.edit("⚠️ <b>Kuch posts skip ho gayi ya range me photo nahi mili, kripya dubara click karein!</b>")
        
    except Exception as e:
        print(f"Photo Fetch Error: {e}")
        await processing_msg.edit(f"⚠️ <b>Koshish nakam rahi!</b> Debug Info: {e}")

# =================================================
# 📜 HELPER HANDLERS
# =================================================
@Client.on_message(filters.command("disclaimer") & filters.private)
async def legal_disclaimer(client, message: Message):
    await send_legal_text(client, message, script.DISCLAIMER_TXT)

@Client.on_message(filters.command("terms") & filters.private)
async def legal_terms(client, message: Message):
    await send_legal_text(client, message, script.TERMS_TXT)

@Client.on_message(filters.command("about") & filters.private)
async def legal_about(client, message: Message):
    await send_about_text(client, message)

@Client.on_message(filters.command("help") & filters.private)
async def legal_hepl(client, message: Message):
    await send_legal_text(client, message, script.HELP_TXT)
    
async def send_legal_text(client, message, text):
    inline_buttons = [[InlineKeyboardButton('• ᴄʟᴏsᴇ •', callback_data='close_data')]]
    await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(inline_buttons), disable_web_page_preview=True)

async def send_about_text(client, message):
    inline_buttons = [[InlineKeyboardButton('• ᴄʟᴏsᴇ •', callback_data='close_data')]]
    await message.reply_text(text=script.ABOUT_TXT.format(temp.B_NAME, temp.B_LINK), reply_markup=InlineKeyboardMarkup(inline_buttons), disable_web_page_preview=True)

# =========================================================
# 🔙 CALLBACK QUERY HANDLER
# =========================================================
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    if data == "close_data":
        await query.message.delete()
    elif data == "get":
        buttons = [[InlineKeyboardButton('• 𝖢𝗅𝗈𝑠𝖾 •', callback_data='close_data')]]
        await query.message.reply_photo(
            photo=QR_CODE_IMAGE,
            caption=script.SEENBUY_TXT.format(DAILY_LIMIT, PREMIUM_DAILY_LIMIT, UPI_ID),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
