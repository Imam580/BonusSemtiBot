# bot.py
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
# === ÇEKİLİŞ GLOBAL ===
cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1
cekilis_kazananlar = []

ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@hergunikioran",
    "@BahisKarhanesi",
    "@ozel_oran_2024",
]


# ---- çekiliş ----
cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1
cekilis_kazananlar = []

# ---- mesaj ----
kullanici_mesaj = {}
min_mesaj = 0

# ---- küfür / spam ----
KUFUR_LISTESI = [
    "amk","aq","amq","orospu","orospu çocuğu","piç","ibne",
    "yarrak","yarak","sik","siktir","amcık","anan","amına"
]
kufur_sayaci = {}
spam_log = {}
spam_warn = {}
SPAM_SURE = 5
SPAM_LIMIT = 5

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

EVERY_SPONSOR = [
    ("HIZLICASINO","https://shoort.im/hizlicasino"),
    ("EGEBET","https://shoort.im/egebet"),
    ("KAVBET","https://shoort.im/kavbet"),
    ("PUSULABET","https://shoort.im/pusulabet"),
    ("HITBET","https://shoort.im/hitbet"),
    ("ARTEMISBET","https://shoort.im/artemisbet"),
]

EVERY_DIGER = [
    ("SOSYAL DAVET","https://linkturbo.co/sosyaldavet"),
    ("MATGUNCEL","http://dub.is/matguncel"),
    ("JOJOBET","http://dub.pro/jojoyagit"),
    ("HOLIGANBET","https://dub.pro/holiguncel"),
    ("BETSMOVE","http://dub.is/betsmoveguncel"),
    ("LUNASOSYAL","http://lunalink.org/lunasosyal/"),
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

# ================= KÜFÜR =================
async def kufur_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    text = update.message.text.lower()
    uid = update.message.from_user.id

    for k in KUFUR_LISTESI:
        if k in text:
            await update.message.delete()
            kufur_sayaci[uid] = kufur_sayaci.get(uid,0)+1
            sure = 300 if kufur_sayaci[uid]==1 else 3600
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time())+sure
            )
            return

# ================= LINK =================
async def link_engel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    if any(x in update.message.text.lower() for x in ["http","t.me","www"]):
        await update.message.delete()
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.from_user.id,
            ChatPermissions(can_send_messages=False),
            until_date=int(time.time())+3600
        )

# ================= SPAM =================
async def spam_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return
    uid = update.message.from_user.id
    now = time.time()
    spam_log.setdefault(uid, []).append(now)
    spam_log[uid] = [t for t in spam_log[uid] if now-t<=SPAM_SURE]

    if len(spam_log[uid])>=SPAM_LIMIT:
        await update.message.delete()
        if spam_warn.get(uid):
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time())+3600
            )
            spam_log[uid]=[]
            spam_warn[uid]=False
        else:
            spam_warn[uid]=True

# ================= /SPONSOR =================
async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb=[]
    row=[]
    for i,(k,v) in enumerate(filters_dict.items(),1):
        row.append(InlineKeyboardButton(k.upper(),url=v))
        if i%2==0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "⭐ **SPONSOR SİTELER**\n\n👇 **Butona tıklayarak siteye yönelebilirsiniz.**",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================= EVERY =================
async def every(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" not in update.message.text.lower():
        return
    kb=[]
    r=[]
    for i,(n,l) in enumerate(EVERY_SPONSOR,1):
        r.append(InlineKeyboardButton(n,url=l))
        if i%2==0: kb.append(r); r=[]
    if r: kb.append(r)
    kb.append([InlineKeyboardButton("──── DİĞERLERİ ────",callback_data="x")])
    r=[]
    for i,(n,l) in enumerate(EVERY_DIGER,1):
        r.append(InlineKeyboardButton(n,url=l))
        if i%2==0: kb.append(r); r=[]
    if r: kb.append(r)

    await update.message.reply_text(
        "🔥 **EVERYMATRIX SİTELERİ**\n\n👇 **Butona tıklayarak siteye yönelebilirsiniz.**",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================= DOĞUM =================
async def dogum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "doğum" not in update.message.text.lower():
        return
    kb=[]
    row=[]
    for i,(k,v) in enumerate(filters_dict.items(),1):
        row.append(InlineKeyboardButton(k.upper(),url=v))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)
    await update.message.reply_text(
        "🎁 **DOĞUM GÜNÜ BONUSLARI**",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================= !SİL =================
async def sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    try:
        n=int(update.message.text.split()[1])
    except:
        return
    for i in range(n):
        try:
            await context.bot.delete_message(
                update.effective_chat.id,
                update.message.message_id-i
            )
        except: pass

# ================= BAN / MUTE =================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and update.message.reply_to_message:
        await context.bot.ban_chat_member(
            update.effective_chat.id,
            update.message.reply_to_message.from_user.id
        )

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and context.args:
        await context.bot.unban_chat_member(
            update.effective_chat.id,int(context.args[0])
        )

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and update.message.reply_to_message:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.reply_to_message.from_user.id,
            ChatPermissions(can_send_messages=False)
        )

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context) and update.message.reply_to_message:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.reply_to_message.from_user.id,
            ChatPermissions(can_send_messages=True)
        )

