import os
import random
import time
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    filters as tg_filters
)

# ================== ENV ==================

load_dotenv()
TOKEN = os.environ.get("TOKEN")


# ================== GLOBAL ==================

cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1
cekilis_kazananlar = []

BOT_BASLANGIC_ZAMANI = time.time()

kullanici_mesaj_sayisi = {}
min_mesaj_sayisi = 0

ZORUNLU_KANALLAR = [
    "@Canli_Izleme_Mac_Linkleri",
    "@plasespor",
    "@bonussemti",
    "@bonussemtietkinlik",
    "@hergunikioran",
    "@BahisKarhanesi",
    "@ozel_oran_2024",
]
# ================== KÜFÜR / SPAM / LİNK ==================

KUFUR_LISTESI = [
    "amk","aq","amq",
    "orospu","orospuçocuğu","orospu çocuğu",
    "piç","ibne",
    "yarrak","yarak",
    "sik","sikerim","siktir","sikeyim",
    "amcık","amcik",
    "anan","ananı","amina","amına",
    "götveren","gavat",
    "pezevenk","puşt"
]

kullanici_kufur_sayisi = {}

SPAM_SURE = 5      # saniye
SPAM_LIMIT = 5
kullanici_spam = {}
kullanici_spam_uyari = {}


# --- Tüm filtreler ve linkler ---
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


# --- Yönetici kontrolü ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
        )
        return member.status in ("administrator", "creator")
    except:
        return False

# --- /filter komutu ---
async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Bu komutu sadece yönetici kullanabilir!")
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Kullanım: /filter <site_ismi> <site_linki>")
        return
    site_ismi = context.args[0].lower()
    site_linki = context.args[1]
    filters_dict[site_ismi] = site_linki
    await update.message.reply_text(f"✅ Filtre eklendi: {site_ismi} → {site_linki}")

   # --- Küfür engeli ---
async def kufur_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if await is_admin(update, context):
        return

    text = update.message.text.lower()
    user = update.message.from_user
    user_id = user.id

    for kufur in KUFUR_LISTESI:
        if kufur in text:
            try:
                await update.message.delete()
            except:
                pass

            kullanici_kufur_sayisi[user_id] = kullanici_kufur_sayisi.get(user_id, 0) + 1

            if kullanici_kufur_sayisi[user_id] == 1:
                sure = 5 * 60
                mesaj = "Küfürlü mesaj nedeniyle 5 dakika susturuldunuz."
            else:
                sure = 60 * 60
                mesaj = "Tekrar küfür edildiği için 1 saat susturuldunuz."

            try:
                await context.bot.restrict_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=int(time.time()) + sure
                )

                await update.effective_chat.send_message(
                    f"🔇 @{user.username or user.first_name}\n{mesaj}"
                )
            except:
                pass
            return


# --- /filtre komutu ---
async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece yönetici kullanabilir!")
        return

    if not context.args:
        await update.message.reply_text("Kullanım: /remove <site_ismi>")
        return

    site_ismi = context.args[0].lower()

    if site_ismi in filters_dict:
        del filters_dict[site_ismi]
        await update.message.reply_text(f"✅ {site_ismi} filtresi kaldırıldı!")
    else:
        await update.message.reply_text(f"❌ {site_ismi} filtresi bulunamadı!")

    if not filters_dict:
        await update.message.reply_text("❌ Filtre yok!")
        return
    msg = "\n".join([f"{k} → {v}" for k, v in filters_dict.items()])
    await update.message.reply_text(f"🔹 Filtreler:\n{msg}")


# --- Link engeli ---
async def link_engel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if await is_admin(update, context):
        return

    text = update.message.text.lower()
    user = update.message.from_user

    if "http://" in text or "https://" in text or "t.me/" in text or "www." in text:
        try:
            await update.message.delete()

            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=int(time.time()) + 3600
            )

            await update.effective_chat.send_message(
                f"🔇 @{user.username or user.first_name}\n"
                "Link paylaşımı yasak olduğu için 1 saat susturuldunuz."
            )
        except:
            pass


