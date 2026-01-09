# bot.py
import os
import time
import random
from dotenv import load_dotenv
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

# ================= KÜFÜR / SPAM =================
KUFUR = [
    "amk","aq","amq","orospu","piç","ibne",
    "yarrak","sik","amcık","anan","amına"
]
kufur_sayaci = {}
spam_log = {}
SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= SİTELER =================
filters_dict = {
    "zbahis": "https://shoort.im/zbahis",
    "padisahbet": "https://shoort.im/padisahbet",
    "fixbet": "https://shoort.im/fixbet",
    "betoffice": "https://shoort.im/betoffice",
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

# ================= DOĞUM =================
DOGUM = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("PADİŞAHBET","https://shoort.im/padisahbet"),
    ("FİXBET","https://shoort.im/fixbet"),
    ("BETOFFİCE","https://shoort.im/betoffice"),
]

# ================= ADMIN =================
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = await context.bot.get_chat_member(
            update.effective_chat.id, update.effective_user.id
        )
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

# ================= KORUMALAR =================
async def kufur_kontrol(update, context):
    if await is_admin(update, context): return
    text = update.message.text.lower()
    uid = update.message.from_user.id
    for k in KUFUR:
        if k in text:
            await update.message.delete()
            kufur_sayaci[uid] = kufur_sayaci.get(uid,0)+1
            await context.bot.restrict_chat_member(
                update.effective_chat.id, uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time())+3600
            )
            return

async def spam_kontrol(update, context):
    if await is_admin(update, context): return
    uid = update.message.from_user.id
    now = time.time()
    spam_log.setdefault(uid, []).append(now)
    spam_log[uid] = [t for t in spam_log[uid] if now-t<=SPAM_SURE]
    if len(spam_log[uid]) >= SPAM_LIMIT:
        await update.message.delete()

async def link_engel(update, context):
    if await is_admin(update, context): return
    if any(x in update.message.text.lower() for x in ["http","t.me","www"]):
        await update.message.delete()

# ================= MESAJ SAY =================
async def mesaj_say(update, context):
    if update.message.date.timestamp() < BOT_START: return
    uid = update.message.from_user.id
    kullanici_mesaj[uid] = kullanici_mesaj.get(uid,0)+1

# ================= SİTE =================
async def site_kontrol(update, context):
    text = update.message.text.lower()
    for k,v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]]
            )
            await update.message.reply_text(
                f"✅ <b>{k.upper()} GİRİŞ</b>",
                reply_markup=kb,
                parse_mode="HTML"
            )
            return

# ================= DOĞUM =================
async def dogum_kontrol(update, context):
    if "doğum" not in update.message.text.lower(): return
    kb, row = [], []
    for i,(n,l) in enumerate(DOGUM,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)
    await update.message.reply_text(
        "🎁 <b>DOĞUM GÜNÜ BONUSLARI</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= EVERY =================
async def every_kontrol(update, context):
    if "every" not in update.message.text.lower(): return
    kb=[]
    row=[]
    for i,(n,l) in enumerate(EVERY_SPONSOR,1):
        row.append(InlineKeyboardButton(n,url=l))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)
    kb.append([InlineKeyboardButton("— DİĞER EVERYMATRIX —",callback_data="x")])
    row=[]
    for i,(n,l) in enumerate(EVERY_DIGER,1):
        row.append(InlineKeyboardButton(n,url=l))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)
    await update.message.reply_text(
        "🔥 <b>EVERYMATRIX SİTELERİ</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= SPONSOR =================
async def sponsor(update, context):
    kb=[]
    row=[]
    for i,(n,l) in enumerate(filters_dict.items(),1):
        row.append(InlineKeyboardButton(n.upper(),url=l))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)
    await update.message.reply_text(
        "⭐ <b>SPONSOR SİTELER</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= ÇEKİLİŞ =================
async def cekilis(update, context):
    global cekilis_aktif
    cekilis_aktif=True
    cekilis_katilimcilar.clear()
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL",callback_data="katil")]])
    await context.bot.send_photo(
        update.effective_chat.id,
        open("cekilis.jpg","rb"),
        caption=(
            "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
            "🔥 <b>KATILIMCI SAYISI :</b> 0\n\n"
            "🏆 Katılımcıların kanalları takip etmesi zorunludur!"
        ),
        reply_markup=kb,
        parse_mode="HTML"
    )

async def cekilis_buton(update, context):
    q=update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n🔥 <b>KATILIMCI SAYISI :</b> {len(cekilis_katilimcilar)}",
        reply_markup=q.message.reply_markup,
        parse_mode="HTML"
    )

async def sayi(update, context):
    global cekilis_kazanan_sayisi
    cekilis_kazanan_sayisi=int(context.args[0])

async def bitir(update, context):
    global cekilis_aktif
    cekilis_aktif=False
    kazananlar=random.sample(list(cekilis_katilimcilar),cekilis_kazanan_sayisi)
    msg="🏆 <b>KAZANANLAR</b>\n\n"
    for uid in kazananlar:
        msg+=f"🎁 <a href='tg://user?id={uid}'>Kazanan</a>\n"
    await update.message.reply_text(msg,parse_mode="HTML")

async def kontrol(update, context):
    msg="📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"
    for uid in cekilis_katilimcilar:
        mesaj=kullanici_mesaj.get(uid,0)
        msg+=f"❌ <a href='tg://user?id={uid}'>Kullanıcı</a>\n"
        msg+=f"   📨 Mesaj durumu: {mesaj}/{min_mesaj}\n\n"
    await update.message.reply_text(msg,parse_mode="HTML")

# ================= YÖNETİM =================
async def ban(update, context):
    if update.message.reply_to_message:
        await context.bot.ban_chat_member(
            update.effective_chat.id,
            update.message.reply_to_message.from_user.id
        )

async def unban(update, context):
    await context.bot.unban_chat_member(update.effective_chat.id,int(context.args[0]))

async def mute(update, context):
    target=update.message.reply_to_message.from_user
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        target.id,
        ChatPermissions(can_send_messages=False)
    )

async def unmute(update, context):
    target=update.message.reply_to_message.from_user
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        target.id,
        ChatPermissions(can_send_messages=True)
    )

async def lock(update, context):
    await context.bot.set_chat_permissions(update.effective_chat.id,ChatPermissions())

async def unlock(update, context):
    await context.bot.set_chat_permissions(update.effective_chat.id,ChatPermissions(can_send_messages=True))

async def sil(update, context):
    n=int(update.message.text.split()[1])
    for i in range(n):
        await context.bot.delete_message(update.effective_chat.id,update.message.message_id-i)

# ================= BOT =================
app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("ban",ban))
app.add_handler(CommandHandler("unban",unban))
app.add_handler(CommandHandler("mute",mute))
app.add_handler(CommandHandler("unmute",unmute))
app.add_handler(CommandHandler("lock",lock))
app.add_handler(CommandHandler("unlock",unlock))
app.add_handler(CommandHandler("sponsor",sponsor))
app.add_handler(CommandHandler("cekilis",cekilis))
app.add_handler(CommandHandler("sayi",sayi))
app.add_handler(CommandHandler("bitir",bitir))
app.add_handler(CommandHandler("kontrol",kontrol))
app.add_handler(MessageHandler(tg_filters.Regex(r"^!sil \d+$"),sil))
app.add_handler(CallbackQueryHandler(cekilis_buton))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, kufur_kontrol),0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, link_engel),1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, spam_kontrol),2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, mesaj_say),3)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, dogum_kontrol),4)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every_kontrol),5)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, site_kontrol),6)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
