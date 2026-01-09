import os, time, random, re
from datetime import timedelta
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatMemberStatus

# ================= ENV =================
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ================= GLOBAL =================
BOT_START = time.time()

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazananlar = []
cekilis_kazanan_sayisi = 1
min_mesaj_sayisi = 0
cekilis_mesaj_id = None

mesaj_sayaci = {}
spam_log = {}
spam_warn = {}

SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= ZORUNLU KANALLAR =================
ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@BahisKarhanesi"
]

# ================= KÜFÜR =================
KUFUR_LISTESI = [
    "amk","aq","amq","orospu","piç","ibne","yarrak","yarak",
    "sik","siktir","amcık","anan","amına","oc"
]

# ================= SİTELER =================
SITE_LINKLERI = {
    "zbahis":"https://shoort.im/zbahis",
    "padisahbet":"https://shoort.im/padisahbet",
    "fixbet":"https://shoort.im/fixbet",
    "betoffice":"https://shoort.im/betoffice",
}

SPONSOR_SITELER = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("PADİŞAHBET","https://shoort.im/padisahbet"),
    ("FIXBET","https://shoort.im/fixbet"),
]

EVERY_SITELER = [
    ("HIZLICASINO","https://shoort.im/hizlicasino"),
    ("EGEBET","https://shoort.im/egebet"),
    ("KAVBET","https://shoort.im/kavbet"),
]

DOGUM_BONUS = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("FIXBET","https://shoort.im/fixbet"),
    ("BETOFFICE","https://shoort.im/betoffice"),
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

def mention(user):
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

# ================= FORWARD ENGEL =================
async def forward_engel(update, context):
    if not update.message:
        return

    # bağlı kanal postu serbest
    if update.message.sender_chat and update.message.sender_chat.type == "channel":
        return

    if await is_admin(update, context):
        return

    if update.message.forward_from or update.message.forward_from_chat:
        try:
            await update.message.delete()
        except:
            pass

# ================= KANAL ETİKET =================
async def kanal_etiket_engel(update, context):
    if not update.message or not update.message.text:
        return

    if update.message.sender_chat:
        return

    if await is_admin(update, context):
        return

    if re.search(r'@[\w_]{5,}', update.message.text):
        try:
            await update.message.delete()
        except:
            pass

# ================= SPAM =================
async def spam_kontrol(update, context):
    if not update.message:
        return
    if await is_admin(update, context):
        return

    uid = update.message.from_user.id
    now = time.time()
    spam_log.setdefault(uid, []).append(now)
    spam_log[uid] = [t for t in spam_log[uid] if now - t <= SPAM_SURE]

    if len(spam_log[uid]) >= SPAM_LIMIT:
        try:
            await update.message.delete()
        except:
            pass

# ================= KÜFÜR =================
async def kufur_kontrol(update, context):
    if not update.message or not update.message.text:
        return

    if await is_admin(update, context):
        return

    text = update.message.text.lower()
    for k in KUFUR_LISTESI:
        if k in text:
            try:
                await update.message.delete()
            except:
                pass
            return

# ================= MESAJ SAY =================
async def mesaj_say(update, context):
    if update.message.date.timestamp() < BOT_START:
        return
    uid = update.message.from_user.id
    mesaj_sayaci[uid] = mesaj_sayaci.get(uid, 0) + 1

