from db.basemodel.basedao import *
from ..ormmodels.models import *


class CategoryDao(BaseDAO[Category]):
    model = Category

class ProductDao(BaseDAO[Product]):
    model = Product


class PurchaseDao(BaseDAO[Product]):
    model = Purchase

    @classmethod
    async def get_full_summ(cls, session: AsyncSession) -> int:
        """Получить общую сумму покупок."""
        query = select(func.sum(cls.model.price).label('total_price'))
        result = await session.execute(query)
        total_price = result.scalars().one_or_none()
        return total_price if total_price is not None else 0