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