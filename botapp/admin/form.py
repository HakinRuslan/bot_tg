from aiogram.fsm.state import StatesGroup, State

class AddCategory(StatesGroup):
    category_name = State()
    confirm_add = State()

class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    file_id = State()
    category_id = State()
    hidden_content = State()
    confirm_add = State()