import os
import time
import random
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
    filters as tg_filters
)

# ================= ENV =================
load_dotenv()
TOKEN = os.environ.get("TOKEN")

# ================= GLOBAL =================
cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1
cekilis_kazananlar = []

BOT_BASLANGIC_ZAMANI = time.time()
kullanici_mesaj_sayisi = {}
min_mesaj_sayisi = 0
EVERY_SPONSOR = [
    ("HIZLICASINO", "https://shoort.im/hizlicasino"),
    ("EGEBET", "https://shoort.im/egebet"),
    ("KAVBET", "https://shoort.im/kavbet"),
    ("PUSULABET", "https://shoort.im/pusulabet"),
    ("HITBET", "https://shoort.im/hitbet"),
    ("ARTEMISBET", "https://shoort.im/artemisbet"),
]

EVERY_DIGER = [
    ("SOSYAL DAVET", "https://linkturbo.co/sosyaldavet"),
    ("MATGUNCEL", "http://dub.is/matguncel"),
    ("JOJOBET", "http://dub.pro/jojoyagit"),
    ("HOLIGANBET", "https://dub.pro/holiguncel"),
    ("BETSMOVE", "http://dub.is/betsmoveguncel"),
    ("LUNASOSYAL", "http://lunalink.org/lunasosyal/"),
    ("MEGABAHIS", "https://dub.is/megaguncel"),
    ("ZIRVEBET", "https://dub.is/zirveguncel"),
    ("ODEONBET", "http://dub.is/odeonguncel"),
    ("MAVIBET", "http://dub.is/maviguncel"),
    ("LINKELIT", "https://linkelit.co/sosyaldavet"),
    ("COINBAR", "http://shoort.in/coinbar"),
    ("NAKITBAHIS", "https://shoort.in/nakitbahis"),
]


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

# ================= DOĞUM BONUS =================
DOGUM_BONUS_BUTONLARI = [
    ("ZBAHİS", "https://shoort.im/zbahis"),
    ("PADİŞAHBET", "https://shoort.im/padisahbet"),
    ("FİXBET", "https://shoort.im/fixbet"),
    ("BETMATİK", "https://shoort.im/betmatik"),
    ("BAYSPİN", "http://shoort.im/bayspinn"),
    ("BETOFFİCE", "https://shoort.im/betoffice"),
    ("BETİNE", "https://shoort.im/betinee"),
    ("XSLOT", "https://shoort.im/xslot"),
    ("STARZBET", "https://shoort.im/starzbet"),
    ("BETPİPO", "https://shoort.im/betpipo"),
    ("NORABAHİS", "https://shoort.im/norabahis"),
    ("SPİNCO", "https://shoort.im/spinco"),
    ("HERMESBET", "https://hermesbet.wiki/telegram"),
    ("CRATOSBET", "https://shoort.im/cratosbet"),
    ("BETKOM", "http://shoort.im/betkom"),
    ("MASTERBET", "https://shoort.im/masterbetting"),
    ("MARİOBET", "http://shoort.im/mariobonus"),
    ("BETWİLD", "http://shoort.im/betwild"),
    ("PASHAGAMING", "https://shoort.im/pashagaming"),
    ("ROYALBET", "https://shoort.im/royalbet"),
    ("RADİSSONBET", "https://shoort.im/radissonbet"),
    ("JOJOBET", "https://dub.pro/jojoyagit"),
    ("HOLIGANBET", "http://t.t2m.io/holiguncel"),
    ("KAVBET", "https://shoort.im/kavbet"),
    ("BETGİT", "https://shoort.im/betgit"),
    ("MADRIDBET", "https://shoort.im/madridbet"),
    ("ARTEMİSBET", "https://shoort.im/artemisbet"),
]

# ================= KÜFÜR / SPAM =================
KUFUR_LISTESI = [
    "amk","amq","orospu","orospu çocuğu","piç","ibne",
    "yarrak","yarak","sik","siktir","amcık","anan","amına"
]

kufur_sayaci = {}
spam_log = {}
spam_warn = {}

SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= SİTE LİNKLERİ =================
filters_dict = {
    # --- urllink.me ---
    "mekanbahis": "urllink.me/mekanbahis",
    "betnosa": "urllink.me/betnosa",
    "babilbet": "urllink.me/babilbet",
    "casibom": "urllink.me/casibom",
    "lordpalace": "urllink.me/lordpalace",
    "betwinner": "urllink.me/betwinner",
    "winwin": "urllink.me/winwin",
    "melbet": "urllink.me/melbet",
    "grbets": "urllink.me/grbets",
    "betine": "urllink.me/betine",
    "redfoxbet": "urllink.me/redfoxbet",
    "bayspin": "urllink.me/bayspin",
    "solobet": "urllink.me/solobet",
    "betorspin": "urllink.me/betorspin",
    "antikbet": "urllink.me/antikbet",
    "supertotobet": "urllink.me/supertotobet",
    "888starz": "urllink.me/888starz",
    "1king": "urllink.me/1king",
    "mariobet": "urllink.me/mariobet",


    # --- shoort.im ---
    "betkom": "shoort.im/betkom",
    "dodobet": "shoort.im/dodo",
    "xbahis": "shoort.im/xbahis",
    "mariobet": "shoort.im/mariobonus",
    "tarafbet": "shoort.im/tarafbet",
    "betjuve": "shoort.im/betjuve",
    "grandpasha": "shoort.im/grandpasha",
    "egebet": "shoort.im/egebet",
    "goldenbahis": "shoort.im/goldenbahis",
    "betigma": "shoort.im/betigma",
    "nerobet": "shoort.im/nerobet",
    "1king": "shoort.im/1king",
    "ngsbahis": "shoort.im/ngsbahis",
    "gettobet": "shoort.im/gettobet",
    "betrupi": "shoort.im/betrupi",
    "kingroyal": "shoort.im/kingroyal",
    "madridbet": "shoort.im/madridbet",
    "meritking": "shoort.im/meritking",
    "hızlıcasino": "shoort.im/hizlicasino",
    "heybet": "shoort.im/heybet",
    "betturkey": "shoort.im/betturkey",
    "golegol": "shoort.im/golegol",
    "venombet": "shoort.im/venombet",
    "palazzo": "shoort.im/palazzo",
    "fixbet": "shoort.im/fixbet",
    "matador": "shoort.im/matador",
    "zbahis": "shoort.im/zbahis",
    "mersobahis": "shoort.im/merso",
    "amgbahis": "shoort.im/amg",
    "saltbahis": "shoort.im/saltbahis",
    "betorbet": "shoort.im/betorbet",
    "virabet": "shoort.im/virabet",
    "betlike": "shoort.im/betlike",
    "betticket": "shoort.im/betticket",
    "bahislion": "shoort.im/bahislion",
    "winbir": "shoort.im/winbir",
    "betpir": "shoort.im/betpir",
    "gamabet": "shoort.im/gamabet",
    "otobet": "shoort.im/otobet",
    "bycasino": "shoort.im/bycasino",
    "bayspin": "shoort.im/bayspinn",
    "bahisbudur": "shoort.im/bahisbudur",
    "ikasbet": "shoort.im/ikasbet",
    "pusulabet": "shoort.im/pusulabet",
    "starzbet": "shoort.im/starzbet",
    "ramadabet": "shoort.im/ramadabet",
    "padisahbet": "shoort.im/padisahbet",
    "casinra": "shoort.im/casinra",
    "betroz": "shoort.im/betroz",
    "makrobet": "shoort.im/makrobet",
    "betra": "shoort.im/betra",
    "netbahis": "shoort.im/netbahis",
    "maksibet": "shoort.im/maksibet",
    "mercure": "shoort.im/mercure",
    "rbet": "shoort.im/rbet",
    "favorislot": "shoort.im/favorislot",
    "pasacasino": "shoort.im/pasacasino",
    "romabet": "shoort.im/romabet",
    "roketbet": "shoort.im/roketbet",
    "betgar": "shoort.im/betgar",
    "pradabet": "shoort.im/pradabet",
    "festwin": "shoort.im/festwin",
    "yedibahis": "shoort.im/yedibahis",
    "bekabet": "shoort.im/bekabet",
    "titobet": "shoort.im/titobet",
    "betci": "shoort.im/betci",
    "betbox": "shoort.im/betbox",
    "alfabahis": "shoort.im/alfabahis",
    "hiltonbet": "shoort.im/hiltonbet",
    "baywin": "shoort.im/baywinn",
    "betorspin": "shoort.im/betorspinn",
    "betine": "shoort.im/betinee",
    "betist": "shoort.im/betist",
    "masterbetting": "shoort.im/masterbetting",
    "betpipo": "shoort.im/betpipo",
    "sahabet": "shoort.im/sahabet",
    "stake": "shoort.im/stake",
    "onwin": "shoort.im/onwin",
    "tipobet": "shoort.im/tipobet",
    "solobet": "shoort.im/solo",
    "supertotobet": "shoort.im/supertotobet",
    "ligobet": "shoort.im/ligobet",
    "hilarionbet": "shoort.im/hilarionbet",
    "dengebet": "shoort.im/dengebet",
    "bahiscom": "shoort.im/bahisbonus",
    "hitbet": "shoort.im/hitbet",
    "betoffice": "shoort.im/betoffice",
    "galabet": "shoort.im/galabet",
    "zenginsin": "shoort.im/zenginsin",
    "casinowon": "shoort.im/casinowon",
    "tlcasino": "shoort.im/tlcasino",
    "wbahis": "shoort.im/wbahis",
    "bahiscasino": "shoort.im/bahiscasino",
    "bethand": "shoort.im/bethandd",
    "grbets": "shoort.im/grbets",
    "gorabet": "shoort.im/gorabet",
    "norabahis": "shoort.im/norabahis",
    "xslot": "shoort.im/xslot",
    "spinco": "shoort.im/spinco",
    "superbet": "shoort.im/superbet",
    "betsin": "shoort.im/betsin",
    "dedebet": "shoort.im/dedebet",
    "maxwin": "shoort.im/maxwin",
    "damabet": "shoort.im/damabet",
    "palacebet": "shoort.im/palacebet",
    "betwoon": "shoort.im/betwoon",
    "cratosbet": "shoort.im/cratosbet",
    "betwild": "shoort.im/betwild",
    "pashagaming": "shoort.im/pashagaming",
    "hızlıbahis": "shoort.im/hızlıbahis",
    "royalbet": "shoort.im/royalbet",
    "radissonbet": "shoort.im/radissonbet",
    "betsalvador": "shoort.im/betsalvador",
    "gobahis": "shoort.im/gobonus",
}

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

