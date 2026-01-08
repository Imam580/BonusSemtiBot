import os
import time
import random
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
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
TOKEN = os.environ.get("TOKEN")

# ================= GLOBAL =================
cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1
cekilis_kazananlar = []

BOT_BASLANGIC_ZAMANI = time.time()
kullanici_mesaj_sayisi = {}
min_mesaj_sayisi = 0

# ================= KANALLAR =================
ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@hergunikioran",
    "@BahisKarhanesi",
    "@ozel_oran_2024",
]

# ================= DOĞUM BONUS =================
DOGUM_BONUS_BUTONLARI = [
    ("ZBAHİS", "https://shoort.im/zbahis"),
    ("PADİŞAHBET", "https://shoort.im/padisahbet"),
    ("FİXBET", "https://shoort.im/fixbet"),
    ("BETMATİK", "https://shoort.im/betmatik"),
    ("BAYSPİN", "http://shoort.im/bayspinn"),
    ("BETOFFİCE", "https://shoort.im/betoffice"),
    ("BETİNE", "https://shoort.im/betinee"),
    ("XSLOT", "https://shoort.im/xslot"),
    ("STARZBET", "https://shoort.im/starzbet"),
    ("BETPİPO", "https://shoort.im/betpipo"),
    ("NORABAHİS", "https://shoort.im/norabahis"),
    ("SPİNCO", "https://shoort.im/spinco"),
    ("HERMESBET", "https://hermesbet.wiki/telegram"),
    ("CRATOSBET", "https://shoort.im/cratosbet"),
    ("BETKOM", "http://shoort.im/betkom"),
    ("MASTERBET", "https://shoort.im/masterbetting"),
    ("MARİOBET", "http://shoort.im/mariobonus"),
    ("BETWİLD", "http://shoort.im/betwild"),
    ("PASHAGAMING", "https://shoort.im/pashagaming"),
    ("ROYALBET", "https://shoort.im/royalbet"),
    ("RADİSSONBET", "https://shoort.im/radissonbet"),
    ("JOJOBET", "https://dub.pro/jojoyagit"),
    ("HOLIGANBET", "http://t.t2m.io/holiguncel"),
    ("KAVBET", "https://shoort.im/kavbet"),
    ("BETGİT", "https://shoort.im/betgit"),
    ("MADRIDBET", "https://shoort.im/madridbet"),
    ("ARTEMİSBET", "https://shoort.im/artemisbet"),
]

# ================= KÜFÜR / SPAM =================
KUFUR_LISTESI = [
    "amk","aq","amq","orospu","orospu çocuğu","piç","ibne",
    "yarrak","yarak","sik","siktir","amcık","anan","amına"
]

kufur_sayaci = {}
spam_log = {}
spam_warn = {}

SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= SİTE FİLTRELER =================
filters_dict = {
    "zbahis": "https://shoort.im/zbahis",
    "padisahbet": "https://shoort.im/padisahbet",
    "fixbet": "https://shoort.im/fixbet",
    "betoffice": "https://shoort.im/betoffice",
    "betpipo": "https://shoort.im/betpipo",
}

# ================= ADMIN =================
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
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
                until_date=int(time.time()) + sure
            )
            return

# ================= LİNK =================
async def link_engel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return

    if any(x in update.message.text.lower() for x in ["http","t.me","www"]):
        await update.message.delete()
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.from_user.id,
            ChatPermissions(can_send_messages=False),
            until_date=int(time.time()) + 3600
        )

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
        if spam_warn.get(uid):
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time()) + 3600
            )
            spam_log[uid] = []
            spam_warn[uid] = False
        else:
            spam_warn[uid] = True

# ================= SİTE =================
async def site_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for k, v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton(f"{k.upper()} GİRİŞ", url=v)]]
            )
            await update.message.reply_text("🔗 Giriş Linki:", reply_markup=kb)
            return

# ================= EVERY =================
async def every_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" in update.message.text.lower():
        await update.message.reply_text("🔥 EveryMatrix Siteleri aktif.")

# ================= DOĞUM =================
async def dogum_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "doğum" not in update.message.text.lower():
        return

    kb, row = [], []
    for i,(n,l) in enumerate(DOGUM_BONUS_BUTONLARI,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i % 2 == 0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🎁 DOĞUM GÜNÜ BONUSLARI",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= !SİL =================
async def sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    try:
        n = int(update.message.text.split()[1])
    except:
        return
    for i in range(n):
        try:
            await context.bot.delete_message(
                update.effective_chat.id,
                update.message.message_id - i
            )
        except:
            pass

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(tg_filters.Regex(r"^!sil \d+$"), sil))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, kufur_kontrol), group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, link_engel), group=1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, spam_kontrol), group=2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every_kontrol), group=3)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, dogum_kontrol), group=4)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, site_kontrol), group=5)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
