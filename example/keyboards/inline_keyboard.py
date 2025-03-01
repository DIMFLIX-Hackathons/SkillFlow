from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

choose_mode = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text="перевести предложения по теме",
                             callback_data="translate_practice")
    ],[
        InlineKeyboardButton(text="режим диалога с ИИ",
                             callback_data="dialog_with_AI")
    ],[
        InlineKeyboardButton(text="проверка произношения",
                             callback_data="check_speech")
    ]]
)