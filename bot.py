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
TOKEN = os.environ.get("TOKEN")

# ================= GLOBAL =================
BOT_BASLANGIC = time.time()

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazananlar = []
cekilis_kazanan_sayisi = 1

kullanici_mesaj_sayisi = {}
min_mesaj_sayisi = 0

kufur_sayaci = {}
spam_log = {}
spam_warn = {}

# ================= ZORUNLU KANALLAR =================
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
    "amk","aq","amq","orospu","orospu çocuğu","piç","ibne",
    "yarrak","yarak","sik","siktir","amcık","anan","amına"
]

# ================= SPAM =================
SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= FİLTRELER =================
filters_dict = {
    "zbahis":"https://shoort.im/zbahis",
    "padisahbet":"https://shoort.im/padisahbet",
    "fixbet":"https://shoort.im/fixbet",
    "betmatik":"https://shoort.im/betmatik",
    "egebet":"https://shoort.im/egebet",
    "kavbet":"https://shoort.im/kavbet",
    "hitbet":"https://shoort.im/hitbet",
    "pusulabet":"https://shoort.im/pusulabet",
    "artemisbet":"https://shoort.im/artemisbet",
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
    ("ODEONBET","http://dub.is/odeonguncel"),
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
    spam_log.setdefault(uid,[]).append(now)
    spam_log[uid] = [t for t in spam_log[uid] if now-t<=SPAM_SURE]

    if len(spam_log[uid])>=SPAM_LIMIT:
        await update.message.delete()

# ================= SİTE =================
async def site_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for k,v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]]
            )
            await update.message.reply_text(
                f"🔗 {k.upper()} GİRİŞ",
                reply_markup=kb
            )
            return

# ================= EVERY =================
async def every_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" not in update.message.text.lower():
        return

    kb=[]
    row=[]
    for i,(n,l) in enumerate(EVERY_SPONSOR,1):
        row.append(InlineKeyboardButton(n,url=l))
        if i%2==0:
            kb.append(row); row=[]
    if row: kb.append(row)

    kb.append([InlineKeyboardButton("────────",callback_data="x")])

    row=[]
    for i,(n,l) in enumerate(EVERY_DIGER,1):
        row.append(InlineKeyboardButton(n,url=l))
        if i%2==0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🔥 BonusSemti Güvencesiyle EveryMatrix Siteleri\n\n"
        "⭐ Sponsorumuz Olan Siteler\n"
        "👇 Butona tıklayarak siteye yönelebilirsiniz.",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= MESAJ SAY =================
async def mesaj_say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.date.timestamp() < BOT_BASLANGIC:
        return
    uid = update.message.from_user.id
    kullanici_mesaj_sayisi[uid]=kullanici_mesaj_sayisi.get(uid,0)+1

# ================= /MESAJ =================
async def mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global min_mesaj_sayisi
    if not await is_admin(update, context):
        return
    min_mesaj_sayisi = int(context.args[0])
    await update.message.reply_text(f"📝 Minimum mesaj: {min_mesaj_sayisi}")

# ================= ÇEKİLİŞ =================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    cekilis_aktif=True
    cekilis_katilimcilar.clear()

    kb=InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL",callback_data="katil")]]
    )

    await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption="🔥 BONUSSEMTİ ÇEKİLİŞİ\n\nKatılımcı: 0",
        reply_markup=kb
    )

async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🔥 BONUSSEMTİ ÇEKİLİŞİ\n\nKatılımcı: {len(cekilis_katilimcilar)}"
    )

# ================= /SAYI =================
async def sayi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_kazanan_sayisi
    cekilis_kazanan_sayisi=int(context.args[0])
    await update.message.reply_text("🎯 Ayarlandı")

# ================= /BITIR =================
async def bitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_kazananlar
    cekilis_aktif=False
    cekilis_kazananlar=random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi,len(cekilis_katilimcilar))
    )
    await update.message.reply_text("🏆 Kazananlar belirlendi")

# ================= KONTROL =================
async def kanallari_kontrol(uid,context):
    eksik=[]
    for k in ZORUNLU_KANALLAR:
        try:
            m=await context.bot.get_chat_member(k,uid)
            if m.status not in ["member","administrator","creator"]:
                eksik.append(k)
        except:
            eksik.append(k)
    return eksik

async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg="📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"
    for uid in cekilis_kazananlar:
        u=await context.bot.get_chat_member(update.effective_chat.id,uid)
        isim=f"@{u.user.username}" if u.user.username else u.user.first_name
        mesaj=kullanici_mesaj_sayisi.get(uid,0)
        eksik=await kanallari_kontrol(uid,context)

        msg+=f"❌ {isim}\n"
        msg+=f"   📨 Mesaj durumu: {mesaj} / {min_mesaj_sayisi}\n"
        if eksik:
            msg+="   📢 Kanal durumu:\n"
            for e in eksik:
                msg+=f"      • {e}\n"
        else:
            msg+="   📢 Kanal durumu: Tüm kanallara katılım sağlanmıştır.\n"
        msg+="\n"

    await update.message.reply_text(msg,parse_mode="HTML")

# ================= BOT =================
app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("cekilis",cekilis))
app.add_handler(CommandHandler("sayi",sayi))
app.add_handler(CommandHandler("bitir",bitir))
app.add_handler(CommandHandler("kontrol",kontrol))
app.add_handler(CommandHandler("mesaj",mesaj))
app.add_handler(CallbackQueryHandler(cekilis_buton,"katil"))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, kufur_kontrol),0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, link_engel),1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, spam_kontrol),2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, mesaj_say),3)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every_kontrol),4)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, site_kontrol),5)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
