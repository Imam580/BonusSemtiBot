# bot.py
import os, time, random, re
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
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
kufur_sayaci = {}
spam_log = {}
spam_warn = {}

SPAM_SURE = 5
SPAM_LIMIT = 5

# ================= KANALLAR =================
ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@BahisKarhanesi",
]

# ================= KÜFÜR =================
KUFUR_LISTESI = [
    "amk","amq",
    "sik","sikerim","sikti","siktim","siktir","sikeyim",
    "yarak","yarrak","yarram","yarrağım",
    "am","amı","amına","amın","amcık","amcik",
    "göt","götü","götüne","götveren",
    "taşak","taşşak","taşşağım",
    "piç",
    "ibne",
    "orospu","orospuçocuğu","orospu çocuğu",
    "pezevenk",
    "puşt",
    "yavşak",
    "gavat",
    "bok","bokum",
    "sidik",
    "osur",
    "çük",
    "malafat",
    "pipi",
    "anan","ananı","anana",
    "bacını",
    "sülaleni",
    "tipini",
    "amına koyim","amına koyayım",
    "sikik",
    "yarramın",
    "amkafa",
    "götlek",
    "taşaklı",
    "amcığın",
    "siktiğimin",
    "sikiyim",
    "sikiyim seni",
    "amına sokayım",
    "götüne sokayım",
    "sikerler",
    "sikmişim",
    "yarrak kafalı",
    "amını",
    "götünü",
    "taşşağını"
]

