from aiogram.types import InlineKeyboardButton

to_start_menu_btn = InlineKeyboardButton(
    text="В главное меню", callback_data="start_menu"
)

ai_dialog_text = InlineKeyboardButton(
    text="Текстовый диалог", callback_data="text_dialog"
)
ai_dialog_real = InlineKeyboardButton(
    text="Реальный диалог", callback_data="real_dialog"
)
