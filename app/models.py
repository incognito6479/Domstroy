from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.db.models.fields import DateField
from django.db.models.functions import ExtractMonth
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from app.validators import validate_phone

from mptt.models import MPTTModel, TreeForeignKey


class Action(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Page(MPTTModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Permission(models.Model):
    user = models.ForeignKey('app.Staff', on_delete=models.PROTECT)
    page = models.ManyToManyField('app.Page', blank=True, null=True, related_name='permission_page')
    action = models.ManyToManyField('app.Action', blank=True, null=True, related_name='permission_action')

    def __str__(self):
        return f"{self.user}"


# class CounterParty(models.Model):
#     name = models.CharField(max_length=255)
#     phone = models.CharField(max_length=255, blank=True, null=True)
#     address = models.CharField(max_length=500, blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    branch = models.ForeignKey('app.Branch', on_delete=models.PROTECT)
    client = models.ForeignKey('app.Client', on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.client}"


class OrderItem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('app.Order', on_delete=models.PROTECT)
    product = models.ForeignKey('app.Product', on_delete=models.PROTECT)
    count = models.FloatField(default=0)
    price = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def __str__(self):
        return f"{self.product} | {self.count}"


class Staff(AbstractUser):
    """Xodimlar"""
    class StaffTypeChoices(models.TextChoices):
        CEO = "ceo"
        DIRECTOR = "Direktor"
        MANAGER = "Menejer"
        FINANCIER = 'Moliyachi'
        HEAD_OF_BRANCH = "Filial boshlig'i"
        DELIVER = "Yetkazib beruvchi"
        SELLER = "Sotuvchi"
        CASHIER = "Kassir"
        PROVIDER = "Ta'minotchi"
        SELLER_WITH_CASHIER = "Sotuvchi kassir"
        WAREHOUSEMAN = "Omborchi"
        BAG = "Qopchi"

    STATUS = (
        ('active', 'active'),
        ('inactive', 'inactive'),
    )
    # Relationships
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey("app.Section", on_delete=models.CASCADE, null=True, blank=True)
    # Only for Providers (Provider can work with multiple branch at a time)
    branches = models.ManyToManyField("app.Branch", related_name='providers')

    # Fields
    fathers_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True, validators=[validate_phone])
    role = models.CharField(max_length=35, choices=StaffTypeChoices.choices, null=True, blank=True)
    salary = models.FloatField(default=0)
    status = models.CharField(max_length=10, choices=STATUS, default=STATUS[0][0],
                              null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.id} - {self.branch.name if self.branch else ''} - {self.role}"

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(Staff, self).save(*args, **kwargs)

    def get_seller_shop(self):
        return self.shop_seller.all()

    @property
    def get_cash_sum(self):
        return sum([item.cash_sum for item in self.shop_seller.all()])

    @property
    def get_loan_sum(self):
        return sum([item.loan_sum for item in self.shop_seller.all()])

    @property
    def get_loan_dollar(self):
        return sum([item.loan_dollar for item in self.shop_seller.all()])

    @property
    def get_cash_dollar(self):
        return sum([item.cash_dollar for item in self.shop_seller.all()])

    @property
    def get_card(self):
        return sum([item.card for item in self.shop_seller.all()])

    @property
    def get_transfer(self):
        return sum([item.transfer for item in self.shop_seller.all()])


class StaffSalary(models.Model):
    """Xodim ish haqi, bonus, ushlamalar, qarzlar"""

    # Relationships
    staff = models.ForeignKey("app.Staff", on_delete=models.CASCADE)

    # Fields
    payment_delay = models.FloatField(default=0)
    loan = models.FloatField(default=0)
    bonus = models.FloatField(default=0)
    comment = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class BonusProduct(models.Model):
    """Bonusga kelgan tovarlar"""

    # Relationships
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    cost = models.FloatField(default=0)
    amount = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class DiscountCard(models.Model):
    """Chegirma karta"""

    card = models.CharField(max_length=20, unique=True)
    bonus_dollar = models.FloatField(default=0)
    bonus_sum = models.FloatField(default=0)
    percentage = models.SmallIntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


# class DiscountCartItem(models.Model):
#     """
#      bu model savdo oynasida cart item da skidka kiritib ketishda
#     """
#     cart_item = models.ForeignKey("CartItem", on_delete=models.CASCADE, related_name="discount_cart_item")
#     percent = models.FloatField(default=0)


class CartItem(models.Model):
    """Sotuv qilishdagi savatdagi tovar"""

    # Relationships
    cart = models.ForeignKey("app.Cart", on_delete=models.CASCADE)
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    percent = models.SmallIntegerField(default=0)
    expire_date = models.DateField(null=True, blank=True)
    is_bonus = models.BooleanField(default=False)
    commit = models.CharField(max_length=250, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.cart.id)

    @property
    def selling_price(self):
        if self.cart.shop:
            branch = self.cart.shop.branch
            pro_through_branch = ProductThroughBranch.objects.filter(product=self.product,
                                                                     branch=branch).first()
            return pro_through_branch.selling_price
        return 0

    @property
    def total_summa(self):
        return self.amount * self.selling_price

    @property
    def total_ball(self):
        return self.amount * self.product.ball


class ReturnPrice(models.Model):
    """Maxsulot qaytim narxi"""
    class Currency(models.TextChoices):
        SUM = "sum"
        DOLLAR = "dollar"

    cart_item = models.ForeignKey(CartItem, models.CASCADE, related_name="return_price")
    price = models.FloatField(default=0)
    currency = models.CharField(max_length=20, choices=Currency.choices, default=Currency.SUM, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.pk)


class Cart(models.Model):
    """Sotuv qilishdagi savatcha"""

    STATUS = (
        ('processing', 'processing'),
        ('waiting_loading', 'waiting_loading'),
        ('finished', 'finished')
    )

    # Relationships
    shop = models.OneToOneField("app.Shop", on_delete=models.CASCADE, blank=True, null=True)

    # Fields
    status = models.CharField(max_length=15, choices=STATUS, default=STATUS[0][0])
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Shop(models.Model):
    """Savdo"""

    # Relationships
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE)
    seller = models.ForeignKey("app.Staff", on_delete=models.CASCADE, related_name="shop_seller")
    client = models.ForeignKey("app.Client", null=True, blank=True, on_delete=models.CASCADE)
    section = models.ForeignKey("app.Section", null=True, blank=True, on_delete=models.CASCADE)

    # Fields
    check_number = models.IntegerField(default=0)
    traded_at = models.DateTimeField()
    card = models.FloatField(default=0)
    loan_sum = models.FloatField(default=0)
    cash_sum = models.FloatField(default=0)
    discount_sum = models.FloatField(default=0)
    loan_dollar = models.FloatField(default=0)
    discount_dollar = models.FloatField(default=0)
    transfer = models.FloatField(default=0)
    cash_dollar = models.FloatField(default=0)
    change_sum = models.FloatField(default=0)
    change_dollar = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk) if self.pk else "None"

    def __repr__(self):
        return str(self.pk) if self.pk else "None"

    @property
    def total_summa(self):
        return sum([item.total_summa for item in self.cart.cartitem_set.all()])

    @property
    def total_sum(self):
        return sum([item.total_summa for item in self.cart.cartitem_set.filter(
            product__currency='sum')])

    @property
    def total_dollar(self):
        return sum([item.total_summa for item in self.cart.cartitem_set.filter(
            product__currency='dollar')])

    @property
    def total_ball(self):
        return sum([item.total_ball for item in self.cart.cartitem_set.all()])

    # @property
    # def get_total_summ_for_accountant(self):
    # queryset = self.objects.filter(branch_id=branch)


