from pydantic import BaseModel, ConfigDict, Field

class ProductCategoryIDModel(BaseModel):
    id: int


# class ProductCategoryIDModel(BaseModel):
#     category_id: int

class CategoryModel(BaseModel):
    category_name: str = Field(..., min_length=5)

class ProductModel(BaseModel):
    name: str = Field(..., min_length=5)
    description: str = Field(..., min_length=5)
    price: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    file_id: str | None = None
    hidden_content: str = Field(..., min_length=5)



class PaymentData(BaseModel):
    user_id: int = Field(..., description="ID пользователя Telegram")
    payment_id: str = Field(..., max_length=255, description="Уникальный ID платежа")
    price: int = Field(..., description="Сумма платежа в рублях")
    product_id: int = Field(..., description="ID товара")