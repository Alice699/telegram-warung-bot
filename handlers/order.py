from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_all_menu, get_menu_item, create_order

# States
NAME, TABLE, ITEM, QUANTITY, CONFIRM = range(5)

def format_price(price: float) -> str:
    return f"Rp {int(price):,}".replace(",", ".")

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["cart"] = []
    await update.message.reply_text(
        "🛒 *Mulai Pemesanan!*\n\n"
        "Siapa nama pemesan? (ketik nama kamu)",
        parse_mode="Markdown"
    )
    return NAME

async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["customer_name"] = update.message.text.strip()
    await update.message.reply_text(
        f"Halo, *{context.user_data['customer_name']}!* 👋\n\n"
        "Di meja berapa? (ketik angka, atau ketik `0` kalau takeaway)",
        parse_mode="Markdown"
    )
    return TABLE

async def order_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        table = int(update.message.text.strip())
        context.user_data["table_number"] = table if table > 0 else None
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka nomor meja ya!")
        return TABLE

    return await show_item_picker(update, context)

async def show_item_picker(update_or_query, context: ContextTypes.DEFAULT_TYPE, edit=False):
    items = get_all_menu()
    keyboard = []
    for item in items:
        emoji = item.get("emoji", "🍽️")
        label = f"{emoji} {item['name']} — {format_price(item['price'])}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"item_{item['id']}")])
    keyboard.append([InlineKeyboardButton("✅ Selesai Pesan", callback_data="item_done")])

    cart = context.user_data.get("cart", [])
    cart_text = ""
    if cart:
        cart_text = "\n\n🛒 *Keranjang:*\n"
        total = 0
        for c in cart:
            subtotal = c["price"] * c["qty"]
            total += subtotal
            cart_text += f"• {c['name']} x{c['qty']} = {format_price(subtotal)}\n"
        cart_text += f"\n💰 *Total: {format_price(total)}*"

    text = "🍽️ *Pilih Menu:*" + cart_text

    if edit and hasattr(update_or_query, "edit_message_text"):
        await update_or_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        msg = update_or_query.message if hasattr(update_or_query, "message") else update_or_query
        await msg.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return ITEM

async def order_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "item_done":
        if not context.user_data.get("cart"):
            await query.answer("Keranjang masih kosong!", show_alert=True)
            return ITEM
        return await show_confirmation(query, context)

    item_id = int(query.data.replace("item_", ""))
    context.user_data["selected_item_id"] = item_id
    item = get_menu_item(item_id)

    await query.edit_message_text(
        f"{item['emoji']} *{item['name']}*\n"
        f"💰 {format_price(item['price'])}\n\n"
        "Berapa porsi yang kamu inginkan?",
        parse_mode="Markdown"
    )
    return QUANTITY

async def order_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        qty = int(update.message.text.strip())
        if qty <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka jumlah yang valid!")
        return QUANTITY

    item_id = context.user_data["selected_item_id"]
    item = get_menu_item(item_id)

    # Update or add to cart
    cart = context.user_data["cart"]
    for c in cart:
        if c["id"] == item_id:
            c["qty"] += qty
            break
    else:
        cart.append({"id": item_id, "name": item["name"], "price": item["price"], "qty": qty})

    await update.message.reply_text(
        f"✅ *{item['name']} x{qty}* ditambahkan ke keranjang!\n\nMau tambah lagi?",
        parse_mode="Markdown"
    )
    return await show_item_picker(update, context)

async def show_confirmation(query, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data["cart"]
    name = context.user_data["customer_name"]
    table = context.user_data.get("table_number")
    table_text = f"Meja {table}" if table else "Takeaway 🥡"

    total = sum(c["price"] * c["qty"] for c in cart)
    lines = "\n".join(
        f"• {c['name']} x{c['qty']} = {f'Rp {int(c[\"price\"] * c[\"qty\"]):,}'.replace(',', '.')}"
        for c in cart
    )

    text = (
        f"📋 *Konfirmasi Pesanan*\n"
        f"{'─' * 28}\n"
        f"👤 Nama: *{name}*\n"
        f"🪑 {table_text}\n\n"
        f"{lines}\n\n"
        f"💰 *Total: {f'Rp {int(total):,}'.replace(',', '.')}*\n\n"
        f"Konfirmasi pesanan?"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Ya, Pesan!", callback_data="confirm"),
            InlineKeyboardButton("❌ Batal", callback_data="cancel"),
        ]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM

async def order_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ Pesanan dibatalkan. Ketik /pesan untuk mulai lagi.")
        return ConversationHandler.END

    cart = context.user_data["cart"]
    items = [(c["id"], c["qty"]) for c in cart]

    try:
        order_id, total = create_order(
            telegram_id=update.effective_user.id,
            customer_name=context.user_data["customer_name"],
            table_number=context.user_data.get("table_number"),
            items=items
        )
        await query.edit_message_text(
            f"🎉 *Pesanan Berhasil Dibuat!*\n\n"
            f"📌 ID Pesanan: `#{order_id}`\n"
            f"💰 Total: {f'Rp {int(total):,}'.replace(',', '.')}\n\n"
            f"Status pesananmu bisa dicek dengan:\n"
            f"`/status {order_id}`\n\n"
            f"Terima kasih! Pesananmu sedang diproses 🍳",
            parse_mode="Markdown"
        )
    except Exception as e:
        await query.edit_message_text(f"❌ Gagal membuat pesanan: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def order_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Pemesanan dibatalkan. Ketik /pesan untuk mulai lagi.")
    return ConversationHandler.END