class ProductRequestItem(models.Model):
    """Otkaz tovarlar soni"""
    # Relationships
    product_request = models.ForeignKey("app.ProductRequest", on_delete=models.CASCADE)
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    expire_date = models.DateField(null=True, blank=True)
    selling_price = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class ProductRequest(models.Model):
    """Otkaz: Tovar uchun so'rov yuborish"""

    # Relationships
    STATUS = (
        ('requested', 'request'),
        ('accepted', 'accepted'),
        ('finished', 'finished'),
        ('rejected', 'rejected'),
    )

    # Relationships
    from_branch = models.ForeignKey("app.Branch", models.CASCADE, "sended_from_branch")
    to_branch = models.ForeignKey("app.Branch", models.CASCADE, "recieved_to_branch",
                                  null=True, blank=True)
    created_by = models.ForeignKey("app.Staff", models.CASCADE, "created_product_request")
    reviewed_by = models.ForeignKey("app.Staff", models.CASCADE, "reviewed_product_request",
                                    null=True, blank=True)

    # Fields
    status = models.CharField(max_length=30, choices=STATUS, default=STATUS[0][0])
    comment = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class ProductMoveBranchItem(models.Model):
    """Filialdan filialga ko'chiriladigan tovar"""

    # Relationships
    productmovegroup = models.ForeignKey("app.ProductMoveBranchGroup",
                                         on_delete=models.CASCADE,
                                         related_name="items")
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    expire_date = models.DateField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)

    @property
    def get_summa(self):
        return self.amount * self.selling_price


class ProductMoveBranchGroup(models.Model):
    """Bir guruh tovarlarni filialdan filialga ko'chirish. Avval guruh create qilib,
       shu guruhga ko'chiriladigan tovarlar qo'shiladi"""

    STATUS = (
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
    )

    # Relationships
    from_branch = models.ForeignKey("app.Branch", models.CASCADE, "move_from_branch")
    to_branch = models.ForeignKey("app.Branch", models.CASCADE, "move_to_branch")
    created_by = models.ForeignKey("app.Staff", models.CASCADE, "created_product_move")
    reviewed_by = models.ForeignKey("app.Staff", models.CASCADE, "reviewed_product_move",
                                    null=True, blank=True)

    # Fields
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=55, choices=STATUS, default=STATUS[0][0])

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def summa_sum(self):
        summa = 0
        for item in self.items.all():
            if item.product.currency == 'sum':
                summa += item.amount * item.selling_price  # or item.selling_price
        return summa

    def summa_dollar(self):
        summa = 0
        for item in self.items.all():
            if item.product.currency == 'dollar':
                summa += item.amount * item.selling_price  # or item.selling_price
        return summa


class PriceType(models.Model):
    """
    bu model tovar prixod chiqim uchun, tovar prixoda avval nima uchun chiqim qilingani yozib qo'yiladi
    """

    title = models.CharField(max_length=255)
    deliver = models.ForeignKey("Deliver", on_delete=models.CASCADE, related_name="price_type_deliver", null=True,
                                blank=True)
    client = models.ForeignKey("Client", on_delete=models.CASCADE, related_name="price_type_client", null=True,
                               blank=True)

    def __str__(self):
        return self.title


