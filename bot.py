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
BOT_START = time.time()

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazananlar = []
cekilis_kazanan_sayisi = 1

kullanici_mesaj = {}
min_mesaj = 0

spam_log = {}
spam_warn = {}

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
    "amk","aq","amq","orospu","orospu çocuğu","piç","ibne",
    "yarrak","yarak","sik","siktir","amcık","anan","amına"
]

# ================= SİTELER =================
filters_dict = {
    "zbahis": "https://shoort.im/zbahis",
    "padisahbet": "https://shoort.im/padisahbet",
    "fixbet": "https://shoort.im/fixbet",
    "betmatik": "https://shoort.im/betmatik",
    "betoffice": "https://shoort.im/betoffice",
    "betpipo": "https://shoort.im/betpipo",
    "norabahis": "https://shoort.im/norabahis",
    "spinco": "https://shoort.im/spinco",
    "cratosbet": "https://shoort.im/cratosbet",
    "mariobet": "http://shoort.im/mariobonus",
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
    ("COINBAR", "http://shoort.in/coinbar"),
    ("NAKITBAHIS", "https://shoort.in/nakitbahis"),
]

# ================= DOĞUM =================
DOGUM_BONUS = [
    ("ZBAHİS", "https://shoort.im/zbahis"),
    ("PADİŞAHBET", "https://shoort.im/padisahbet"),
    ("FIXBET", "https://shoort.im/fixbet"),
    ("BETMATİK", "https://shoort.im/betmatik"),
    ("BETOFFICE", "https://shoort.im/betoffice"),
]

# ================= ADMIN =================
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except:
        return False

# ================= YARDIMCI =================
def mention(user):
    return f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

# ================= KÜFÜR =================
async def kufur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    if any(k in update.message.text.lower() for k in KUFUR_LISTESI):
        await update.message.delete()

# ================= İLETİLEN =================
async def forward_sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.forward_from or update.message.forward_from_chat:
        if not await is_admin(update, context):
            await update.message.delete()

# ================= LINK =================
async def link_engel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    if any(x in update.message.text.lower() for x in ["http", "t.me", "www"]):
        await update.message.delete()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔓 Muteyi Kaldır", callback_data=f"unmute:{update.message.from_user.id}")]
        ])
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.from_user.id,
            ChatPermissions(can_send_messages=False),
            until_date=timedelta(minutes=30)
        )
        await update.effective_chat.send_message(
            f"🔇 {mention(update.message.from_user)} link paylaştı.",
            reply_markup=kb,
            parse_mode="HTML"
        )

# ================= SPAM =================
async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    uid = update.message.from_user.id
    spam_log.setdefault(uid, []).append(time.time())
    spam_log[uid] = [t for t in spam_log[uid] if time.time()-t < 5]

    if len(spam_log[uid]) == 5:
        await update.message.reply_text("⚠️ Spam yapma.")
    elif len(spam_log[uid]) >= 8:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, uid,
            ChatPermissions(can_send_messages=False),
            until_date=timedelta(hours=1)
        )

# ================= SİTE =================
async def site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for k,v in filters_dict.items():
        if k in update.message.text.lower():
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]])
            await update.message.reply_text("Giriş linki:", reply_markup=kb)
            return

# ================= SPONSOR =================
async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(k.upper(), url=v)] for k,v in filters_dict.items()]
    await update.message.reply_text("⭐ BONUSSEMTİ SPONSORLARI", reply_markup=InlineKeyboardMarkup(kb))

# ================= EVERY =================
async def every(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" not in update.message.text.lower():
        return
    kb=[]
    for n,l in EVERY_SPONSOR:
        kb.append([InlineKeyboardButton(n, url=l)])
    kb.append([InlineKeyboardButton("────", callback_data="x")])
    for n,l in EVERY_DIGER:
        kb.append([InlineKeyboardButton(n, url=l)])
    await update.message.reply_text(
        "🔥 EveryMatrix Siteleri\n⭐ Sponsorlar / Diğerleri",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= DOĞUM =================
async def dogum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "doğum" not in update.message.text.lower():
        return
    kb=[]
    for n,l in DOGUM_BONUS:
        kb.append([InlineKeyboardButton(n, url=l)])
    await update.message.reply_text("🎁 DOĞUM GÜNÜ BONUSLARI", reply_markup=InlineKeyboardMarkup(kb))

# ================= ÇEKİLİŞ =================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]])

    await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=(
            "🔥 BONUSSEMTİ ÇEKİLİŞİ\n\n"
            "🔥 KATILIMCI SAYISI : 0\n\n"
            "🏆 Katılımcıların kanallarımızı takip etmesi zorunludur!\n\n" +
            "\n".join([f"🔥 https://t.me/{k[1:]}" for k in ZORUNLU_KANALLAR])
        ),
        reply_markup=kb
    )

async def katil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)

async def bitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    cekilis_aktif=False
    kazananlar=random.sample(list(cekilis_katilimcilar), min(cekilis_kazanan_sayisi,len(cekilis_katilimcilar)))
    msg="🏆 ÇEKİLİŞ BİTTİ\n\n"
    for uid in kazananlar:
        user=await context.bot.get_chat_member(update.effective_chat.id,uid)
        msg+=f"🎁 {mention(user.user)}\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# ================= KONTROL =================
async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg="📋 KAZANAN KONTROL RAPORU\n\n"
    for uid in cekilis_katilimcilar:
        member=await context.bot.get_chat_member(update.effective_chat.id,uid)
        mcount=kullanici_mesaj.get(uid,0)
        eksik=[]
        for ch in ZORUNLU_KANALLAR:
            try:
                cm=await context.bot.get_chat_member(ch,uid)
                if cm.status not in ("member","administrator","creator"):
                    eksik.append(ch)
            except:
                eksik.append(ch)
        msg+=f"❌ {mention(member.user)}\n"
        msg+=f"   📨 Mesaj durumu: {mcount}/{min_mesaj}\n"
        if eksik:
            msg+="   📢 Kanal durumu:\n"
            for e in eksik:
                msg+=f"      • {e}\n"
        else:
            msg+="   📢 Kanal durumu: Tüm kanallara katılım sağlanmıştır.\n"
        msg+="\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# ================= MESAJ SAY =================
async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.date.timestamp() < BOT_START:
        return
    uid=update.message.from_user.id
    kullanici_mesaj[uid]=kullanici_mesaj.get(uid,0)+1

# ================= BOT =================
app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CommandHandler("bitir", bitir))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CommandHandler("sponsor", sponsor))

app.add_handler(CallbackQueryHandler(katil, pattern="katil"))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, forward_sil), group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, kufur), group=1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, link_engel), group=2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, spam), group=3)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, say), group=4)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every), group=5)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, dogum), group=6)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, site), group=7)

print("🔥 BonusSemti Bot Aktif")
app.run_polling()