# ================= SİTELER =================
SITE_LINKLERI = {
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

SITE_BUTON_LISTESI = [

    # --- urllink.me ---
    ("MEKANBAHIS","https://urllink.me/mekanbahis"),
    ("BETNOSA","https://urllink.me/betnosa"),
    ("BABILBET","https://urllink.me/babilbet"),
    ("CASIBOM","https://urllink.me/casibom"),
    ("LORDPALACE","https://urllink.me/lordpalace"),
    ("BETWINNER","https://urllink.me/betwinner"),
    ("WINWIN","https://urllink.me/winwin"),
    ("MELBET","https://urllink.me/melbet"),
    ("GRBETS","https://urllink.me/grbets"),
    ("BETINE","https://urllink.me/betine"),
    ("REDFOXBET","https://urllink.me/redfoxbet"),
    ("BAYSPIN","https://urllink.me/bayspin"),
    ("SOLOBET","https://urllink.me/solobet"),
    ("BETORSPIN","https://urllink.me/betorspin"),
    ("ANTIKBET","https://urllink.me/antikbet"),
    ("SUPERTOTOBET","https://urllink.me/supertotobet"),
    ("888STARZ","https://urllink.me/888starz"),
    ("1KING","https://urllink.me/1king"),
    ("MARIOBET","https://urllink.me/mariobet"),

    # --- shoort.im ---
    ("BETKOM","https://shoort.im/betkom"),
    ("DODOBET","https://shoort.im/dodo"),
    ("XBAHIS","https://shoort.im/xbahis"),
    ("MARIOBET","https://shoort.im/mariobonus"),
    ("TARAFBET","https://shoort.im/tarafbet"),
    ("BETJUVE","https://shoort.im/betjuve"),
    ("GRANDPASHA","https://shoort.im/grandpasha"),
    ("EGEBET","https://shoort.im/egebet"),
    ("GOLDENBAHIS","https://shoort.im/goldenbahis"),
    ("BETIGMA","https://shoort.im/betigma"),
    ("NEROBET","https://shoort.im/nerobet"),
    ("NGSBAHIS","https://shoort.im/ngsbahis"),
    ("GETTOBET","https://shoort.im/gettobet"),
    ("BETRUPI","https://shoort.im/betrupi"),
    ("KINGROYAL","https://shoort.im/kingroyal"),
    ("MADRIDBET","https://shoort.im/madridbet"),
    ("MERITKING","https://shoort.im/meritking"),
    ("HIZLICASINO","https://shoort.im/hizlicasino"),
    ("HEYBET","https://shoort.im/heybet"),
    ("BETTURKEY","https://shoort.im/betturkey"),
    ("GOLEGOL","https://shoort.im/golegol"),
    ("VENOMBET","https://shoort.im/venombet"),
    ("PALAZZO","https://shoort.im/palazzo"),
    ("FIXBET","https://shoort.im/fixbet"),
    ("MATADOR","https://shoort.im/matador"),
    ("ZBAHIS","https://shoort.im/zbahis"),
    ("MERSOBAHIS","https://shoort.im/merso"),
    ("AMGBAHIS","https://shoort.im/amg"),
    ("SALTBAHIS","https://shoort.im/saltbahis"),
    ("BETORBET","https://shoort.im/betorbet"),
    ("VIRABET","https://shoort.im/virabet"),
    ("BETLIKE","https://shoort.im/betlike"),
    ("BETTICKET","https://shoort.im/betticket"),
    ("BAHISLION","https://shoort.im/bahislion"),
    ("WINBIR","https://shoort.im/winbir"),
    ("BETPIR","https://shoort.im/betpir"),
    ("GAMABET","https://shoort.im/gamabet"),
    ("OTOBET","https://shoort.im/otobet"),
    ("BYCASINO","https://shoort.im/bycasino"),
    ("BAHISBUDUR","https://shoort.im/bahisbudur"),
    ("IKASBET","https://shoort.im/ikasbet"),
    ("PUSULABET","https://shoort.im/pusulabet"),
    ("STARZBET","https://shoort.im/starzbet"),
    ("RAMADABET","https://shoort.im/ramadabet"),
    ("PADISAHBET","https://shoort.im/padisahbet"),
    ("CASINRA","https://shoort.im/casinra"),
    ("BETROZ","https://shoort.im/betroz"),
    ("MAKROBET","https://shoort.im/makrobet"),
    ("BETRA","https://shoort.im/betra"),
    ("NETBAHIS","https://shoort.im/netbahis"),
    ("MAKSIBET","https://shoort.im/maksibet"),
    ("MERCURE","https://shoort.im/mercure"),
    ("RBET","https://shoort.im/rbet"),
    ("FAVORISLOT","https://shoort.im/favorislot"),
    ("PASACASINO","https://shoort.im/pasacasino"),
    ("ROMABET","https://shoort.im/romabet"),
    ("ROKETBET","https://shoort.im/roketbet"),
    ("BETGAR","https://shoort.im/betgar"),
    ("PRADEBET","https://shoort.im/pradabet"),
    ("FESTWIN","https://shoort.im/festwin"),
    ("YEDIBAHIS","https://shoort.im/yedibahis"),
    ("BEKABET","https://shoort.im/bekabet"),
    ("TITOBET","https://shoort.im/titobet"),
    ("BETCI","https://shoort.im/betci"),
    ("BETBOX","https://shoort.im/betbox"),
    ("ALFABAHIS","https://shoort.im/alfabahis"),
    ("HILTONBET","https://shoort.im/hiltonbet"),
    ("BAYWIN","https://shoort.im/baywinn"),
    ("BETORSPIN","https://shoort.im/betorspinn"),
    ("BETIST","https://shoort.im/betist"),
    ("MASTERBETTING","https://shoort.im/masterbetting"),
    ("BETPIPO","https://shoort.im/betpipo"),
    ("SAHABET","https://shoort.im/sahabet"),
    ("STAKE","https://shoort.im/stake"),
    ("ONWIN","https://shoort.im/onwin"),
    ("TIPOBET","https://shoort.im/tipobet"),
    ("LIGOBET","https://shoort.im/ligobet"),
    ("HILARIONBET","https://shoort.im/hilarionbet"),
    ("DENGEBET","https://shoort.im/dengebet"),
    ("BAHISCOM","https://shoort.im/bahisbonus"),
    ("BETOFFICE","https://shoort.im/betoffice"),
    ("GALABET","https://shoort.im/galabet"),
    ("ZENGINSIN","https://shoort.im/zenginsin"),
    ("CASINOWON","https://shoort.im/casinowon"),
    ("TLCASINO","https://shoort.im/tlcasino"),
    ("WBAHIS","https://shoort.im/wbahis"),
    ("BAHISCASINO","https://shoort.im/bahiscasino"),
    ("BETHAND","https://shoort.im/bethandd"),
    ("GORABET","https://shoort.im/gorabet"),
    ("NORABAHIS","https://shoort.im/norabahis"),
    ("XSLOT","https://shoort.im/xslot"),
    ("SPINCO","https://shoort.im/spinco"),
    ("SUPERBET","https://shoort.im/superbet"),
    ("BETSIN","https://shoort.im/betsin"),
    ("DEDEBET","https://shoort.im/dedebet"),
    ("MAXWIN","https://shoort.im/maxwin"),
    ("DAMABET","https://shoort.im/damabet"),
    ("PALACEBET","https://shoort.im/palacebet"),
    ("BETWOON","https://shoort.im/betwoon"),
    ("CRATOSBET","https://shoort.im/cratosbet"),
    ("BETWILD","https://shoort.im/betwild"),
    ("PASHAGAMING","https://shoort.im/pashagaming"),
    ("HIZLIBAHIS","https://shoort.im/hızlıbahis"),
    ("ROYALBET","https://shoort.im/royalbet"),
    ("RADISSONBET","https://shoort.im/radissonbet"),
    ("BETSALVADOR","https://shoort.im/betsalvador"),
    ("GOBAHIS","https://shoort.im/gobonus"),
]

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
    ("MEGABAHIS","https://dub.is/megaguncel"),
    ("ZIRVEBET","https://dub.is/zirveguncel"),
    ("ODEONBET","http://dub.is/odeonguncel"),
    ("MAVIBET","http://dub.is/maviguncel"),
    ("LINKELIT","https://linkelit.co/sosyaldavet"),
    ("COINBAR","http://shoort.in/coinbar"),
    ("NAKITBAHIS","https://shoort.in/nakitbahis"),
]