# --- /remove filters ---
async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece yönetici kullanabilir!")
        return
    if not context.args:
        await update.message.reply_text("Kullanım: /remove filters <site_ismi>")
        return
    site_ismi = context.args[0].lower()
    if site_ismi in filters_dict:
        del filters_dict[site_ismi]
        await update.message.reply_text(f"✅ {site_ismi} filtresi kaldırıldı!")
    else:
        await update.message.reply_text(f"❌ {site_ismi} filtresi bulunamadı!")


# --- Spam engeli ---
async def spam_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if await is_admin(update, context):
        return

    user = update.message.from_user
    user_id = user.id
    now = time.time()

    if user_id not in kullanici_spam:
        kullanici_spam[user_id] = []

    kullanici_spam[user_id].append(now)
    kullanici_spam[user_id] = [
        t for t in kullanici_spam[user_id]
        if now - t <= SPAM_SURE
    ]

    if len(kullanici_spam[user_id]) >= SPAM_LIMIT:
        try:
            await update.message.delete()
        except:
            pass

        if not kullanici_spam_uyari.get(user_id):
            kullanici_spam_uyari[user_id] = True
            await update.effective_chat.send_message(
                f"⚠️ @{user.username or user.first_name}\n"
                "Çok hızlı mesaj atıyorsunuz, lütfen yavaşlayın."
            )
        else:
            try:
                await context.bot.restrict_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=int(time.time()) + 3600
                )

                await update.effective_chat.send_message(
                    f"🔇 @{user.username or user.first_name}\n"
                    "Spam nedeniyle 1 saat susturuldunuz."
                )
            except:
                pass

            kullanici_spam[user_id] = []
            kullanici_spam_uyari[user_id] = False


# --- /lock ve /unlock ---
async def lock_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Bu komutu sadece yönetici kullanabilir!")
        return
    await context.bot.set_chat_permissions(update.effective_chat.id, permissions=None)
    await update.message.reply_text("🔒 Kanal kilitlendi!")

async def unlock_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Bu komutu sadece yönetici kullanabilir!")
        return
    await context.bot.set_chat_permissions(update.effective_chat.id, permissions=ChatPermissions(can_send_messages=True))
    await update.message.reply_text("🔓 Kanal kilidi açıldı!")

# --- Ban / Unban / Mute / Unmute ---
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece yönetici kullanabilir!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Ban için birini yanıtlayın!")
        return
    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"🔨 {user.full_name} banlandı!")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece yönetici kullanabilir!")
        return
    if not context.args:
        await update.message.reply_text("❌ Kullanım: /unban <user_id>")
        return
    user_id = int(context.args[0])
    await context.bot.unban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text(f"✅ {user_id} banı kaldırıldı!")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece yönetici kullanabilir!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Mute için birini yanıtlayın!")
        return
    user = update.message.reply_to_message.from_user
    await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=ChatPermissions(can_send_messages=False))
    await update.message.reply_text(f"🔇 {user.full_name} susturuldu!")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece yönetici kullanabilir!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Unmute için birini yanıtlayın!")
        return
    user = update.message.reply_to_message.from_user
    await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=ChatPermissions(can_send_messages=True))
    await update.message.reply_text(f"🔊 {user.full_name} konuşabilir artık!")

# --- !sil ---
async def sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    try:
        adet = int(update.message.text.split()[1])
    except:
        await update.message.reply_text("Kullanım: !sil 10")
        return

    for i in range(adet):
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id - i
            )
        except:
            pass


