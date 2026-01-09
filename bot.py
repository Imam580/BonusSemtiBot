# bot.py
import os, time, random
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
BOT_START = time.time()

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazananlar = []
cekilis_kazanan_sayisi = 1

min_mesaj = 0
kullanici_mesaj = {}

# ================= KANALLAR =================
ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@BahisKarhanesi",
]

# ================= KÜFÜR =================
KUFUR = ["amk","orospu","piç","ibne","sik","yarrak","amcık","anan","amına"]

# ================= SPAM =================
spam_log = {}
SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= DOĞUM =================
DOGUM = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("PADİŞAHBET","https://shoort.im/padisahbet"),
    ("FİXBET","https://shoort.im/fixbet"),
    ("BETMATİK","https://shoort.im/betmatik"),
]

# ================= EVERY =================
EVERY_SPONSOR = [
    ("HIZLICASINO","https://shoort.im/hizlicasino"),
    ("EGEBET","https://shoort.im/egebet"),
    ("KAVBET","https://shoort.im/kavbet"),
]

EVERY_DIGER = [
    ("JOJOBET","http://dub.pro/jojoyagit"),
    ("HOLIGANBET","https://dub.pro/holiguncel"),
]

# ================= FİLTRE =================
filters_dict = {
    "zbahis":"https://shoort.im/zbahis",
    "egebet":"https://shoort.im/egebet",
    "kavbet":"https://shoort.im/kavbet",
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

# ================= MESAJ SAY =================
async def mesaj_say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if update.message.date.timestamp() < BOT_START:
        return
    uid = update.message.from_user.id
    kullanici_mesaj[uid] = kullanici_mesaj.get(uid, 0) + 1

# ================= KÜFÜR (MUTE YOK) =================
async def kufur_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    text = update.message.text.lower()
    for k in KUFUR:
        if k in text:
            await update.message.delete()
            await update.effective_chat.send_message(
                f"⚠️ @{update.message.from_user.username or update.message.from_user.first_name} küfür yasaktır."
            )
            return

# ================= LINK / SPAM MUTE + BUTON =================
async def mute_with_button(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
    user = update.message.from_user
    await update.message.delete()

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False),
        until_date=int(time.time()) + 3600
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 MUTENİ KALDIR", callback_data=f"unmute:{user.id}")]
    ])

    await update.effective_chat.send_message(
        f"🔇 @{user.username or user.first_name}\n{reason}",
        reply_markup=kb
    )

async def link_engel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    if any(x in update.message.text.lower() for x in ["http","t.me","www"]):
        await mute_with_button(update, context, "🔗 Link paylaşımı yasaktır. 1 saat susturuldu.")

async def spam_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    uid = update.message.from_user.id
    now = time.time()
    spam_log.setdefault(uid, []).append(now)
    spam_log[uid] = [t for t in spam_log[uid] if now-t <= SPAM_SURE]
    if len(spam_log[uid]) >= SPAM_LIMIT:
        await mute_with_button(update, context, "📛 Spam nedeniyle 1 saat susturuldu.")

# ================= UNMUTE BUTONU =================
async def unmute_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not await is_admin(update, context):
        await query.answer("Yetkin yok", show_alert=True)
        return

    uid = int(query.data.split(":")[1])
    await context.bot.restrict_chat_member(
        query.message.chat.id,
        uid,
        ChatPermissions(can_send_messages=True)
    )

    await query.edit_message_text("🔓 Susturma kaldırıldı.")

# ================= SITE =================
async def site_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = update.message.text.lower()
    for k,v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]]
            )
            await update.message.reply_text("🔗 Giriş Linki:", reply_markup=kb)
            return

# ================= DOĞUM =================
async def dogum_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or "doğum" not in update.message.text.lower():
        return
    kb,row=[],[]
    for i,(n,l) in enumerate(DOGUM,1):
        row.append(InlineKeyboardButton(n,url=l))
        if i%2==0:
            kb.append(row);row=[]
    if row:kb.append(row)
    await update.message.reply_text("🎁 DOĞUM GÜNÜ BONUSLARI",reply_markup=InlineKeyboardMarkup(kb))

# ================= EVERY =================
async def every_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or "every" not in update.message.text.lower():
        return
    kb=[]
    for n,l in EVERY_SPONSOR:
        kb.append([InlineKeyboardButton(f"⭐ {n}",url=l)])
    kb.append([InlineKeyboardButton("────────",callback_data="bos")])
    for n,l in EVERY_DIGER:
        kb.append([InlineKeyboardButton(n,url=l)])
    await update.message.reply_text(
        "🔥 BonusSemti Güvencesiyle EveryMatrix Siteleri",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= ÇEKİLİŞ =================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    if not await is_admin(update, context):
        return
    cekilis_aktif=True
    cekilis_katilimcilar.clear()

    kb=InlineKeyboardMarkup([[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL",callback_data="katil")]])
    await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=(
            "🔥 BONUSSEMTİ ÇEKİLİŞİ\n\n"
            "🔥 KATILIMCI SAYISI : 0\n\n"
            "🏆 Katılımcıların kanalları takip etmesi zorunludur!"
        ),
        reply_markup=kb
    )

async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        q.message.caption.split("\n")[0]+f"\n\n🔥 KATILIMCI SAYISI : {len(cekilis_katilimcilar)}"
    )

# ================= BOT =================
app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("cekilis",cekilis))
app.add_handler(CallbackQueryHandler(cekilis_buton,"katil"))
app.add_handler(CallbackQueryHandler(unmute_button,"unmute"))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,kufur_kontrol),group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,link_engel),group=1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,spam_kontrol),group=2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,mesaj_say),group=3)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,site_kontrol),group=4)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,dogum_kontrol),group=5)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,every_kontrol),group=6)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
