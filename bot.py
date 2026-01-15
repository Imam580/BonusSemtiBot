# bot.py
from openai import OpenAI
import os
import re
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
Sen Bonussemti adlı bir Telegram bahis asistanısın.

Kurallar:
- Kullanıcı kupon isterse DOĞRUDAN kupon öner
- 2–4 maçlı örnek kuponlar oluştur
- Her maç için:
  • Maç adı
  • Market (MS, KG, Üst/Alt vb.)
  • Tahmini oran
- Toplam oran ve risk seviyesi belirt
- Kısa ve net yaz, lafı uzatma
- "kesin", "garanti", "banko" ASLA deme

Örnek format:
Kupon Önerisi:
1️⃣ Takım A – Takım B | MS 1 | Oran: 1.65
2️⃣ Takım C – Takım D | KG Var | Oran: 1.55

Toplam Oran: 2.55
Risk: Orta
"""
AI_IMAGE_PROMPT = """
Sen bahis kuponu analiz eden bir asistansın.

Kurallar:
- Fotoğraftaki kuponu incele
- Maç sayısına göre risk seviyesi belirt
- Çok maçlı kuponların riskli olduğunu söyle
- Gerekirse daha güvenli alternatif kupon öner
- Oran mantığını kısaca açıkla
- "kesin", "garanti", "banko" ASLA deme

