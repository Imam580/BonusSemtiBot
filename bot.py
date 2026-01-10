# bot.py
import os
import re
import json

SPONSOR_FILE = "sponsorlar.json"

def load_sponsorlar():
    try:
        with open(SPONSOR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_sponsorlar(data):
    with open(SPONSOR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

from datetime import timedelta
from dotenv import load_dotenv

from telegram import (
    Update,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ChatMemberStatus, MessageEntityType
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ================= ENV =================
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN missing")

# ================= LİNK LİSTELERİ =================
# 🔧 BURAYA AYNI FORMATTA EKLEYEREK ÇOĞALT

SPONSORLAR = load_sponsorlar()


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
        await update.message.reply_text("Kullanım: /filtre siteismi link")
        return

    site = context.args[0].lower()
    link = context.args[1]

    # shoort.in → shoort.im
    if link.startswith("http://shoort.in/") or link.startswith("https://shoort.in/"):
        link = link.replace("shoort.in", "shoort.im")

    SPONSORLAR[site] = link
    save_sponsorlar(SPONSORLAR)

    await update.message.reply_text(
        f"✅ **{site.upper()}** eklendi",
        parse_mode="Markdown"
    )

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
        return await update.message.reply_text(
            "Kullanım: /remove siteismi"
        )

    site = context.args[0].lower()

   if site in SPONSORLAR:
    SPONSORLAR.pop(site)
    save_sponsorlar(SPONSORLAR)   # 👈 SADECE BU SATIR
    await update.message.reply_text(
        f"🗑️ **{site.upper()}** kaldırıldı",
        parse_mode="Markdown"
    )
    else:
        await update.message.reply_text("❌ Site bulunamadı")


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


# ================= SİTE ADI ALGILAMA =================
async def site_kontrol(update, context):
    if update.message.sender_chat:
        return

    key = update.message.text.lower().strip()
    if key in SPONSORLAR:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{key.upper()} GİRİŞ", url=SPONSORLAR[key])]
        ])
        await update.message.reply_text(
            f"{key.upper()} sitesine gitmek için tıklayın",
            reply_markup=kb,
            reply_to_message_id=update.message.message_id
        )

# ================= EVERY / DOĞUM =================
async def every_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if update.message.sender_chat:
        return
    if update.message.text.lower() != "every":
        return

    mesaj = (
        "🔥 **BonusSemti Güvencesiyle Sponsorumuz Olan EveryMatrix Altyapılı Siteler**\n\n"
        "https://shoort.im/hizlicasino\n"
        "https://shoort.im/egebet\n"
        "https://shoort.im/kavbet\n"
        "https://shoort.im/pusulabet\n"
        "https://shoort.im/hitbet\n"
        "https://shoort.im/artemisbet\n\n"
        "⚡ **DİĞER EVERYMATRIX ALTYAPISINDA OLAN SİTELER**\n\n"
        "https://linkturbo.co/sosyaldavet\n"
        "http://dub.is/matguncel\n"
        "http://dub.pro/jojoyagit\n"
        "https://dub.pro/holiguncel\n"
        "http://dub.is/betsmoveguncel\n"
        "http://lunalink.org/lunasosyal/\n"
        "https://dub.is/megaguncel\n"
        "https://dub.is/zirveguncel\n"
        "http://dub.is/odeonguncel\n"
        "http://dub.is/maviguncel\n"
        "https://shoort.in/coinbar\n"
        "https://shoort.in/nakitbahis\n"
    )

    kb1 = yatay_butonlar(EVERY_SPONSOR_BUTON, satir=2)
    kb2 = yatay_butonlar(EVERY_DIGER_BUTON, satir=2)

    await update.message.reply_text(
        mesaj,
        reply_markup=InlineKeyboardMarkup(
            kb1.inline_keyboard + kb2.inline_keyboard
        ),
        disable_web_page_preview=True,
        parse_mode="Markdown"
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



async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.sender_chat:
        return

    if not SPONSORLAR:
        return await update.message.reply_text("Sponsor bulunamadı.")

    kb = yatay_butonlar(SPONSORLAR, satir=2)

    await update.message.reply_text(
        "🤝 **Sponsorlarımız**",
        reply_markup=kb,
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


# ================= 🚨 3️⃣ FLOOD / SPAM (EN SON – DOKUNULMAZ) =================

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, emoji_flood_guard),
    group=98
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, spam_guard),
    group=99
)

# ================= RUN =================
print("🔥 BOT AKTİF")
app.run_polling(drop_pending_updates=True)


