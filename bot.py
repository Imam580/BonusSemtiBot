# bot.py
from openai import OpenAI
import os
import re
import requests
import time
import base64
from collections import defaultdict

MESSAGE_COUNT = defaultdict(int)


from datetime import datetime, timedelta
from dotenv import load_dotenv
from zoneinfo import ZoneInfo


TR_TZ = ZoneInfo("Europe/Istanbul")

def get_today():
    return datetime.now(TR_TZ)

def get_utc_date(days=0):
    return (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")










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
    filters
)

from database import get_db

# ================= CACHE =================
SPONSOR_CACHE = {}


def db_get_all_sponsors():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT trigger, response FROM filters")
    rows = cur.fetchall()
    cur.close()
    db.close()

    sponsors = {}
    for row in rows:
        sponsors[row["trigger"]] = row["response"]

    return sponsors




def db_add_sponsor(site, link):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO filters (trigger, response)
        VALUES (%s, %s)
        ON CONFLICT (trigger)
        DO UPDATE SET response = EXCLUDED.response
        """,
        (site.lower(), link)
    )
    db.commit()
    cur.close()
    db.close()


def db_remove_sponsor(site):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM filters WHERE trigger = %s",
        (site.lower(),)
    )
    db.commit()
    cur.close()
    db.close()

  






# ================= ENV =================
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN missing")

ai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
AI_SYSTEM_PROMPT = """
Sen Bonussemti adlı bir Telegram asistanısın.
Bu bot @Tostcu tarafından geliştirilmiştir.

GENEL DAVRANIŞ:
- Normal sorularda genel bir yapay zeka gibi cevap ver
- Sohbet edebilir, açıklama yapabilirsin
- Kupon İSTENMEDEN asla kupon yazma

BAHİS / KUPON MODU:
- Kullanıcı açıkça kupon isterse kupon hazırla
- 2–4 maçlı kupon oluştur
- SADECE sana verilen (API’den gelen) gerçek maçları kullan
- Uydurma maç, Takım A–B, X–Y ASLA yazma

HER MAÇ İÇİN ZORUNLU:
- Maç adı
- Market (MS, KG Var, Üst/Alt vb.)
- Tahmini oran

KUPOUN SONUNDA ZORUNLU:
- Toplam oran
- Risk seviyesi: Düşük / Orta / Yüksek
- Kısa 1 cümlelik genel yorum

KURALLAR:
- “kesin”, “garanti”, “banko” kelimelerini ASLA kullanma
- Emin olmadığın konuda uydurma bilgi verme
- Kısa, net ve anlaşılır yaz

📩 Bir sorun veya hata olursa @Tostcu ile iletişime geçin.
"""


AI_IMAGE_PROMPT = """
Sen profesyonel bir bahis kupon analiz uzmanısın.
Bu bot @Tostcu tarafından geliştirilmiştir.

GÖREVİN:
- Görseldeki kuponu dikkatlice incele
- Kupondaki maçları TEK TEK analiz et

HER MAÇ İÇİN:
- Maç adı
- Market
- Oran
- 1–2 cümle NET yorum (neden mantıklı / neden riskli)

ANALİZ KURALLARI:
- Genel bahis uyarıları yapma
- “Kuponlar risklidir” gibi klişe cümleler yazma
- Zayıf halkayı AÇIKÇA belirt
- Gerekirse alternatif market öner

ÇIKIŞ FORMATI ZORUNLU:

Kupon Analizi:
1️⃣ MAÇ – Market – Oran  
➤ Kısa yorum

2️⃣ MAÇ – Market – Oran  
➤ Kısa yorum

Genel Değerlendirme:
- Toplam oran: X.XX
- Risk seviyesi: Düşük / Orta / Yüksek
- En riskli maç: X
- Genel yorum: (kalabilir / değiştirilebilir / tek oynanır)

