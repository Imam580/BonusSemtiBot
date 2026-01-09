# bot.py
import os, time, random, re
from dotenv import load_dotenv
from telegram import *
from telegram.ext import *
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
kufur_sayaci = {}

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
    "amk","oç","amq","orospu","orospu çocuğu",
    "piç","ibne","yarrak","yarak",
    "sik","siktir","amcık","anan","amına"
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

EVERY_DIGER = [
    ("HIZLICASINO","https://shoort.im/hizlicasino"),
    ("EGEBET","https://shoort.im/egebet"),
]

DOGUM_SITELER = SPONSOR_SITELER

# ================= ADMIN =================
async def is_admin(update, context):
    m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

def mention(u):
    return f"<a href='tg://user?id={u.id}'>{u.full_name}</a>"

def hedef_kullanici(update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    return None

# ================= ENGELLER =================
async def forward_engel(update, context):
    if update.message.forward_from or update.message.forward_from_chat:
        await update.message.delete()

async def kanal_etiket_engel(update, context):
    if await is_admin(update, context): return
    text = update.message.text or ""
    for m in re.findall(r'@([A-Za-z0-9_]{5,})', text):
        try:
            await context.bot.get_chat_member(f"@{m}", update.message.from_user.id)
            await update.message.delete()
            return
        except:
            pass

# ================= MESAJ SAY =================
async def mesaj_say(update, context):
    if update.message.date.timestamp() < BOT_START:
        return
    uid = update.message.from_user.id
    mesaj_sayaci[uid] = mesaj_sayaci.get(uid,0) + 1

# ================= KÜFÜR =================
async def kufur_kontrol(update, context):
    if await is_admin(update, context): return
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

# ================= SİTE / EVERY / DOĞUM =================
async def site_kontrol(update, context):
    t = update.message.text.lower()

    if "every" in t:
        kb = []
        for a,b in SPONSOR_SITELER:
            kb.append([InlineKeyboardButton(a,url=b)])
        for a,b in EVERY_DIGER:
            kb.append([InlineKeyboardButton(a,url=b)])
        await update.message.reply_text(
            "🔥 <b>EVERYMATRIX SİTELER</b>",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )
        return

    if "doğum" in t:
        kb = [[InlineKeyboardButton(a,url=b)] for a,b in DOGUM_SITELER]
        await update.message.reply_text(
            "🎁 <b>DOĞUM GÜNÜ BONUSLARI</b>",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )
        return

    for k,v in SITE_LINKLERI.items():
        if k in t:
            kb=[[InlineKeyboardButton("🔗 BUTONA TIKLAYARAK SİTEYE GİR",url=v)]]
            await update.message.reply_text(
                f"✅ <b>{k.upper()}</b>",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return

# ================= SPONSOR =================
async def sponsor(update, context):
    kb = [[InlineKeyboardButton(a,url=b)] for a,b in SPONSOR_SITELER]
    await update.message.reply_text(
        "⭐ <b>SPONSOR SİTELER</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= BAN / MUTE =================
async def ban(update, context):
    if not await is_admin(update, context): return
    user = hedef_kullanici(update)
    if not user:
        await update.message.reply_text("❌ Bir mesajı yanıtla")
        return
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"🔨 {mention(user)} banlandı", parse_mode="HTML")

async def unban(update, context):
    if not await is_admin(update, context): return
    if not context.args: return
    await context.bot.unban_chat_member(update.effective_chat.id, int(context.args[0]))

async def mute(update, context):
    if not await is_admin(update, context): return
    user = hedef_kullanici(update)
    if not user:
        await update.message.reply_text("❌ Bir mesajı yanıtla")
        return
    kb=[[InlineKeyboardButton("🔊 MUTEDEN ÇIKAR",callback_data=f"unmute:{user.id}")]]
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text(
        f"🔇 {mention(user)} susturuldu",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def unmute(update, context):
    if not await is_admin(update, context): return
    user = hedef_kullanici(update)
    if not user: return
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=True)
    )

async def unmute_button(update, context):
    q = update.callback_query
    uid = int(q.data.split(":")[1])
    await context.bot.restrict_chat_member(
        q.message.chat.id,
        uid,
        ChatPermissions(can_send_messages=True)
    )
    await q.answer("Mute kaldırıldı")

# ================= !SİL =================
async def sil(update, context):
    if not await is_admin(update, context): return
    try:
        n=int(update.message.text.split()[1])
    except:
        return
    for i in range(n):
        try:
            await context.bot.delete_message(update.effective_chat.id, update.message.message_id-i)
        except:
            pass

# ================= ÇEKİLİŞ =================
def cekilis_text():
    return (
        "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
        f"🔥 <b>KATILIMCI SAYISI :</b> {len(cekilis_katilimcilar)}\n\n"
        "🏆 Katılımcıların kanallarımızı takip etmesi zorunludur!\n\n"
        "🔥 https://t.me/Canli_Izleme_Mac_Linkleri\n"
        "🔥 https://t.me/plasespor\n"
        "🔥 https://t.me/bonussemti\n"
        "🔥 https://t.me/bonussemtietkinlik\n"
        "🔥 https://t.me/BahisKarhanesi"
    )

async def cekilis(update, context):
    global cekilis_aktif, cekilis_mesaj_id
    cekilis_aktif=True
    cekilis_katilimcilar.clear()
    kb=[[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL",callback_data="katil")]]
    msg=await context.bot.send_message(
        update.effective_chat.id,
        cekilis_text(),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )
    cekilis_mesaj_id=msg.message_id

async def cekilis_buton(update, context):
    q=update.callback_query
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_text(
        cekilis_text(),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL",callback_data="katil")]]),
        parse_mode="HTML"
    )

# ================= SAYI / MESAJ / BİTİR / KONTROL =================
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
        ms=mesaj_sayaci.get(uid,0)
        eksik=[]
        for k in ZORUNLU_KANALLAR:
            try:
                u=await context.bot.get_chat_member(k,uid)
                if u.status not in ["member","administrator","creator"]:
                    eksik.append(k)
            except:
                eksik.append(k)
        msg+=(
            f"❌ {mention(m.user)}\n"
            f"   📨 Mesaj durumu: {ms}/{min_mesaj_sayisi}\n"
        )
        if eksik:
            msg+="   📢 Eksik kanallar:\n"
            for e in eksik:
                msg+=f"      • {e}\n"
        else:
            msg+="   📢 Tüm kanallara katılmış\n"
        msg+="\n"
    await update.message.reply_text(msg,parse_mode="HTML")

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
