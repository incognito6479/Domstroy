from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("minimal", views.MinimalViewSet)
router.register("warehouse", views.WarehouseViewSet)
router.register("return-deliver-product", views.ReturnDeliverProductViewSet)
# router.register("differproductrecievehistory", api.DifferProductRecieveHistoryViewSet)
router.register("cart", views.CartViewSet)
router.register("cart-item", views.CartItemViewSet)
router.register("shop", views.ShopViewSet)
router.register("staff", views.StaffViewSet)
router.register("check", views.CheckViewSet)
router.register("client", views.ClientViewSet)
router.register("client-loan", views.ClientLoanViewSet)
router.register("client-loan-payment", views.ClientLoanPaymentViewSet)
router.register("realize", views.RealizeViewSet)
router.register("baseproduct", views.ProductViewSet)
router.register("product", views.ProductThroughBranchtViewSet)
router.register("add-product", views.ProductViewSet)
router.register("producer", views.ProducerViewSet)
router.register("invoice", views.InvoiceViewSet)
router.register("invoiceitem", views.InvoiceItemViewSet)
router.register("branch", views.BranchViewSet)
router.register("section", views.SectionViewSet)
router.register("deliver", views.DeliverViewSet)
router.register("deliver-loans", views.DeliverLoanViewSet)
router.register("checkitem", views.CheckViewSet)
router.register("showcase", views.ShowcaseViewSet)
router.register("currency", views.CurrencyViewSet)
router.register("category", views.CategoryViewSet)
router.register("client-return-cart", views.ClientReturnCartViewSet)
router.register("client-return-cart-item", views.ClientReturnCartItemViewSet)
router.register("discountcard", views.DiscountCardViewSet)
router.register("bonus-product", views.BonusProductViewSet)
router.register("brokenproduct", views.BrokenProductViewSet)
router.register("inventory-item", views.InventoryItemViewSet)
router.register("product-request", views.ProductRequestViewSet)
router.register("product-request-item", views.ProductRequestItemViewSet)
router.register("product-receipt", views.ProductReceiptViewSet)
router.register("product-receipt-item", views.ProductReceiptItemViewSet)
router.register("inventory-invoice", views.InventoryInvoiceViewSet)
router.register("product-move-branch-item", views.ProductMoveBranchItemViewSet)
router.register("product-move-branch-group", views.ProductMoveBranchGroupViewSet)
router.register("provider-invoice", views.ProviderInvoiceViewSet)
router.register("provider-invoice-item", views.ProviderInvoiceItemViewSet)
router.register("product-change-price", views.ProductPriceChangeViewSet)
router.register("make-purchase", views.MakePurchaseViewSet)
router.register("outcome", views.OutcomeViewSet)
router.register("outcome-type", views.OutcomeTypeViewSet)
router.register("accountan", views.AccountantApiView)
router.register("change-currency", views.ChangeCurrency)
router.register("discount-product-receipt", views.DiscountProductReceiptViewSet)
router.register('price-type', views.PriceTypeProductReceiptViewSet)
# router.register("chang-currency", views.ChangeCurrency)
# router.register("accountant", views.AccountantApiView)