Kısa ve net cevap ver.
"""



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
import time
import re

EMOJI_REGEX = re.compile("[\U0001F300-\U0001FAFF]")

emoji_tracker = {}
emoji_warned = set()

async def emoji_flood_guard(update, context):
    msg = update.message
    if not msg or not msg.text or msg.sender_chat:
        return
    if await is_admin(update, context):
        return

    emojis = EMOJI_REGEX.findall(msg.text)
    if len(emojis) < 5:
        return

    uid = msg.from_user.id
    now = time.time()

    data = emoji_tracker.get(uid)

    if not data:
        emoji_tracker[uid] = {"count": 1, "first": now}
        await msg.delete()
        return

    if now - data["first"] > 5:
        emoji_tracker[uid] = {"count": 1, "first": now}
        emoji_warned.discard(uid)
        await msg.delete()
        return

    data["count"] += 1

    # ⚠️ uyarı
    if data["count"] == 2 and uid not in emoji_warned:
        emoji_warned.add(uid)
        await msg.delete()
        await context.bot.send_message(
            update.effective_chat.id,
            f"⚠️ {msg.from_user.first_name}, emoji flood yapma!"
        )
        return

    # 🔇 mute
    if data["count"] >= 3:
        await msg.delete()
        emoji_tracker.pop(uid, None)
        emoji_warned.discard(uid)

        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            uid,
            ChatPermissions(can_send_messages=False),
            until_date=timedelta(hours=1)
        )

        await context.bot.send_message(
            update.effective_chat.id,
            f"🔇 {msg.from_user.first_name} emoji flood nedeniyle 1 saat mute edildi."
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
async def link_guard(update, context):
    if not update.message or update.message.sender_chat:
        return
    if update.message.forward_from_chat:
        return
    if await is_admin(update, context):
        return

    text = update.message.text.lower()
    if "http://" in text or "https://" in text or "t.me/" in text:
        uid = update.message.from_user.id
        await update.message.delete()
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            uid,
            ChatPermissions(can_send_messages=False),
            until_date=timedelta(hours=1)
        )
        await update.effective_chat.send_message(
            "🔇 Link paylaştığınız için 1 saat mute",
            reply_markup=unmute_keyboard(uid)
        )


# ================= GUARD: KANAL ETİKET =================
MENTION_SPAM_WORDS = [
    "bonus", "kazanç", "bahis", "free",
    "kazan", "link", "telegram", "grup","yaz","gel","herkese",
]

async def mention_reklam_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    # kanal / bot mesajı
    if msg.sender_chat:
        return

    # admin muaf
    if await is_admin(update, context):
        return

    text = msg.text.lower()

    mention_count = text.count("@")
    if mention_count == 0:
        return

    has_link = bool(re.search(r"http|t\.me|\.com|\.net|\.org", text))
    has_spam_word = any(w in text for w in MENTION_SPAM_WORDS)

    if (
        mention_count >= 2 or
        (mention_count >= 1 and has_link) or
        (mention_count >= 1 and has_spam_word)
    ):
        # 🧹 mesajı sil
        await msg.delete()

        # ⚠️ uyarı
        await context.bot.send_message(
            update.effective_chat.id,
            f"🚫 {msg.from_user.first_name}, @ ile reklam yapmak yasaktır."
        )

async def ai_image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.photo:
        return

    chat_type = update.effective_chat.type

    # Grup → sadece etiketliyse
    if chat_type in ["group", "supergroup"]:
        if not msg.caption or not is_bot_mentioned(msg.caption):
            return

        user_text = re.sub(
            rf"@{re.escape(os.getenv('BOT_USERNAME'))}",
            "",
            msg.caption,
            flags=re.I
        ).strip()
    else:
        user_text = msg.caption or "Bu kuponu analiz eder misin?"

    photo = msg.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_url = file.file_path

    try:
        response = ai_client.chat.completions.create(
            model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": AI_IMAGE_PROMPT + "\n" + user_text},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens=300
        )

        await msg.reply_text(response.choices[0].message.content.strip())

    except Exception as e:
        await msg.reply_text("⚠️ Kuponu analiz edemedim.")


async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    chat_type = update.effective_chat.type
    text = msg.text.strip()

    # Grup → sadece etiketliyse
    if chat_type in ["group", "supergroup"]:
        if not is_bot_mentioned(text):
            return

        text = re.sub(
            rf"@{re.escape(os.getenv('BOT_USERNAME'))}",
            "",
            text,
            flags=re.I
        ).strip()

        if not text:
            return

    # özel tetikleyiciler AI'ye gitmesin
    lower_text = text.lower()
    if lower_text in ["every", "doğum"] or lower_text in SPONSOR_CACHE:
        return

    try:
        response = ai_client.chat.completions.create(
            model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            max_tokens=350
        )

        await msg.reply_text(response.choices[0].message.content.strip())

    except Exception:
        await msg.reply_text("⚠️ Şu anda cevap veremiyorum.")



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

# ================= COMMANDS =================
app.add_handler(CommandHandler("sponsor", sponsor))
app.add_handler(CommandHandler("filtre", add_filter))
app.add_handler(CommandHandler("remove", remove_filter))

app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))

app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))


# ================= CALLBACK =================
app.add_handler(
    CallbackQueryHandler(unmute_button, pattern="^unmute:")
)

app.add_handler(
    CallbackQueryHandler(sponsor_page_callback, pattern=r"^sponsor:\d+")
)


# ================= 1️⃣ ÖZEL CEVAPLAR (ASLA SİLİNMEZ) =================

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, every_kontrol),
    group=1
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, dogum_kontrol),
    group=2
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, site_kontrol),
    group=3
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, yakisana_yapar),
    group=4
)

# ================= 2️⃣ GENEL KORUMALAR =================

app.add_handler(
    MessageHandler(filters.FORWARDED, forward_guard),
    group=10
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, link_guard),
    group=11
)

# ================= GUARD: KANAL ETİKET =================
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, mention_reklam_guard),
    group=12
)



# ================= 🚨 3️⃣ FLOOD / SPAM (EN SON – DOKUNULMAZ) =================

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, emoji_flood_guard),
    group=98
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, spam_guard),
    group=99
)

app.add_handler(
    MessageHandler(filters.PHOTO, ai_image_handler),
    group=190
)


app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handler),
    group=200
)


# ================= RUN =================
if __name__ == "__main__":
    print("🔥 BOT AKTİF")

    # cache doldur (GLOBAL YAZILMAZ)
    SPONSOR_CACHE = db_get_all_sponsors()
    print("CACHE DOLDU:", len(SPONSOR_CACHE))

    app.run_polling(drop_pending_updates=True)





