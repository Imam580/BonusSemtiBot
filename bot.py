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
    filters
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
    "@BahisKarhanesi",
]

# ================= SİTE FİLTRELERİ =================
filters_dict = {
    "zbahis": "https://shoort.im/zbahis",
    "egebet": "https://shoort.im/egebet",
    "kavbet": "https://shoort.im/kavbet",
    "hitbet": "https://shoort.im/hitbet",
    "pusulabet": "https://shoort.im/pusulabet",
}

# ================= SPONSOR & DOĞUM =================
SPONSOR_SITELER = list(filters_dict.items())

DOGUM_SITELER = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("PADİŞAHBET","https://shoort.im/padisahbet"),
    ("FIXBET","https://shoort.im/fixbet"),
    ("BETMATİK","https://shoort.im/betmatik"),
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
        username = context.args[0].replace("@","")
        members = await context.bot.get_chat_administrators(update.effective_chat.id)
        for m in members:
            if m.user.username == username:
                return m.user
    return None

# ================= FILTER =================
async def filter_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Yetkin yok")
    if len(context.args) < 2:
        return await update.message.reply_text("Kullanım: /filter site link")
    filters_dict[context.args[0].lower()] = context.args[1]
    await update.message.reply_text("✅ Filtre eklendi")

async def filter_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    key = context.args[0].lower()
    if key in filters_dict:
        del filters_dict[key]
        await update.message.reply_text("🗑️ Filtre silindi")

# ================= SPONSOR =================
async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb, row = [], []
    for i,(n,l) in enumerate(filters_dict.items(),1):
        row.append(InlineKeyboardButton(n.upper(), url=l))
        if i % 2 == 0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🔥 BONUSSEMTİ SPONSOR SİTELER\n👇 Butona tıklayarak siteye gidebilirsiniz",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= DOĞUM =================
async def dogum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb, row = [], []
    for i,(n,l) in enumerate(DOGUM_SITELER,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i % 2 == 0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🎁 DOĞUM GÜNÜ BONUSLARI",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= ÇEKİLİŞ =================
def cekilis_text():
    t = "🔥 BONUSSEMTİ ÇEKİLİŞİ\n\n"
    t += f"🔥 KATILIMCI SAYISI : {len(cekilis_katilimcilar)}\n\n"
    t += "🏆 Katılımcıların kanalları takip etmesi zorunludur!\n\n"
    for k in ZORUNLU_KANALLAR:
        t += f"🔥 {k}\n"
    return t

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
        caption=cekilis_text(),
        reply_markup=kb
    )

async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(cekilis_text(), reply_markup=q.message.reply_markup)

async def sayi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_kazanan_sayisi
    cekilis_kazanan_sayisi = int(context.args[0])
    await update.message.reply_text(f"🎯 Kazanan sayısı {cekilis_kazanan_sayisi}")

async def mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global min_mesaj_sayisi
    min_mesaj_sayisi = int(context.args[0])
    await update.message.reply_text(f"📝 Mesaj şartı {min_mesaj_sayisi}")

async def bitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    cekilis_aktif = False
    kazananlar = random.sample(list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi,len(cekilis_katilimcilar)))
    msg = "🏆 ÇEKİLİŞ BİTTİ\n\n"
    for u in kazananlar:
        msg += f"🎁 <a href='tg://user?id={u}'>Kazanan</a>\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# ================= KONTROL =================
async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📋 KAZANAN KONTROL RAPORU\n\n"
    for uid in cekilis_kazananlar:
        ms = kullanici_mesaj_sayisi.get(uid,0)
        msg += f"❌ <a href='tg://user?id={uid}'>Kullanıcı</a>\n"
        msg += f"   📨 Mesaj: {ms}/{min_mesaj_sayisi}\n\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# ================= ADMIN CEZALAR =================
async def ban(update, context):
    if not await is_admin(update, context): return
    u = await get_target_user(update, context)
    if not u: return await update.message.reply_text("❌ Yanıtla veya /ban @user")
    await context.bot.ban_chat_member(update.effective_chat.id, u.id)

async def unban(update, context):
    if not await is_admin(update, context): return
    uid = int(context.args[0])
    await context.bot.unban_chat_member(update.effective_chat.id, uid)

async def mute(update, context):
    if not await is_admin(update, context): return
    u = await get_target_user(update, context)
    if not u: return
    await context.bot.restrict_chat_member(
        update.effective_chat.id, u.id,
        ChatPermissions(can_send_messages=False)
    )

async def unmute(update, context):
    if not await is_admin(update, context): return
    u = await get_target_user(update, context)
    if not u: return
    await context.bot.restrict_chat_member(
        update.effective_chat.id, u.id,
        ChatPermissions(can_send_messages=True)
    )

async def lock(update, context):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(update.effective_chat.id, ChatPermissions())

async def unlock(update, context):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(can_send_messages=True)
        )

async def sil(update, context):
    if not await is_admin(update, context): return
    n = int(update.message.text.split()[1])
    for i in range(n):
        try:
            await context.bot.delete_message(
                update.effective_chat.id,
                update.message.message_id - i
            )
        except: pass

# ================= MESSAGE =================
async def mesaj_say(update, context):
    uid = update.message.from_user.id
    kullanici_mesaj_sayisi[uid] = kullanici_mesaj_sayisi.get(uid,0)+1

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("filter", filter_add))
app.add_handler(CommandHandler("remove", filter_remove))
app.add_handler(CommandHandler("sponsor", sponsor))
app.add_handler(CommandHandler("dogum", dogum))
app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CommandHandler("sayi", sayi))
app.add_handler(CommandHandler("mesaj", mesaj))
app.add_handler(CommandHandler("bitir", bitir))
app.add_handler(CommandHandler("kontrol", kontrol))

app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))
app.add_handler(MessageHandler(filters.Regex(r"^!sil \d+$"), sil))

app.add_handler(CallbackQueryHandler(cekilis_buton))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_say))

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
