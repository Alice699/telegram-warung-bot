from telegram import Update
from telegram.ext import ContextTypes
from database import get_orders_by_user, get_order_detail

STATUS_EMOJI = {
    "pending":   "⏳ Menunggu",
    "preparing": "🍳 Sedang Dimasak",
    "ready":     "✅ Siap Diambil",
    "done":      "🎉 Selesai",
    "cancelled": "❌ Dibatalkan",
}

def format_price(price: float) -> str:
    return f"Rp {int(price):,}".replace(",", ".")

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = get_orders_by_user(update.effective_user.id)
    if not orders:
        await update.message.reply_text("📭 Kamu belum punya pesanan. Ketik /pesan untuk mulai!")
        return

    text = "📋 *5 Pesanan Terakhirmu:*\n\n"
    for o in orders:
        status = STATUS_EMOJI.get(o["status"], o["status"])
        text += (
            f"🆔 `#{o['id']}` — {status}\n"
            f"   👤 {o['customer_name']} | 💰 {format_price(o['total_price'])}\n"
            f"   🕐 {o['created_at'][:16]}\n\n"
        )
    text += "Cek detail: `/status <id>`"
    await update.message.reply_text(text, parse_mode="Markdown")

async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❓ Gunakan: `/status <id_pesanan>`\nContoh: `/status 3`", parse_mode="Markdown")
        return

    try:
        order_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID pesanan harus berupa angka.")
        return

    detail = get_order_detail(order_id)
    if not detail:
        await update.message.reply_text("❌ Pesanan tidak ditemukan.")
        return

    status = STATUS_EMOJI.get(detail["status"], detail["status"])
    items_text = "\n".join(
        f"  • {i['item_name']} x{i['quantity']} = {format_price(i['subtotal'])}"
        for i in detail["items"]
    )
    table = f"Meja {detail['table_number']}" if detail["table_number"] else "Takeaway 🥡"

    await update.message.reply_text(
        f"📦 *Detail Pesanan #{order_id}*\n"
        f"{'─' * 28}\n"
        f"👤 {detail['customer_name']} | 🪑 {table}\n"
        f"📊 Status: {status}\n\n"
        f"{items_text}\n\n"
        f"💰 *Total: {format_price(detail['total_price'])}*\n"
        f"🕐 {detail['created_at'][:16]}",
        parse_mode="Markdown"
    )