# ================= ÇEKİLİŞ =================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_katilimcilar

    if not await is_admin(update, context):
        return

    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="cekilise_katil")]
    ])

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("cekilis.jpg", "rb"),
        caption=(
            "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
            "👥 <b>KATILIMCI SAYISI:</b> 0\n\n"
            "📌 <b>Katılım Şartları</b>\n"
            "• Kanallarımızı takip et\n"
            "• Aktif üye ol\n\n"
            "📢 <b>Zorunlu Kanallar</b>\n"
            "🔹 https://t.me/Canli_Izleme_Mac_Linkleri\n"
            "🔹 https://t.me/plasespor\n"
            "🔹 https://t.me/bonussemti\n"
            "🔹 https://t.me/bonussemtietkinlik\n"
            "🔹 https://t.me/hergunikioran\n"
            "🔹 https://t.me/BahisKarhanesi\n"
            "🔹 https://t.me/ozel_oran_2024"
        ),
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_katilimcilar

    query = update.callback_query
    await query.answer()

    if not cekilis_aktif:
        return

    uid = query.from_user.id

    if uid in cekilis_katilimcilar:
        await query.answer("Zaten katıldın 😊", show_alert=True)
        return

    cekilis_katilimcilar.add(uid)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="cekilise_katil")]
    ])

    await query.edit_message_caption(
        caption=query.message.caption.replace(
            "KATILIMCI SAYISI:</b>",
            f"KATILIMCI SAYISI:</b> {len(cekilis_katilimcilar)}"
        ),
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def sayi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_kazanan_sayisi

    if not await is_admin(update, context):
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Kullanım: /sayi 3")
        return

    cekilis_kazanan_sayisi = int(context.args[0])
    await update.message.reply_text(
        f"🎯 Kazanan sayısı {cekilis_kazanan_sayisi} olarak ayarlandı."
    )

async def bitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_kazananlar

    if not await is_admin(update, context):
        return

    cekilis_aktif = False

    if not cekilis_katilimcilar:
        await update.message.reply_text("Katılım olmadığı için çekiliş iptal edildi.")
        return

    cekilis_kazananlar = random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi, len(cekilis_katilimcilar))
    )

    msg = "🏆 <b>ÇEKİLİŞ KAZANANLARI</b>\n\n"

    for uid in cekilis_kazananlar:
        msg += f"🎁 <a href='tg://user?id={uid}'>Kazanan</a>\n"

    await update.message.reply_text(msg, parse_mode="HTML")

async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not cekilis_kazananlar:
        await update.message.reply_text("Henüz kazanan yok.")
        return

    msg = "📋 <b>KAZANAN KONTROL</b>\n\n"

    for uid in cekilis_kazananlar:
        eksik = []
        for kanal in ZORUNLU_KANALLAR:
            try:
                m = await context.bot.get_chat_member(kanal, uid)
                if m.status not in ["member", "administrator", "creator"]:
                    eksik.append(kanal)
            except:
                eksik.append(kanal)

        msg += f"👤 <a href='tg://user?id={uid}'>Kullanıcı</a>\n"
        msg += "✅ Tüm kanallar tamam\n\n" if not eksik else "❌ Eksik kanallar:\n" + "\n".join(eksik) + "\n\n"

    await update.message.reply_text(msg, parse_mode="HTML")



# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("sponsor", sponsor))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CommandHandler("sayi", sayi))
app.add_handler(CommandHandler("bitir", bitir))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CallbackQueryHandler(cekilis_buton, pattern="^cekilise_katil$"))
app.add_handler(MessageHandler(tg_filters.Regex(r"^!sil \d+$"), sil))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, kufur_kontrol), group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, link_engel), group=1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, spam_kontrol), group=2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every), group=3)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, dogum), group=4)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