class ProductReceipt(models.Model):
    """ Tovar prixod. Prixod qilingan tovarlar haqidagi malumotlar
        shu table da saqlab boriladi """

    STATUS = (
        ("processing", "processing"),
        ('saved', 'saved'),
        ('accepted', 'accepted'),
        ("rejected", "rejected")
    )
    # Relationships
    # from_branch = models.ForeignKey("app.Branch", models.CASCADE,
    #                                 "reciepts_from_branch", null=True, blank=True)
    # to_branch = models.ForeignKey("app.Branch", models.CASCADE, "reciepts_to_branch", null=True, blank=True)
    staff = models.ForeignKey("app.Staff", models.CASCADE, "reciepts", null=True, blank=True)
    deliver = models.ForeignKey("app.Deliver", on_delete=models.CASCADE, related_name="deliver_reciepts", null=True,
                                blank=True)
    currency = models.ForeignKey("Currency", on_delete=models.CASCADE, related_name="receipt_currency", null=True,
                                 blank=True)
    price_type = models.ForeignKey(PriceType, on_delete=models.CASCADE, related_name="receipt_price_type", null=True,
                                   blank=True)
    warehouse = models.ForeignKey("Warehouse", on_delete=models.CASCADE, related_name="warehouse", null=True,
                                  blank=True)
    # Fields
    name = models.CharField(max_length=150)
    comment = models.CharField(max_length=1024)
    status = models.CharField(max_length=55, choices=STATUS, default=STATUS[0][0])
    sum_currency = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    @property
    def summa_sum_selling_price(self):
        summa = 0
        for item in self.items.all():
            if item.product.currency == 'sum':
                summa += item.amount * item.selling_price  # or item.selling_price
        return summa

    @property
    def summa_dollar_selling_price(self):
        summa = 0
        for item in self.items.all():
            if item.product.currency == 'dollar':
                summa += item.amount * item.selling_price  # or item.selling_price
        return summa

    @property
    def summa_sum_arrival_price(self):
        summa = 0
        for item in self.items.all():
            if item.product.currency == "sum":
                summa += item.amount * item.cost
        return summa

    @property
    def summa_dollar_arrival_price(self):
        summa = 0
        for item in self.items.all():
            if item.product.currency == "dollar":
                summa += item.amount * item.cost
        return summa


class DiscountProductReceipt(models.Model):
    """
    Chegirma tovarlar kirimi
    """
    class Currency(models.TextChoices):
        SUM = "sum"
        DOLLAR = "dollar"

    receipt = models.ForeignKey(ProductReceipt, on_delete=models.CASCADE, related_name="discount_receipt")
    percent = models.FloatField(default=0, null=True, blank=True)
    summ = models.FloatField(default=0, null=True, blank=True)
    dollar = models.FloatField(default=0, null=True, blank=True)
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.SUM)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pk


class ProductReceiptItem(models.Model):
    """
    tovarlar kirimi soni
    """

    # Relationships
    receipt = models.ForeignKey("app.ProductReceipt",
                                on_delete=models.CASCADE,
                                related_name="items")
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    comment = models.CharField(max_length=1024)
    is_bonus = models.BooleanField(default=False)
    percent = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)

    @property
    def get_summa(self):
        return self.amount * self.cost


class BrokenProduct(models.Model):
    """Hisobdan chiqqaamountn tovarlar"""
    STATUS = (
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected')
    )

    # Relationships
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE)
    section = models.ForeignKey("app.Section", on_delete=models.CASCADE,
                                null=True, blank=True)
    created_by = models.ForeignKey("app.Staff", on_delete=models.CASCADE,
                                   related_name='added_broken_product')
    reviewed_by = models.ForeignKey("app.Staff", on_delete=models.CASCADE,
                                    related_name='approved_broken_product', null=True, blank=True)

    # Fields
    comment = models.CharField(max_length=255)
    broken_date = models.DateField(auto_now_add=True, editable=False)
    amount = models.IntegerField(default=0)
    expire_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=55, choices=STATUS, default=STATUS[0][0])

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    @property
    def get_selling_price(self):
        return sum(i.selling_price for i in self.product.productthroughbranch_set.filter(product_id=self.product_id))

    def __str__(self):
        return str(self.pk)


class ProviderInvoice(models.Model):
    """Ta'minotchi fakturasi"""

    STATUS = (
        ('preparing', 'preparing'),
        ('finished', 'finished')
    )

    # Relationships
    deliver = models.ForeignKey("app.Deliver", models.CASCADE, "invoices")
    to_branch = models.ForeignKey("app.Branch", models.CASCADE, "provider_invoices")
    created_by = models.ForeignKey("app.Staff", models.CASCADE, "invoices")

    # Fields
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=55, choices=STATUS, default=STATUS[0][0])
    delivery_date = DateField()
    comment = models.CharField(max_length=1024)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # def summa_sum(self):
    #     summa = 0
    #     for item in self.items.all():
    #         if item.product.currency == 'sum':
    #             summa += item.amount*item.product.cost # or item.selling_price
    #     return summa

    # def summa_dollar(self):
    #     summa = 0
    #     for item in self.items.all():
    #         if item.product.currency == 'dollar':
    #             summa += item.amount*item.product.cost # or item.selling_price
    #     return summa


class ProviderInvoiceItem(models.Model):
    """Ta'minotchi fakturasidagi tovarlar"""

    # Relationships
    invoice = models.ForeignKey("app.ProviderInvoice", on_delete=models.CASCADE,
                                related_name="items")
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    expire_date = models.DateField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Minimal(models.Model):
    """Tovarni oyiga minimal miqdor bo'lishi"""

    MONTH = (
        ("january", "Yanvar"),
        ("february", "Fevral"),
        ("march", "Mart"),
        ("april", "Aprel"),
        ("may", "May"),
        ("june", "Iyun"),
        ("july", "Iyul"),
        ("august", "Avgust"),
        ("september", "Sentyabr"),
        ("october", "Oktyabr"),
        ("november", "Noyabr"),
        ("december", "Dekabr"),
    )
    # Relationships
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    month = models.CharField(max_length=30, choices=MONTH)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ['product', 'month']

    def __str__(self):
        return str(self.pk)


