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
BOT_START = time.time()
cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazananlar = []
cekilis_kazanan_sayisi = 1
min_mesaj = 0
mesaj_sayaci = {}

# ================= KANALLAR =================
ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@BahisKarhanesi",
]

# ================= KÜFÜR =================
KUFUR = ["amk","aq","orospu","sik","anan","amına"]
kufur_sayac = {}

# ================= SİTELER =================
SITE_LINKLERI = {
    "zbahis":"https://shoort.im/zbahis",
    "padisahbet":"https://shoort.im/padisahbet",
    "fixbet":"https://shoort.im/fixbet",
    "betoffice":"https://shoort.im/betoffice",
}

SPONSOR_EVERY = [
    ("HIZLICASINO","https://shoort.im/hizlicasino"),
    ("EGEBET","https://shoort.im/egebet"),
    ("KAVBET","https://shoort.im/kavbet"),
]

DIGER_EVERY = [
    ("JOJOBET","http://dub.pro/jojoyagit"),
    ("HOLIGANBET","https://dub.pro/holiguncel"),
]

DOGUM_SITELER = [
    ("ZBAHİS","https://shoort.im/zbahis"),
    ("PADİŞAHBET","https://shoort.im/padisahbet"),
    ("FİXBET","https://shoort.im/fixbet"),
]

# ================= YARDIMCI =================
def mention(u):
    return f"<a href='tg://user?id={u.id}'>{u.first_name}</a>"

async def is_admin(update, context):
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def hedef_bul(update, context):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    if context.args:
        return await context.bot.get_chat_member(
            update.effective_chat.id,
            context.args[0].replace("@","")
        )
    return None

# ================= FORWARD ENGEL =================
async def forward_engel(update, context):
    if update.message and (update.message.forward_from or update.message.forward_from_chat):
        await update.message.delete()

# ================= KÜFÜR =================
async def kufur_kontrol(update, context):
    if await is_admin(update, context): return
    t = update.message.text.lower()
    uid = update.message.from_user.id
    for k in KUFUR:
        if k in t:
            await update.message.delete()
            kufur_sayac[uid] = kufur_sayac.get(uid,0)+1
            await context.bot.restrict_chat_member(
                update.effective_chat.id, uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time())+300
            )
            return

# ================= EVERY =================
async def every_kontrol(update, context):
    if "every" not in update.message.text.lower(): return

    kb=[]
    kb.append([InlineKeyboardButton("⭐ SPONSOR SİTELER",callback_data="x")])
    for a,b in SPONSOR_EVERY:
        kb.append([InlineKeyboardButton(a,url=b)])

    kb.append([InlineKeyboardButton("— DİĞER SİTELER —",callback_data="x")])
    for a,b in DIGER_EVERY:
        kb.append([InlineKeyboardButton(a,url=b)])

    await update.message.reply_text(
        "🔥 <b>EVERYMATRIX SİTELER</b>\n👇 Butona tıklayarak siteye gidebilirsiniz",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= DOĞUM =================
async def dogum_kontrol(update, context):
    if "doğum" not in update.message.text.lower(): return
    kb=[[InlineKeyboardButton(a,url=b)] for a,b in DOGUM_SITELER]
    await update.message.reply_text(
        "🎁 <b>DOĞUM GÜNÜ BONUSLARI</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= SİTE TETİK =================
async def site_kontrol(update, context):
    t = update.message.text.lower()
    for k,v in SITE_LINKLERI.items():
        if k in t:
            kb=[[InlineKeyboardButton("🔗 BUTONA TIKLAYARAK GİR",url=v)]]
            await update.message.reply_text(
                f"✅ <b>{k.upper()}</b>",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return

# ================= FILTER =================
async def filter_add(update, context):
    if not await is_admin(update, context): return
    SITE_LINKLERI[context.args[0].lower()] = context.args[1]
    await update.message.reply_text("✅ Eklendi")

async def filter_remove(update, context):
    if not await is_admin(update, context): return
    SITE_LINKLERI.pop(context.args[0].lower(),None)
    await update.message.reply_text("❌ Silindi")

async def filter_show(update, context):
    await update.message.reply_text("\n".join(SITE_LINKLERI.keys()))

# ================= ÇEKİLİŞ =================
async def cekilis(update, context):
    global cekilis_aktif
    cekilis_aktif=True
    cekilis_katilimcilar.clear()
    kb=[[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL",callback_data="katil")]]
    await context.bot.send_photo(
        update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=(
            "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
            "🔥 <b>KATILIMCI SAYISI :</b> 0\n\n"
            "🏆 Kanalları takip etmek zorunludur!"
        ),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def cekilis_buton(update, context):
    q=update.callback_query
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🔥 <b>KATILIMCI SAYISI :</b> {len(cekilis_katilimcilar)}",
        parse_mode="HTML"
    )

# ================= KONTROL =================
async def kontrol(update, context):
    msg="📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"
    for uid in cekilis_kazananlar:
        m=await context.bot.get_chat_member(update.effective_chat.id,uid)
        msg+=f"❌ {mention(m.user)}\n"
        msg+=f"   📨 Mesaj: {mesaj_sayaci.get(uid,0)}/{min_mesaj}\n"
    await update.message.reply_text(msg,parse_mode="HTML")

# ================= BOT =================
app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.FORWARDED,forward_engel),group=0)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,kufur_kontrol),group=1)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,every_kontrol),group=2)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,dogum_kontrol),group=3)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,site_kontrol),group=4)

app.add_handler(CommandHandler("filter",filter_add))
app.add_handler(CommandHandler("remove",filter_remove))
app.add_handler(CommandHandler("filtre",filter_show))
app.add_handler(CommandHandler("cekilis",cekilis))
app.add_handler(CallbackQueryHandler(cekilis_buton,"katil"))
app.add_handler(CommandHandler("kontrol",kontrol))

print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
