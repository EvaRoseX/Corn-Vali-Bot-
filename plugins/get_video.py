from os import environ
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database.users_db import db
from info import PROTECT_CONTENT, DAILY_LIMIT, PREMIUM_DAILY_LIMIT, VERIFICATION_DAILY_LIMIT, FSUB, IS_VERIFY
import asyncio
from plugins.verification import av_x_verification
from plugins.ban_manager import ban_manager
from utils import temp, auto_delete_message, is_user_joined


@Client.on_message(filters.command("getvideo") | filters.regex(r"(?i)get video"))
async def handle_video_request(client, m: Message):

    # Safety check
    if not m.from_user:
        return

    # Force subscribe check
    if FSUB and not await is_user_joined(client, m):
        return

    user_id = m.from_user.id
    username = m.from_user.username or m.from_user.first_name or "Unknown"

    # Ban check
    if await ban_manager.check_ban(client, m):
        return

    # Premium + limit info
    is_premium = await db.has_premium_access(user_id)
    # Define limits based on status
    current_limit = PREMIUM_DAILY_LIMIT if is_premium else DAILY_LIMIT
    
    used = await db.get_video_count(user_id) or 0

    # ------------------------------------------------
    # LIMIT & VERIFICATION & PREMIUM SYSTEM
    # ------------------------------------------------
    
    # Message for when any absolute max limit is reached
    limit_reached_msg = (
        f"𝖸𝗈𝗎'𝗏𝖾 𝖱𝖾𝖺𝖼𝗁𝖾𝖽 𝖸𝗈𝗎𝗋 𝖣𝖺𝗂𝗅𝗒 𝖫𝗂𝗆𝗂𝗍 𝖮𝖿 {used} 𝖥𝗂𝗅𝖾𝗌.\n\n"
        "𝖳𝗋𝗒 𝖠𝗀𝖺𝗂𝗇 𝖳𝗈𝗆𝗈𝗋𝗋牟𝗈𝗐!\n"
        "𝖮𝗋 𝖯𝗎𝗋𝖼𝗁𝖺𝗌𝖾 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝗉𝗂𝗈𝗇 𝖳𝗈 𝖡𝗈𝗈𝗌𝗍 𝖸𝗈𝗎𝗋 𝖣𝖺𝗂𝗅𝗒 𝖫𝗂模𝗆𝗂𝗍"
    )
    buy_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("• 𝖯𝗎𝗋𝖼𝗁𝖺𝗌𝖾 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇 •", callback_data="get")]
    ])

    if is_premium:
        # Premium User Logic
        if used >= PREMIUM_DAILY_LIMIT:
            return await m.reply(
                f"𝖸𝗈𝗎'𝗏𝖾 𝖱𝖾𝖺𝖼𝗁𝖾𝖽 𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖫𝗂𝗆𝗂𝗍 𝖮𝖿 {PREMIUM_DAILY_LIMIT} 𝖥𝗂𝗅𝖾𝗌.\n"
                f"𝖳𝗋𝗒 𝖠𝗀𝖺𝗂𝗇 𝖳𝗈𝗆𝗈𝗋𝗋𝗈𝗐!"
            )
    else:
        if used >= VERIFICATION_DAILY_LIMIT:
            return await m.reply(limit_reached_msg, reply_markup=buy_button)
        if used >= DAILY_LIMIT:
            if IS_VERIFY:
                verified = await av_x_verification(client, m)
                if not verified:
                    return 
            else:
                return await m.reply(limit_reached_msg, reply_markup=buy_button)

    # ------------------------------------------------
    # GET VIDEO
    # ------------------------------------------------
    video_id = await db.get_unseen_video(user_id)

    # FIXED: Check if video_id is None, False, or empty string ""
    if not video_id or str(video_id).strip() == "":
        try:
            video_id = await db.get_random_video()
        except Exception as e:
            print(f"[Random Video Error] {e}")
            return await m.reply("❌ Error fetching a random video from database.")

    # FIXED: Double check after random fetch
    if not video_id or str(video_id).strip() == "":
        return await m.reply("❌ No valid videos found in the database. Please add files first.")

    # ------------------------------------------------
    # SEND VIDEO
    # ------------------------------------------------
    try:
        sent = await client.send_video(
            chat_id=m.chat.id,
            video=str(video_id).strip(), # FIXED: Added strip to remove unwanted spaces
            protect_content=PROTECT_CONTENT,
            caption=(
                f"𝘗𝘰𝘸𝘦𝘳𝘦𝘥 𝘉𝘺: {temp.B_LINK}\n\n"
                "<blockquote>"
                "ᴛʜɪꜱ ꜰɪʟᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ 10 ᴍɪɴᴜᴛᴇꜱ.\n"
                "ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛʜɪꜱ ꜰɪʟᴇ ꜱᴏᴍᴇᴡʜᴇʀᴇ ᴇʟꜱᴇ "
                "ᴏʀ ꜱᴀᴠᴇ ɪɴ ꜱᴀᴠᴇ章ᴅ ᴍᴇꜱꜱᴀɢᴇꜱ."
                "</blockquote>"
            ),
            reply_to_message_id=m.id
        )

        # Increase daily count ONLY after successful send
        await db.increase_video_count(user_id, username)

        # Auto delete in background
        asyncio.create_task(auto_delete_message(m, sent))

    except Exception as e:
        await m.reply(f"❌ Failed to send video: {str(e)}\n\n⚠️ *Note:* The file ID in database might be broken/invalid.")
