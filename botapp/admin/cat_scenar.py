import asyncio
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from conf import *
from bot import bot
from user.user import UserDAO
from .kb import *
from .schemas import *
from db.models.models.manager import ProductDao, CategoryDao, PurchaseDao
from .utils import process_dell_text_msg
from .form import *
from .router import admin_router

@admin_router.callback_query(F.data == 'delete_cat', F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим удаления товаров')
    all_products = await CategoryDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text=f"На данный момент в базе данных {len(all_products)} cats. Для удаления нажмите на кнопку ниже"
    )
    for product_data in all_products:
        product_text = (f'🎁 <b>Название Категории:</b> <b>{product_data.category_name}</b>\n')
        await call.message.answer(text=product_text, reply_markup=dell_product_kb(product_data.id))

@admin_router.callback_query(F.data.startswith('dell_'), F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(call.data.split('_')[-1])
    await ProductDao.delete(session=session_with_commit, filters=ProductCategoryIDModel(id=product_id))
    await call.answer(f"Товар с ID {product_id} удален!", show_alert=True)
    await call.message.delete()

@admin_router.callback_query(F.data == 'add_cat', F.from_user.id.in_(ADMINS))
async def admin_process_add_product(call: CallbackQuery, state: FSMContext):
    print("!!!!")
    await call.answer('Запущен scenario addition cat.')
    await call.message.delete()
    msg = await call.message.answer(text="Укажите name for cat: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddCategory.category_name)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), AddCategory.category_name)
async def admin_process_name(message: Message, state: FSMContext):
    await state.update_data(category_name=message.text)
    cat_data = await state.get_data()
    cat_text = (
        f'🛒 Проверьте, все ли корректно:\n\n'
        f'🎁 <b>Название Категории:</b> <b>{cat_data.category_name}</b>\n'
        )
    await process_dell_text_msg(message, state)
    msg = await message.answer(text=cat_text, reply_markup=admin_confirm_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.confirm_add)

@admin_router.callback_query(F.data == "confirm_add", F.from_user.id.in_(ADMINS))
async def admin_process_confirm_add(call: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    await call.answer('Приступаю к сохранению файла!')
    product_data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=product_data["last_msg_id"])
    del product_data["last_msg_id"]
    await CategoryDao.add(session=session_with_commit, values=CategoryModel(**product_data))
    await call.message.answer(text="Товар успешно добавлен в базу данных!", reply_markup=admin_kb())


# @admin_router.message(F.text, F.from_user.id.in_(settings.ADMIN_IDS), AddProduct.description)
# async def admin_process_description(message: Message, state: FSMContext, session_without_commit: AsyncSession):
#     await state.update_data(description=message.html_text)
#     await process_dell_text_msg(message, state)
#     catalog_data = await CategoryDao.find_all(session=session_without_commit)
#     msg = await message.answer(text="Теперь выберите категорию товара: ", reply_markup=catalog_admin_kb(catalog_data))
#     await state.update_data(last_msg_id=msg.message_id)
#     await state.set_state(AddProduct.category_id)


# @admin_router.callback_query(F.data.startswith("add_category_"),
#                              F.from_user.id.in_(settings.ADMIN_IDS),
#                              AddProduct.category_id)
# async def admin_process_category(call: CallbackQuery, state: FSMContext):
#     category_id = int(call.data.split("_")[-1])
#     await state.update_data(category_id=category_id)
#     await call.answer('Категория товара успешно выбрана.')
#     msg = await call.message.edit_text(text="Введите цену товара: ", reply_markup=cancel_kb_inline())
#     await state.update_data(last_msg_id=msg.message_id)
#     await state.set_state(AddProduct.price)


# @admin_router.message(F.text, F.from_user.id.in_(settings.ADMIN_IDS), AddProduct.price)
# async def admin_process_price(message: Message, state: FSMContext):
#     try:
#         price = int(message.text)
#         await state.update_data(price=price)
#         await process_dell_text_msg(message, state)
#         msg = await message.answer(
#             text="Отправьте файл (документ), если требуется или нажмите на 'БЕЗ ФАЙЛА', если файл не требуется",
#             reply_markup=admin_send_file_kb()
#         )
#         await state.update_data(last_msg_id=msg.message_id)
#         await state.set_state(AddProduct.file_id)
#     except ValueError:
#         await message.answer(text="Ошибка! Необходимо ввести числовое значение для цены.")
#         return


# @admin_router.callback_query(F.data == "without_file", F.from_user.id.in_(settings.ADMIN_IDS), AddProduct.file_id)
# async def admin_process_without_file(call: CallbackQuery, state: FSMContext):
#     await state.update_data(file_id=None)
#     await call.answer('Файл не выбран.')
#     msg = await call.message.edit_text(
#         text="Теперь отправьте контент, который отобразится после покупки товара внутри карточки",
#         reply_markup=cancel_kb_inline())
#     await state.update_data(last_msg_id=msg.message_id)
#     await state.set_state(AddProduct.hidden_content)


# @admin_router.message(F.document, F.from_user.id.in_(settings.ADMIN_IDS), AddProduct.file_id)
# async def admin_process_without_file(message: Message, state: FSMContext):
#     await state.update_data(file_id=message.document.file_id)
#     await process_dell_text_msg(message, state)
#     msg = await message.answer(
#         text="Теперь отправьте контент, который отобразится после покупки товара внутри карточки",
#         reply_markup=cancel_kb_inline())
#     await state.update_data(last_msg_id=msg.message_id)
#     await state.set_state(AddProduct.hidden_content)


# @admin_router.message(F.text, F.from_user.id.in_(settings.ADMIN_IDS), AddProduct.hidden_content)
# async def admin_process_hidden_content(message: Message, state: FSMContext, session_without_commit: AsyncSession):
#     await state.update_data(hidden_content=message.html_text)

#     product_data = await state.get_data()
#     category_info = await CategoryDao.find_one_or_none_by_id(session=session_without_commit,
#                                                              data_id=product_data.get("category_id"))

#     file_id = product_data.get("file_id")
#     file_text = "📦 Товар с файлом" if file_id else "📄 Товар без файла"

#     product_text = (f'🛒 Проверьте, все ли корректно:\n\n'
#                     f'🔹 <b>Название товара:</b> <b>{product_data["name"]}</b>\n'
#                     f'🔹 <b>Описание:</b>\n\n<b>{product_data["description"]}</b>\n\n'
#                     f'🔹 <b>Цена:</b> <b>{product_data["price"]} ₽</b>\n'
#                     f'🔹 <b>Описание (закрытое):</b>\n\n<b>{product_data["hidden_content"]}</b>\n\n'
#                     f'🔹 <b>Категория:</b> <b>{category_info.category_name} (ID: {category_info.id})</b>\n\n'
#                     f'<b>{file_text}</b>')
#     await process_dell_text_msg(message, state)

#     if file_id:
#         msg = await message.answer_document(document=file_id, caption=product_text, reply_markup=admin_confirm_kb())
#     else:
#         msg = await message.answer(text=product_text, reply_markup=admin_confirm_kb())
#     await state.update_data(last_msg_id=msg.message_id)
#     await state.set_state(AddProduct.confirm_add)