class Client(models.Model):
    TYPE = (
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
    )

    # Relationships
    discount_card = models.ForeignKey("app.DiscountCard",
                                      on_delete=models.CASCADE, blank=True, null=True)
    # Fields
    type = models.CharField(max_length=25, choices=TYPE)
    phone_1 = models.CharField(max_length=20, validators=[validate_phone])
    phone_2 = models.CharField(max_length=20, null=True, blank=True, validators=[validate_phone])
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    loan_sum = models.FloatField(default=0)  # overall loan in sum
    loan_dollar = models.FloatField(default=0)  # overall loan in dollar
    return_date = models.DateField(null=True, blank=True)  # deadline to pay loan
    ball = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)

    @property
    def full_name(self):
        return self.first_name + self.last_name


class ClientLoan(models.Model):
    """ Client Loans from Branchs """
    client = models.ForeignKey("app.Client", on_delete=models.CASCADE, related_name="client_loan")
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE, related_name='branch_loan')
    loan_sum = models.FloatField(default=0)
    loan_dollar = models.FloatField(default=0)
    return_date = models.DateField()  # deadline to pay loan
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    # staff which has sold product for loan (not required)
    staff = models.ForeignKey("app.Staff", on_delete=models.CASCADE,
                              null=True, blank=True)

    def __str__(self):
        return f"{self.client} - {self.branch}"

    class Meta:
        unique_together = ['client', 'branch']


class InventoryInvoice(models.Model):
    STATUS = (
        ('created', 'Jarayonda'),
        ('closed', 'Tugatildi'),
    )
    # Relationships
    branch = models.ForeignKey("app.Branch", on_delete=models.DO_NOTHING)
    controller = models.ForeignKey("app.Staff", on_delete=models.DO_NOTHING, null=True, blank=True)

    # Fields
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0])

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.status == self.STATUS[1][0]:
            for inventory_item in self.inventoryitem_set.all():
                product = inventory_item.product
                product.amount = inventory_item.real_amount
                product.save()
        super().save(force_insert, force_update, using, update_fields)


class InventoryItem(models.Model):
    """Reviziya, Inventarizatsiya - computerdagi va realdagi tovar miqdorini solishtirish"""

    # Relationships
    product = models.ForeignKey("app.Product", on_delete=models.DO_NOTHING)
    inventory = models.ForeignKey("app.InventoryInvoice", on_delete=models.DO_NOTHING)

    # Fields
    real_amount = models.FloatField(default=0)
    in_program_amount = models.FloatField(default=0)

    difference_sum = models.FloatField(default=0)
    difference_dollar = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class ClientPaymentHistory(models.Model):
    """Klient to'lovlar tarixi"""

    # Relationships
    client = models.ForeignKey("app.Client", on_delete=models.CASCADE)
    staff = models.ForeignKey("app.Staff", on_delete=models.CASCADE)
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE,
                               null=True, blank=True)

    # Fields
    paid_at = models.DateTimeField()
    card = models.FloatField(default=0)
    cash_sum = models.FloatField(default=0)
    cash_dollar = models.FloatField(default=0)
    discount_sum = models.FloatField(default=0)
    discount_dollar = models.FloatField(default=0)
    transfer = models.FloatField(default=0)
    from_ball = models.FloatField(default=0)
    comment = models.TextField(max_length=500, null=True, blank=True)
    payment_for_loan = models.BooleanField(default=False)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class ClientReturn(models.Model):
    """Klient qaytarib kelgan tovar savati"""
    STATUS = (
        ('processing', 'processing'),
        ('finished', 'finished')
    )
    # Relationships
    client = models.ForeignKey("app.Client", on_delete=models.CASCADE,
                               null=True, blank=True)
    staff = models.ForeignKey("app.Staff", on_delete=models.CASCADE)
    cart = models.ForeignKey("app.Cart", on_delete=models.CASCADE)
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE)
    section = models.ForeignKey("app.Section", on_delete=models.CASCADE,
                                null=True, blank=True)

    # Fields
    comment = models.CharField(max_length=1024, blank=True, null=True)
    return_date = models.DateField(null=True)
    took_date = models.DateField(null=True)
    status = models.CharField(max_length=15, choices=STATUS, default=STATUS[0][0])

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)

    @property
    def total_sum(self):
        total = 0
        for item in self.clientreturnitem_set.filter(product__currency='sum'):
            pro_through_branch = ProductThroughBranch.objects.get(
                product=item.product, branch=self.branch
            )
            total += item.amount * pro_through_branch.selling_price
        return total

    @property
    def total_dollar(self):
        total = 0
        for item in self.clientreturnitem_set.filter(product__currency='dollar'):
            pro_through_branch = ProductThroughBranch.objects.get(
                product=item.product, branch=self.branch
            )
            total += item.amount * pro_through_branch.selling_price
        return total


