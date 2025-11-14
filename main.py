from typing import Tuple

class CoffeeOrder:
    def __init__(
        self,
        base: str,
        size: str,
        milk: str = "none",
        syrups: Tuple[str, ...] = (),
        sugar: int = 0,
        iced: bool = False,
        price: float = 0.0,
        description: str = ""
    ):
        self.base = base
        self.size = size
        self.milk = milk
        self.syrups = syrups
        self.sugar = sugar
        self.iced = iced
        self.price = price
        self.description = description
    
    def __str__(self) -> str:
        if self.description:
            return self.description
        return f"Coffee order - {self.price:.2f}"


class CoffeeOrderBuilder:
    """
    Builder для создания заказа кофе с fluent интерфейсом.
    
    Правила:
    - base и size обязательны для build()
    - sugar: 0-5 чайных ложек
    - максимум 4 сиропа
    - дубликаты сиропов игнорируются
    
    Прайсинг:
    - Базовые цены: espresso=200, americano=250, latte=300, cappuccino=320
    - Множители размера: small=1.0, medium=1.2, large=1.4
    - Молоко: whole/skim=30, oat=60, soy=50, none=0
    - Сироп: 40 за каждый
    - Лед: 0.2 при iced=True
    """
    # Базовые цены
    BASE_PRICES = {
        "espresso": 200.0,
        "americano": 250.0,
        "latte": 300.0,
        "cappuccino": 320.0
    }
    
    # Множители размера
    SIZE_MULTIPLIERS = {
        "small": 1.0,
        "medium": 1.2,
        "large": 1.4
    }
    
    # Доплаты за молоко
    MILK_PRICES = {
        "none": 0.0,
        "whole": 30.0,
        "skim": 30.0,
        "oat": 60.0,
        "soy": 50.0
    }
    
    # Цена за сироп
    SYRUP_PRICE = 40.0
    
    # Цена за лед
    ICED_PRICE = 0.2
    
    # Лимиты
    MAX_SUGAR = 5
    MAX_SYRUPS = 4
    
    def __init__(self):
        self.base: str = ""
        self.size: str = ""
        self.milk: str = "none"
        self.syrups: list[str] = []
        self.sugar: int = 0
        self.iced: bool = False
    
    def set_base(self, base: str) -> "CoffeeOrderBuilder":
        self.base = base
        return self
    
    def set_size(self, size: str) -> "CoffeeOrderBuilder":
        self.size = size
        return self
    
    def set_milk(self, milk: str) -> "CoffeeOrderBuilder":
        self.milk = milk
        return self
    
    def add_syrup(self, name: str) -> "CoffeeOrderBuilder":
        if name not in self.syrups and len(self.syrups) < self.MAX_SYRUPS:
            self.syrups.append(name)
        return self
    
    def set_sugar(self, teaspoons: int) -> "CoffeeOrderBuilder":
        if teaspoons < 0 or teaspoons > self.MAX_SUGAR:
            raise ValueError(f"Sugar must be between 0 and {self.MAX_SUGAR}")
        self.sugar = teaspoons
        return self
    
    def set_iced(self, iced: bool = True) -> "CoffeeOrderBuilder":
        self.iced = iced
        return self
    
    def clear_extras(self) -> "CoffeeOrderBuilder":
        self.milk = "none"
        self.syrups = []
        self.sugar = 0
        self.iced = False
        return self
    
    def _calculate_price(self) -> float:
        if self.base not in self.BASE_PRICES:
            return 0.0
        
        base_price = self.BASE_PRICES[self.base]
        size_multiplier = self.SIZE_MULTIPLIERS.get(self.size, 1.0)
        
        price = base_price * size_multiplier
        
        # Добавляем молоко
        milk_price = self.MILK_PRICES.get(self.milk, 0.0)
        price += milk_price
        
        # Добавляем сиропы
        price += len(self.syrups) * self.SYRUP_PRICE
        
        # Добавляем лед
        if self.iced:
            price += self.ICED_PRICE
        
        return price
    
    def _build_description(self) -> str:  
        parts = []
        
        # Размер и база
        if self.size and self.base:
            parts.append(f"{self.size} {self.base}")
        
        # Молоко (если не none)
        if self.milk and self.milk != "none":
            parts.append(f"with {self.milk} milk")
        
        # Сиропы
        if self.syrups:
            syrup_str = ", ".join(self.syrups)
            parts.append(f"+{syrup_str}")
        
        # Лед
        if self.iced:
            parts.append("(iced)")
        
        # Сахар (если больше 0)
        if self.sugar > 0:
            parts.append(f"{self.sugar} tsp sugar")
        
        return " ".join(parts)
    
    def build(self) -> CoffeeOrder:
        if not self.base:
            raise ValueError("Base is required")
        if not self.size:
            raise ValueError("Size is required")
        
        price = self._calculate_price()
        description = self._build_description()
        
        return CoffeeOrder(
            base=self.base,
            size=self.size,
            milk=self.milk,
            syrups=tuple(self.syrups),
            sugar=self.sugar,
            iced=self.iced,
            price=price,
            description=description
        )


# ==================== ТЕСТЫ ====================