# ================= SİTE =================
async def site_kontrol(update, context):
    if not update.message or not update.message.text:
        return
    if update.message.sender_chat:
        return

    text = update.message.text.lower()
    for k,v in SITE_LINKLERI.items():
        if k in text:
            kb = [[InlineKeyboardButton(
                "🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v
            )]]
            await update.message.reply_text(
                f"✅ <b>{k.upper()}</b>",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return

# ================= EVERY =================
async def every_kontrol(update, context):
    if not update.message or "every" not in update.message.text.lower():
        return

    kb = [[InlineKeyboardButton(a, url=b)] for a,b in EVERY_SITELER]
    await update.message.reply_text(
        "🔥 <b>EVERYMATRIX SİTELERİ</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= DOĞUM =================
async def dogum_kontrol(update, context):
    if not update.message or "doğum" not in update.message.text.lower():
        return

    kb = [[InlineKeyboardButton(a, url=b)] for a,b in DOGUM_BONUS]
    await update.message.reply_text(
        "🎁 <b>DOĞUM GÜNÜ BONUSLARI</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= SPONSOR =================
async def sponsor(update, context):
    kb = [[InlineKeyboardButton(a, url=b)] for a,b in SPONSOR_SITELER]
    await update.message.reply_text(
        "⭐ <b>SPONSOR SİTELER</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= BAN / UNBAN =================
async def ban(update, context):
    if not await is_admin(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Bir mesajı yanıtla")
        return
    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)

    kb = [[InlineKeyboardButton(
        "🔓 Banı Kaldır", callback_data=f"unban:{user.id}"
    )]]

    await update.message.reply_text(
        f"🔨 {mention(user)} banlandı",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def unban(update, context):
    pass  # butonla

async def unban_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not await is_admin(q, context):
        await q.answer("❌ Yetkin yok", show_alert=True)
        return

    uid = int(q.data.split(":")[1])
    await context.bot.unban_chat_member(q.message.chat.id, uid)
    await q.edit_message_text("🔓 Ban kaldırıldı")

# ================= MUTE / UNMUTE =================
async def mute(update, context):
    if not await is_admin(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Bir mesajı yanıtla")
        return
    user = update.message.reply_to_message.from_user

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False)
    )

    kb = [[InlineKeyboardButton(
        "🔊 Mute Kaldır", callback_data=f"unmute:{user.id}"
    )]]

    await update.message.reply_text(
        f"🔇 {mention(user)} susturuldu",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def unmute(update, context):
    pass

async def unmute_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not await is_admin(q, context):
        await q.answer("❌ Yetkin yok", show_alert=True)
        return

    uid = int(q.data.split(":")[1])
    await context.bot.restrict_chat_member(
        q.message.chat.id,
        uid,
        ChatPermissions(can_send_messages=True)
    )
    await q.edit_message_text("🔊 Mute kaldırıldı")

# ================= !SİL =================
async def sil(update, context):
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

# ================= LOCK =================
async def lock(update, context):
    if not await is_admin(update, context):
        return
    await context.bot.set_chat_permissions(
        update.effective_chat.id,
        ChatPermissions()
    )
    await update.message.reply_text("🔒 Grup kilitlendi")

async def unlock(update, context):
    if not await is_admin(update, context):
        return
    await context.bot.set_chat_permissions(
        update.effective_chat.id,
        ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text("🔓 Grup açıldı")

# ================= ÇEKİLİŞ =================
async def cekilis(update, context):
    global cekilis_aktif, cekilis_mesaj_id
    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    text = (
        "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
        "🔥 <b>KATILIMCI SAYISI :</b> 0\n\n"
        "🏆 Katılımcıların kanallarımızı takip etmesi zorunludur!\n\n" +
        "\n".join([f"🔥 https://t.me/{c[1:]}" for c in ZORUNLU_KANALLAR])
    )

    kb = [[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]]

    msg = await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )
    cekilis_mesaj_id = msg.message_id

async def cekilis_buton(update, context):
    global cekilis_mesaj_id
    q = update.callback_query
    await q.answer()

    cekilis_katilimcilar.add(q.from_user.id)

    text = (
        "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
        f"🔥 <b>KATILIMCI SAYISI :</b> {len(cekilis_katilimcilar)}\n\n"
        "🏆 Katılımcıların kanallarımızı takip etmesi zorunludur!\n\n" +
        "\n".join([f"🔥 https://t.me/{c[1:]}" for c in ZORUNLU_KANALLAR])
    )

    await q.edit_message_caption(
        caption=text,
        reply_markup=q.message.reply_markup,
        parse_mode="HTML"
    )

# ================= SAYI / MESAJ =================
async def sayi(update, context):
    global cekilis_kazanan_sayisi
    cekilis_kazanan_sayisi = int(context.args[0])
    await update.message.reply_text("🎯 Kazanan sayısı ayarlandı")

async def mesaj(update, context):
    global min_mesaj_sayisi
    min_mesaj_sayisi = int(context.args[0])
    await update.message.reply_text("📝 Mesaj şartı ayarlandı")

# ================= BİTİR =================
async def bitir(update, context):
    global cekilis_aktif, cekilis_kazananlar
    cekilis_aktif = False

    cekilis_kazananlar = random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi, len(cekilis_katilimcilar))
    )

    msg = "🏆 <b>ÇEKİLİŞ SONUCU</b>\n\n"
    for uid in cekilis_kazananlar:
        m = await context.bot.get_chat_member(update.effective_chat.id, uid)
        msg += f"🎁 {mention(m.user)}\n"

    await update.message.reply_text(msg, parse_mode="HTML")

# ================= KONTROL =================
async def kontrol(update, context):
    msg = "📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"
    for uid in cekilis_kazananlar:
        m = await context.bot.get_chat_member(update.effective_chat.id, uid)
        ms = mesaj_sayaci.get(uid,0)
        msg += f"❌ {mention(m.user)}\n   📨 Mesaj: {ms}/{min_mesaj_sayisi}\n\n"

    await update.message.reply_text(msg, parse_mode="HTML")

# ================= FILTER =================
async def add_filter(update, context):
    if not await is_admin(update, context):
        return
    if len(context.args) < 2:
        await update.message.reply_text("/filter site link")
        return
    SITE_LINKLERI[context.args[0].lower()] = context.args[1]
    await update.message.reply_text("✅ Filtre eklendi")

async def remove_filter(update, context):
    if not await is_admin(update, context):
        return
    if not context.args:
        return
    SITE_LINKLERI.pop(context.args[0].lower(), None)
    await update.message.reply_text("🗑️ Filtre kaldırıldı")

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

# COMMANDS
app.add_handler(CommandHandler("sponsor", sponsor))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CommandHandler("sayi", sayi))
app.add_handler(CommandHandler("mesaj", mesaj))
app.add_handler(CommandHandler("bitir", bitir))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))
app.add_handler(CommandHandler("filter", add_filter))
app.add_handler(CommandHandler("remove", remove_filter))

# CALLBACK
app.add_handler(CallbackQueryHandler(cekilis_buton, pattern="^katil$"))
app.add_handler(CallbackQueryHandler(unmute_button, pattern="^unmute:"))
app.add_handler(CallbackQueryHandler(unban_button, pattern="^unban:"))

# MESSAGE
app.add_handler(MessageHandler(filters.FORWARDED, forward_engel), group=0)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, site_kontrol), group=1)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, every_kontrol), group=2)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dogum_kontrol), group=3)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kanal_etiket_engel), group=4)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, spam_kontrol), group=5)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kufur_kontrol), group=6)
app.add_handler(MessageHandler(filters.Regex(r"^!sil \d+$"), sil), group=7)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_say), group=8)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
