from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from . import models
from django.contrib.auth.models import Group


# @admin.site.register(Group)
# @admin.site.register(Permission)


# @admin.register(models.Producer)
# class ProducerAdmin(admin.ModelAdmin):
#     list_display = [
#         'id',
#         "director_name",
#         "address",
#         "bank_hr",
#         "inn",
#         "mfo",
#         "state",
#         "region",
#         "city",
#         "phone_1",
#         "phone_2",
#     ]
#     exclude = ()
@admin.register(models.Action)
class ActionModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Permission)
class ActionModelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Page)
class ActionModelAdmin(MPTTModelAdmin):
    pass


@admin.register(models.DiscountCard)
class DiscountCardAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "bonus_dollar",
        "card",
        "bonus_sum",
        "created_at",
    ]
    exclude = ()


class CartItemInlineModel(admin.TabularInline):
    model = models.CartItem
    fields = ['id', 'product', 'amount']
    extra = 0


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "product_count",
        "created_at",
    ]
    exclude = ()
    inlines = [CartItemInlineModel]

    def product_count(self, obj):
        return obj.cartitem_set.count()


@admin.register(models.Realize)
class RealizeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "purpose",
        "created_at",
    ]


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'cart',
        'product',
        'amount',
        'created_at',
    ]


@admin.register(models.ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "status",
        "created_at",
    ]


@admin.register(models.ProductMoveBranchItem)
class ProductMoveBranchItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "product",
        "amount",
        "selling_price",
        "expire_date",
        "created_at",
        "last_updated"
    ]


@admin.register(models.ProductMoveBranchGroup)
class ProductMoveBranchGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "status",
        "from_branch",
        "to_branch",
        "created_at",
        "last_updated",
        "created_by",
        "reviewed_by",
    ]


@admin.register(models.BrokenProduct)
class BrokenProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "product",
        "comment",
        "broken_date",
        "amount",
        "created_at",
    ]
    exclude = ()


@admin.register(models.Minimal)
class MinimalAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "product",
        "amount",
        "month",
        "created_at",
    ]
    exclude = ()


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "is_active",
        "type",
        "loan_sum",
        "loan_dollar",
        "first_name",
        "last_name",
        "address",
        "birth_date",
        "phone_1",
        "phone_2",
        "discount_card",
        "ball",
        "registered_at",

    ]

    def registered_at(self, obj):
        return obj.created_at

    registered_at.short_description = 'registered at'
    # readonly_fields = [
    #     "phone_1",
    #     "loan_dollar",
    #     "created_at",
    #     "first_name",
    #     "last_name",
    #     "address",
    #     "birth_date",
    #     "last_updated",
    #     "return_date",
    #     "phone_2",
    #     "loan_sum",
    #     "ball",
    # ]
    exclude = ()


@admin.register(models.InventoryInvoice)
class InventoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "created_at",
    ]

    exclude = ()


@admin.register(models.InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "last_updated",
        "created_at",
    ]

    exclude = ()


@admin.register(models.Check)
class CheckAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OutcomeType)
class OutcomeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "balance_sum",
        "balance_dollar",
        "balance_transfer",
        "balance_card",
        "created_at",
    ]


@admin.register(models.CheckItem)
class CheckItemAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ClientPaymentHistory)
class ClientPaymentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "staff",
        "client",
        "paid_at",
        "card",
        "cash_sum",
        "cash_dollar",
        "discount_sum",
        "discount_dollar",
        "transfer",
        "from_ball",
    ]

    exclude = ()


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = [
        "id",
        "branch__name",
        "name",
        "barcode"
    ]


class ProductMetaTabularInline(admin.TabularInline):
    min_num = 0
    extra = 0
    model = models.ProductMeta


@admin.register(models.ProductThroughBranch)
class ProductThroughBranchAdmin(admin.ModelAdmin):
    inlines = [ProductMetaTabularInline]
    list_display = [
        "id",
        "product",
        "branch",
        "status",
        "get_amount",
        "selling_price",
        "created_at",
    ]
    search_fields = [
        "id",
        "branch",
    ]


class ClientReturnItemInline(admin.TabularInline):
    model = models.ClientReturnItem
    fields = ['id', 'product', 'expire_date', 'amount', 'comment']
    extra = 0


