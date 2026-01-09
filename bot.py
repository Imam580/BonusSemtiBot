# bot.py
import os
import time
import random
from datetime import timedelta
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
BOT_START = time.time()

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1
cekilis_kazananlar = []

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

# ================= SİTE LİNKLERİ =================
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
    "royalbet": "https://shoort.im/royalbet",
    "radissonbet": "https://shoort.im/radissonbet",
}

# ================= EVERY =================
EVERY_SPONSOR = [
    ("HIZLICASINO","https://shoort.im/hizlicasino"),
    ("EGEBET","https://shoort.im/egebet"),
    ("KAVBET","https://shoort.im/kavbet"),
    ("PUSULABET","https://shoort.im/pusulabet"),
    ("HITBET","https://shoort.im/hitbet"),
    ("ARTEMISBET","https://shoort.im/artemisbet"),
]

EVERY_DIGER = [
    ("JOJOBET","http://dub.pro/jojoyagit"),
    ("HOLIGANBET","https://dub.pro/holiguncel"),
    ("NAKITBAHIS","https://shoort.in/nakitbahis"),
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

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    if context.args:
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id,
                context.args[0]
            )
            return member.user
        except:
            return None
    return None

# ================= MUTE (SÜRELİ / SÜRESİZ) =================
def parse_time(arg):
    if arg.endswith("m"):
        return int(arg[:-1]) * 60
    if arg.endswith("h"):
        return int(arg[:-1]) * 3600
    return None

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ Yanıtla ya da /mute @kullanici 10m")
        return

    duration = None
    if len(context.args) > 1:
        duration = parse_time(context.args[1])

    until = int(time.time()) + duration if duration else None

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False),
        until_date=until
    )

    await update.message.reply_text(
        f"🔇 @{user.username or user.first_name} susturuldu."
    )

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ Yanıtla ya da /unmute @kullanici")
        return

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text(f"🔊 @{user.username or user.first_name} açıldı.")

# ================= BAN =================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ Yanıtla ya da /ban @kullanici")
        return
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"🔨 @{user.username or user.first_name} banlandı.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    try:
        uid = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, uid)
        await update.message.reply_text("✅ Ban kaldırıldı.")
    except:
        await update.message.reply_text("❌ /unban user_id")

# ================= LOCK =================
async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(update.effective_chat.id, ChatPermissions())
        await update.message.reply_text("🔒 Grup kilitlendi.")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text("🔓 Grup açıldı.")

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

# ================= EVERY =================
async def every(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" not in update.message.text.lower():
        return

    kb = []
    row = []
    for i,(n,l) in enumerate(EVERY_SPONSOR,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i % 2 == 0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🔥 BONUSSEMTİ SPONSOR EVERY SİTELERİ\n\n"
        "👇 Butona tıklayarak siteye yönelebilirsiniz.",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= ÇEKİLİŞ =================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]
    ])

    await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption="🎉 BONUSSEMTİ ÇEKİLİŞİ\n\nKatılımcı: 0",
        reply_markup=kb
    )

async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    cekilis_katilimcilar.add(q.from_user.id)

    await q.edit_message_caption(
        f"🎉 BONUSSEMTİ ÇEKİLİŞİ\n\nKatılımcı: {len(cekilis_katilimcilar)}",
        reply_markup=q.message.reply_markup
    )

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))
app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CallbackQueryHandler(cekilis_buton))

app.add_handler(MessageHandler(tg_filters.Regex(r"^!sil \d+$"), sil))
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every))

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
