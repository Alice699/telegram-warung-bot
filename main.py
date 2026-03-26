import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)
from config import BOT_TOKEN
from handlers.start import start, help_command
from handlers.menu import show_menu, show_category
from handlers.order import (
    order_start, order_name, order_table, order_item,
    order_quantity, order_confirm, order_cancel,
    NAME, TABLE, ITEM, QUANTITY, CONFIRM
)
from handlers.status import my_orders, check_status
from handlers.admin import (
    admin_panel, admin_orders, admin_update_status,
    ADMIN_WAITING_STATUS
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # === ConversationHandler: Pesan baru ===
    order_conv = ConversationHandler(
        entry_points=[CommandHandler("pesan", order_start)],
        states={
            NAME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, order_name)],
            TABLE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, order_table)],
            ITEM:     [CallbackQueryHandler(order_item, pattern="^item_")],
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_quantity)],
            CONFIRM:  [CallbackQueryHandler(order_confirm, pattern="^(confirm|cancel)$")],
        },
        fallbacks=[CommandHandler("batal", order_cancel)],
    )

    # === ConversationHandler: Admin update status ===
    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_update_status, pattern="^update_")],
        states={
            ADMIN_WAITING_STATUS: [CallbackQueryHandler(admin_update_status, pattern="^set_status_")],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", show_menu))
    app.add_handler(CommandHandler("pesananku", my_orders))
    app.add_handler(CommandHandler("status", check_status))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("pesanan_masuk", admin_orders))
    app.add_handler(CallbackQueryHandler(show_category, pattern="^cat_"))
    app.add_handler(order_conv)
    app.add_handler(admin_conv)

    print("🤖 Warung Bot aktif! Tekan Ctrl+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()