@admin.register(models.ClientReturn)
class ClientReturnAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "branch",
        "staff",
        "client",
        "took_date",
        "created_at",
    ]
    exclude = ()
    inlines = [ClientReturnItemInline]


@admin.register(models.StaffSalary)
class StaffSalaryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Producer)
class ProducerAdmin(admin.ModelAdmin):
    exclude = ()


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    fields = ['name', 'branch', "total_sum", "total_dollar", "total_card", "total_loan_sum", "total_loan_dollar"]
    list_display = [
        'id',
        "name",
        "created_at",
    ]


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    fields = [
        "name",
        "from_branch",
        "to_branch",
        "staff",
        "expense",
        "deliver",
        "status",
    ]
    list_display = [
        'id',
        "name",
        "from_branch",
        "to_branch",
        "expense",
        "get_product_count",
        "status",
        "created_at",
    ]

    def get_product_count(self, obj):
        return obj.get_product_count

    get_product_count.short_description = 'product count in Invoice'

    # readonly_fields = [
    #     "created_at",
    #     "last_updated",
    #     "status",
    # ]


@admin.register(models.InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "invoice",
        "product",
        "amount",
        "selling_price",
        "created_at",
    ]
    exclude = [
        "created_at",
        "last_updated",
    ]


@admin.register(models.ReturnDeliverProduct)
class ReturnDeliverProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "comment",
        "amount",
        "created_at",
    ]

    # readonly_fields = [
    #     "comment",
    #     "last_updated",
    #     "amount",
    #     "created_at",
    # ]

    exclude = ()


@admin.register(models.Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "real_currency",
        "selling_currency",
        "ball_price",
        "created_at",
    ]

    # def has_add_permission(self, request):
    #     return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(models.Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "traded_at",
        "card",
        "loan_sum",
        "cash_sum",
        "discount_sum",
        "loan_dollar",
        "discount_dollar",
        "transfer",
        "cash_dollar",
        "created_at",
    ]
    exclude = ()


@admin.register(models.Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "name",
        "address",
        "get_section_count",
        "get_product_count",
    ]
    exclude = ()

    def get_product_count(self, obj):
        return obj.product_set.count()

    get_product_count.short_description = 'product count'


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "name",
    ]


@admin.register(models.ProductMeta)
class ProductMetaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "amount",

    ]


@admin.register(models.Deliver)
class DeliverAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        # "loan_dollar",
        # "loan_sum",
        "name",
        "created_at",
    ]


@admin.register(models.Income)
class IncomeAdmin(admin.ModelAdmin):
    exclude = ()


@admin.register(models.DifferProductRecieveHistory)
class DifferProductRecieveHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "old_price",
        "traded_at",
        "created_at",
    ]

    # readonly_fields = [
    #     "old_price",
    #     "traded_at",
    #     "last_updated",
    #     "created_at",
    # ]

    exclude = ()


class PermissionInline(admin.TabularInline):
    model = models.Permission
    readonly_fields = ('page', 'action')
    can_delete = False
    extra = 0


@admin.register(models.Staff)
class StaffAdmin(admin.ModelAdmin):
    fields = [
        'username',
        'first_name',
        'last_name',
        'branch',
        'section',
        'is_active',
        'birth_date',
        'phone',
        'role',
        'status',
        'salary',
        'password',
    ]
    list_display = [
        'id',
        'username',
        "first_name",
        "salary",
        "address",
        "phone",
        "birth_date",
        "role",
    ]
    inlines = [
        PermissionInline
    ]


@admin.register(models.ClientLoan)
class ClientLoanAdmin(admin.ModelAdmin):
    list_display = ("id", 'client')



@admin.register(models.ProductReceipt)
class ProductReceiptAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(models.ProductReceiptItem)
class ProductReceiptItemAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(models.ReturnPrice)
class ReturnPriceAdmin(admin.ModelAdmin):
    list_display = ("id", "price")


@admin.register(models.Accountant)
class AccountantAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(models.ProductPriceChange)
class ProductPriceChangeAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(models.ChangeCurrency)
class ChangeCurrencyAdmin(admin.ModelAdmin):
    list_display = ("id", "branch", "section")


@admin.register(models.Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(models.PriceType)
class PriceTypeReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", 'title')


admin.site.unregister(Group)
