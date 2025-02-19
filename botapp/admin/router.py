import asyncio
from aiogram import Router, F
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

admin_router = Router()

@admin_router.callback_query(F.data == 'statistic', F.from_user.id.in_(ADMINS))
async def admin_statistic(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Запрос на получение статистики...')
    await call.answer('📊 Собираем статистику...')

    stats = await UserDAO.get_statistics(session=session_without_commit)
    total_summ = await PurchaseDao.get_full_summ(session=session_without_commit)
    stats_message = (
        "📈 Статистика пользователей:\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🆕 Новых за сегодня: {stats['new_today']}\n"
        f"📅 Новых за неделю: {stats['new_week']}\n"
        f"📆 Новых за месяц: {stats['new_month']}\n\n"
        f"💰 Общая сумма заказов: {total_summ} руб.\n\n"
        "🕒 Данные актуальны на текущий момент."
    )
    await call.message.edit_text(
        text=stats_message,
        reply_markup=admin_kb()
    )

@admin_router.callback_query(F.data == "admin_panel", F.from_user.id.in_(ADMINS))
async def start_admin(call: CallbackQuery):
    await call.answer('Доступ в админ-панель разрешен!')
    await call.message.edit_text(
        text="Вам разрешен доступ в админ-панель. Выберите необходимое действие.",
        reply_markup=admin_kb()
    )

@admin_router.callback_query(F.data == "cancel", F.from_user.id.in_(ADMINS))
async def admin_process_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отмена сценария добавления')
    await call.message.delete()
    await call.message.answer(
        text="Отмена добавления",
        reply_markup=admin_kb_back()
    )

@admin_router.callback_query(F.data == 'process_products', F.from_user.id.in_(ADMINS))
async def admin_process_products(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим управления')
    all_products_count = await ProductDao.count(session=session_without_commit)
    await call.message.edit_text(
        text=f"На данный момент в базе данных {all_products_count} товаров. what are u going to do with them?",
        reply_markup=product_management_kb()
    ) 


@admin_router.callback_query(F.data == 'process_category', F.from_user.id.in_(ADMINS))
async def admin_process_cats(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим управления')
    all_cats_count = await CategoryDao.count(session=session_without_commit)
    await call.message.edit_text(
        text=f"На данный момент в базе данных {all_cats_count} категорий. what are u going to do with them?",
        reply_markup=category_management_kb()
    )

@admin_router.callback_query(F.data == 'delete_cat', F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим удаления')
    all_cats = await CategoryDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text=f"На данный момент в базе данных {len(all_cats)} cats. Для удаления нажмите на кнопку ниже"
    )
    for product_data in all_cats:
        product_text = (f'🎁 <b>Название Категории:</b> <b>{product_data.category_name}</b>\n')
        await call.message.answer(text=product_text, reply_markup=dell_cat_kb(product_data.id))

@admin_router.callback_query(F.data.startswith('dell-cat'), F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(call.data.split('_')[-1])
    await CategoryDao.delete(session=session_with_commit, filters=ProductCategoryIDModel(id=product_id))
    await call.answer(f"Категория с ID {product_id} удален!", show_alert=True)
    await call.message.delete()

@admin_router.callback_query(F.data == 'add_cat', F.from_user.id.in_(ADMINS))
async def admin_process_add_cat(call: CallbackQuery, state: FSMContext):
    await call.answer('Запущен scenario addition cat.')
    await call.message.delete()
    msg = await call.message.answer(text="Укажите name for cat: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddCategory.category_name)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), AddCategory.category_name)
async def admin_process_name(message: Message, state: FSMContext):
    await state.update_data(category_name=message.text)
    cat_data = await state.get_data()
    print(cat_data)
    cat_text = (
        f'🛒 Проверьте, все ли корректно:\n\n'
        f'🎁 <b>Название Категории:</b> <b>{cat_data["category_name"]}</b>\n'
        )
    await process_dell_text_msg(message, state)
    msg = await message.answer(text=cat_text, reply_markup=admin_confirm_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddCategory.confirm_add)

@admin_router.callback_query(F.data == "confirm_add", F.from_user.id.in_(ADMINS), AddCategory.confirm_add)
async def admin_process_confirm_add(call: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    category_data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=category_data["last_msg_id"])
    del category_data["last_msg_id"]
    await CategoryDao.add(session=session_with_commit, values=CategoryModel(**category_data))
    await call.message.answer(text="Категория успешно добавлен в базу данных!", reply_markup=admin_kb())


@admin_router.callback_query(F.data == 'add_product', F.from_user.id.in_(ADMINS))
async def admin_process_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer('Запущен сценарий добавления товара.')
    await call.message.delete()
    msg = await call.message.answer(text="Для начала укажите имя товара: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.name)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), AddProduct.name)
async def admin_process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await process_dell_text_msg(message, state)
    msg = await message.answer(text="Теперь дайте короткое описание товару: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.description)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), AddProduct.description)
async def admin_process_description(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await state.update_data(description=message.html_text)
    await process_dell_text_msg(message, state)
    catalog_data = await CategoryDao.find_all(session=session_without_commit)
    msg = await message.answer(text="Теперь выберите категорию товара: ", reply_markup=catalog_admin_kb(catalog_data))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.category_id)


@admin_router.callback_query(F.data.startswith("add_category_"),
                             F.from_user.id.in_(ADMINS),
                             AddProduct.category_id)
async def admin_process_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split("_")[-1])
    await state.update_data(category_id=category_id)
    await call.answer('Категория товара успешно выбрана.')
    msg = await call.message.edit_text(text="Введите цену товара: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.price)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), AddProduct.price)
async def admin_process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await process_dell_text_msg(message, state)
        msg = await message.answer(
            text="Отправьте файл (документ), если требуется или нажмите на 'БЕЗ ФАЙЛА', если файл не требуется",
            reply_markup=admin_send_file_kb()
        )
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(AddProduct.file_id)
    except ValueError:
        await message.answer(text="Ошибка! Необходимо ввести числовое значение для цены.")
        return


@admin_router.callback_query(F.data == "without_file", F.from_user.id.in_(ADMINS), AddProduct.file_id)
async def admin_process_without_file(call: CallbackQuery, state: FSMContext):
    await state.update_data(file_id=None)
    await call.answer('Файл не выбран.')
    msg = await call.message.edit_text(
        text="Теперь отправьте контент, который отобразится после покупки товара внутри карточки",
        reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.hidden_content)


@admin_router.message(F.document, F.from_user.id.in_(ADMINS), AddProduct.file_id)
async def admin_process_without_file(message: Message, state: FSMContext):
    await state.update_data(file_id=message.document.file_id)
    await process_dell_text_msg(message, state)
    msg = await message.answer(
        text="Теперь отправьте контент, который отобразится после покупки товара внутри карточки",
        reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.hidden_content)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), AddProduct.hidden_content)
async def admin_process_hidden_content(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await state.update_data(hidden_content=message.html_text)

    product_data = await state.get_data()
    category_info = await CategoryDao.find_one_or_none_by_id(session=session_without_commit,
                                                             data_id=product_data.get("category_id"))

    file_id = product_data.get("file_id")
    file_text = "📦 Товар с файлом" if file_id else "📄 Товар без файла"

    product_text = (f'🛒 Проверьте, все ли корректно:\n\n'
                    f'🔹 <b>Название товара:</b> <b>{product_data["name"]}</b>\n'
                    f'🔹 <b>Описание:</b>\n\n<b>{product_data["description"]}</b>\n\n'
                    f'🔹 <b>Цена:</b> <b>{product_data["price"]} ₽</b>\n'
                    f'🔹 <b>Описание (закрытое):</b>\n\n<b>{product_data["hidden_content"]}</b>\n\n'
                    f'🔹 <b>Категория:</b> <b>{category_info.category_name} (ID: {category_info.id})</b>\n\n'
                    f'<b>{file_text}</b>')
    await process_dell_text_msg(message, state)

    if file_id:
        msg = await message.answer_document(document=file_id, caption=product_text, reply_markup=admin_confirm_kb())
    else:
        msg = await message.answer(text=product_text, reply_markup=admin_confirm_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.confirm_add)


@admin_router.callback_query(F.data == "confirm_add", F.from_user.id.in_(ADMINS), AddProduct.confirm_add)
async def admin_process_confirm_add(call: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    await call.answer('Приступаю к сохранению файла!')
    product_data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=product_data["last_msg_id"])
    del product_data["last_msg_id"]
    await ProductDao.add(session=session_with_commit, values=ProductModel(**product_data))
    await call.message.answer(text="Товар успешно добавлен в базу данных!", reply_markup=admin_kb())

@admin_router.callback_query(F.data == 'delete_product', F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим удаления')
    all_products = await ProductDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text=f"На данный момент в базе данных {len(all_products)} товаров. Для удаления нажмите на кнопку ниже"
    )

    for product_data in all_products:
        file_id = product_data.file_id
        file_text = "📦 Товар с файлом" if file_id else "📄 Товар без файла"

        product_text = (f'🛒 Описание товара:\n\n'
                        f'🔹 <b>Название товара:</b> <b>{product_data.name}</b>\n'
                        f'🔹 <b>Описание:</b>\n\n<b>{product_data.description}</b>\n\n'
                        f'🔹 <b>Цена:</b> <b>{product_data.price} ₽</b>\n'
                        f'🔹 <b>Описание (закрытое):</b>\n\n<b>{product_data.hidden_content}</b>\n\n'
                        f'<b>{file_text}</b>')
        if file_id:
            await call.message.answer_document(document=file_id, caption=product_text,
                                               reply_markup=dell_product_kb(product_data.id))
        else:
            await call.message.answer(text=product_text, reply_markup=dell_product_kb(product_data.id))

@admin_router.callback_query(F.data.startswith('dell-prod'), F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(call.data.split('_')[-1])
    await ProductDao.delete(session=session_with_commit, filters=ProductCategoryIDModel(id=product_id))
    await call.answer(f"Товар с ID {product_id} удален!", show_alert=True)
    await call.message.delete()