class ClientReturnItem(models.Model):
    """Klient qaytarib kelgan tovar savatidagi tovar"""

    # Relationships
    return_cart = models.ForeignKey("app.ClientReturn", on_delete=models.CASCADE)
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    comment = models.CharField(max_length=1024, blank=True, null=True)
    amount = models.FloatField(default=0)
    expire_date = models.DateField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Producer(models.Model):
    """Ishlab chiqaruvchi"""
    TYPE_OF_BRANCH = (
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
    )
    type = models.CharField(max_length=25, choices=TYPE_OF_BRANCH)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Barcode(models.Model):
    barcode = models.CharField(max_length=255)

    def __str__(self):
        return self.barcode


class Product(models.Model):
    """Mahsulot"""

    class Type(models.TextChoices):
        PRODUCT = "product"
        SERVICE = "service"

    MEASUREMENT = (
        ('dona', 'dona'),
        ('kg', 'kg'),
        ('litr', 'litr'),
        ('metr', 'metr')
    )
    CURRENCY = (
        ('sum', 'sum'),
        ('dollar', 'dollar'),
    )

    # Relationships
    section = models.ForeignKey("app.Section", null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey("app.Category", null=True, blank=True, on_delete=models.CASCADE)
    deliver = models.ForeignKey("app.Deliver", null=True, blank=True, on_delete=models.CASCADE,
                                related_name="deliver_product")
    branch = models.ManyToManyField("app.Branch", through='ProductThroughBranch',
                                    through_fields=('product', 'branch'))
    producer = models.ForeignKey("app.Producer", null=True, blank=True, on_delete=models.CASCADE,
                                 related_name="product_producer")
    warehouse = models.ForeignKey("Warehouse", on_delete=models.CASCADE, related_name="product_warehouse", null=True,
                                  blank=True)
    # Fields
    type = models.CharField(max_length=50, choices=Type.choices, default=Type.PRODUCT, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    currency = models.CharField(max_length=15, choices=CURRENCY)
    name = models.CharField(max_length=255)
    ball = models.IntegerField(null=True, blank=True, default=0)
    measurement = models.CharField(max_length=25, choices=MEASUREMENT)
    cost = models.FloatField(default=0)
    barcode = models.ManyToManyField(Barcode, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.name)

    @property
    def amount(self):  # branchdagi productlar soni
        all_amount = 0
        if not (branch_product := self.productthroughbranch_set.first()):
            return all_amount
        for meta in branch_product.product_meta.filter(product_through_branch=branch_product, amount__gt=0):
            all_amount += meta.amount
        return all_amount

    @property
    def monthly_minimal_amout(self):
        current_month = datetime.today().strftime("%B").lower()
        minimal_amount = Minimal.objects.filter(product_id=self.id, month=current_month).first()
        if minimal_amount:
            return minimal_amount.amount
        else:
            return "Minimal miqdor yo'q"


class ProductThroughBranch(models.Model):
    """ Filialga tegishli tovar status bilan """

    STATUS = (
        ('tugagan', 'tugagan'),
        ('kam qolgan', 'kam qolgan'),
        ('yetarli', 'yetarli'),
    )

    # Relationships
    product = models.ForeignKey('app.Product', on_delete=models.CASCADE)
    branch = models.ForeignKey('app.Branch', on_delete=models.CASCADE)

    # Fields
    selling_price = models.FloatField(default=0)
    status = models.CharField(max_length=25, default=STATUS[0][0], blank=True, choices=STATUS)
    normative = models.IntegerField(default=0, verbose_name="Normativ kun")
    is_valid = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ['product', 'branch']
        verbose_name = "Filialdagi mahsulot"
        verbose_name_plural = "Filialdagi mahsulotlar"

    def __str__(self):
        return str(self.product.name)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        current_month = datetime.today().strftime("%B").lower()
        current_minimal = self.product.minimal_set.filter(month=current_month).first()
        all_amount = self.get_amount
        if current_minimal:
            if all_amount == 0:
                self.status = "tugagan"
            elif all_amount <= current_minimal.amount:
                self.status = "kam qolgan"
            elif all_amount > current_minimal.amount:
                self.status = "yetarli"
            else:
                self.status = ""
            self.product.save()
        super().save(force_insert, force_update, using, update_fields)

    @property
    def get_amount(self):
        all_amount = 0
        for meta in self.product_meta.filter(product_through_branch=self, amount__gt=0):
            all_amount += meta.amount
        return all_amount

    def get_minus_amount(self, amount, id):
        for meta in self.product_meta.filter(product_through_branch_id=id):
            if amount > meta.amount:
                return None
            else:
                meta.amount -= amount
                meta.save()

        return self.get_amount

    @property
    def get_cost(self):
        """
            Kirim narxi
        """
        return float(self.product.cost)

    @property
    def mod_amount(self):
        """
            Qoldiq dona
        """
        amount = self.get_amount
        cart_item_amount = sum([i.amount for i in CartItem.objects.filter(product_id=self.product.id)])
        if int(amount - cart_item_amount) <= 0:
            return 0
        else:
            return int(amount - cart_item_amount)

    @property
    def daily_selling_amount(self):
        """
            O'rtacha kunlik savdo
        """
        from datetime import datetime
        cart_item = CartItem.objects.annotate(
            month=ExtractMonth('created_at')).values('month').annotate(
            count=Sum('amount')).get(product_id=self.id)
        current_day = datetime.now().day
        if cart_item is None:
            return 1
        elif int(cart_item['count'] / current_day) == 0:
            return 1
        else:
            return int(cart_item['count'] / current_day)

    def total_mode_sum(self):
        """
            Umumiy qoldiq sum
        """
        product_mod_amount = self.mod_amount
        cost = self.get_cost
        return round(float(product_mod_amount * cost), 2)

    @property
    def mod_day(self):
        """
            Qoldiq kun
        """
        product_mod_amount = self.mod_amount
        daily_selling_amount = self.daily_selling_amount
        if daily_selling_amount <= 0 or daily_selling_amount >= 0:
            daily_selling_amount = 1
        else:
            daily_selling_amount = self.daily_selling_amount

        return int(product_mod_amount / daily_selling_amount)

    @property
    def total_income_daily(self):
        """
            Yalpi daromad kunlik
        """
        selling_price = self.selling_price
        daily_selling_amount = self.daily_selling_amount
        cost = self.get_cost
        return round(float((selling_price - cost) * daily_selling_amount), 2)

    @property
    def total_income_in_percent(self):
        """
            Yalpi daromad ulushlar
        """
        # product_total_income = sum([i.total_income_daily for i in app.models.ProductThroughBranch.objects.all()])
        all_product_through_branch = ProductThroughBranch.objects.all()
        product_total_income_list = []
        for i in all_product_through_branch:
            try:
                c = i.total_income_daily
                product_total_income_list.append(c)
            except:
                c = 0
                product_total_income_list.append(c)
        product_total_income = sum(product_total_income_list)
        total_income_daily = self.total_income_daily
        if round(float((total_income_daily / product_total_income) * 100), 2):
            return round(float((total_income_daily / product_total_income) * 100), 2)
        else:
            return 0

    @property
    def margin(self):
        """
            Marja
        """
        selling_price = self.selling_price
        cost = self.get_cost
        if selling_price <= 0:
            return 0
        return round(float((selling_price - cost) / selling_price), 2)

    @property
    def ustama(self):
        """
            Ustama
        """
        selling_price = self.selling_price
        cost = self.get_cost
        if cost <= 0:
            return 0
        return round(float((selling_price - cost) / cost), 2)

    @property
    def oos_lost(self):
        """
            OOS sababli yo'qotish
        """
        mod_day = self.mod_day
        normativ_day = self.normative
        total_income_daily = self.total_income_daily
        return round(float((mod_day - normativ_day) * total_income_daily), 2)

    @property
    def frozen_cash(self):
        """
            Muzlatilgan pul
        """
        mod_day = self.mod_day
        normativ_day = self.normative
        daily_selling_amount = self.daily_selling_amount
        cost = self.get_cost
        if cost == 0:
            return 0
        return round(float((mod_day - normativ_day) * daily_selling_amount * cost), 2)


class ProductMeta(models.Model):
    """Tovar soni va yaroqlilik muddati"""

    # Relationships
    product_through_branch = models.ForeignKey("app.ProductThroughBranch", on_delete=models.CASCADE,
                                               related_name="product_meta")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_meta", null=True)
    # Fields
    amount = models.FloatField(default=0)
    cost = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # class Meta:
    #     unique_together = ['product_through_branch', 'expire_date']

    def __str__(self):
        return str(self.pk)


class InvoiceItem(models.Model):
    """Fakturaga ichidagi tovar"""

    STATUS = (
        ('preparing', 'preparing'),
        ('send', 'send'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
    )

    # Relationships
    invoice = models.ForeignKey("app.Invoice", on_delete=models.CASCADE)
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    expire_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=55, choices=STATUS, default=STATUS[0][0])

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)

    @property
    def get_summa(self):
        return self.amount * self.selling_price


class Invoice(models.Model):
    """Faktura"""

    STATUS = (
        ('preparing', 'preparing'),
        ('send', 'send'),
        ('accepted', 'accepted'),
        ('cancelled', 'cancelled'),
    )

    # Relationships
    from_branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE, related_name="from_branch",
                                    null=True, blank=True)
    to_branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE, related_name="to_branch",
                                  null=True, blank=True)
    section = models.ForeignKey("app.Section", on_delete=models.CASCADE, null=True, blank=True)
    staff = models.ForeignKey("app.Staff", on_delete=models.CASCADE)
    deliver = models.ForeignKey("app.Deliver", on_delete=models.CASCADE, null=True, blank=True)

    # Fields
    expense = models.FloatField(default=0)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=55, choices=STATUS, default=STATUS[0][0])

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     if self.status == self.STATUS[2][0]:
    #         for invoiceitem in self.invoiceitem_set.all():
    #             product = invoiceitem.product
    #             product_meta, created = ProductMeta.objects.get_or_create(
    #                 product=product,
    #                 expire_date=invoiceitem.expire_date
    #             )
    #             product_meta.amout = invoiceitem.product
    #             product_meta.save()
    #
    #             products_meta = product.productmeta_set.filter(expire_date=invoiceitem.expire_date)
    #             for product_meta in products_meta:
    #                 product_meta.amount += invoiceitem.amount
    #                 product_meta.save()
    #
    #     super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return str(self.name)

    @property
    def get_product_count(self):
        return self.invoiceitem_set.count()

    @property
    def summa_sum(self):
        sum_ = 0
        for item in self.invoiceitem_set.filter(product__currency=Product.CURRENCY[0][1]):
            sum_ += item.amount * item.selling_price
        return sum_

    @property
    def summa_dollar(self):
        dollar = 0
        for item in self.invoiceitem_set.filter(product__currency=Product.CURRENCY[1][1]):
            dollar += item.amount * item.selling_price
        return dollar


