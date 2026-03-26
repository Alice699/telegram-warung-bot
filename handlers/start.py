from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import WARUNG_NAME
from database import init_db

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_db()
    name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🍛 Lihat Menu", callback_data="cat_all")],
        [InlineKeyboardButton("📋 Pesanan Saya", callback_data="my_orders")],
    ]
    await update.message.reply_text(
        f"Halo, *{name}!* 👋\n\n"
        f"Selamat datang di *{WARUNG_NAME}* 🍜\n\n"
        "Apa yang bisa kami bantu?\n\n"
        "📌 *Perintah tersedia:*\n"
        "/menu — Lihat daftar menu\n"
        "/pesan — Buat pesanan baru\n"
        "/pesananku — Riwayat pesananmu\n"
        "/status — Cek status pesanan\n"
        "/help — Bantuan",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Panduan Warung Bot*\n\n"
        "🛒 *Pemesanan:*\n"
        "  /pesan — Mulai pesan makanan\n"
        "  /batal — Batalkan pesanan yang sedang dibuat\n\n"
        "📋 *Riwayat:*\n"
        "  /pesananku — Lihat 5 pesanan terakhirmu\n"
        "  /status `<id>` — Cek status pesanan tertentu\n\n"
        "🍽️ *Menu:*\n"
        "  /menu — Lihat semua menu\n\n"
        "👑 *Admin:*\n"
        "  /admin — Panel admin\n"
        "  /pesanan_masuk — Lihat pesanan masuk\n\n"
        "_Dibuat dengan ❤️ dari Palembang 🇮🇩_",
        parse_mode="Markdown"
    )