DOGUM_BONUS_SITELERI = [
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
    ("RADISSONBET", "https://shoort.im/radissonbet"),
    ("JOJOBET", "https://dub.pro/jojoyagit"),
    ("HOLIGANBET", "http://t.t2m.io/holiguncel"),
    ("KAVBET", "https://shoort.im/kavbet"),
    ("BETGİT", "https://shoort.im/betgit"),
    ("MADRIDBET", "https://shoort.im/madridbet"),
    ("ARTEMİSBET", "https://shoort.im/artemisbet"),
]

# ================= YARDIMCI =================
def mention(u):
    return f"<a href='tg://user?id={u.id}'>{u.first_name}</a>"

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except:
        return False

async def hedef_kullanici(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    return None

# ================= ENGELLER =================
async def forward_engel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.forward_from or update.message.forward_from_chat:
        await update.message.delete()

async def kanal_etiket_engel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context): return
    text = update.message.text or ""
    for m in re.findall(r'@([A-Za-z0-9_]{5,})', text):
        try:
            await context.bot.get_chat_member(f"@{m}", update.message.from_user.id)
            await update.message.delete()
            await update.effective_chat.send_message("🚫 Kanal/grup etiketlemek yasaktır.")
            return
        except:
            pass

async def kufur_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context): return
    t = (update.message.text or "").lower()
    uid = update.message.from_user.id
    for k in KUFUR_LISTESI:
        if k in t:
            await update.message.delete()
            kufur_sayaci[uid] = kufur_sayaci.get(uid,0)+1
            await context.bot.restrict_chat_member(
                update.effective_chat.id, uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time())+300
            )
            return

async def spam_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context): return
    uid = update.message.from_user.id
    now = time.time()
    spam_log.setdefault(uid, []).append(now)
    spam_log[uid] = [t for t in spam_log[uid] if now-t<=SPAM_SURE]
    if len(spam_log[uid])>=SPAM_LIMIT:
        await update.message.delete()
        if spam_warn.get(uid):
            await context.bot.restrict_chat_member(
                update.effective_chat.id, uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time())+3600
            )
            spam_log[uid]=[]
            spam_warn[uid]=False
        else:
            spam_warn[uid]=True