class ReturnDeliverProduct(models.Model):
    """Yetkazib beruvchiga qaytarilgan tovarlar"""

    # Relationships
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)
    deliver = models.ForeignKey("app.Deliver", on_delete=models.CASCADE,
                                related_name='returned_products')
    from_branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE,
                                    related_name="returnings")
    staff = models.ForeignKey("app.Staff", on_delete=models.CASCADE)

    # Fields
    comment = models.CharField(max_length=200)
    amount = models.IntegerField()
    cost = models.FloatField(default=0)
    expire_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)

    def overall_summa(self):
        return self.amount * self.cost


class Currency(models.Model):
    """Valyuta"""

    # Fields
    real_currency = models.FloatField(default=0)
    selling_currency = models.FloatField(default=0)
    ball_price = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Branch(models.Model):
    """Filial"""

    TYPE_OF_BRANCH = (
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
    )

    # Fields
    type_of_branch = models.CharField(max_length=25, choices=TYPE_OF_BRANCH)
    address = models.CharField(max_length=100)
    name = models.CharField(max_length=50)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"

    def __str__(self):
        return str(self.name)

    def get_section_count(self):
        return self.section_set.count()

    def get_total_branch_shop_sum(self):
        shop = self.shop_set.filter()
        total_sum = []
        for i in shop:
            total_sum.append(i.cash_sum)
        return sum(total_sum)

    def get_total_branch_created_at(self):
        return [[i.created_at.strftime('%Y/%m/%d %H:%M:%S'), i.cash_sum] for i in
                self.shop_set.filter(branch__type_of_branch='b2b')]
        # return [[i.cash_sum] for i in self.shop_set.all()]

    def get_total_branch_shop_dollar(self):
        shop = self.shop_set.filter()
        total_dollar = []
        for i in shop:
            total_dollar.append(i.cash_dollar)
        return sum(total_dollar)

    def get_total_branch_shop_card(self):
        shop = self.shop_set.filter()
        total_card = []
        for i in shop:
            total_card.append(i.card)
        return sum(total_card)

    def get_total_branch_shop_transfer(self):
        shop = self.shop_set.filter()
        total_transfer = []
        for i in shop:
            total_transfer.append(i.transfer)
        return sum(total_transfer)

    def get_total_branch_shop_loan_sum(self):
        shop = self.shop_set.filter()
        total_loan_sum = []
        for i in shop:
            total_loan_sum.append(i.loan_sum)
        return sum(total_loan_sum)

    def get_total_branch_shop_loan_dollar(self):
        shop = self.shop_set.filter()
        total_loan_dollar = []
        for i in shop:
            total_loan_dollar.append(i.loan_dollar)
        return sum(total_loan_dollar)

    def get_total_sum_client_return(self):
        client_returns = self.clientreturn_set.filter()
        cart_id_list = []
        product_list = []
        for client_return in client_returns:
            cart_id_list.append(client_return.cart.id)

        cart_list = Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='sum')
        for cart in cart_list:
            for cartitem in cart.cartitem_set.all():
                product_list.append(cartitem.product)

        a = []
        for i in product_list:
            for item in i.productthroughbranch_set.all():
                a.append(item.selling_price)

        return sum(a)

    def get_total_dollar_client_return(self):
        client_returns = self.clientreturn_set.filter()
        cart_id_list = []
        product_list = []
        for client_return in client_returns:
            cart_id_list.append(client_return.cart.id)

        cart_list = Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='dollar')
        for cart in cart_list:
            for cartitem in cart.cartitem_set.all():
                product_list.append(cartitem.product)

        a = []
        for i in product_list:
            for item in i.productthroughbranch_set.all():
                a.append(item.selling_price)

        return sum(a)


