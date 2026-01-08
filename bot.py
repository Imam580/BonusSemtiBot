import os
import random
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

load_dotenv()
TOKEN = os.environ.get("TOKEN")

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
        chat_member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
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

# --- /filtre komutu ---
async def show_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Sadece yönetici kullanabilir!")
        return
    if not filters_dict:
        await update.message.reply_text("❌ Filtre yok!")
        return
    msg = "\n".join([f"{k} → {v}" for k, v in filters_dict.items()])
    await update.message.reply_text(f"🔹 Filtreler:\n{msg}")

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
async def delete_messages_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Yetkin yok")
        return
    args = update.message.text.split()
    if len(args) != 2:
        await update.message.reply_text("❌ Kullanım: !sil 10")
        return
    try:
        count = int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Kullanım: !sil 10")
        return
    for i in range(count):
        try:
            await context.bot.delete_message(update.effective_chat.id, update.message.message_id - i)
        except:
            pass
    await update.message.reply_text(f"🧹 {count} mesaj silindi!")

# --- Mesaj filtreleme ---
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        text = update.message.text.lower()
        for key, value in filters_dict.items():
            if key in text:
                await update.message.reply_text(value)
# ================== ÇEKİLİŞ SİSTEMİ ==================
# ================== ÇEKİLİŞ SİSTEMİ (BUTONLU) ==================
cekilis_aktif = False
cekilis_katilimcilar = set()
cekilis_kazanan_sayisi = 1


async def cekilis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif, cekilis_katilimcilar
    if not await is_admin(update, context):
        return

    cekilis_aktif = True
    cekilis_katilimcilar.clear()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 Çekilişe Katıl", callback_data="cekilis_katil")]
    ])

    await update.message.reply_text(
        "🎁 ÇEKİLİŞ BAŞLADI!\n\nKatılmak için aşağıdaki butona bas 👇",
        reply_markup=keyboard
    )


async def cekilis_buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not cekilis_aktif:
        await query.reply_text("❌ Çekiliş aktif değil")
        return

    cekilis_katilimcilar.add(query.from_user.id)
    await query.reply_text("✅ Çekilişe katıldın!")


async def sayi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_kazanan_sayisi
    if not await is_admin(update, context):
        return

    cekilis_kazanan_sayisi = int(context.args[0])
    await update.message.reply_text(f"🎯 {cekilis_kazanan_sayisi} kazanan seçilecek")


async def bitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cekilis_aktif
    if not await is_admin(update, context):
        return

    cekilis_aktif = False

    if not cekilis_katilimcilar:
        await update.message.reply_text("❌ Katılım yok")
        return

    kazananlar = random.sample(
        list(cekilis_katilimcilar),
        min(cekilis_kazanan_sayisi, len(cekilis_katilimcilar))
    )

    msg = "🏆 KAZANANLAR:\n"
    for uid in kazananlar:
        msg += f"👤 <a href='tg://user?id={uid}'>Kazanan</a>\n"

    await update.message.reply_text(msg, parse_mode="HTML")





# --- Bot başlat ---
app = ApplicationBuilder().token(TOKEN).build()

# --- ADMIN KOMUTLARI ---
app.add_handler(CommandHandler("filter", add_filter))
app.add_handler(CommandHandler("filtre", show_filters))
app.add_handler(CommandHandler("remove", remove_filter))
app.add_handler(CommandHandler("lock", lock_channel))
app.add_handler(CommandHandler("unlock", unlock_channel))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))

# --- MESAJ SİL ---
app.add_handler(
    MessageHandler(tg_filters.TEXT & tg_filters.Regex(r"^!sil \d+$"), delete_messages_cmd),
    group=0
# === ÇEKİLİŞ KOMUTLARI (ADMIN) ===
app.add_handler(CommandHandler("cekilis", cekilis), group=1)
app.add_handler(CommandHandler("sayi", sayi), group=1)
app.add_handler(CommandHandler("bitir", bitir), group=1)

# === ÇEKİLİŞE KATILIM (BUTON) ===
app.add_handler(
    CallbackQueryHandler(cekilis_buton, pattern="^cekilis_katil$")
)


# === LİNK FİLTRE (EN SON ÇALIŞACAK) ===
app.add_handler(
    MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, check_message),
    group=3
)


if __name__ == "__main__":
    app.run_polling()