# ================= SİTE / EVERY / DOĞUM =================
async def site_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = (update.message.text or "").lower()
    for k,v in SITE_LINKLERI.items():
        if k in t:
            kb = [[InlineKeyboardButton("🔗 BUTONA TIKLAYARAK SİTEYE YÖNELEBİLİRSİNİZ", url=v)]]
            await update.message.reply_text(
                f"✅ <b>{k.upper()}</b>",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return

async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb=[]; row=[]
    for i,(a,b) in enumerate(SPONSOR_SITELER,1):
        row.append(InlineKeyboardButton(a,url=b))
        if i%2==0: kb.append(row); row=[]
    if row: kb.append(row)
    await update.message.reply_text(
        "⭐ <b>SPONSOR SİTELER</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def every_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "every" not in (update.message.text or "").lower(): return
    kb=[]
    r=[]
    for i,(a,b) in enumerate(EVERY_SPONSOR,1):
        r.append(InlineKeyboardButton(a,url=b))
        if i%2==0: kb.append(r); r=[]
    if r: kb.append(r)
    kb.append([InlineKeyboardButton("────────────", callback_data="x")])
    r=[]
    for i,(a,b) in enumerate(EVERY_DIGER,1):
        r.append(InlineKeyboardButton(a,url=b))
        if i%2==0: kb.append(r); r=[]
    if r: kb.append(r)
    await update.message.reply_text(
        "🔥 <b>EveryMatrix Siteleri</b>\n\n👇 Butonlara tıklayın",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def dogum_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "doğum" not in (update.message.text or "").lower(): return
    kb=[]; r=[]
    for i,(a,b) in enumerate(DOGUM_BONUS,1):
        r.append(InlineKeyboardButton(a,url=b))
        if i%2==0: kb.append(r); r=[]
    if r: kb.append(r)
    await update.message.reply_text(
        "🎁 <b>DOĞUM GÜNÜ BONUSLARI</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================= ADMIN KOMUTLARI =================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Bir mesajı yanıtla")
        return

    user = update.message.reply_to_message.from_user

    await context.bot.ban_chat_member(update.effective_chat.id, user.id)

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🔓 BANI KALDIR",
            callback_data=f"unban:{user.id}"
        )
    ]])

    await update.message.reply_text(
        f"🔨 {user.mention_html()} banlandı",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Unban için bir mesajı yanıtla")
        return

    user = update.message.reply_to_message.from_user

    await context.bot.unban_chat_member(
        update.effective_chat.id,
        user.id
    )

    await update.message.reply_text(
        f"✅ {user.mention_html()} banı kaldırıldı",
        parse_mode="HTML"
    )

    await query.edit_message_text("✅ Ban kaldırıldı")


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🔓 MUTEYİ KALDIR",
            callback_data=f"unmute:{user.id}"
        )
    ]])

    await update.message.reply_text(
        f"🔇 {user.mention_html()} susturuldu",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Unmute için bir mesajı yanıtla")
        return

    user = update.message.reply_to_message.from_user

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    await update.message.reply_text(
        f"🔊 {user.mention_html()} artık konuşabilir",
        parse_mode="HTML"
    )

async def unmute_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # sadece admin basabilsin
    try:
        member = await context.bot.get_chat_member(
            query.message.chat.id,
            query.from_user.id
        )
        if member.status not in ["administrator", "creator"]:
            await query.answer("❌ Yetkin yok", show_alert=True)
            return
    except:
        return

    # callback_data: unmute:USERID
    data = query.data.split(":")
    if len(data) != 2:
        return

    user_id = int(data[1])

    await context.bot.restrict_chat_member(
        query.message.chat.id,
        user_id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    await query.edit_message_text("🔊 Mute kaldırıldı")



async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    await context.bot.set_chat_permissions(update.effective_chat.id, ChatPermissions())
    await update.message.reply_text("🔒 Grup kilitlendi")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    await context.bot.set_chat_permissions(
        update.effective_chat.id,
        ChatPermissions(can_send_messages=True, can_send_media_messages=True)
    )
    await update.message.reply_text("🔓 Grup açıldı")

async def sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    try: n=int(update.message.text.split()[1])
    except: return
    for i in range(n):
        try:
            await context.bot.delete_message(update.effective_chat.id, update.message.message_id-i)
        except: pass

async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: /filter site link")
        return

    site = context.args[0].lower()
    link = context.args[1]

    SITE_LINKLERI[site] = link
    await update.message.reply_text(f"✅ {site} eklendi")


async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not context.args:
        await update.message.reply_text("Kullanım: /remove site")
        return

    site = context.args[0].lower()

    if site in SITE_LINKLERI:
        del SITE_LINKLERI[site]
        await update.message.reply_text(f"🗑️ {site} silindi")
    else:
        await update.message.reply_text("❌ Site bulunamadı")


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

async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_mesaj_id
    cekilis_aktif=True
    cekilis_katilimcilar.clear()
    msg = await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("cekilis.jpg","rb"),
        caption=cekilis_text(),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]]
        ),
        parse_mode="HTML"
    )
    cekilis_mesaj_id = msg.message_id

