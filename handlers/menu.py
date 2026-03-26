from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_categories, get_menu_by_category, get_all_menu

def format_price(price: float) -> str:
    return f"Rp {int(price):,}".replace(",", ".")

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = get_categories()
    keyboard = [[InlineKeyboardButton(f"📂 {cat}", callback_data=f"cat_{cat}")] for cat in categories]
    keyboard.append([InlineKeyboardButton("📋 Semua Menu", callback_data="cat_all")])

    await update.message.reply_text(
        "🍽️ *Pilih Kategori Menu:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cat = query.data.replace("cat_", "")
    items = get_all_menu() if cat == "all" else get_menu_by_category(cat)

    if not items:
        await query.edit_message_text("❌ Menu tidak tersedia saat ini.")
        return

    title = "📋 *Semua Menu*" if cat == "all" else f"📂 *Kategori: {cat}*"
    text = f"{title}\n{'─' * 28}\n\n"

    current_cat = ""
    for item in items:
        if cat == "all" and item["category"] != current_cat:
            current_cat = item["category"]
            text += f"*── {current_cat} ──*\n"
        emoji = item.get("emoji", "🍽️")
        text += (
            f"{emoji} *{item['name']}*\n"
            f"   {item.get('description', '')}\n"
            f"   💰 {format_price(item['price'])}\n\n"
        )

    text += "━━━━━━━━━━━━━━\n"
    text += "Ketik /pesan untuk memesan! 🛒"

    await query.edit_message_text(text, parse_mode="Markdown")
