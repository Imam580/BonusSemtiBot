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
cekilis_kazananlar = []
cekilis_kazanan_sayisi = 1

min_mesaj = 0
mesaj_sayaci = {}

# ================= SİTE FİLTRELERİ =================
SITE_LINKLERI = {
    "zbahis": "https://shoort.im/zbahis",
    "fixbet": "https://shoort.im/fixbet",
    "betoffice": "https://shoort.im/betoffice",
    "padisahbet": "https://shoort.im/padisahbet",
    "betpipo": "https://shoort.im/betpipo",
    "norabahis": "https://shoort.im/norabahis",
    "spinco": "https://shoort.im/spinco",
    "cratosbet": "https://shoort.im/cratosbet",
    "xbahis": "https://shoort.im/xbahis",
    "egebet": "https://shoort.im/egebet",
    "kavbet": "https://shoort.im/kavbet",
}

# ================= SABİTLER =================
ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@BahisKarhanesi"
]

SPONSOR_SITELER = [
    ("HIZLICASINO", "https://shoort.im/hizlicasino"),
    ("EGEBET", "https://shoort.im/egebet"),
    ("KAVBET", "https://shoort.im/kavbet"),
    ("PUSULABET", "https://shoort.im/pusulabet"),
]

DOGUM_SITELER = [
    ("ZBAHİS", "https://shoort.im/zbahis"),
    ("PADİŞAHBET", "https://shoort.im/padisahbet"),
    ("FİXBET", "https://shoort.im/fixbet"),
]

KUFUR = ["amk","aq","orospu","piç","ibne","yarrak","sik","amcık"]

# ================= YARDIMCI =================
def mention(u):
    return f"<a href='tg://user?id={u.id}'>{u.first_name}</a>"

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def get_target(update, context):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    if context.args:
        username = context.args[0].replace("@","")
        try:
            m = await context.bot.get_chat_member(update.effective_chat.id, f"@{username}")
            return m.user
        except:
            return None
    return None

# ================= MODERASYON =================
async def ban(update, context):
    if not await is_admin(update, context): return
    u = await get_target(update, context)
    if not u:
        await update.message.reply_text("❌ Yanıtla veya /ban @kullanici")
        return
    await context.bot.ban_chat_member(update.effective_chat.id, u.id)
    await update.message.reply_text(f"🔨 {mention(u)} banlandı", parse_mode="HTML")

async def unban(update, context):
    if not await is_admin(update, context): return
    if not context.args:
        await update.message.reply_text("❌ /unban @kullanici")
        return
    await context.bot.unban_chat_member(update.effective_chat.id, context.args[0])
    await update.message.reply_text("✅ Ban kaldırıldı")

async def mute(update, context):
    if not await is_admin(update, context): return
    u = await get_target(update, context)
    if not u:
        await update.message.reply_text("❌ Yanıtla veya /mute @kullanici [dk]")
        return
    dakika = int(context.args[1]) if len(context.args) > 1 and context.args[1].isdigit() else None
    until = timedelta(minutes=dakika) if dakika else None
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        u.id,
        ChatPermissions(can_send_messages=False),
        until_date=until
    )
    await update.message.reply_text(f"🔇 {mention(u)} susturuldu", parse_mode="HTML")

async def unmute(update, context):
    if not await is_admin(update, context): return
    u = await get_target(update, context)
    if not u:
        await update.message.reply_text("❌ Yanıtla veya /unmute @kullanici")
        return
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        u.id,
        ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text(f"🔊 {mention(u)} susturma kaldırıldı", parse_mode="HTML")

async def lock(update, context):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(update.effective_chat.id, ChatPermissions())
        await update.message.reply_text("🔒 Grup kilitlendi")

async def unlock(update, context):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text("🔓 Grup açıldı")

# ================= ÇEKİLİŞ =================
def cekilis_caption():
    return (
        "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
        f"🔥 <b>KATILIMCI SAYISI :</b> {len(cekilis_katilimcilar)}\n\n"
        "🏆 Katılımcıların kanalları takip etmesi zorunludur!\n\n"
        + "\n".join([f"🔥 {k}" for k in ZORUNLU_KANALLAR])
    )