# ================= SPONSOR KOMUTLARI =================

# /filter → sponsor ekle
async def sponsor_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece admin kullanabilir")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: /filter siteadi link")
        return

    site = context.args[0].lower()
    link = context.args[1]

    filters_dict[site] = link
    await update.message.reply_text(f"✅ Sponsor eklendi: {site.upper()}")


# /remove → sponsor sil
async def sponsor_sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece admin kullanabilir")
        return

    if not context.args:
        await update.message.reply_text("Kullanım: /remove siteadi")
        return

    site = context.args[0].lower()

    if site in filters_dict:
        del filters_dict[site]
        await update.message.reply_text(f"🗑 Sponsor silindi: {site.upper()}")
    else:
        await update.message.reply_text("❌ Böyle bir sponsor yok")


# /sponsor → tüm sponsorları butonlu at
async def sponsor_liste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece admin kullanabilir")
        return

    if not filters_dict:
        await update.message.reply_text("❌ Sponsor site yok")
        return

    keyboard = []
    row = []

    for i, (site, link) in enumerate(filters_dict.items(), start=1):
        row.append(
            InlineKeyboardButton(
                site.upper(),
                url=link if link.startswith("http") else f"https://{link}"
            )
        )
        if i % 2 == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await update.message.reply_text(
        "⭐ <b>SPONSOR SİTELER</b>\n\n"
        "👇 <i>Butona tıklayarak siteye yönelebilirsiniz</i>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


# ================= KÜFÜR =================
async def kufur_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return

    text = update.message.text.lower()
    uid = update.message.from_user.id

    for k in KUFUR_LISTESI:
        if k in text:
            await update.message.delete()
            kufur_sayaci[uid] = kufur_sayaci.get(uid, 0) + 1
            sure = 300 if kufur_sayaci[uid] == 1 else 3600
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time()) + sure
            )
            return

# ================= LİNK =================
async def link_engel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return

    if any(x in update.message.text.lower() for x in ["http","t.me","www"]):
        await update.message.delete()
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.from_user.id,
            ChatPermissions(can_send_messages=False),
            until_date=int(time.time()) + 3600
        )

