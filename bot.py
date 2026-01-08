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
TOKEN = os.getenv("TOKEN")

# ================= GLOBAL =================
cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazananlar = []
min_mesaj_sayisi = 0
kullanici_mesaj_sayisi = {}
BOT_BASLANGIC = time.time()

# ================= SPAM =================
SPAM_SURE = 5
SPAM_LIMIT = 5
spam_log = {}
spam_warn = {}

# ================= KÜFÜR =================
KUFUR = ["amk","aq","orospu","piç","ibne","sik","amına"]

# ================= SPONSOR =================
SPONSOR_SITELER = [
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
    ("COINBAR", "http://shoort.in/coinbar"),
    ("NAKITBAHIS", "https://shoort.in/nakitbahis"),
]

DOGUM_BONUS = [
    ("ZBAHİS", "https://shoort.im/zbahis"),
    ("PADİŞAHBET", "https://shoort.im/padisahbet"),
    ("FİXBET", "https://shoort.im/fixbet"),
    ("BETPİPO", "https://shoort.im/betpipo"),
]

# ================= FİLTRELER =================
filters_dict = {}

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

# ================= /FILTER =================
async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: /filter site link")
        return
    key = context.args[0].lower()
    link = context.args[1]
    filters_dict[key] = link
    await update.message.reply_text(f"✅ Eklendi: {key}")

# ================= /REMOVE =================
async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    if not context.args:
        return
    key = context.args[0].lower()
    if key in filters_dict:
        del filters_dict[key]
        await update.message.reply_text(f"❌ Silindi: {key}")
    else:
        await update.message.reply_text("Bulunamadı")

# ================= MESAJ SAY =================
async def mesaj_say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.date.timestamp() < BOT_BASLANGIC:
        return
    uid = update.message.from_user.id
    kullanici_mesaj_sayisi[uid] = kullanici_mesaj_sayisi.get(uid, 0) + 1

# ================= /MESAJ =================
async def mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global min_mesaj_sayisi
    if not await is_admin(update, context):
        return
    if not context.args or not context.args[0].isdigit():
        return
    min_mesaj_sayisi = int(context.args[0])
    await update.message.reply_text(f"📨 Minimum mesaj: {min_mesaj_sayisi}")

# ================= /KONTROL =================
async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    if not cekilis_kazananlar:
        await update.message.reply_text("Kazanan yok")
        return

    msg = "📋 KAZANAN KONTROL\n\n"
    for uid in cekilis_kazananlar:
        sayi = kullanici_mesaj_sayisi.get(uid, 0)
        durum = "✅" if sayi >= min_mesaj_sayisi else "❌"
        msg += f"{durum} {uid} → {sayi} mesaj\n"

    await update.message.reply_text(msg)

# ================= SİTE =================
async def site_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for k, v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ",
                    url=v
                )]
            ])
            await update.message.reply_text(
                f"🔗 {k.upper()} GİRİŞ",
                reply_markup=kb
            )
            return

# ================= EVERY =================
async def every(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" not in update.message.text.lower():
        return
    kb, row = [], []
    for i,(n,l) in enumerate(SPONSOR_SITELER + EVERY_DIGER,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i % 2 == 0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🔥 EVERYMATRIX SİTELERİ",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= DOĞUM =================
async def dogum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "doğum" not in update.message.text.lower():
        return
    kb, row = [], []
    for i,(n,l) in enumerate(DOGUM_BONUS,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i % 2 == 0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🎁 DOĞUM GÜNÜ BONUSLARI",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= ÇEKİLİŞ =================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_katilimcilar
    if not await is_admin(update, context):
        return
    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]
    ])

    await context.bot.send_photo(
        update.effective_chat.id,
        open("cekilis.jpg", "rb"),
        caption="🎉 BONUSSEMTİ ÇEKİLİŞİ",
        reply_markup=kb
    )

async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_kazananlar
    q = update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)

    await q.edit_message_caption(
        f"🎉 Katılımcı: {len(cekilis_katilimcilar)}"
    )

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("filter", add_filter))
app.add_handler(CommandHandler("remove", remove_filter))
app.add_handler(CommandHandler("mesaj", mesaj))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CallbackQueryHandler(cekilis_buton))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, mesaj_say), group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, site_kontrol), group=1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every), group=2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, dogum), group=3)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
