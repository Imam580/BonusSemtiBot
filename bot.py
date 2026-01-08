# ================= IMPORT =================
import os
import time
import random
from datetime import timedelta
from dotenv import load_dotenv

from telegram import (
    Update,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters as tg_filters
)

# ================= ENV =================
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ================= GLOBAL =================
cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1

# ================= KÜFÜR =================
KUFUR_LISTESI = [
    "amk","aq","amq","orospu","orospu çocuğu","piç","ibne",
    "yarrak","yarak","sik","siktir","amcık","anan","amına"
]
kufur_sayaci = {}

# ================= SPAM =================
spam_log = {}
SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= SİTELER =================
filters_dict = {
    "zbahis": "https://shoort.im/zbahis",
    "padisahbet": "https://shoort.im/padisahbet",
    "fixbet": "https://shoort.im/fixbet",
    "betmatik": "https://shoort.im/betmatik",
    "betoffice": "https://shoort.im/betoffice",
    "xslot": "https://shoort.im/xslot",
    "starzbet": "https://shoort.im/starzbet",
    "betpipo": "https://shoort.im/betpipo",
    "norabahis": "https://shoort.im/norabahis",
    "spinco": "https://shoort.im/spinco",
    "cratosbet": "https://shoort.im/cratosbet",
    "betwild": "https://shoort.im/betwild",
    "pashagaming": "https://shoort.im/pashagaming",
    "royalbet": "https://shoort.im/royalbet",
    "radissonbet": "https://shoort.im/radissonbet"
}

# ================= EVERY =================
EVERY_SPONSOR = [
    ("HIZLICASINO", "https://shoort.im/hizlicasino"),
    ("EGEBET", "https://shoort.im/egebet"),
    ("KAVBET", "https://shoort.im/kavbet"),
    ("PUSULABET", "https://shoort.im/pusulabet"),
    ("HITBET", "https://shoort.im/hitbet"),
    ("ARTEMISBET", "https://shoort.im/artemisbet"),
]

EVERY_DIGER = [
    ("JOJOBET", "http://dub.pro/jojoyagit"),
    ("HOLIGANBET", "https://dub.pro/holiguncel"),
    ("MATGUNCEL", "http://dub.is/matguncel"),
    ("MEGAGUNCEL", "https://dub.is/megaguncel"),
    ("ZIRVE", "https://dub.is/zirveguncel"),
    ("NAKITBAHIS", "https://shoort.in/nakitbahis"),
]

# ================= ADMIN =================
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = await context.bot.get_chat_member(
            update.effective_chat.id, update.effective_user.id
        )
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

# ================= KÜFÜR =================
async def kufur_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return

    text = update.message.text.lower()
    uid = update.message.from_user.id

    for k in KUFUR_LISTESI:
        if k in text:
            await update.message.delete()
            kufur_sayaci[uid] = kufur_sayaci.get(uid, 0) + 1
            sure = 300 if kufur_sayaci[uid] == 1 else 3600
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                uid,
                ChatPermissions(can_send_messages=False),
                until_date=timedelta(seconds=sure)
            )
            return

# ================= SPAM =================
async def spam_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return

    uid = update.message.from_user.id
    now = time.time()
    spam_log.setdefault(uid, []).append(now)
    spam_log[uid] = [t for t in spam_log[uid] if now - t <= SPAM_SURE]

    if len(spam_log[uid]) >= SPAM_LIMIT:
        await update.message.delete()

# ================= SİTE BUTON =================
async def site_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for k, v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]
            ])
            await update.message.reply_text(
                f"✅ <b>{k.upper()} GİRİŞ</b>",
                reply_markup=kb,
                parse_mode="HTML"
            )
            return

# ===
