from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def kb_client():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("Menu 🔥")
    b2 = KeyboardButton("Restaurants near 🥰")
    b3 = KeyboardButton("Support 😐")
    b4 = KeyboardButton("Add Food")

    kb.add(b1).add(b2)
    kb.insert(b3).insert(b4)
    return kb

def kb_fsm_cancel():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('Cancel')

    kb.add(b1)
    return kb