# --- Mesaj filtreleme ---
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        text = update.message.text.lower()

        for key, value in filters_dict.items():
            if key in text:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        f"🔗 {key.upper()} GİRİŞ İÇİN TIKLA",
                        url=f"https://{value}"
                    )]
                ])

                await update.message.reply_text(
                    f"✅ <b>{key.upper()} için giriş linki</b>",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                return


# ================== /cekilis ==================
async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_katilimcilar

    if not await is_admin(update, context):
        return

    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="cekilise_katil")]
    ])

    with open("cekilis.jpg", "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=(
                "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
                "🔥 <b>KATILIMCI SAYISI :</b> 0\n\n"
                "🏆 <b>Katılımcıların kanallarımızı ve botumuzu takip etmesi zorunludur!</b>\n\n"
                "🔥 https://t.me/Canli_Izleme_Mac_Linkleri\n"
                "🔥 https://t.me/plasespor\n"
                "🔥 https://t.me/bonussemti\n"
                "🔥 https://t.me/bonussemtietkinlik\n"
                "🔥 https://t.me/hergunikioran\n"
                "🔥 https://t.me/BahisKarhanesi\n"
                "🔥 https://t.me/ozel_oran_2024\n"
                "🔥 https://t.me/bonussemtii_bot"
            ),
            reply_markup=keyboard,
            parse_mode="HTML"
        )

# ================== BUTON ==================
async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not cekilis_aktif:
        return

    uid = query.from_user.id

    if uid in cekilis_katilimcilar:
        await query.answer("Zaten katılmış durumdasınız 😊", show_alert=True)
        return

    cekilis_katilimcilar.add(uid)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 ÇEKİLİŞE KATIL", callback_data="cekilise_katil")]
    ])

    await query.edit_message_caption(
        caption=(
            "🔥 <b>BONUSSEMTİ ÇEKİLİŞİ</b>\n\n"
            f"🔥 <b>KATILIMCI SAYISI :</b> {len(cekilis_katilimcilar)}\n\n"
            "🏆 <b>Katılımcıların kanallarımızı ve botumuzu takip etmesi zorunludur!</b>\n\n"
            "🔥 https://t.me/Canli_Izleme_Mac_Linkleri\n"
            "🔥 https://t.me/plasespor\n"
            "🔥 https://t.me/bonussemti\n"
            "🔥 https://t.me/bonussemtietkinlik\n"
            "🔥 https://t.me/hergunikioran\n"
            "🔥 https://t.me/BahisKarhanesi\n"
            "🔥 https://t.me/ozel_oran_2024\n"
            "🔥 https://t.me/bonussemtii_bot"
        ),
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ================== /sayi ==================
async def sayi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_kazanan_sayisi

    if not await is_admin(update, context):
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Kullanım: /sayi 3")
        return

    cekilis_kazanan_sayisi = int(context.args[0])
    await update.message.reply_text(
        f"🎯 Kazanan sayısı {cekilis_kazanan_sayisi} olarak ayarlandı."
    )

# ================== MESAJ SAY ==================
async def mesaj_say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    if update.message.date.timestamp() < BOT_BASLANGIC_ZAMANI:
        return

    uid = update.message.from_user.id
    kullanici_mesaj_sayisi[uid] = kullanici_mesaj_sayisi.get(uid, 0) + 1

# ================== /mesaj ==================
async def mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global min_mesaj_sayisi

    if not await is_admin(update, context):
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Kullanım: /mesaj 200")
        return

    min_mesaj_sayisi = int(context.args[0])
    await update.message.reply_text(
        f"📝 Minimum mesaj şartı {min_mesaj_sayisi} olarak ayarlandı."
    )

# ================== KANAL KONTROL ==================
async def kanallari_kontrol_et_detayli(user_id, context):
    eksik = []

    for kanal in ZORUNLU_KANALLAR:
        try:
            uye = await context.bot.get_chat_member(kanal, user_id)
            if uye.status not in ["member", "administrator", "creator"]:
                eksik.append(kanal)
        except:
            eksik.append(kanal)

    return eksik

# ================== /bitir ==================
async def bitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_kazananlar

    if not await is_admin(update, context):
        return

    cekilis_aktif = False

    if not cekilis_katilimcilar:
        await update.message.reply_text("Katılım olmadığı için çekiliş tamamlanamadı.")
        return

    cekilis_kazananlar = random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi, len(cekilis_katilimcilar))
    )

    msg = "🏆 <b>ÇEKİLİŞ SONUCU</b>\n\n"

    for uid in cekilis_kazananlar:
        member = await context.bot.get_chat_member(update.effective_chat.id, uid)
        user = member.user
        msg += f"🎁 @{user.username}\n" if user.username else f"🎁 <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"

    await update.message.reply_text(msg, parse_mode="HTML")

