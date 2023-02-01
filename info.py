import re
from os import environ

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = 4188464
API_HASH = "f6189c2a8ef9335fc0d0ece65b2d9057"
BOT_TOKEN = "5567826874:AAEwNlJk3TPZhKD6XWvV8VW3PP85D4Kyzr8"

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = True
PICS = ""

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS','1710688204').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1001625189909').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS','').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = ""
auth_grp =""
AUTH_CHANNEL = (auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# MongoDB information
DATABASE_URI = "mongodb+srv://slofficial:slofficial@cluster0.mwxky.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = environ.get('DATABASE_NAME', "cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegr')

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'slofficialcommunity')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "False")), False)
IMDB = is_enabled((environ.get('IMDB', "True")), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), True)
CUSTOM_FILE_CAPTION = "<b>{file_caption}</b>"
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE","\n🎬 𝙏𝙞𝙩𝙡𝙚 \t: <i><b>{title}</b></i> 🔘 <b>{kind}</b>\n⭐️ 𝙍𝙖𝙩𝙞𝙣𝙜 \t: <b>{rating}/10</b> (<i>From {votes} user ratings.)</i>\n\n ‌©ꜱʟ ᴏꜰꜰɪᴄɪᴀʟ")
IMDB_TEMPLATE2 = environ.get("IMDB_TEMPLATE2","\n🎬 𝙏𝙞𝙩𝙡𝙚 \t: <i><b>{title}</b></i> 🔘 <b>{kind}</b>\n ⭐️ 𝙍𝙖𝙩𝙞𝙣𝙜 \t: <b>{rating}/10</b> (<i>From {votes} user ratings.)</i>\n 📆 𝙍𝙚𝙡𝙚𝙖𝙨𝙚 𝙞𝙣𝙛𝙤 \t: <b>{release_date}</b>\n 🎃 𝙂𝙚𝙣𝙧𝙚𝙨 \t: <b>{genres}</b>\n 🎙️ 𝙇𝙖𝙣𝙜𝙪𝙖𝙜𝙚(𝙨) \t: <b>{languages}</b>\n 🗂 𝙎𝙚𝙖𝙨𝙤𝙣𝙨 \t: <b>{seasons}</b>\n 🎛️ 𝙍𝙪𝙣 𝙩𝙞𝙢𝙚 \t: <b>{runtime} Mins</b>\n 🤵 𝘿𝙞𝙧𝙚𝙘𝙩𝙤𝙧(𝙨) \t: <b>{director}</b>\n 📝 𝙒𝙧𝙞𝙩𝙚𝙧(𝙨) \t: <b>{writer}</b>\n ✏️ 𝙎𝙩𝙤𝙧𝙮 𝙇𝙞𝙣𝙚 \t: <b>{plot}</b> \n\n ‌‎<b>©️ＳＬＯＦＦＩＣＩＡＬ</b>")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "False"), False)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))

LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two seperate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as diffrent buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your Currect IMDB template is {IMDB_TEMPLATE}"
