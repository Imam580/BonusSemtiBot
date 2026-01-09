# ===============================
# BONUSSEMTİ FULL PROFESYONEL BOT
# ===============================

import os
import time
import random
from dotenv import load_dotenv
from datetime import timedelta

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
BOT_START = time.time()

kullanici_mesaj_sayisi = {}
min_mesaj_sayisi = 0

kufur_sayaci = {}
spam_log = {}

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazananlar = []
cekilis_kazanan_sayisi = 1

# ================= KANALLAR =================
ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@BahisKarhanesi",
]

# ================= KÜFÜR =================
KUFUR_LISTESI = [
    "amk","aq","amq","orospu","orospu çocuğu",
    "piç","ibne","yarrak","sik","amcık",
    "anan","amına","siktir"
]

# ================= SPAM =================
SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= SİTELER =================
filters_dict = {
    "zbahis": "https://shoort.im/zbahis",
    "fixbet": "https://shoort.im/fixbet",
    "betmatik": "https://shoort.im/betmatik",
    "padisahbet": "https://shoort.im/padisahbet",
}

# ================= EVERY =================
EVERY_SPONSOR = [
    ("HIZLICASINO", "https://shoort.im/hizlicasino"),
    ("EGEBET", "https://shoort.im/egebet"),
    ("KAVBET", "https://shoort.im/kavbet"),
]

EVERY_DIGER = [
    ("JOJOBET", "http://dub.pro/jojoyagit"),
    ("HOLIGANBET", "https://dub.pro/holiguncel"),
]

# ================= DOĞUM =================
DOGUM_BONUS = [
    ("ZBAHİS", "https://shoort.im/zbahis"),
    ("FIXBET", "https://shoort.im/fixbet"),
    ("BETMATİK", "https://shoort.im/betmatik"),
]

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

# ================= LINK =================
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
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            uid,
            ChatPermissions(can_send_messages=False),
            until_date=int(time.time()) + 3600
        )
        spam_log[uid] = []

# ================= MESAJ SAY =================
async def mesaj_say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if update.message.date.timestamp() < BOT_START:
        return
    uid = update.message.from_user.id
    kullanici_mesaj_sayisi[uid] = kullanici_mesaj_sayisi.get(uid, 0) + 1

# ================= /mesaj =================
async def mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global min_mesaj_sayisi
    if not await is_admin(update, context):
        return
    min_mesaj_sayisi = int(context.args[0])
    await update.message.reply_text(f"📝 Mesaj şartı: {min_mesaj_sayisi}")

# ================= SİTE =================
async def site_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for k, v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]
            ])
            await update.message.reply_text(
                f"✅ {k.upper()} GİRİŞ",
                reply_markup=kb
            )
            return

# ================= /sponsor =================
async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(k.upper(), url=v)] for k, v in filters_dict.items()]
    await update.message.reply_text(
        "⭐ SPONSOR SİTELER",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= EVERY =================
async def every(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" not in update.message.text.lower():
        return
    kb = []
    for s in EVERY_SPONSOR:
        kb.append([InlineKeyboardButton(s[0], url=s[1])])
    kb.append([InlineKeyboardButton("────────", callback_data="bos")])
    for d in EVERY_DIGER:
        kb.append([InlineKeyboardButton(d[0], url=d[1])])
    await update.message.reply_text(
        "🔥 EveryMatrix Siteleri",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= DOĞUM =================
async def dogum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "doğum" not in update.message.text.lower():
        return
    kb = [[InlineKeyboardButton(a[0], url=a[1])] for a in DOGUM_BONUS]
    await update.message.reply_text(
        "🎁 DOĞUM GÜNÜ BONUSLARI",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= ÇEKİLİŞ =================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    if not await is_admin(update, context):
        return
    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]
    ])

    await context.bot.send_photo(
        update.effective_chat.id,
        open("cekilis.jpg","rb"),
        caption="🎉 BONUSSEMTİ ÇEKİLİŞİ\n\nKatılımcı: 0",
        reply_markup=kb
    )

async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🎉 BONUSSEMTİ ÇEKİLİŞİ\n\nKatılımcı: {len(cekilis_katilimcilar)}"
    )

# ================= /kontrol =================
async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📋 KAZANAN KONTROL RAPORU\n\n"
    for uid in cekilis_katilimcilar:
        mesaj = kullanici_mesaj_sayisi.get(uid, 0)
        msg += f"❌ <a href='tg://user?id={uid}'>Kullanıcı</a>\n"
        msg += f"   📨 Mesaj: {mesaj}/{min_mesaj_sayisi}\n\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# ================= !sil =================
async def sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    adet = int(update.message.text.split()[1])
    for i in range(adet):
        try:
            await context.bot.delete_message(
                update.effective_chat.id,
                update.message.message_id - i
            )
        except:
            pass

# ================= LOCK / BAN =================
async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(update.effective_chat.id, ChatPermissions())
        await update.message.reply_text("🔒 Kilitlendi")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text("🔓 Açıldı")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and update.message.reply_to_message:
        await context.bot.ban_chat_member(
            update.effective_chat.id,
            update.message.reply_to_message.from_user.id
        )

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.unban_chat_member(
            update.effective_chat.id,
            int(context.args[0])
        )

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and update.message.reply_to_message:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.reply_to_message.from_user.id,
            ChatPermissions(can_send_messages=False)
        )

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and update.message.reply_to_message:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.reply_to_message.from_user.id,
            ChatPermissions(can_send_messages=True)
        )

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CallbackQueryHandler(cekilis_buton))
app.add_handler(CommandHandler("mesaj", mesaj))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CommandHandler("sponsor", sponsor))
app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))

app.add_handler(MessageHandler(tg_filters.Regex(r"^!sil \d+$"), sil))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, kufur_kontrol), group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, link_engel), group=1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, spam_kontrol), group=2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, mesaj_say), group=3)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every), group=4)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, dogum), group=5)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, site_kontrol), group=6)

print("🔥 BONUSSEMTİ BOT ÇALIŞIYOR")
app.run_polling()
