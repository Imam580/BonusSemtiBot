# ===============================
# BONUSSEMTİ PROFESYONEL BOT v2
# ===============================

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
    "@BahisKarhanesi",
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

# ================= MESAJ SAY =================
async def mesaj_say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if update.message.date.timestamp() < BOT_START:
        return
    uid = update.message.from_user.id
    kullanici_mesaj[uid] = kullanici_mesaj.get(uid, 0) + 1

# ================= /mesaj =================
async def mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global min_mesaj
    if not await is_admin(update, context):
        return
    min_mesaj = int(context.args[0])
    await update.message.reply_text(
        f"📝 Minimum mesaj şartı {min_mesaj} olarak ayarlandı."
    )

# ================= ÇEKİLİŞ TEXT =================
CEKILIS_TEXT = (
    "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
    "🔥 <b>KATILIMCI SAYISI :</b> {sayi}\n\n"
    "🏆 <b>Katılımcıların kanallarımızı takip etmesi zorunludur!</b>\n\n"
    "🔥 https://t.me/Canli_Izleme_Mac_Linkleri\n"
    "🔥 https://t.me/plasespor\n"
    "🔥 https://t.me/bonussemti\n"
    "🔥 https://t.me/bonussemtietkinlik\n"
    "🔥 https://t.me/BahisKarhanesi\n"
)

# ================= /cekilis =================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    if not await is_admin(update, context):
        return

    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]
    ])

    with open("cekilis.jpg", "rb") as foto:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=foto,
            caption=CEKILIS_TEXT.format(sayi=0),
            reply_markup=kb,
            parse_mode="HTML"
        )

# ================= BUTON =================
async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not cekilis_aktif:
        return

    uid = q.from_user.id
    cekilis_katilimcilar.add(uid)

    await q.edit_message_caption(
        caption=CEKILIS_TEXT.format(sayi=len(cekilis_katilimcilar)),
        reply_markup=q.message.reply_markup,
        parse_mode="HTML"
    )

# ================= /sayi =================
async def sayi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_kazanan_sayisi
    if not await is_admin(update, context):
        return
    cekilis_kazanan_sayisi = int(context.args[0])
    await update.message.reply_text(
        f"🎯 Kazanan sayısı {cekilis_kazanan_sayisi}"
    )

# ================= /bitir =================
async def bitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_kazananlar
    if not await is_admin(update, context):
        return

    cekilis_aktif = False

    cekilis_kazananlar = random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi, len(cekilis_katilimcilar))
    )

    msg = "🏆 <b>KAZANANLAR</b>\n\n"
    for uid in cekilis_kazananlar:
        member = await context.bot.get_chat_member(update.effective_chat.id, uid)
        user = member.user
        msg += f"🎁 @{user.username}\n" if user.username else f"🎁 {user.first_name}\n"

    await update.message.reply_text(msg, parse_mode="HTML")

# ================= /kontrol =================
async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"

    for uid in cekilis_kazananlar:
        member = await context.bot.get_chat_member(update.effective_chat.id, uid)
        user = member.user
        isim = f"@{user.username}" if user.username else user.first_name

        mesaj_sayi = kullanici_mesaj.get(uid, 0)
        eksik = []

        for kanal in ZORUNLU_KANALLAR:
            try:
                m = await context.bot.get_chat_member(kanal, uid)
                if m.status not in ["member","administrator","creator"]:
                    eksik.append(kanal)
            except:
                eksik.append(kanal)

        msg += f"❌ {isim}\n"
        msg += f"   📨 Mesaj durumu: {mesaj_sayi}/{min_mesaj}\n"

        if eksik:
            msg += "   📢 Kanal durumu: Eksik\n"
            for k in eksik:
                msg += f"      • {k}\n"
        else:
            msg += "   📢 Kanal durumu: Tüm kanallara katılım sağlanmıştır.\n"

        msg += "\n"

    await update.message.reply_text(msg, parse_mode="HTML")

# ================= BAN / MUTE / LOCK =================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"🔨 @{user.username} banlandı.")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user.id,
            ChatPermissions(can_send_messages=False),
            until_date=int(time.time()) + 3600
        )
        await update.message.reply_text(f"🔇 @{user.username} 1 saat susturuldu.")

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text("🔒 Grup kilitlendi.")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text("🔓 Grup açıldı.")

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CommandHandler("sayi", sayi))
app.add_handler(CommandHandler("bitir", bitir))
app.add_handler(CommandHandler("mesaj", mesaj))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))

app.add_handler(CallbackQueryHandler(cekilis_buton))
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, mesaj_say))

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
