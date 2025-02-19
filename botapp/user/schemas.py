from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UserBaseInDB(BaseModel):
    telegram_id: int

    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(from_attributes=True)


class User(UserBaseInDB):
    username: str
    first_name: str
    last_name: Optional[str] = None


class ProductIDModel(BaseModel):
    id: int


class ProductCategoryIDModel(BaseModel):
    category_id: int


class PaymentData(BaseModel):
    user_id: int = Field(..., description="ID пользователя Telegram")
    payment_id: str = Field(..., max_length=255, description="Уникальный ID платежа")
    price: int = Field(..., description="Сумма платежа в рублях")
    product_id: int = Field(..., description="ID товара")
 