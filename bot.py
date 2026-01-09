# =========================
# BONUSSEMTİ BOT - FULL FIX
# python-telegram-bot 20.3
# =========================

import os, time, random, re
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
min_mesaj_sayisi = 0
cekilis_mesaj_id = None

mesaj_sayaci = {}

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
    "amk","oç","amq","orospu","orospu çocuğu",
    "piç","ibne","yarrak","yarak",
    "sik","siktir","amcık","anan","amına"
]

kufur_sayaci = {}

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

DOGUM_SITELER = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("PADİŞAHBET","https://shoort.im/padisahbet"),
    ("FIXBET","https://shoort.im/fixbet"),
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
    if context.args:
        username = context.args[0].replace("@","")
        member = await context.bot.get_chat_member(
            update.effective_chat.id, username
        )
        return member.user
    return None

def mention(user):
    return f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"

# ================= KANAL ETİKET ENGEL =================
async def kanal_etiket_engel(update, context):
    if not update.message or not update.message.text:
        return
    if await is_admin(update, context):
        return

    mentions = re.findall(r'@([A-Za-z0-9_]{5,})', update.message.text)
    for m in mentions:
        try:
            await context.bot.get_chat_member(f"@{m}", update.message.from_user.id)
            await update.message.delete()
            return
        except:
            pass

# ================= FORWARD ENGEL =================
async def forward_engel(update, context):
    if update.message.forward_from or update.message.forward_from_chat:
        await update.message.delete()

# ================= MESAJ SAY =================
async def mesaj_say(update, context):
    if update.message.date.timestamp() < BOT_START:
        return
    uid = update.message.from_user.id
    mesaj_sayaci[uid] = mesaj_sayaci.get(uid,0) + 1

# ================= KÜFÜR =================
async def kufur_kontrol(update, context):
    if await is_admin(update, context):
        return
    text = update.message.text.lower()
    uid = update.message.from_user.id
    for k in KUFUR_LISTESI:
        if k in text:
            await update.message.delete()
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time())+300
            )
            return

# ================= SİTE TETİK =================
async def site_kontrol(update, context):
    text = update.message.text.lower()

    if "doğum" in text:
        kb = [[InlineKeyboardButton(a, url=b)] for a,b in DOGUM_SITELER]
        await update.message.reply_text(
            "🎁 <b>DOĞUM GÜNÜ BONUSLARI</b>",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )
        return

    if "every" in text:
        kb = [[InlineKeyboardButton(a, url=b)] for a,b in SPONSOR_SITELER]
        await update.message.reply_text(
            "⭐ <b>EVERYMATRIX SPONSOR SİTELER</b>\n👇 Butona tıklayarak siteye gidebilirsiniz",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )
        return

    for k,v in SITE_LINKLERI.items():
        if k in text:
            kb=[[InlineKeyboardButton(
                "🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ",
                url=v
            )]]
            await update.message.reply_text(
                f"✅ <b>{k.upper()}</b>",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return

# ================= SPONSOR =================
async def sponsor(update, context):
    kb = [[InlineKeyboardButton(a, url=b)] for a,b in SPONSOR_SITELER]
    await update.message.reply_text(
        "⭐ <b>SPONSOR SİTELER</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= BAN / MUTE =================
async def ban(update, context):
    if not await is_admin(update, context): return
    user = await hedef_kullanici(update, context)
    if not user:
        await update.message.reply_text("❌ Birini yanıtla veya /ban @kullanici")
        return
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"🔨 {mention(user)} banlandı", parse_mode="HTML")

async def unban(update, context):
    if not await is_admin(update, context): return
    user = await hedef_kullanici(update, context)
    if not user:
        await update.message.reply_text("❌ /unban @kullanici")
        return
    await context.bot.unban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"✅ {mention(user)} banı açıldı", parse_mode="HTML")

async def mute(update, context):
    if not await is_admin(update, context): return
    user = await hedef_kullanici(update, context)
    if not user:
        await update.message.reply_text("❌ /mute @kullanici 10")
        return

    dakika = int(context.args[1]) if len(context.args)>1 and context.args[1].isdigit() else None
    until = int(time.time()) + (dakika*60) if dakika else None

    kb = [[InlineKeyboardButton("🔓 Muteyi Kaldır", callback_data=f"unmute:{user.id}")]]
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False),
        until_date=until
    )
    await update.message.reply_text(
        f"🔇 {mention(user)} susturuldu",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def unmute(update, context):
    if not await is_admin(update, context): return
    user = await hedef_kullanici(update, context)
    if not user:
        return
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text(f"🔊 {mention(user)} açıldı", parse_mode="HTML")

async def unmute_button(update, context):
    q = update.callback_query
    uid = int(q.data.split(":")[1])
    await context.bot.restrict_chat_member(
        q.message.chat.id,
        uid,
        ChatPermissions(can_send_messages=True)
    )
    await q.edit_message_text("🔓 Mute kaldırıldı")

# ================= !SİL =================
async def sil(update, context):
    if not await is_admin(update, context): return
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

# ================= ÇEKİLİŞ =================
async def cekilis(update, context):
    global cekilis_aktif, cekilis_mesaj_id
    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    kb = [[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]]
    msg = await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=(
            "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
            "🔥 <b>KATILIMCI SAYISI :</b> 0\n\n"
            "🏆 Katılımcıların kanallarımızı takip etmesi zorunludur!"
        ),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )
    cekilis_mesaj_id = msg.message_id

async def cekilis_buton(update, context):
    q = update.callback_query
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🔥 <b>KATILIMCI SAYISI :</b> {len(cekilis_katilimcilar)}",
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
        eksik = []
        for ch in ZORUNLU_KANALLAR:
            try:
                cm = await context.bot.get_chat_member(ch, uid)
                if cm.status == "left":
                    eksik.append(ch)
            except:
                eksik.append(ch)

        msg += f"❌ {mention(m.user)}\n"
        msg += f"   📨 Mesaj: {ms}/{min_mesaj_sayisi}\n"
        if eksik:
            msg += "   📢 Eksik kanallar:\n"
            for e in eksik:
                msg += f"      • {e}\n"
        msg += "\n"

    await update.message.reply_text(msg, parse_mode="HTML")

# ================= LOCK =================
async def lock(update, context):
    if not await is_admin(update, context): return
    await context.bot.set_chat_permissions(update.effective_chat.id, ChatPermissions())
    await update.message.reply_text("🔒 Grup kilitlendi")

async def unlock(update, context):
    if not await is_admin(update, context): return
    await context.bot.set_chat_permissions(
        update.effective_chat.id,
        ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text("🔓 Grup açıldı")

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

# CALLBACK
app.add_handler(CallbackQueryHandler(cekilis_buton, pattern="^katil$"))
app.add_handler(CallbackQueryHandler(unmute_button, pattern="^unmute:"))

# MESSAGE
app.add_handler(MessageHandler(filters.Regex(r"^!sil \d+$"), sil))
app.add_handler(MessageHandler(filters.FORWARDED, forward_engel))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kanal_etiket_engel))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, site_kontrol))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_say))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kufur_kontrol))

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