class Warehouse(models.Model):
    """
    sklad fillialga tegishli
    """
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="branch_warehouse", null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="staff_warehouse", null=True, blank=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Section(models.Model):
    """Bo'limlar"""

    # Relationships1
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE)

    # Fields
    name = models.CharField(max_length=255)
    total_sum = models.FloatField(default=0)
    total_dollar = models.FloatField(default=0)
    total_card = models.FloatField(default=0)
    total_loan_sum = models.FloatField(default=0)
    total_loan_dollar = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.name)


class Category(models.Model):
    """tovarlarni kategoriyasi"""

    # Fields
    name = models.CharField(max_length=255)
    is_mobile = models.BooleanField(default=False)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.name)


class Deliver(models.Model):
    """Yetkazib beruvchi"""
    TYPE_OF_BRANCH = (
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
    )
    # Fields
    type = models.CharField(max_length=200, choices=TYPE_OF_BRANCH)
    name = models.CharField(max_length=255)
    director_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    bank_hr = models.CharField(max_length=255, blank=True, null=True)
    inn = models.CharField(max_length=255, blank=True, null=True)
    mfo = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    phone_1 = models.CharField(max_length=25, blank=True, null=True)
    phone_2 = models.CharField(max_length=25, blank=True, null=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.name)


class DeliverLoan(models.Model):
    """ Filialning deliverdan qarzdorligi. Agar balans musbat bo'lsa
        unda filial deliverdan qarzdor, aks holda deliver filialdan
        qarzdor bo'ladi.
    """
    deliver = models.ForeignKey("app.Deliver", on_delete=models.CASCADE,
                                related_name='loans')
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE,
                               related_name='loan_from_delivers')
    loan_dollar = models.FloatField(default=0)
    loan_sum = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"{self.deliver.name} - {self.branch.name}"

    class Meta:
        unique_together = ['deliver', 'branch']