def test_basic_order():
    builder = CoffeeOrderBuilder()
    order = builder.set_base("latte").set_size("medium").set_milk("oat").add_syrup("vanilla").set_sugar(2).build()
    
    assert order.base == "latte"
    assert order.size == "medium"
    assert order.milk == "oat"
    assert "vanilla" in order.syrups
    assert order.sugar == 2
    assert isinstance(order.price, float)
    assert order.price > 0
    assert isinstance(order.description, str)
    assert len(order.description) > 0
    print("Базовый заказ: тест пройден")


def test_builder_reuse():
    builder = CoffeeOrderBuilder()
    
    order1 = builder.set_base("espresso").set_size("small").set_sugar(1).build()
    price1 = order1.price
    sugar1 = order1.sugar
    
    order2 = builder.set_size("large").set_sugar(3).build()
    price2 = order2.price
    sugar2 = order2.sugar
    
    assert order1.price == price1, "order1 не должен измениться"
    assert order1.sugar == sugar1, "order1 не должен измениться"
    assert order2.price != price1, "order2 должен отличаться"
    assert order2.sugar == 3, "order2 должен иметь новое значение сахара"
    assert order2.price > 0, "цена order2 должна быть валидной"
    print("Переиспользование билдера: тест пройден")


def test_validation_missing_base():
    builder = CoffeeOrderBuilder()
    builder.set_size("medium")
    
    try:
        builder.build()
        assert False, "Должен быть ValueError"
    except ValueError as e:
        assert "base" in str(e).lower() or "Base" in str(e)
        print("Валидация отсутствующего base: тест пройден")


def test_validation_missing_size():
    builder = CoffeeOrderBuilder()
    builder.set_base("latte")
    
    try:
        builder.build()
        assert False, "Должен быть ValueError"
    except ValueError as e:
        assert "size" in str(e).lower() or "Size" in str(e)
        print("Валидация отсутствующего size: тест пройден")


def test_validation_sugar_limit():
    builder = CoffeeOrderBuilder()
    
    try:
        builder.set_sugar(6)
        assert False, "Должен быть ValueError"
    except ValueError:
        print("Валидация лимита сахара: тест пройден")


def test_syrup_duplicates():
    builder = CoffeeOrderBuilder()
    order1 = builder.set_base("latte").set_size("medium").add_syrup("vanilla").add_syrup("vanilla").build()
    
    assert len(order1.syrups) == 1, "Дубликат сиропа не должен добавляться"
    
    builder2 = CoffeeOrderBuilder()
    order2 = builder2.set_base("latte").set_size("medium").add_syrup("vanilla").build()
    
    assert order1.price == order2.price, "Цена не должна меняться при дубликате"
    print("Дубликаты сиропов: тест пройден")


def test_iced_price():
    builder = CoffeeOrderBuilder()
    order_without_ice = builder.set_base("americano").set_size("small").set_iced(False).build()
    price_without_ice = order_without_ice.price
    
    builder2 = CoffeeOrderBuilder()
    order_with_ice = builder2.set_base("americano").set_size("small").set_iced(True).build()
    price_with_ice = order_with_ice.price
    
    assert price_with_ice > price_without_ice, "Лед должен добавлять доплату"
    assert abs(price_with_ice - price_without_ice - CoffeeOrderBuilder.ICED_PRICE) < 0.01, "Доплата за лед должна быть 0.2"
    print("Доплата за лед: тест пройден")


def test_max_syrups():
    builder = CoffeeOrderBuilder()
    builder.set_base("latte").set_size("medium")
    builder.add_syrup("vanilla").add_syrup("caramel").add_syrup("hazelnut").add_syrup("chocolate")
    
    # Пятый сироп не должен добавиться
    builder.add_syrup("cinnamon")
    order = builder.build()
    
    assert len(order.syrups) == 4, "Максимум 4 сиропа"
    print("Лимит сиропов: тест пройден")


def test_description_format():
    builder = CoffeeOrderBuilder()
    order = builder.set_base("cappuccino").set_size("large").set_milk("soy").add_syrup("vanilla").set_sugar(2).set_iced(True).build()
    
    desc = order.description
    assert "large" in desc
    assert "cappuccino" in desc
    assert "soy" in desc
    assert "vanilla" in desc
    assert "iced" in desc.lower()
    assert "2 tsp sugar" in desc or "2" in desc
    print("Формат описания: тест пройден")


def test_default_values():
    builder = CoffeeOrderBuilder()
    order = builder.set_base("espresso").set_size("small").build()
    
    assert order.milk == "none"
    assert len(order.syrups) == 0
    assert order.sugar == 0
    assert order.iced == False
    print("Значения по умолчанию: тест пройден")


def test_clear_extras():
    builder = CoffeeOrderBuilder()
    builder.set_base("latte").set_size("medium").set_milk("oat").add_syrup("vanilla").set_sugar(3).set_iced(True)
    builder.clear_extras()
    order = builder.build()
    
    assert order.milk == "none"
    assert len(order.syrups) == 0
    assert order.sugar == 0
    assert order.iced == False
    print("clear_extras: тест пройден")


if __name__ == "__main__":
    print("Запуск тестов...\n")
    
    test_basic_order()
    test_builder_reuse()
    test_validation_missing_base()
    test_validation_missing_size()
    test_validation_sugar_limit()
    test_syrup_duplicates()
    test_iced_price()
    test_max_syrups()
    test_description_format()
    test_default_values()
    test_clear_extras()
    
    print("\n🎉 Все тесты успешно пройдены!\n")
    