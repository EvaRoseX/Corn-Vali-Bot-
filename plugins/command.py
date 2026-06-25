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

    # 1️⃣ FORMAT: Agar link me 'avx-' prefix ho
    if argument and argument.startswith("avx-"):
        search_id = argument.replace("avx-", "")
        await send_requested_file(client, message, user_id, search_id)
        return

    # 2️⃣ NEW FIXED: Agar link me DIRECT TELEGRAM FILE_ID ho (Jaise BAACAg...)
    if argument:
        try:
            # Agar id direct telegram ki file_id hai toh bina db check ke direct send karo
            sent = await client.send_video(
                chat_id=message.chat.id,
                video=str(argument).strip(),
                protect_content=True,
                caption="🔥 <b>Your Requested Video Is Ready!</b> 🔥\n\n<i>Enjoy streaming...</i>"
            )
            
            # Optional: Auto delete after 10 mins task
            try:
                from utils import auto_delete_message
                asyncio.create_task(auto_delete_message(message, sent))
            except:
                pass
            return
            
        except Exception as e:
            print(f"Direct Send Error: {e}")
            # Agar direct send fail ho (manlo wo file_id na ho kar unique_id ho), toh purane system par bhej do
            try:
                await send_requested_file(client, message, user_id, argument)
                return
            except Exception as err:
                return await message.reply("❌ Video send karne me dikkat aayi ya file expire ho gayi hai.")

    # --- New User Add Process ---
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        try:
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(me2, user_id, mention))
        except Exception:
            pass
            
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Get Video"), KeyboardButton("Brazzers")],
            [KeyboardButton("My plan"), KeyboardButton("Subscription")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await message.reply_photo(
        photo=START_PIC,
        caption=script.START_TXT.format(mention, temp.U_NAME, temp.U_NAME),
        reply_markup=reply_keyboard,
        has_spoiler=True
    )