class DifferProductRecieveHistory(models.Model):
    """Qabuldagi har hil tovarlar"""

    # Relationships
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)
    inventory = models.ForeignKey("app.InventoryInvoice", on_delete=models.CASCADE)

    # Fields
    old_price = models.FloatField(default=0)
    traded_at = models.DateTimeField()

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class ProductPriceChange(models.Model):
    """Tovar narxini o'zgartirgandagi pereotsenka"""

    # Relationships
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)
    # brat qalesiz
    # Fields
    amount = models.FloatField(default=0)
    old_price = models.FloatField(default=0)
    new_price = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class Income(models.Model):
    """Kirimlar"""

    # Relationships
    branch = models.ForeignKey("app.Branch", on_delete=models.DO_NOTHING, null=True, blank=True)
    section = models.ForeignKey("app.Section", on_delete=models.DO_NOTHING, null=True, blank=True)

    # Fields
    whom = models.CharField(max_length=255, blank=True, null=True)
    card = models.FloatField(default=0, null=True)
    sum = models.FloatField(default=0, null=True)
    dollar = models.FloatField(default=0, null=True)
    transfer = models.FloatField(default=0, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.whom


class Outcome(models.Model):
    """Chiqimlar - harajatlar"""

    STATUS = (
        ('requested', 'requested'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected')
    )

    # Relationships
    type = models.ForeignKey("app.OutcomeType", on_delete=models.CASCADE)
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    # Fields
    status = models.CharField(max_length=10, choices=STATUS, default=STATUS[0][0])
    whom = models.CharField(max_length=255, blank=True, null=True)
    card = models.FloatField(default=0, null=True)
    sum = models.FloatField(default=0, null=True)
    dollar = models.FloatField(default=0, null=True)
    transfer = models.FloatField(default=0, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class OutcomeType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Showcase(models.Model):
    """
    Vitrina uchun, magazindagi ko'rinish uchun qo'yiladigan tovar
    branch - qaysi filialda qancha miqdorda, qancha summadagi tovar borligi
    """

    # Relationships
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    expire_date = models.DateField(null=True, blank=True)
    dollar_summa = models.FloatField(default=0)
    sum_summa = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class Amount(models.Model):
    # Relationships
    branch = models.ForeignKey("app.Branch", on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE, related_name="product_amount_branch")

    # Fields
    amount = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class Realize(models.Model):
    # Fields
    purpose = models.CharField(max_length=50)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Company(models.Model):
    balance_sum = models.FloatField(default=0)
    balance_dollar = models.FloatField(default=0)
    balance_transfer = models.FloatField(default=0)
    balance_card = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class Accountant(models.Model):
    """Bugalter"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="branch_for_accountant")
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="staff_for_accountant")
    cash_sum = models.FloatField(default=0)
    cash_dollar = models.FloatField(default=0)
    card = models.FloatField(default=0)
    loan_sum = models.FloatField(default=0)
    loan_dollar = models.FloatField(default=0)
    discount_sum = models.FloatField(default=0)
    discount_dollar = models.FloatField(default=0)
    transfer = models.FloatField(default=0)
    change_sum = models.FloatField(default=0)
    change_dollar = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.branch.name)


class Check(models.Model):
    STATUS = (
        ('active', 'active'),
        ('inactive', 'inactive'),
    )

    # Relationships
    staff = models.ForeignKey("app.Staff", on_delete=models.CASCADE)

    # Fields
    status = models.CharField(max_length=10, choices=STATUS, default=STATUS[0][0])
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    @property
    def get_all_sum(self):
        summa = 0
        for check_item in self.checkitem_set.all():
            summa += check_item.product.selling_price
        return summa


class CheckItem(models.Model):
    # Relationships
    checks = models.ForeignKey("app.Check", on_delete=models.CASCADE)
    product = models.ForeignKey("app.Product", on_delete=models.CASCADE)

    # Fields
    amount = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class ChangeCurrency(models.Model):
    CURRENCY = (
        ('sum', 'sum'),
        ('dollar', 'dollar'),
    )

    # Relationships
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="change_currency_branch")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="change_currency_section")

    # Fields
    from_sum = models.FloatField(default=0)
    from_dollar = models.FloatField(default=0)
    currency = models.CharField(max_length=20, choices=CURRENCY, default="dollar")
    changed_at = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.pk)




def compute_product_ball(product):
    selling_prices = list(product.productthroughbranch_set.values_list(
        'selling_price', flat=True))
    branch_product_ids = product.productthroughbranch_set.values_list(
        'id', flat=True)
    product_metas = ProductMeta.objects.filter(
        product_through_branch__id__in=branch_product_ids).distinct()
    costs = list(product_metas.values_list('cost', flat=True))
    costs.append(product.cost)
    if len(selling_prices) > 0:
        selling_price = max(selling_prices)
        cost = max(costs)
        return (selling_price - cost) / 100
    return 0


@receiver(post_save, sender=ProductThroughBranch)
def _set_ball_onchange_branch_product_receiver(sender, instance, **kwargs):
    product = instance.product
    ball = compute_product_ball(product)
    product.ball = ball
    product.save()


@receiver(post_save, sender=ProductMeta)
def _set_ball_onchange_product_meta_receiver(sender, instance, **kwargs):
    product = instance.product_through_branch.product
    ball = compute_product_ball(product)
    product.ball = ball
    product.save()


@receiver(pre_save, sender=Product)
def _set_ball_onchange_product_receiver(sender, instance, **kwargs):
    ball = compute_product_ball(instance)
    instance.ball = ball


@receiver(post_save, sender=ClientLoan)
def _update_loans_onchange_client_loan_receiver(sender, instance, **kwargs):
    client = instance.client
    client.loan_sum = sum([i.loan_sum for i in client.client_loan.all()])
    client.loan_dollar = sum([i.loan_dollar for i in client.client_loan.all()])
    client.save()

# ddddddddd
