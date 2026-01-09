# bot.py
import os, time, random
from dotenv import load_dotenv
from datetime import timedelta

from telegram import (
    Update, ChatPermissions,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters as tg_filters
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

# ================= SİTELER =================
filters_dict = {
    "zbahis": "https://shoort.im/zbahis",
    "fixbet": "https://shoort.im/fixbet",
    "betkom": "https://shoort.im/betkom",
    "padisahbet": "https://shoort.im/padisahbet",
    "betpipo": "https://shoort.im/betpipo",
}

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
    ("COINBAR","http://shoort.in/coinbar"),
    ("NAKITBAHIS","https://shoort.in/nakitbahis"),
]

DOGUM_BONUS = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("FIXBET","https://shoort.im/fixbet"),
    ("BETPİPO","https://shoort.im/betpipo"),
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

async def hedef_kullanici(update, context):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    if context.args and context.args[0].startswith("@"):
        username = context.args[0][1:]
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id, username
            )
            return member.user
        except:
            return None
    return None

# ================= FILTER =================
async def add_filter(update, context):
    if not await is_admin(update, context):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: /filter site link")
        return
    filters_dict[context.args[0].lower()] = context.args[1]
    await update.message.reply_text("✅ Site eklendi")

async def remove_filter(update, context):
    if not await is_admin(update, context):
        return
    if not context.args:
        await update.message.reply_text("Kullanım: /remove site")
        return
    if context.args[0].lower() in filters_dict:
        del filters_dict[context.args[0].lower()]
        await update.message.reply_text("🗑️ Site silindi")
    else:
        await update.message.reply_text("❌ Bulunamadı")

# ================= BAN / MUTE =================
async def ban(update, context):
    if not await is_admin(update, context):
        return
    user = await hedef_kullanici(update, context)
    if not user:
        await update.message.reply_text("❌ Birini yanıtla ya da /ban @kullanici")
        return
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"🔨 {user.full_name} banlandı")

async def mute(update, context):
    if not await is_admin(update, context):
        return
    user = await hedef_kullanici(update, context)
    if not user:
        await update.message.reply_text("❌ Birini yanıtla ya da /mute @kullanici")
        return
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text(f"🔇 {user.full_name} susturuldu")

async def unban(update, context):
    if not await is_admin(update, context):
        return
    if not context.args:
        await update.message.reply_text("Kullanım: /unban user_id")
        return
    await context.bot.unban_chat_member(update.effective_chat.id, int(context.args[0]))
    await update.message.reply_text("✅ Ban kaldırıldı")

async def unmute(update, context):
    if not await is_admin(update, context):
        return
    user = await hedef_kullanici(update, context)
    if not user:
        await update.message.reply_text("❌ Yanıtla ya da @kullanici")
        return
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text(f"🔊 {user.full_name} açıldı")

# ================= MESAJ / KONTROL =================
async def mesaj(update, context):
    global min_mesaj
    if not await is_admin(update, context):
        return
    min_mesaj = int(context.args[0])
    await update.message.reply_text(f"📨 Minimum mesaj: {min_mesaj}")

async def mesaj_say(update, context):
    if update.message.date.timestamp() < BOT_START:
        return
    uid = update.message.from_user.id
    kullanici_mesaj[uid] = kullanici_mesaj.get(uid, 0) + 1

async def kontrol(update, context):
    if not await is_admin(update, context):
        return
    msg = "📋 **KAZANAN KONTROL RAPORU**\n\n"
    for uid in cekilis_kazananlar:
        member = await context.bot.get_chat_member(update.effective_chat.id, uid)
        isim = f"@{member.user.username}" if member.user.username else member.user.first_name
        sayi = kullanici_mesaj.get(uid, 0)
        eksik = []
        for kanal in ZORUNLU_KANALLAR:
            try:
                uye = await context.bot.get_chat_member(kanal, uid)
                if uye.status not in ["member","administrator","creator"]:
                    eksik.append(kanal)
            except:
                eksik.append(kanal)

        msg += f"❌ {isim}\n"
        msg += f"   📨 Mesaj: {sayi}/{min_mesaj}\n"
        if eksik:
            msg += "   📢 Eksik kanallar:\n"
            for k in eksik:
                msg += f"      • {k}\n"
        else:
            msg += "   📢 Kanal durumu: Tamam\n"
        msg += "\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ================= ÇEKİLİŞ =================
async def cekilis(update, context):
    global cekilis_aktif
    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]
    ])

    await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=(
            "🎉 **BONUSSEMTİ ÇEKİLİŞİ**\n\n"
            "Katılımcı: 0\n\n"
            "📢 Kanalları takip etmek zorunludur!"
        ),
        reply_markup=kb,
        parse_mode="Markdown"
    )

async def cekilis_buton(update, context):
    q = update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🎉 **BONUSSEMTİ ÇEKİLİŞİ**\n\nKatılımcı: {len(cekilis_katilimcilar)}",
        parse_mode="Markdown"
    )

async def sayi(update, context):
    global cekilis_kazanan_sayisi
    cekilis_kazanan_sayisi = int(context.args[0])
    await update.message.reply_text("🎯 Kazanan sayısı ayarlandı")

async def bitir(update, context):
    global cekilis_aktif, cekilis_kazananlar
    cekilis_aktif = False
    cekilis_kazananlar = random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi, len(cekilis_katilimcilar))
    )
    await update.message.reply_text("🏆 Çekiliş bitti")

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("filter", add_filter))
app.add_handler(CommandHandler("remove", remove_filter))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("mesaj", mesaj))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CommandHandler("sayi", sayi))
app.add_handler(CommandHandler("bitir", bitir))

app.add_handler(CallbackQueryHandler(cekilis_buton))
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, mesaj_say))

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