async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    cekilis_katilimcilar.add(q.from_user.id)
    await q.edit_message_caption(
        caption=cekilis_text(),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="katil")]]
        ),
        parse_mode="HTML"
    )

async def sayi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_kazanan_sayisi
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Kullanım: /sayi 3")
        return
    cekilis_kazanan_sayisi=int(context.args[0])
    await update.message.reply_text(f"🎯 Kazanan sayısı: {cekilis_kazanan_sayisi}")

async def mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global min_mesaj_sayisi
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Kullanım: /mesaj 20")
        return
    min_mesaj_sayisi=int(context.args[0])
    await update.message.reply_text(f"📝 Mesaj şartı: {min_mesaj_sayisi}")

async def bitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_kazananlar
    cekilis_aktif=False
    cekilis_kazananlar=random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi,len(cekilis_katilimcilar))
    )
    msg="🏆 <b>ÇEKİLİŞ SONUCU</b>\n\n"
    for uid in cekilis_kazananlar:
        m=await context.bot.get_chat_member(update.effective_chat.id, uid)
        msg+=f"🎁 {mention(m.user)}\n"
    await update.message.reply_text(msg, parse_mode="HTML")

async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg="📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"
    for uid in cekilis_kazananlar:
        m=await context.bot.get_chat_member(update.effective_chat.id, uid)
        ms=mesaj_sayaci.get(uid,0)
        eksik=[]
        for k in ZORUNLU_KANALLAR:
            try:
                u=await context.bot.get_chat_member(k, uid)
                if u.status not in ("member","administrator","creator"):
                    eksik.append(k)
            except:
                eksik.append(k)
        msg+=f"❌ {mention(m.user)}\n"
        msg+=f"   📨 Mesaj durumu: {ms}/{min_mesaj_sayisi}\n"
        if eksik:
            msg+="   📢 Eksik kanallar:\n"
            for e in eksik: msg+=f"      • {e}\n"
        else:
            msg+="   📢 Kanal durumu: Tümü tamam\n"
        msg+="\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# ================= MESAJ SAYACI =================
async def mesaj_say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.date.timestamp()<BOT_START: return
    uid=update.message.from_user.id
    mesaj_sayaci[uid]=mesaj_sayaci.get(uid,0)+1

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

# 🔥 EKLENENLER
app.add_handler(CommandHandler("filter", add_filter))
app.add_handler(CommandHandler("remove", remove_filter))

# CALLBACK
app.add_handler(CallbackQueryHandler(cekilis_buton, pattern="^katil$"))
app.add_handler(CallbackQueryHandler(unmute_button, pattern="^unmute:"))
app.add_handler(CallbackQueryHandler(unban_button, pattern="^unban:"))

# MESSAGE (SIRA ÖNEMLİ)
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

