# bot.py
import os, time, random, re
from datetime import timedelta
from dotenv import load_dotenv
from telegram import *
from telegram.constants import ChatMemberStatus
from telegram.ext import *

# ================= ENV =================
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ================= GLOBAL =================
BOT_BASLANGIC = time.time()

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazananlar = []
cekilis_kazanan_sayisi = 1

min_mesaj_sayisi = 0
kullanici_mesaj_sayisi = {}

kufur_sayaci = {}
spam_log = {}

# ================= KANALLAR =================
ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@BahisKarhanesi"
]

# ================= KÜFÜR =================
KUFUR_LISTESI = [
    "amk","aq","oç","amq","orospu","orospu çocuğu",
    "piç","ibne","yarrak","yarak","sik","siktir",
    "amcık","anan","amına"
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

DOGUM_BONUS = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("FIXBET","https://shoort.im/fixbet"),
    ("BETOFFICE","https://shoort.im/betoffice"),
]

EVERY_SPONSOR = [
    ("HIZLICASINO","https://shoort.im/hizlicasino"),
    ("EGEBET","https://shoort.im/egebet"),
]

EVERY_DIGER = [
    ("JOJOBET","http://dub.pro/jojoyagit"),
    ("HOLIGANBET","https://dub.pro/holiguncel"),
]

# ================= YARDIMCI =================
def mention(user):
    if user.username:
        return f"@{user.username}"
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

async def is_admin(update, context):
    try:
        m = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
        )
        return m.status in ["administrator","creator"]
    except:
        return False

async def hedef_kullanici(update, context):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    if context.args:
        uname = context.args[0].replace("@","")
        m = await context.bot.get_chat_member(update.effective_chat.id, uname)
        return m.user
    return None

# ================= ENGELLER =================
async def kanal_etiket_engel(update, context):
    if await is_admin(update, context): return
    mentions = re.findall(r'@([A-Za-z0-9_]{5,})', update.message.text)
    for m in mentions:
        try:
            await context.bot.get_chat_member(f"@{m}", update.message.from_user.id)
            await update.message.delete()
            return
        except:
            pass

async def forward_engel(update, context):
    if update.message.forward_from or update.message.forward_from_chat:
        await update.message.delete()

async def link_engel(update, context):
    if await is_admin(update, context): return
    if any(x in update.message.text.lower() for x in ["http","t.me","www"]):
        await update.message.delete()
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.from_user.id,
            ChatPermissions(can_send_messages=False),
            until_date=int(time.time())+3600
        )

async def kufur_kontrol(update, context):
    if await is_admin(update, context): return
    text = update.message.text.lower()
    for k in KUFUR_LISTESI:
        if k in text:
            await update.message.delete()
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                update.message.from_user.id,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time())+300
            )
            return

# ================= MESAJ SAY =================
async def mesaj_say(update, context):
    if update.message.date.timestamp() < BOT_BASLANGIC: return
    uid = update.message.from_user.id
    kullanici_mesaj_sayisi[uid] = kullanici_mesaj_sayisi.get(uid,0)+1

# ================= SPONSOR / EVERY / DOGUM =================
async def sponsor(update, context):
    kb, row = [], []
    for i,(a,b) in enumerate(SPONSOR_SITELER,1):
        row.append(InlineKeyboardButton(a,url=b))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)
    await update.message.reply_text(
        "⭐ <b>SPONSOR SİTELER</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def every_kontrol(update, context):
    if "every" not in update.message.text.lower(): return
    kb=[]
    for a,b in EVERY_SPONSOR:
        kb.append([InlineKeyboardButton(f"⭐ {a}",url=b)])
    kb.append([InlineKeyboardButton("────────",callback_data="bos")])
    for a,b in EVERY_DIGER:
        kb.append([InlineKeyboardButton(a,url=b)])
    await update.message.reply_text(
        "🔥 <b>EVERYMATRIX SİTELER</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def dogum(update, context):
    if "doğum" not in update.message.text.lower(): return
    kb=[]
    for a,b in DOGUM_BONUS:
        kb.append([InlineKeyboardButton(a,url=b)])
    await update.message.reply_text(
        "🎁 <b>DOĞUM GÜNÜ BONUSLARI</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def site_kontrol(update, context):
    for k,v in SITE_LINKLERI.items():
        if k in update.message.text.lower():
            await update.message.reply_text(
                "👇 BUTONA TIKLAYARAK GİRİŞ YAPABİLİRSİNİZ",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(k.upper(),url=v)]]
                )
            )
            return