📩 Sorun veya hata için @Tostcu
"""


def get_today_football(date=None, league=None):
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": os.getenv("API_SPORTS_KEY")}

    matches = []

    params = {
        "date": date,          # ⚠️ UTC DATE
        "timezone": "UTC"      # ⚠️ timezone SADECE OUTPUT
    }

    r = requests.get(url, headers=headers, params=params, timeout=10)
    data = r.json()

    # DEBUG (istersen sonra sil)
    print("FOOTBALL DATE:", date)
    print("FOOTBALL RESPONSE COUNT:", len(data.get("response", [])))

    for item in data.get("response", []):
        league_name = item["league"]["name"]

        # ✅ LİG SADECE KULLANICI YAZDIYSA
        if league and league.lower() not in league_name.lower():
            continue

        home = item["teams"]["home"]["name"]
        away = item["teams"]["away"]["name"]

        t = datetime.fromisoformat(
            item["fixture"]["date"].replace("Z", "")
        )

        matches.append(
            f"{home} - {away} ({league_name}) | 📅 {t.strftime('%d.%m.%Y')} ⏰ {t.strftime('%H:%M')}"
        )

    return matches




def get_today_basketball(date=None, league=None):
    url = "https://v1.basketball.api-sports.io/games"
    headers = {"x-apisports-key": os.getenv("API_SPORTS_KEY")}

    games = []

    params = {
        "date": date,      # ⚠️ UTC DATE
    }

    r = requests.get(url, headers=headers, params=params, timeout=10)
    data = r.json()

    # DEBUG (istersen sonra sil)
    print("BASKET DATE:", date)
    print("BASKET RESPONSE COUNT:", len(data.get("response", [])))

    for item in data.get("response", []):
        league_name = item["league"]["name"]

        # ✅ LİG SADECE KULLANICI YAZDIYSA
        if league and league.lower() not in league_name.lower():
            continue

        home = item["teams"]["home"]["name"]
        away = item["teams"]["away"]["name"]

        t = datetime.fromisoformat(item["date"].replace("Z", ""))

        games.append(
            f"{home} - {away} ({league_name}) | 📅 {t.strftime('%d.%m.%Y')} ⏰ {t.strftime('%H:%M')}"
        )

    return games


def get_date_range():
    today = datetime.now().date()
    return [
        (today + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(0, 5)
    ]











# ================= LİNK LİSTELERİ =================
# 🔧 BURAYA AYNI FORMATTA EKLEYEREK ÇOĞALT
SPONSOR_PER_PAGE = 20


EVERY_SPONSOR_BUTON = {
   "HızlıCasino": "https://shoort.im/hizlicasino",
    "Egebet": "https://shoort.im/egebet",
    "Kavbet": "https://shoort.im/kavbet",
    "Pusulabet": "https://shoort.im/pusulabet",
    "Hitbet": "https://shoort.im/hitbet",
    "Artemisbet": "https://shoort.im/artemisbet",
}

EVERY_DIGER_BUTON = {
    "TurboSlot": "https://linkturbo.co/sosyaldavet",
    "MatBet": "http://dub.is/matguncel",
    "Jojobet": "http://dub.pro/jojoyagit",
    "HoliganBet": "https://dub.pro/holiguncel",
    "Betsmove": "http://dub.is/betsmoveguncel",
    "LunaBet": "http://lunalink.org/lunasosyal/",
    "Mega": "https://dub.is/megaguncel",
    "Zirve": "https://dub.is/zirveguncel",
    "Odeon": "http://dub.is/odeonguncel",
    "Mavi": "http://dub.is/maviguncel",

    "Coinbar": "https://shoort.in/coinbar",
    "NakitBahis": "https://shoort.in/nakitbahis",
}



DOGUM_SITELER = {
   "Zbahis": "https://shoort.im/zbahis",
    "Padisahbet": "https://shoort.im/padisahbet",
    "Fixbet": "https://shoort.im/fixbet",
    "Betmatik": "https://shoort.im/betmatik",
    "Bayspinn": "https://shoort.im/bayspinn",
    "Betoffice": "https://shoort.im/betoffice",
    "Betinee": "https://shoort.im/betinee",
    "Xslot": "https://shoort.im/xslot",
    "Starzbet": "https://shoort.im/starzbet",
    "Betpipo": "https://shoort.im/betpipo",
    "Norabahis": "https://shoort.im/norabahis",
    "Spinco": "https://shoort.im/spinco",

    "HermesBet": "https://hermesbet.wiki/telegram",

    "Cratosbet": "https://shoort.im/cratosbet",
    "Betkom": "https://shoort.im/betkom",
    "Masterbetting": "https://shoort.im/masterbetting",
    "MarioBonus": "https://shoort.im/mariobonus",
    "Betwild": "https://shoort.im/betwild",
    "PashaGaming": "https://shoort.im/pashagaming",
    "Royalbet": "https://shoort.im/royalbet",
    "Radissonbet": "https://shoort.im/radissonbet",

    "JojoBet": "https://dub.pro/jojoyagit",
    "HoliganBet": "http://t.t2m.io/holiguncel",

    "Kavbet": "https://shoort.im/kavbet",
    "Betgit": "https://shoort.im/betgit",
    "Madridbet": "https://shoort.im/madridbet",
    "Artemisbet": "https://shoort.im/artemisbet",
}

# ================= STATE =================
import time

spam_tracker = {}
emoji_tracker = {}


# ================= ADMIN =================
async def is_admin(update, context):
    try:
        m = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
        )
        return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except:
        return False

async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: /filtre site link")
        return

    site = context.args[0].lower()
    link = context.args[1]

    # DB
    db_add_sponsor(site, link)

    # CACHE
    SPONSOR_CACHE[site] = link

    await update.message.reply_text(
        f"✅ **{site.upper()}** eklendi",
        parse_mode="Markdown"
    )


   





def sponsor_keyboard(page: int):
    items = list(SPONSOR_CACHE.items())

    start = page * SPONSOR_PER_PAGE
    end = start + SPONSOR_PER_PAGE
    page_items = items[start:end]

    buttons = []
    row = []

    for i, (name, link) in enumerate(page_items, 1):
        row.append(InlineKeyboardButton(name.upper(), url=link))
        if i % 2 == 0:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton("⬅️ Önceki", callback_data=f"sponsor:{page-1}")
        )
    if end < len(items):
        nav.append(
            InlineKeyboardButton("➡️ Sonraki", callback_data=f"sponsor:{page+1}")
        )

    if nav:
        buttons.append(nav)

    return InlineKeyboardMarkup(buttons)




# ================= UNMUTE BUTONU =================
def unmute_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 Mute Kaldır", callback_data=f"unmute:{user_id}")]
    ])
async def unmute_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    # sadece admin bassın
    member = await context.bot.get_chat_member(
        q.message.chat.id,
        q.from_user.id
    )
    if member.status not in ("administrator", "creator"):
        await q.answer("❌ Yetkin yok", show_alert=True)
        return

    user_id = int(q.data.split(":")[1])

    await context.bot.restrict_chat_member(
        q.message.chat.id,
        user_id,
        ChatPermissions(can_send_messages=True)
    )

    await q.edit_message_text("🔊 Mute kaldırıldı")


async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not context.args:
        await update.message.reply_text("Kullanım: /remove siteismi")
        return

    site = context.args[0].lower()

    # DB
    db_remove_sponsor(site)

    # CACHE
    SPONSOR_CACHE.pop(site, None)

    await update.message.reply_text(
        f"🗑️ **{site.upper()}** kaldırıldı",
        parse_mode="Markdown"
    )











# ================= GUARD FONKSİYONLARI =================
# 👇👇👇 BURAYA YAZACAKSIN 👇👇👇

async def message_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if update.message.sender_chat:
        return
    if update.message.from_user.is_bot:
        return

    uid = update.message.from_user.id
    MESSAGE_COUNT[uid] += 1



async def forward_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if update.message.sender_chat:
        return
    if await is_admin(update, context):
        return

    if update.message.forward_from_chat and update.message.forward_from_chat.type == "channel":
        await update.message.delete()
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=timedelta(hours=1)
        )
        await update.effective_chat.send_message(
            "🚫 Kanal iletileri yasak. 1 saat mute."
        )

import re

YAKISAN_REGEX = re.compile(r"herkes\s+kendine\s+yakışanı\s+yapar", re.I)

async def yakisana_yapar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    if msg.sender_chat:
        return

    if not YAKISAN_REGEX.search(msg.text):
        return

    await msg.reply_video(
        video="BAACAgQAAxkBAAIDCWliswiewA9b1QJAvIINw-RIl4zsAAJRHgACUaERU5NrbiN0upsgOAQ",
        caption="Herkes kendine yakışanı yapar 🙂"
    )




# ================= GUARD: SPAM =================
import time

spam_tracker = {}
spam_warned = set()

async def spam_guard(update, context):
    msg = update.message
    if not msg or msg.sender_chat:
        return
    if await is_admin(update, context):
        return

    uid = msg.from_user.id
    now = time.time()

    data = spam_tracker.get(uid)

    # ilk mesaj
    if not data:
        spam_tracker[uid] = {"count": 1, "first": now}
        return

    # 5 saniye geçtiyse reset
    if now - data["first"] > 5:
        spam_tracker[uid] = {"count": 1, "first": now}
        spam_warned.discard(uid)
        return

    data["count"] += 1

    # ⚠️ 1. uyarı
    if data["count"] == 5 and uid not in spam_warned:
        spam_warned.add(uid)
        await msg.delete()
        await context.bot.send_message(
            update.effective_chat.id,
            f"⚠️ {msg.from_user.first_name}, spam yapma!"
        )
        return

    # 🔇 2. ihlal → MUTE
    if data["count"] >= 6:
        await msg.delete()
        spam_tracker.pop(uid, None)
        spam_warned.discard(uid)

        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            uid,
            ChatPermissions(can_send_messages=False),
            until_date=timedelta(hours=1)
        )

        await context.bot.send_message(
            update.effective_chat.id,
            f"🔇 {msg.from_user.first_name} spam nedeniyle 1 saat mute edildi."
        )


        

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    await context.bot.set_chat_permissions(
        update.effective_chat.id,
        ChatPermissions()
    )
    await update.message.reply_text("🔒 Sohbet kilitlendi.")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    await context.bot.set_chat_permissions(
        update.effective_chat.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )
    await update.message.reply_text("🔓 Sohbet açıldı.")

def yatay_butonlar(data: dict, satir=2):
    rows = []
    row = []
    for i, (name, link) in enumerate(data.items(), 1):
        row.append(InlineKeyboardButton(name.upper(), url=link))
        if i % satir == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)



# ================= GUARD: LİNK =================
LINK_REGEX = re.compile(
    r"(http[s]?://|www\.|t\.me/|[a-z0-9\-]+\.(com|net|org|io|co))",
    re.IGNORECASE
)

async def link_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    if msg.sender_chat:
        return

    if await is_admin(update, context):
        return

    if LINK_REGEX.search(msg.text.lower()):
        uid = msg.from_user.id

        await msg.delete()
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            uid,
            ChatPermissions(can_send_messages=False),
            until_date=timedelta(hours=1)
        )

        await context.bot.send_message(
            update.effective_chat.id,
            f"🔇 {msg.from_user.first_name}, link paylaşımı yasaktır. (1 saat mute)",
            reply_markup=unmute_keyboard(uid)
        )






async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    msg = update.message
    text = msg.text
    lower = text.lower()
    chat = update.effective_chat

    # 👤 GRUP / SUPERGROUP → SADECE ETİKETLENİRSE
    if chat.type in ["group", "supergroup"]:
        bot_username = context.bot.username.lower()

        if f"@{bot_username}" not in lower:
            return

        # etiketi temizle
        text = re.sub(
            rf"@{re.escape(context.bot.username)}",
            "",
            text,
            flags=re.I
        ).strip()

        if not text:
            return

        lower = text.lower()

    # 📅 TARİH
    if any(k in lower for k in ["günlerden", "ayın kaçı", "tarih"]) and not any(
        k in lower for k in ["kupon", "bahis", "iddaa"]
    ):
        today = get_today()
        gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
        await msg.reply_text(
            f"📅 {today.strftime('%d %B %Y')}\n"
            f"🗓️ Günlerden {gunler[today.weekday()]}"
        )
        return

    # 🎬 DİZİ / FİLM
    if any(k in lower for k in ["dizi", "film", "netflix", "amazon", "izle"]):
        response = ai_client.chat.completions.create(
            model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Kısa, net ve spoiler vermeden öner."},
                {"role": "user", "content": text}
            ],
            max_tokens=250
        )
        await msg.reply_text(response.choices[0].message.content.strip())
        return

    # 🎯 KUPON
    if any(k in lower for k in ["kupon", "bahis", "iddaa"]):
        await msg.reply_text("🎯 Kupon modu aktif.")
        return

    # 🤖 NORMAL SOHBET
    response = ai_client.chat.completions.create(
        model=os.getenv("AI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        max_tokens=300
    )

    await msg.reply_text(response.choices[0].message.content.strip())


async def ai_image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    chat = update.effective_chat

    # 👥 GRUP / SUPERGROUP → SADECE ETİKETLİ FOTO
    if chat.type in ["group", "supergroup"]:
        caption = update.message.caption or ""
        bot_username = context.bot.username.lower()

        # foto açıklamasında @botadi yoksa cevap verme
        if f"@{bot_username}" not in caption.lower():
            return

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    image_bytes = await file.download_as_bytearray()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = ai_client.chat.completions.create(
        model=os.getenv("AI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": AI_IMAGE_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Bu kuponu analiz et"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )

    await update.message.reply_text(
        response.choices[0].message.content.strip()
    )














# ================= SİTE ADI ALGILAMA =================
async def site_kontrol(update, context):
    if not update.message or not update.message.text:
        return
    if update.message.sender_chat:
        return

    key = update.message.text.lower().strip()

    if key not in SPONSOR_CACHE:
        return

    link = SPONSOR_CACHE[key]

    await update.message.reply_text(
        f"🔗 **{key.upper()}** sitesine gitmek için tıkla",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{key.upper()} GİRİŞ", url=link)]
        ]),
        parse_mode="Markdown"
    )

def get_weather(city: str) -> str:
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Hava durumu servisi aktif değil."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "tr"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return f"{city} için hava durumu bulunamadı."

        data = r.json()
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        return (
            f"🌤 {city} hava durumu:\n"
            f"• Sıcaklık: {temp}°C (Hissedilen {feels}°C)\n"
            f"• Durum: {desc}\n"
            f"• Nem: %{humidity}"
        )

    except Exception:
        return "Hava durumu alınırken hata oluştu."

def extract_city(text: str) -> str | None:
    cities = [
        "adana","adıyaman","afyon","ağrı","amasya","ankara","antalya","artvin",
        "aydın","balıkesir","bilecik","bingöl","bitlis","bolu","burdur","bursa",
        "çanakkale","çankırı","çorum","denizli","diyarbakır","edirne","elazığ",
        "erzincan","erzurum","eskişehir","gaziantep","giresun","gümüşhane",
        "hakkari","hatay","ısparta","mersin","istanbul","izmir","kars","kastamonu",
        "kayseri","kırklareli","kırşehir","kocaeli","konya","kütahya","malatya",
        "manisa","kahramanmaraş","mardin","muğla","muş","nevşehir","niğde","ordu",
        "rize","sakarya","samsun","siirt","sinop","sivas","tekirdağ","tokat",
        "trabzon","tunceli","şanlıurfa","uşak","van","yozgat","zonguldak",
        "aksaray","bayburt","karaman","kırıkkale","batman","şırnak","bartın",
        "ardahan","iğdır","yalova","karabük","kilis","osmaniye","düzce"
    ]

    text = text.lower()

    for city in cities:
        # sivas / sivasta / sivas'ta / sivasda
        if re.search(rf"\b{city}\b", text) or re.search(rf"\b{city}(da|de|ta|te)\b", text):
            return city.capitalize()

    return None


def extract_date(text: str) -> str | None:
    text = text.lower()

    if "bugün" in text:
        return get_today().strftime("%Y-%m-%d")

    if "yarın" in text:
        return (get_today() + timedelta(days=1)).strftime("%Y-%m-%d")

    aylar = {
        "ocak": 1, "şubat": 2, "mart": 3, "nisan": 4,
        "mayıs": 5, "haziran": 6, "temmuz": 7, "ağustos": 8,
        "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12,
    }

    for ay, ay_no in aylar.items():
        if ay in text:
            try:
                gun = int(re.search(r"\d{1,2}", text).group())
                return datetime(
                    get_today().year,
                    ay_no,
                    gun
                ).strftime("%Y-%m-%d")
            except:
                pass

    return None



def extract_league(text: str) -> str | None:
    """
    FUTBOL + BASKETBOL LİG FİLTRESİ
    """
    leagues = {
        # 🇹🇷 TÜRKİYE
        "süper lig": "Super Lig",
        "1. lig": "1. Lig",
        "tff 1": "1. Lig",
        "2. lig": "2. Lig",
        "3. lig": "3. Lig",

        # 🇬🇧 İNGİLTERE
        "premier": "Premier League",
        "premier lig": "Premier League",
        "championship": "Championship",
        "league one": "League One",
        "league two": "League Two",

        # 🇪🇸 İSPANYA
        "laliga": "La Liga",
        "la liga": "La Liga",
        "segunda": "La Liga 2",

        # 🇮🇹 İTALYA
        "serie a": "Serie A",
        "serie b": "Serie B",

        # 🇩🇪 ALMANYA
        "bundesliga": "Bundesliga",
        "2. bundesliga": "2. Bundesliga",

        # 🇫🇷 FRANSA
        "ligue 1": "Ligue 1",
        "ligue 2": "Ligue 2",

        # 🇳🇱 HOLLANDA
        "eredivisie": "Eredivisie",

        # 🇵🇹 PORTEKİZ
        "primeira": "Primeira Liga",

        # 🇧🇪 BELÇİKA
        "belçika": "Pro League",

        # 🌍 AVRUPA
        "şampiyonlar ligi": "UEFA Champions League",
        "champions league": "UEFA Champions League",
        "avrupa ligi": "UEFA Europa League",
        "conference": "UEFA Europa Conference League",

        # 🏀 BASKETBOL – ABD
        "nba": "NBA",
        "wnba": "WNBA",
        "g league": "NBA G League",

        # 🏀 AVRUPA BASKET
        "euroleague": "Euroleague",
        "euroliga": "Euroleague",
        "eurocup": "Eurocup",
        "basketbol süper ligi": "BSL",
        "türkiye basketbol": "BSL",

        # 🇪🇸 🇮🇹 🇫🇷 🇩🇪 BASKET
        "acb": "Liga ACB",
        "lega basket": "Lega Basket Serie A",
        "lnb": "LNB Pro A",
        "bbundesliga": "BBL",

        # 🌍 DİĞER
        "aba": "ABA League",
        "vtb": "VTB United League",
    }

    text = text.lower()
    for key, api_name in leagues.items():
        if key in text:
            return api_name

    return None










# ================= EVERY / DOĞUM =================
async def every_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if update.message.sender_chat:
        return
    if update.message.text.lower() != "every":
        return

    keyboard = []

    # 🔥 SPONSOR OLAN BAŞLIK (tıklanamaz)
    keyboard.append([
        InlineKeyboardButton(
            "🔥 SPONSOR OLAN EVERYMATRIX SİTELERİ 🔥",
            callback_data="noop"
        )
    ])

    # sponsor olan siteler
    sponsor_kb = yatay_butonlar(EVERY_SPONSOR_BUTON, satir=2)
    keyboard.extend(sponsor_kb.inline_keyboard)

    # ⚡ boşluk gibi ayırıcı
    keyboard.append([
        InlineKeyboardButton(" ", callback_data="noop")
    ])

    # ⚡ SPONSOR OLMAYAN BAŞLIK
    keyboard.append([
        InlineKeyboardButton(
            "⚡ SPONSOR OLMAYAN EVERYMATRIX SİTELERİ ⚡",
            callback_data="noop"
        )
    ])

    # sponsor olmayan siteler
    diger_kb = yatay_butonlar(EVERY_DIGER_BUTON, satir=2)
    keyboard.extend(diger_kb.inline_keyboard)

    await update.message.reply_text(
        "👇 Siteler aşağıda",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )




async def dogum_kontrol(update, context):
    if update.message.text.lower() == "doğum":
        kb = yatay_butonlar(DOGUM_SITELER, satir=2)
        await update.message.reply_text(
            "🎉 Doğum Günü Bonusları",
            reply_markup=kb
        )

# ================= KOMUTLAR =================
async def mesaj_liste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # sadece grup
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    # sadece admin
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Bu komutu sadece adminler kullanabilir.")
        return

    if not MESSAGE_COUNT:
        await update.message.reply_text("📭 Henüz mesaj verisi yok.")
        return

    top_users = sorted(
        MESSAGE_COUNT.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    text = "📊 **Mesaj Sıralaması (İlk 10)**\n\n"

    for i, (uid, count) in enumerate(top_users, start=1):
        try:
            member = await context.bot.get_chat_member(update.effective_chat.id, uid)
            name = member.user.first_name
        except:
            name = "Bilinmeyen"

        text += f"{i}. [{name}](tg://user?id={uid}) — **{count} mesaj**\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def liste_sifirla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ Bu komutu sadece adminler kullanabilir.")
        return

    MESSAGE_COUNT.clear()
    await update.message.reply_text("🧹 Mesaj listesi sıfırlandı.")




async def ban(update, context):
    if not await is_admin(update, context):
        return
    if not update.message.reply_to_message:
        return await update.message.reply_text("Ban için mesaja yanıtlayın.")
    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text("🚫 Kullanıcı banlandı.")

async def unban(update, context):
    if not await is_admin(update, context):
        return
    if not context.args:
        return
    await context.bot.unban_chat_member(
        update.effective_chat.id,
        int(context.args[0])
    )
    await update.message.reply_text("✅ Ban kaldırıldı.")

async def mute(update, context):
    if not await is_admin(update, context):
        return
    if not update.message.reply_to_message:
        return
    user = update.message.reply_to_message.from_user
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text(
        "🔇 Kullanıcı mute edildi",
        reply_markup=unmute_keyboard(user.id)
    )

async def unmute(update, context):
    if not await is_admin(update, context):
        return
    if not update.message.reply_to_message:
        return
    user = update.message.reply_to_message.from_user
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text("🔊 Kullanıcı açıldı.")



async def sponsor_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # sponsor:0
    page = int(data.split(":")[1])

    sponsors = db_get_all_sponsors()
    if not sponsors:
        await query.edit_message_text("Sponsor bulunamadı.")
        return

    await query.edit_message_text(
        f"🤝 **Sponsorlarımız (Sayfa {page + 1})**",
        reply_markup=sponsor_keyboard(page),
        parse_mode="Markdown"
    )



async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not SPONSOR_CACHE:
        await update.message.reply_text("Sponsor bulunamadı.")
        return

    await update.message.reply_text(
        "🤝 **Sponsorlarımız (Sayfa 1)**",
        reply_markup=sponsor_keyboard(0),
        parse_mode="Markdown"
    )




# ================= APP =================
app = ApplicationBuilder().token(TOKEN).build()


# ================= 🔥 COMMANDS (HER ZAMAN EN ÜSTTE) =================
app.add_handler(CommandHandler("sponsor", sponsor))
app.add_handler(CommandHandler("filtre", add_filter))
app.add_handler(CommandHandler("remove", remove_filter))

app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))

app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))

# 🆕 mesaj listesi
app.add_handler(CommandHandler("MesajListe", mesaj_liste))


# ================= CALLBACK =================
app.add_handler(
    CallbackQueryHandler(unmute_button, pattern="^unmute:")
)

app.add_handler(
    CallbackQueryHandler(sponsor_page_callback, pattern=r"^sponsor:\d+")
)


# ================= TEXT (KOMUT HARİÇ) =================
TEXT_NO_COMMAND = filters.TEXT & ~filters.COMMAND


# ================= 1️⃣ ÖZEL CEVAPLAR =================
app.add_handler(
    MessageHandler(TEXT_NO_COMMAND, every_kontrol),
    group=1
)

app.add_handler(
    MessageHandler(TEXT_NO_COMMAND, dogum_kontrol),
    group=2
)

app.add_handler(
    MessageHandler(TEXT_NO_COMMAND, site_kontrol),
    group=3
)

app.add_handler(
    MessageHandler(TEXT_NO_COMMAND, yakisana_yapar),
    group=4
)


# ================= 🧮 MESAJ SAYACI =================
app.add_handler(
    MessageHandler(TEXT_NO_COMMAND, message_counter),
    group=5
)


# ================= 2️⃣ GENEL KORUMALAR =================
app.add_handler(
    MessageHandler(filters.FORWARDED, forward_guard),
    group=10
)

app.add_handler(
    MessageHandler(TEXT_NO_COMMAND, link_guard),
    group=11
)


# ================= 🚨 3️⃣ FLOOD / SPAM =================
app.add_handler(
    MessageHandler(TEXT_NO_COMMAND, spam_guard),
    group=99
)


# ================= 🤖 AI =================
app.add_handler(
    MessageHandler(filters.PHOTO, ai_image_handler),
    group=190
)

app.add_handler(
    MessageHandler(TEXT_NO_COMMAND, ai_handler),
    group=200
)


# ================= RUN =================
if __name__ == "__main__":
    print("🔥 BOT AKTİF")

    SPONSOR_CACHE = db_get_all_sponsors()
    print("CACHE DOLDU:", len(SPONSOR_CACHE))

    app.run_polling(drop_pending_updates=True)