# ================== /kontrol ==================
async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not cekilis_kazananlar:
        await update.message.reply_text("Kontrol edilecek kazanan bulunmamaktadır.")
        return

    msg = "📋 <b>KAZANAN KONTROL RAPORU</b>\n\n"

    for uid in cekilis_kazananlar:
        member = await context.bot.get_chat_member(update.effective_chat.id, uid)
        user = member.user

        isim = f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

        mesaj_sayi = kullanici_mesaj_sayisi.get(uid, 0)
        eksik_kanallar = await kanallari_kontrol_et_detayli(uid, context)

        msg += f"❌ {isim}\n"

        # Mesaj durumu
        if mesaj_sayi >= min_mesaj_sayisi:
            msg += (
                f"   📨 Mesaj durumu: "
                f"Gerekli mesaj sayısına ulaşılmıştır ({mesaj_sayi}).\n"
            )
        else:
            msg += (
                f"   📨 Mesaj durumu: "
                f"{mesaj_sayi} mesaj bulunuyor, "
                f"en az {min_mesaj_sayisi} mesaj gerekmektedir.\n"
            )

        # Kanal durumu
        if eksik_kanallar:
            msg += "   📢 Kanal durumu: Aşağıdaki kanallara katılım eksiktir:\n"
            for kanal in eksik_kanallar:
                msg += f"      • {kanal}\n"
        else:
            msg += "   📢 Kanal durumu: Tüm kanallara katılım sağlanmıştır.\n"

        msg += "\n"

    await update.message.reply_text(msg, parse_mode="HTML")







# --- Bot başlat ---
app = ApplicationBuilder().token(TOKEN).build()

# === KOMUTLAR ===
app.add_handler(CommandHandler("filter", add_filter))
app.add_handler(CommandHandler("remove", remove_filter))
app.add_handler(CommandHandler("lock", lock_channel))
app.add_handler(CommandHandler("unlock", unlock_channel))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(MessageHandler(tg_filters.Regex(r"^!sil \d+$"), sil))

app.add_handler(CommandHandler("cekilis", cekilis))
app.add_handler(CommandHandler("sayi", sayi))
app.add_handler(CommandHandler("mesaj", mesaj))
app.add_handler(CommandHandler("bitir", bitir))
app.add_handler(CommandHandler("kontrol", kontrol))
app.add_handler(CallbackQueryHandler(cekilis_buton, pattern="^cekilise_katil$"))

# ================== FİLTRELER (ÇOK ÖNEMLİ SIRA) ==================

# 1️⃣ KÜFÜR (EN ÖNCE)
app.add_handler(
    MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, kufur_kontrol),
    group=0
)

# 2️⃣ LİNK
app.add_handler(
    MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, link_engel),
    group=1
)

# 3️⃣ SPAM
app.add_handler(
    MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, spam_kontrol),
    group=2
)

# 4️⃣ MESAJ SAYACI (SADECE SAYAR, CEZA YOK)
app.add_handler(
    MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, mesaj_say),
    group=3
)

# 5️⃣ SİTE / REKLAM LİNKLERİ (EN SON)
app.add_handler(
    MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, check_message),
    group=4
)

if __name__ == "__main__":
    app.run_polling()