# ================= SPAM =================
async def spam_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update, context):
        return

    uid = update.message.from_user.id
    now = time.time()
    spam_log.setdefault(uid, []).append(now)
    spam_log[uid] = [t for t in spam_log[uid] if now - t <= SPAM_SURE]

    if len(spam_log[uid]) >= SPAM_LIMIT:
        await update.message.delete()
        if spam_warn.get(uid):
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time()) + 3600
            )
            spam_log[uid] = []
            spam_warn[uid] = False
        else:
            spam_warn[uid] = True

# ================= SİTE =================
async def site_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for k, v in filters_dict.items():
        if k in text:
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    f"🔗 {k.upper()}",
                    url=v
                )]]
            )

            await update.message.reply_text(
                f"✅ <b>{k.upper()}</b>\n\n"
                "👇 <b>Butona tıklayarak siteye yönelebilirsiniz.</b>",
                reply_markup=kb,
                parse_mode="HTML"
            )
            return
# ================= EVERY =================
async def every_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if "every" not in update.message.text.lower():
        return

    keyboard = []

    # --- Sponsor Butonları ---
    sponsor_row = []
    for i, (isim, link) in enumerate(EVERY_SPONSOR, start=1):
        sponsor_row.append(InlineKeyboardButton(isim, url=link))
        if i % 2 == 0:
            keyboard.append(sponsor_row)
            sponsor_row = []
    if sponsor_row:
        keyboard.append(sponsor_row)

    # Ayraç satırı (boşluk hissi verir)
    keyboard.append([InlineKeyboardButton("────────────", callback_data="bos")])

    # --- Diğer Siteler ---
    diger_row = []
    for i, (isim, link) in enumerate(EVERY_DIGER, start=1):
        diger_row.append(InlineKeyboardButton(isim, url=link))
        if i % 2 == 0:
            keyboard.append(diger_row)
            diger_row = []
    if diger_row:
        keyboard.append(diger_row)

    await update.message.reply_text(
        "🔥 **BonusSemti Güvencesiyle EveryMatrix Altyapılı Siteler**\n\n"
        "⭐ **Sponsorumuz Olan Siteler**\n\n"
        "👇 **Butona tıklayarak siteye yönelebilirsiniz.**\n\n"
        "🔹 *Aşağıda diğer EveryMatrix siteleri de yer almaktadır.*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ================= DOĞUM =================
async def dogum_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "doğum" not in update.message.text.lower():
        return

    kb, row = [], []
    for i,(n,l) in enumerate(DOGUM_BONUS_BUTONLARI,1):
        row.append(InlineKeyboardButton(n, url=l))
        if i % 2 == 0:
            kb.append(row); row=[]
    if row: kb.append(row)

    await update.message.reply_text(
        "🎁 DOĞUM GÜNÜ BONUSLARI",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= !SİL =================
async def sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ================= LOCK / UNLOCK =================
async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(update.effective_chat.id, ChatPermissions())
        await update.message.reply_text("🔒 Grup kilitlendi")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text("🔓 Grup açıldı")

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
            update.effective_chat.id,
            int(context.args[0])
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

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]
    ])

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("cekilis.jpg", "rb"),
        caption="🎉 ÇEKİLİŞ BAŞLADI!",
        reply_markup=kb
    )

async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        f"🎉 Katılımcı: {len(cekilis_katilimcilar)}"
    )

# ================= BOT =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CallbackQueryHandler(cekilis_buton))

app.add_handler(MessageHandler(tg_filters.Regex(r"^!sil \d+$"), sil))

app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, kufur_kontrol), group=0)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, link_engel), group=1)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, spam_kontrol), group=2)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, every_kontrol), group=3)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, dogum_kontrol), group=4)
app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, site_kontrol), group=5)
app = ApplicationBuilder().token(TOKEN).build()
# ================= SPONSOR HANDLER =================
app.add_handler(CommandHandler("filter", sponsor_ekle))
app.add_handler(CommandHandler("remove", sponsor_sil))
app.add_handler(CommandHandler("sponsor", sponsor_liste))


print("🔥 BONUSSEMTİ BOT AKTİF")
app.run_polling()