async def cekilis(update, context):
    global cekilis_aktif
    if not await is_admin(update, context): return
    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]
    ])

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=cekilis_caption(),
        reply_markup=kb,
        parse_mode="HTML"
    )

async def cekilis_buton(update, context):
    q = update.callback_query
    await q.answer()

    if not cekilis_aktif:
        return

    if q.from_user.id in cekilis_katilimcilar:
        await q.answer("Zaten katıldın", show_alert=True)
        return

    cekilis_katilimcilar.add(q.from_user.id)

    await q.edit_message_caption(
        caption=cekilis_caption(),
        reply_markup=q.message.reply_markup,
        parse_mode="HTML"
    )

# ================= KOMUTLAR =================
async def sayi(update, context):
    global cekilis_kazanan_sayisi
    if await is_admin(update, context):
        cekilis_kazanan_sayisi = int(context.args[0])
        await update.message.reply_text(f"🎯 Kazanan sayısı {cekilis_kazanan_sayisi}")

async def mesaj(update, context):
    global min_mesaj
    if await is_admin(update, context):
        min_mesaj = int(context.args[0])
        await update.message.reply_text(f"📝 Min mesaj: {min_mesaj}")

async def bitir(update, context):
    global cekilis_aktif, cekilis_kazananlar
    if not await is_admin(update, context): return
    cekilis_aktif = False

    cekilis_kazananlar = random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi, len(cekilis_katilimcilar))
    )

    msg = "🏆 <b>ÇEKİLİŞ BİTTİ</b>\n\n"
    for uid in cekilis_kazananlar:
        m = await context.bot.get_chat_member(update.effective_chat.id, uid)
        msg += f"🎁 {mention(m.user)}\n"

    await update.message.reply_text(msg, parse_mode="HTML")

async def kontrol(update, context):
    if not await is_admin(update, context): return
    msg = "📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"
    for uid in cekilis_kazananlar:
        m = await context.bot.get_chat_member(update.effective_chat.id, uid)
        sayi = mesaj_sayaci.get(uid,0)
        msg += f"❌ {mention(m.user)}\n"
        msg += f"   📨 Mesaj durumu: {sayi}/{min_mesaj}\n\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# ================= MESAJ KORUMA =================
async def mesaj_kontrol(update, context):
    if not update.message:
        return

    # ❌ HER TÜRLÜ İLETİLEN MESAJ YASAK
    if update.message.forward_from or update.message.forward_from_chat:
        await update.message.delete()
        return

    if await is_admin(update, context):
        return

    text = update.message.text.lower()

    # küfür
    if any(k in text for k in KUFUR):
        await update.message.delete()
        return

    # site tetik
    for k, v in SITE_LINKLERI.items():
        if k in text:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]
            ])
            await update.message.reply_text(
                f"✅ <b>{k.upper()}</b>",
                reply_markup=kb,
                parse_mode="HTML"
            )
            return

    # mesaj sayacı
    if update.message.date.timestamp() >= BOT_START:
        uid = update.message.from_user.id
        mesaj_sayaci[uid] = mesaj_sayaci.get(uid,0)+1

    # doğum kelimesi
    if "doğum" in text:
        kb = [[InlineKeyboardButton(a,url=b)] for a,b in DOGUM_SITELER]
        await update.message.reply_text(
            "🎁 <b>DOĞUM GÜNÜ BONUSLARI</b>",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

async def sponsor(update, context):
    kb = [[InlineKeyboardButton(a,url=b)] for a,b in SPONSOR_SITELER]
    await update.message.reply_text(
        "⭐ <b>SPONSOR SİTELER</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= APP =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))

app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CommandHandler("sayi", sayi))
app.add_handler(CommandHandler("mesaj", mesaj))
app.add_handler(CommandHandler("bitir", bitir))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CommandHandler("sponsor", sponsor))

app.add_handler(CallbackQueryHandler(cekilis_buton, pattern="^katil$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_kontrol))

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
