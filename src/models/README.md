В SQLAlchemy существует несколько стратегий загрузки связанных объектов, и термин "lazy" (ленивая загрузка) относится к
одной из них. Вот основные стратегии загрузки:

Lazy (ленивая загрузка): Связанные объекты загружаются только тогда, когда они фактически запрашиваются. Это означает,
что первый доступ к связанному объекту вызовет отдельный запрос к базе данных для его загрузки. Это поведение по
умолчанию для большинства отношений.

Eager (нетерпеливая загрузка):

joinedload: Связанные объекты загружаются с использованием соединения (JOIN) в одном запросе с основным объектом. Это
приводит к более сложному SQL-запросу, но уменьшает количество запросов.
selectinload: Связанные объекты загружаются в отдельном запросе, который выполняется сразу после основного запроса.
SQLAlchemy автоматически оптимизирует эти запросы, чтобы минимизировать их количество. Это вариант нетерпеливой
загрузки, который эффективно справляется с задачами, где требуется загрузить связанные объекты.
Subqueryload: Связанные объекты загружаются с использованием подзапросов (subqueries). Это похоже на joinedload, но
SQLAlchemy использует подзапрос для загрузки связанных данных.

Теперь, почему lazy="selectin" относится к ленивой загрузке:

Lazy (ленивая) загрузка: означает, что связанные объекты загружаются только по мере необходимости, а не сразу с основным
объектом. Это позволяет отложить выполнение дополнительных запросов до тех пор, пока данные не будут действительно
нужны.

**selectinload: это оптимизированная форма ленивой загрузки, где связанные объекты загружаются в отдельном запросе, но
сразу после основного запроса. Это позволяет минимизировать количество запросов, необходимых для загрузки связанных
данных, при этом сохраняя преимущества ленивой загрузки, такие как отложенное выполнение.**

Поэтому lazy="selectin" называется ленивой загрузкой, потому что она сохраняет основную идею ленивой загрузки (загрузка
по мере необходимости), но делает это более эффективно, чем обычная ленивая загрузка (где каждый доступ к связанному
объекту вызывает отдельный запрос).

seconadry - это название таблицы
back_populates - это название поля в связанной таблице (relationship)

**Использование uselist=False в отношениях "Один-к-одному"
Если отношения между вашими таблицами должны быть "Один-к-одному", убедитесь, что вы используете uselist=False в relationship.**


**Если появляется ошибка при попытке связать таблицы, то можно попробовать использовать `lazy='selectin` для relationship**
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place?
```
https://www.reddit.com/r/FastAPI/comments/17nnxa0/need_help_fastapi_and_sqlalchemy_issue_with/?rdt=49810
прочитать: https://medium.com/@vickypalaniappan12/relationship-loading-techniques-in-sqlalchemy-4e7d1ff96f75

**ATTENTION: `lazy='selectin` может вызвать рекурсию -> заменить на `lazy='select`
Ошибка появляется когда Pydantic модель состоит из других моделей, одновременно связанных с помощью `lazy='selectin`**

Если в M -> M связи используется кол-во, то нужно строить связь не напрямую, а через промежуточную таблицу (пример Cocktails -> Carts)
```python
class Cart(Base):
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Ассоциация с таблицей User (1 cart -> 1 user)
    user = relationship("User", back_populates="cart", lazy="selectin")
    # Ассоциация с таблицей Cocktail через `cart_items` (M carts -> M cocktails)
    cart_items = relationship(
        "CartItem", back_populates="cart", lazy="selectin"
    )

    def to_dict(self):
        return {"id": self.id, "user_id": self.user, "cocktails": self.cart_items}


class CartItem(Base):
    __tablename__ = "cart_items"
    cart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("carts.id"), primary_key=True)
    cocktail_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cocktails.id"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationship with Cart (M cart_items -> 1 cart)
    cart = relationship("Cart", back_populates="cart_items")

    # Relationship with Cocktail (M cart_items -> 1 cocktail)
    cocktail = relationship("Cocktail", lazy="selectin")
```

# TCF
## Cart Logic
Логика работы
**Создание корзины**
При первом добавлении товара проверяется наличие Cart со статусом DRAFT

Если нет — создаётся новая

**Добавление товаров**
Добавление в CartOffer с cart_id

Если offer_id уже есть — увеличивается количество

**Оформление заказа**
Меняется статус корзины: Cart.status = ORDERED

По корзине создаётся Order (через серверный экшн)

Создаётся новая пустая Cart со статусом DRAFT
