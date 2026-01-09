# bot.py
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

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1
cekilis_kazananlar = []

kullanici_mesaj = {}
min_mesaj = 0

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

# ================= KÜFÜR =================
KUFUR_LISTESI = [
    "amk","aq","amına","anan","orospu","piç","ibne",
    "sik","siktir","yarak","amcık","mal","salak"
]
kufur_sayac = {}

# ================= SPAM =================
spam_log = {}
SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= SİTELER =================
filters_dict = {
    "zbahis": "https://shoort.im/zbahis",
    "fixbet": "https://shoort.im/fixbet",
    "betkom": "https://shoort.im/betkom",
    "padisahbet": "https://shoort.im/padisahbet",
    "betpipo": "https://shoort.im/betpipo",
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

DOGUM_BONUS = [
    ("ZBAHİS", "https://shoort.im/zbahis"),
    ("FIXBET", "https://shoort.im/fixbet"),
    ("BETPIPO", "https://shoort.im/betpipo"),
    ("CRATOSBET", "https://shoort.im/cratosbet"),
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

# ================= SPONSOR =================
async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() != "sponsor":
        return

    kb = []
    row = []
    for i,(n,l) in enumerate(filters_dict.items(),1):
        row.append(InlineKeyboardButton(n.upper(), url=l))
        if i % 2 == 0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "⭐ **BONUSSEMTİ SPONSOR SİTELERİ**\n\n👇 Butona tıklayarak siteye gidebilirsiniz.",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================= EVERY =================
async def every(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" not in update.message.text.lower():
        return

    kb, row = [], []
    for i,(n,l) in enumerate(EVERY_SPONSOR,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)

    kb.append([InlineKeyboardButton("────────────", callback_data="x")])

    row=[]
    for i,(n,l) in enumerate(EVERY_DIGER,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🔥 **EveryMatrix Siteleri**\n\n⭐ **Sponsorlar & Diğerleri**",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================= DOĞUM =================
async def dogum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "doğum" not in update.message.text.lower():
        return

    kb,row=[],[]
    for i,(n,l) in enumerate(DOGUM_BONUS,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🎁 **DOĞUM GÜNÜ BONUSLARI**",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================= SITE =================
async def site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for k,v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]]
            )
            await update.message.reply_text(
                f"✅ **{k.upper()}**",
                reply_markup=kb,
                parse_mode="Markdown"
            )
            return

# ================= BAN / MUTE =================
async def ban(update,context):
    if await is_admin(update,context) and update.message.reply_to_message:
        u=update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id,u.id)
        await update.message.reply_text(f"🔨 {u.full_name} banlandı")

async def unban(update,context):
    if await is_admin(update,context) and context.args:
        await context.bot.unban_chat_member(update.effective_chat.id,int(context.args[0]))
        await update.message.reply_text("✅ Ban kaldırıldı")

async def mute(update,context):
    if await is_admin(update,context) and update.message.reply_to_message:
        u=update.message.reply_to_message.from_user
        await context.bot.restrict_chat_member(
            update.effective_chat.id,u.id,ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(f"🔇 {u.full_name} susturuldu")

async def unmute(update,context):
    if await is_admin(update,context) and update.message.reply_to_message:
        u=update.message.reply_to_message.from_user
        await context.bot.restrict_chat_member(
            update.effective_chat.id,u.id,ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text(f"🔊 {u.full_name} açıldı")

# ================= LOCK =================
async def lock(update,context):
    if await is_admin(update,context):
        await context.bot.set_chat_permissions(update.effective_chat.id,ChatPermissions())
        await update.message.reply_text("🔒 Grup kilitlendi")

async def unlock(update,context):
    if await is_admin(update,context):
        await context.bot.set_chat_permissions(
            update.effective_chat.id,ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text("🔓 Grup açıldı")

# ================= !SİL =================
async def sil(update,context):
    if not await is_admin(update,context): return
    n=int(update.message.text.split()[1])
    for i in range(n):
        try:
            await context.bot.delete_message(update.effective_chat.id,update.message.message_id-i)
        except: pass

# ================= ÇEKİLİŞ =================
async def cekilis(update,context):
    global cekilis_aktif
    cekilis_aktif=True
    cekilis_katilimcilar.clear()

    kb=InlineKeyboardMarkup([[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL",callback_data="katil")]])
    await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption="🎉 **BONUSSEMTİ ÇEKİLİŞİ**\n\nKatılımcı: 0",
        reply_markup=kb,
        parse_mode="Markdown"
    )

async def cekilis_buton(update,context):
    q=update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🎉 **BONUSSEMTİ ÇEKİLİŞİ**\n\nKatılımcı: {len(cekilis_katilimcilar)}",
        parse_mode="Markdown"
    )

# ================= BOT =================
app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("ban",ban))
app.add_handler(CommandHandler("unban",unban))
app.add_handler(CommandHandler("mute",mute))
app.add_handler(CommandHandler("unmute",unmute))
app.add_handler(CommandHandler("lock",lock))
app.add_handler(CommandHandler("unlock",unlock))
app.add_handler(CommandHandler("cekilis",cekilis))
app.add_handler(CallbackQueryHandler(cekilis_buton))

app.add_handler(MessageHandler(tg_filters.Regex(r"^!sil \d+$"),sil))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,sponsor),group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,every),group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,dogum),group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND,site),group=1)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
