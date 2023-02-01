#Kanged From @TroJanZheX
import asyncio
import re
import ast

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp , replace
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import(
   del_all,
   find_filter,
   get_filters,
)
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & ~filters.edited & filters.incoming)
async def give_filter(client,message):
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)   

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):

    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This is not for you! ", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("This is not for you!",show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("𝘽𝘼𝘾𝙆", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"𝙋𝘼𝙂𝙀 {round(int(offset)/10)+1} / {round(total/10)}", callback_data="pages")]
        )
    elif off_set is None:
        btn.append([InlineKeyboardButton(f"𝙋𝘼𝙂𝙀 {round(int(offset)/10)+1} / {round(total/10)}", callback_data="pages"), InlineKeyboardButton("𝙉𝙀𝙓𝙏", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("𝘽𝘼𝘾𝙆", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"𝙋𝘼𝙂𝙀 {round(int(offset)/10)+1} / {round(total/10)}", callback_data="pages"),
                InlineKeyboardButton("𝙉𝙀𝙓𝙏", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup( 
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("This is not for you!", show_alert=True)
    if movie_  == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.message_id)
    if not movies:
        return await query.answer("This is not for you!", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for subtitle in database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k==False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit('❌This Subtitle Not Found In DataBase❌ \n\n\n 🎲 May be your spellings were wrong. So you can find the correct one in google. \n\n🎲 May be that movie is not in our database. So you can send a request \nusing @slofficialcotactbot, our admins will help you quickly. \n\n\n ')
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            grpid  = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == "creator") or (str(userid) in ADMINS):    
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!",show_alert=True)

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == "creator") or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Thats not for you!!",show_alert=True)


    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]
        
        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
                InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("𝘽𝘼𝘾𝙆", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode="md"
        )
        return

    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text('Some error occured!!', parse_mode="md")
        return

    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text(
                f"Some error occured!!",
                parse_mode="md"
            )
        return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occured!!",
                parse_mode="md"
            )
        return
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert,show_alert=True)

    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size=get_size(files.file_size)
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption=f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
            
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            elif P_TTI_SHOW_OFF:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption
                    )
                await query.answer('Check PM !',show_alert = True)
        except UserIsBlocked:
            await query.answer('Unblock the bot man !',show_alert = True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart 😒",show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size=get_size(files.file_size)
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption=f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption
            )

    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('𝙃𝙀𝙇𝙋', callback_data='help'),
            InlineKeyboardButton('𝘼𝘽𝙊𝙐𝙏', callback_data='about')
        ],[
           InlineKeyboardButton('🔍 𝙎𝙀𝘼𝙍𝘾𝙃 🔍', switch_inline_query_current_chat=''),
           InlineKeyboardButton('➕ 𝘼𝘿𝘿 ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('𝘾𝙇𝙊𝙎𝙀', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html',
           disable_web_page_preview=True
        )
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('𝐌𝐨𝐯𝐢𝐞𝐬 & 𝐓𝐯 𝐒𝐞𝐫𝐢𝐞𝐬', callback_data='film'),
            InlineKeyboardButton('𝐒𝐮𝐛𝐭𝐢𝐭𝐥𝐞𝐬', callback_data='subtitles')
            ],[
            InlineKeyboardButton('𝐓𝐡𝐞 𝐋𝐢𝐛𝐫𝐚𝐫𝐲', callback_data='library'),
            InlineKeyboardButton('𝐓𝐡𝐞 𝐅𝐢𝐠𝐡𝐭 𝐂𝐥𝐮𝐛', callback_data='fightclub')
            ],[
            InlineKeyboardButton('𝐌𝐨𝐝 𝐀𝐩𝐩 𝐒𝐭𝐨𝐫𝐞', callback_data='appsore'),
            InlineKeyboardButton('𝐂𝐫𝐚𝐜𝐤𝐞𝐝 𝐒𝐨𝐟𝐭𝐰𝐚𝐫𝐞𝐬', callback_data='software')
            ],[
            InlineKeyboardButton('𝐏𝐂 𝐆𝐚𝐦𝐞𝐬', callback_data='pcgames'),
            InlineKeyboardButton('𝐃𝐚𝐢𝐥𝐲 𝐍𝐞𝐰𝐬𝐩𝐚𝐩𝐞𝐫𝐬', callback_data='dailynews')
            ],[
            InlineKeyboardButton('𝐅𝐫𝐞𝐞 𝐈𝐧𝐭𝐞𝐫𝐧𝐞𝐭 𝐓𝐫𝐢𝐜𝐤𝐬', callback_data='freezone'),
            InlineKeyboardButton('𝐓𝐡𝐞 𝐌𝐞𝐦𝐞 𝐒𝐭𝐨𝐫𝐞', callback_data='meme')
            ],[
            InlineKeyboardButton('𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐆𝐚𝐦𝐞𝐬', callback_data='tggame'),
            InlineKeyboardButton('𝐅𝐫𝐞𝐞𝐝𝐨𝐦 𝐌𝐮𝐬𝐢𝐜', callback_data='music')
            ],[
            InlineKeyboardButton('𝐓𝐡𝐞 𝐂𝐨𝐦𝐢𝐜 𝐊𝐢𝐧𝐠𝐝𝐨𝐦 ', callback_data='comics')
            ],[ 
            InlineKeyboardButton('𝐀𝐛𝐨𝐮𝐭 𝐔𝐬', callback_data='about'),
            InlineKeyboardButton('📤', url=f'https://t.me/share/url?url=https://t.me/slofficialmain'),
            InlineKeyboardButton('𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐔𝐬', url=f'https://t.me/Slofficialcontactbot')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode='html',
            disable_web_page_preview=True
        )
    elif query.data == "about":
        buttons= [[
           InlineKeyboardButton('𝐒𝐡𝐚𝐫𝐞 & 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 𝐔𝐬', url=f'https://t.me/share/url?url=https://t.me/slofficialmain')
           ],[
           InlineKeyboardButton('𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐔𝐬', url=f'https://t.me/Slofficialcontactbot'),
           InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help')
           ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT,
            reply_markup=reply_markup,
            parse_mode='html',
            disable_web_page_preview=True
        )
    elif query.data == "film":
        buttons = [[
            InlineKeyboardButton('𝐍𝐞𝐰 𝐑𝐞𝐥𝐞𝐚𝐬𝐞', url=f"https://t.me/+6qUAQS0uOCphMDE1"),
            InlineKeyboardButton('𝐒𝐢𝐧𝐡𝐚𝐥𝐚 𝐌𝐨𝐯𝐢𝐞', url=f"https://t.me/+2jrQRGu6Mls4M2Fl")
        ],[
            InlineKeyboardButton('𝐓𝐯 𝐒𝐞𝐫𝐢𝐞𝐬 𝐖𝐨𝐫𝐥𝐝', url=f"https://t.me/+S9IF9-GLNfQxNmU1"),
            InlineKeyboardButton('𝐌𝐨𝐯𝐢𝐞 𝐂𝐨𝐥𝐥𝐞𝐜𝐭𝐢𝐨𝐧𝐬', url=f'https://t.me/+PIFOZgFxw1diNmI9')
        ],[
            InlineKeyboardButton('𝐒𝐢𝐧𝐡𝐚𝐥𝐚 𝐃𝐮𝐛𝐛𝐞𝐝 𝐌𝐨𝐯𝐢𝐞𝐬/ 𝐓𝐯 𝐒𝐞𝐫𝐢𝐞𝐬', url=f"https://t.me/+hRpevOadeGphMzNl")
        ],[
            InlineKeyboardButton('𝐑𝐞𝐚𝐝 𝐌𝐨𝐫𝐞...', url=f"https://telegra.ph/Read-more-07-09")
        ],[
            InlineKeyboardButton('𝐅𝐫𝐞𝐪𝐮𝐞𝐧𝐭𝐥𝐲 𝐀𝐬𝐤𝐞𝐝 𝐐𝐮𝐞𝐬𝐭𝐢𝐨𝐧𝐬', url=f"https://telegra.ph/Frequently-Asked-QuestionsAbout-Movies--Tv-Series-07-10")
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='comics'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='subtitles')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FILM_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "subtitles":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/sinhala_subtitle_slofficial')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='film'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='library') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SUBTITLES_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "library":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/Slofficialbooks')
        ],[
            InlineKeyboardButton('𝐂𝐫𝐞𝐚𝐭𝐞 𝐏𝐃𝐅...', url=f'https://telegra.ph/Create-PDF-07-10')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='subtitles'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='fightclub') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.LIBRARY_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "fightclub":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/+mGBUF1OhFJA2ZWQ1')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='library'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='appstore') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FIGHTCLUB_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "appstore":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/Slmodstore')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='fightclub'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='software') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.APPSTORE_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "software":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/Pcsoftwaressl')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='appstore'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='pcgames') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOFTWARE_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "pcgames":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/+S7iZt5viFF3JnU7n')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='software'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='dailynews') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PCGAMES_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "dailynews":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/sldailynews')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='pcgames'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='freezone') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DAILYNEWS_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "freezone":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/FreeZonebySLofficial')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='dailynews'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='meme') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FREEZONE_TXT,
            reply_markup=reply_markup,
            parse_mode='html',
            disable_web_page_preview=True
        )
    elif query.data == "meme":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/slofficialmemes')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='freezone'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='tggame') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MEME_TXT,
            reply_markup=reply_markup,
            parse_mode='html',
            disable_web_page_preview=True
        )
    elif query.data == "tggame":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/slofficialgames')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='meme'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='music') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TGGAME_TXT,
            reply_markup=reply_markup,
            parse_mode='html',
            disable_web_page_preview=True
        )
    elif query.data == "music":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/freedom_musics')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='tggame'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='comics') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MUSIC_TXT,
            reply_markup=reply_markup,
            parse_mode='html',
            disable_web_page_preview=True
        )
    elif query.data == "comics":
        buttons = [[
            InlineKeyboardButton('𝐉𝐨𝐢𝐧 𝐍𝐨𝐰', url=f'https://t.me/the_comic_kingdom')
        ],[
            InlineKeyboardButton('𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬', callback_data='music'),
            InlineKeyboardButton('𝐇𝐨𝐦𝐞', callback_data='help'),
            InlineKeyboardButton('𝐍𝐞𝐱𝐭', callback_data='film') 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.COMICS_TXT,
            reply_markup=reply_markup,
            parse_mode='html',
            disable_web_page_preview=True
        )
 
 
async def auto_filter(client, msg, spoll=False):
   if not spoll:
        message = msg
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if SPELL_CHECK_REPLY:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
   else:
        message = msg.message.reply_to_message # msg will be callback query
        search, files, offset, total_results = spoll
   if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
   else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'files#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

   if offset != "":
        key = f"{message.chat.id}-{message.message_id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"𝙋𝘼𝙂𝙀 1/{round(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝙉𝙀𝙓𝙏",callback_data=f"next_{req}_{key}_{offset}")]
        )
   else:
        btn.append(
            [InlineKeyboardButton(text="𝙋𝘼𝙂𝙀 1/1",callback_data="pages")]
        )
   imdb = await get_poster(search, file=(files[0]).file_name) if IMDB else None
   if imdb:
        cap = IMDB_TEMPLATE.format(
            query = search,
            title = imdb['title'],
            votes = imdb['votes'],
            aka = imdb["aka"],
            seasons = imdb["seasons"],
            box_office = imdb['box_office'],
            localized_title = imdb['localized_title'],
            kind = imdb['kind'],
            imdb_id = imdb["imdb_id"],
            cast = imdb["cast"],
            runtime = imdb["runtime"],
            countries = imdb["countries"],
            certificates = imdb["certificates"],
            languages = imdb["languages"],
            director = imdb["director"],
            writer = imdb["writer"],
            producer = imdb["producer"],
            composer = imdb["composer"],
            cinematographer = imdb["cinematographer"],
            music_team = imdb["music_team"],
            distributors = imdb["distributors"],
            release_date = imdb['release_date'],
            year = imdb['year'],
            genres = imdb['genres'],
            poster = imdb['poster'],
            plot = imdb['plot'],
            rating = imdb['rating'],
            url = imdb['url'],
            **locals()
        )
   else:
        cap = f"𝙃𝙀𝙍𝙀 𝙒𝙃𝘼𝙏 𝙄 𝙁𝙊𝙐𝙉𝘿 𝙏𝙊, {search}"
   if imdb and imdb.get('poster'):
        try:
          await message.reply(text=cap, reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
          await message.reply(text=cap, reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
   else:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
   if spoll:
        await msg.message.delete()
        

async def advantage_spell_chok(msg):
    query = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)", "", msg.text, flags=re.IGNORECASE) # plis contribute some common words 
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("I couldn't find any movie in that name.")
        await asyncio.sleep(8)
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE) # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)', '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*", re.IGNORECASE) # match something like Watch Niram | Amazon Prime 
        for mv in g_s:
            match  = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed)) # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True) # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist)) # removing duplicates
    if not movielist:
        k = await msg.reply("𝙄 𝘾𝙊𝙐𝙇𝘿𝙉'𝙏 𝙁𝙄𝙉𝘿 𝘼𝙉𝙔 𝙁𝙄𝙇𝙀 𝙍𝙀𝙇𝘼𝙏𝙀𝘿 𝙏𝙊 𝙏𝙃𝘼𝙏. 𝘾𝙃𝙀𝘾𝙆 𝙔𝙊𝙐𝙍 𝙎𝙋𝙀𝙇𝙇𝙄𝙉𝙂𝙎 𝙊𝙍 𝙍𝙀𝙋𝙊𝙍𝙏 𝙏𝙊 𝙊𝙐𝙍 𝘼𝘿𝙈𝙄𝙉𝙎 𝙑𝙄𝘼 @𝙎𝙇𝙊𝙁𝙁𝙄𝘾𝙄𝘼𝙇𝘾𝙊𝙉𝙏𝘼𝘾𝙏𝘽𝙊𝙏 ")
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.message_id] = movielist
    btn = [[
                InlineKeyboardButton(
                    text=movie.strip(),
                    callback_data=f"spolling#{user}#{k}",
                )
            ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    await msg.reply("𝙄 𝘾𝙊𝙐𝙇𝘿𝙉'𝙏 𝙁𝙄𝙉𝘿 𝘼𝙉𝙔 𝙁𝙄𝙇𝙀 𝙍𝙀𝙇𝘼𝙏𝙀𝘿 𝙏𝙊 𝙏𝙃𝘼𝙏. 𝘾𝙃𝙀𝘾𝙆 𝙔𝙊𝙐𝙍 𝙎𝙋𝙀𝙇𝙇𝙄𝙉𝙂𝙎 𝙊𝙍 𝙍𝙀𝙋𝙊𝙍𝙏 𝙏𝙊 𝙊𝙐𝙍 𝘼𝘿𝙈𝙄𝙉𝙎 𝙑𝙄𝘼 @𝙎𝙇𝙊𝙁𝙁𝙄𝘾𝙄𝘼𝙇𝘾𝙊𝙉𝙏𝘼𝘾𝙏𝘽𝙊𝙏", reply_markup=InlineKeyboardMarkup(btn))
    

async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id, 
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id = reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id = reply_id
                        )
                    else:
                        button = eval(btn) 
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id = reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