# ================= YÖNETİM =================
async def ban(update, context):
    if not await is_admin(update, context): return
    user = await hedef_kullanici(update, context)
    if not user:
        await update.message.reply_text("❌ Reply ya da /ban @kullanici")
        return
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"🔨 {mention(user)} banlandı", parse_mode="HTML")

async def mute(update, context):
    if not await is_admin(update, context): return
    user = await hedef_kullanici(update, context)
    if not user:
        await update.message.reply_text("❌ Reply ya da /mute @kullanici 10")
        return
    dk = int(context.args[1]) if len(context.args)>1 and context.args[1].isdigit() else 5
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False),
        until_date=int(time.time())+dk*60
    )
    await update.message.reply_text(f"🔇 {mention(user)} susturuldu", parse_mode="HTML")

async def unmute(update, context):
    if not await is_admin(update, context): return
    user = await hedef_kullanici(update, context)
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=True)
    )

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

async def sil(update, context):
    if not await is_admin(update, context): return
    n = int(update.message.text.split()[1])
    for i in range(n):
        try:
            await context.bot.delete_message(
                update.effective_chat.id,
                update.message.message_id-i
            )
        except: pass

# ================= ÇEKİLİŞ =================
async def cekilis(update, context):
    global cekilis_aktif
    cekilis_aktif=True
    cekilis_katilimcilar.clear()
    await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=(
            "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
            "🔥 <b>KATILIMCI SAYISI :</b> 0\n\n"
            "🏆 Kanalları takip etmek zorunludur"
        ),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL",callback_data="katil")]]
        ),
        parse_mode="HTML"
    )

async def cekilis_buton(update, context):
    q=update.callback_query
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🔥 <b>KATILIMCI SAYISI :</b> {len(cekilis_katilimcilar)}",
        parse_mode="HTML"
    )

async def sayi(update, context):
    global cekilis_kazanan_sayisi
    cekilis_kazanan_sayisi=int(context.args[0])

async def mesaj(update, context):
    global min_mesaj_sayisi
    min_mesaj_sayisi=int(context.args[0])

async def bitir(update, context):
    global cekilis_aktif, cekilis_kazananlar
    cekilis_aktif=False
    cekilis_kazananlar=random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi,len(cekilis_katilimcilar))
    )
    msg="🏆 <b>ÇEKİLİŞ SONUCU</b>\n\n"
    for uid in cekilis_kazananlar:
        m=await context.bot.get_chat_member(update.effective_chat.id,uid)
        msg+=f"🎁 {mention(m.user)}\n"
    await update.message.reply_text(msg,parse_mode="HTML")

async def kontrol(update, context):
    msg="📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"
    for uid in cekilis_kazananlar:
        m=await context.bot.get_chat_member(update.effective_chat.id,uid)
        ms=kullanici_mesaj_sayisi.get(uid,0)
        eksik=[]
        for k in ZORUNLU_KANALLAR:
            try:
                cm=await context.bot.get_chat_member(k,uid)
                if cm.status not in ["member","administrator","creator"]:
                    eksik.append(k)
            except:
                eksik.append(k)
        msg+=f"❌ {mention(m.user)}\n   📨 {ms}/{min_mesaj_sayisi}\n"
        if eksik:
            for e in eksik: msg+=f"      • {e}\n"
        msg+="\n"
    await update.message.reply_text(msg,parse_mode="HTML")

# ================= BOT =================
app=ApplicationBuilder().token(TOKEN).build()

# COMMANDS
app.add_handler(CommandHandler("sponsor",sponsor))
app.add_handler(CommandHandler("ban",ban))
app.add_handler(CommandHandler("mute",mute))
app.add_handler(CommandHandler("unmute",unmute))
app.add_handler(CommandHandler("lock",lock))
app.add_handler(CommandHandler("unlock",unlock))
app.add_handler(CommandHandler("cekilis",cekilis))
app.add_handler(CommandHandler("sayi",sayi))
app.add_handler(CommandHandler("mesaj",mesaj))
app.add_handler(CommandHandler("bitir",bitir))
app.add_handler(CommandHandler("kontrol",kontrol))

# CALLBACK
app.add_handler(CallbackQueryHandler(cekilis_buton,"katil"))

# MESSAGE
app.add_handler(MessageHandler(filters.FORWARDED,forward_engel),group=0)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,kanal_etiket_engel),group=1)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,link_engel),group=2)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,site_kontrol),group=3)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,every_kontrol),group=4)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,dogum),group=5)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,mesaj_say),group=6)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,kufur_kontrol),group=7)
app.add_handler(MessageHandler(filters.Regex(r"^!sil \d+$"),sil),group=8)

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
