from datetime import datetime

import pytest
import test_helpers

from django.urls import reverse
from django.test import Client

pytestmark = [pytest.mark.django_db]


def tests_discountcard_list_view():
    instance1 = test_helpers.create_app_DiscountCard()
    instance2 = test_helpers.create_app_DiscountCard()
    client = Client()
    url = reverse("app_DiscountCard_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_discountcard_create_view():
    client = Client()
    url = reverse("app_DiscountCard_create")
    data = {
        "bonus_dollar": 1.0,
        "card": "text",
        "bonus_sum": 1.0
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_discountcard_detail_view():
    client = Client()
    instance = test_helpers.create_app_DiscountCard()
    url = reverse("app_DiscountCard_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_discountcard_update_view():
    client = Client()
    instance = test_helpers.create_app_DiscountCard()
    url = reverse("app_DiscountCard_update", args=[instance.pk, ])
    data = {
        "bonus_dollar": 1.0,
        "card": "text",
        "bonus_sum": 1.0,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_cart_list_view():
    instance1 = test_helpers.create_app_Cart()
    instance2 = test_helpers.create_app_Cart()
    client = Client()
    url = reverse("app_Cart_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_cart_create_view():
    shop = test_helpers.create_app_Shop()
    product = test_helpers.create_app_Product()
    client = Client()
    url = reverse("app_Cart_create")
    data = {
        "amount": 1,
        "shop": shop.pk,
        "product": product.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_cart_detail_view():
    client = Client()
    instance = test_helpers.create_app_Cart()
    url = reverse("app_Cart_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_cart_update_view():
    shop = test_helpers.create_app_Shop()
    product = test_helpers.create_app_Product()
    client = Client()
    instance = test_helpers.create_app_Cart()
    url = reverse("app_Cart_update", args=[instance.pk, ])
    data = {
        "amount": 1,
        "shop": shop.pk,
        "product": product.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_realize_list_view():
    instance1 = test_helpers.create_app_Realize()
    instance2 = test_helpers.create_app_Realize()
    client = Client()
    url = reverse("app_Realize_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_realize_create_view():
    client = Client()
    url = reverse("app_Realize_create")
    data = {
        "purpose": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_realize_detail_view():
    client = Client()
    instance = test_helpers.create_app_Realize()
    url = reverse("app_Realize_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_realize_update_view():
    client = Client()
    instance = test_helpers.create_app_Realize()
    url = reverse("app_Realize_update", args=[instance.pk, ])
    data = {
        "purpose": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_productrequest_list_view():
    instance1 = test_helpers.create_app_ProductRequest()
    instance2 = test_helpers.create_app_ProductRequest()
    client = Client()
    url = reverse("app_ProductRequest_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_productrequest_create_view():
    staff = test_helpers.create_app_Staff()
    branch = test_helpers.create_app_Branch()
    client = Client()
    url = reverse("app_ProductRequest_create")
    data = {
        "status": "text",
        "staff": staff.pk,
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_productrequest_detail_view():
    client = Client()
    instance = test_helpers.create_app_ProductRequest()
    url = reverse("app_ProductRequest_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_productrequest_update_view():
    staff = test_helpers.create_app_Staff()
    branch = test_helpers.create_app_Branch()
    client = Client()
    instance = test_helpers.create_app_ProductRequest()
    url = reverse("app_ProductRequest_update", args=[instance.pk, ])
    data = {
        "status": "text",
        "staff": staff.pk,
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_invoiceitem_list_view():
    instance1 = test_helpers.create_app_InvoiceItem()
    instance2 = test_helpers.create_app_InvoiceItem()
    client = Client()
    url = reverse("app_InvoiceItem_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_invoiceitem_create_view():
    invoice = test_helpers.create_app_Invoice()
    product = test_helpers.create_app_Product()
    client = Client()
    url = reverse("app_InvoiceItem_create")
    data = {
        "amount": 1.0,
        "selling_price": 1.0,
        "invoice": invoice.pk,
        "product": product.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_invoiceitem_detail_view():
    client = Client()
    instance = test_helpers.create_app_InvoiceItem()
    url = reverse("app_InvoiceItem_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_invoiceitem_update_view():
    invoice = test_helpers.create_app_Invoice()
    product = test_helpers.create_app_Product()
    client = Client()
    instance = test_helpers.create_app_InvoiceItem()
    url = reverse("app_InvoiceItem_update", args=[instance.pk, ])
    data = {
        "amount": 1.0,
        "selling_price": 1.0,
        "invoice": invoice.pk,
        "product": product.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_brokenproduct_list_view():
    instance1 = test_helpers.create_app_BrokenProduct()
    instance2 = test_helpers.create_app_BrokenProduct()
    client = Client()
    url = reverse("app_BrokenProduct_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_brokenproduct_create_view():
    product = test_helpers.create_app_Product()
    section = test_helpers.create_app_Section()
    branch = test_helpers.create_app_Branch()
    client = Client()
    url = reverse("app_BrokenProduct_create")
    data = {
        "comment": "text",
        "count": 1,
        "product": product.pk,
        "section": section.pk,
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_brokenproduct_detail_view():
    client = Client()
    instance = test_helpers.create_app_BrokenProduct()
    url = reverse("app_BrokenProduct_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_brokenproduct_update_view():
    product = test_helpers.create_app_Product()
    section = test_helpers.create_app_Section()
    branch = test_helpers.create_app_Branch()
    client = Client()
    instance = test_helpers.create_app_BrokenProduct()
    url = reverse("app_BrokenProduct_update", args=[instance.pk, ])
    data = {
        "comment": "text",
        "count": 1,
        "product": product.pk,
        "section": section.pk,
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_minimal_list_view():
    instance1 = test_helpers.create_app_Minimal()
    instance2 = test_helpers.create_app_Minimal()
    client = Client()
    url = reverse("app_Minimal_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_minimal_create_view():
    product = test_helpers.create_app_Product()
    client = Client()
    url = reverse("app_Minimal_create")
    data = {
        "amount": 1.0,
        "month": "text",
        "product": product.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_minimal_detail_view():
    client = Client()
    instance = test_helpers.create_app_Minimal()
    url = reverse("app_Minimal_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_minimal_update_view():
    product = test_helpers.create_app_Product()
    client = Client()
    instance = test_helpers.create_app_Minimal()
    url = reverse("app_Minimal_update", args=[instance.pk, ])
    data = {
        "amount": 1.0,
        "month": "text",
        "product": product.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_client_list_view():
    instance1 = test_helpers.create_app_Client()
    instance2 = test_helpers.create_app_Client()
    client = Client()
    url = reverse("app_Client_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_client_create_view():
    discount_card = test_helpers.create_app_DiscountCard()
    branch = test_helpers.create_app_Branch()
    client = Client()
    url = reverse("app_Client_create")
    data = {
        "phone_1": "text",
        "loan_dollar": 1.0,
        "first_name": "text",
        "last_name": "text",
        "address": "text",
        "birth_date": datetime.now(),
        "return_date": datetime.now(),
        "phone_2": "text",
        "load_sum": 1.0,
        "ball": 1,
        "discount_card": discount_card.pk,
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_client_detail_view():
    client = Client()
    instance = test_helpers.create_app_Client()
    url = reverse("app_Client_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_client_update_view():
    discount_card = test_helpers.create_app_DiscountCard()
    branch = test_helpers.create_app_Branch()
    client = Client()
    instance = test_helpers.create_app_Client()
    url = reverse("app_Client_update", args=[instance.pk, ])
    data = {
        "phone_1": "text",
        "loan_dollar": 1.0,
        "first_name": "text",
        "last_name": "text",
        "address": "text",
        "birth_date": datetime.now(),
        "return_date": datetime.now(),
        "phone_2": "text",
        "load_sum": 1.0,
        "ball": 1,
        "discount_card": discount_card.pk,
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_inventory_list_view():
    instance1 = test_helpers.create_app_Inventory()
    instance2 = test_helpers.create_app_Inventory()
    client = Client()
    url = reverse("app_Inventory_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_inventory_create_view():
    staff = test_helpers.create_app_Staff()
    client = Client()
    url = reverse("app_Inventory_create")
    data = {
        "staff": staff.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_inventory_detail_view():
    client = Client()
    instance = test_helpers.create_app_Inventory()
    url = reverse("app_Inventory_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_inventory_update_view():
    staff = test_helpers.create_app_Staff()
    client = Client()
    instance = test_helpers.create_app_Inventory()
    url = reverse("app_Inventory_update", args=[instance.pk, ])
    data = {
        "staff": staff.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_clientpaymenthistory_list_view():
    instance1 = test_helpers.create_app_ClientPaymentHistory()
    instance2 = test_helpers.create_app_ClientPaymentHistory()
    client = Client()
    url = reverse("app_ClientPaymentHistory_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_clientpaymenthistory_create_view():
    client = test_helpers.create_app_Client()
    staff = test_helpers.create_app_Staff()
    url = reverse("app_ClientPaymentHistory_create")
    data = {
        "paid_at": datetime.now(),
        "client": client.pk,
        "staff": staff.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_clientpaymenthistory_detail_view():
    client = Client()
    instance = test_helpers.create_app_ClientPaymentHistory()
    url = reverse("app_ClientPaymentHistory_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_clientpaymenthistory_update_view():
    client = test_helpers.create_app_Client()
    staff = test_helpers.create_app_Staff()
    instance = test_helpers.create_app_ClientPaymentHistory()
    url = reverse("app_ClientPaymentHistory_update", args=[instance.pk, ])
    data = {
        "paid_at": datetime.now(),
        "client": client.pk,
        "staff": staff.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_product_list_view():
    instance1 = test_helpers.create_app_Product()
    instance2 = test_helpers.create_app_Product()
    client = Client()
    url = reverse("app_Product_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_product_create_view():
    section = test_helpers.create_app_Section()
    category = test_helpers.create_app_Category()
    deliver = test_helpers.create_app_Deliver()
    branch = test_helpers.create_app_Branch()
    client = Client()
    url = reverse("app_Product_create")
    data = {
        "expire_date": datetime.now(),
        "currency": "text",
        "name": "text",
        "amount": 1.0,
        "ball": 1,
        "measurement": "text",
        "producer": "text",
        "cost": 1.0,
        "barcode": "text",
        "selling_price": 1.0,
        "section": section.pk,
        "category": category.pk,
        "deliver": deliver.pk,
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_product_detail_view():
    client = Client()
    instance = test_helpers.create_app_Product()
    url = reverse("app_Product_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_product_update_view():
    section = test_helpers.create_app_Section()
    category = test_helpers.create_app_Category()
    deliver = test_helpers.create_app_Deliver()
    branch = test_helpers.create_app_Branch()
    client = Client()
    instance = test_helpers.create_app_Product()
    url = reverse("app_Product_update", args=[instance.pk, ])
    data = {
        "expire_date": datetime.now(),
        "currency": "text",
        "name": "text",
        "amount": 1.0,
        "ball": 1,
        "measurement": "text",
        "producer": "text",
        "cost": 1.0,
        "barcode": "text",
        "selling_price": 1.0,
        "section": section.pk,
        "category": category.pk,
        "deliver": deliver.pk,
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_clientreturn_list_view():
    instance1 = test_helpers.create_app_ClientReturn()
    instance2 = test_helpers.create_app_ClientReturn()
    client = Client()
    url = reverse("app_ClientReturn_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_clientreturn_create_view():
    client = test_helpers.create_app_Client()
    staff = test_helpers.create_app_Staff()
    cart = test_helpers.create_app_Cart()
    url = reverse("app_ClientReturn_create")
    data = {
        "return_date": datetime.now(),
        "took_date": datetime.now(),
        "client": client.pk,
        "staff": staff.pk,
        "cart": cart.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_clientreturn_detail_view():
    client = Client()
    instance = test_helpers.create_app_ClientReturn()
    url = reverse("app_ClientReturn_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_clientreturn_update_view():
    client = test_helpers.create_app_Client()
    staff = test_helpers.create_app_Staff()
    cart = test_helpers.create_app_Cart()
    instance = test_helpers.create_app_ClientReturn()
    url = reverse("app_ClientReturn_update", args=[instance.pk, ])
    data = {
        "return_date": datetime.now(),
        "took_date": datetime.now(),
        "client": client.pk,
        "staff": staff.pk,
        "cart": cart.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_section_list_view():
    instance1 = test_helpers.create_app_Section()
    instance2 = test_helpers.create_app_Section()
    client = Client()
    url = reverse("app_Section_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_section_create_view():
    branch = test_helpers.create_app_Branch()
    client = Client()
    url = reverse("app_Section_create")
    data = {
        "name": "text",
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_section_detail_view():
    client = Client()
    instance = test_helpers.create_app_Section()
    url = reverse("app_Section_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_section_update_view():
    branch = test_helpers.create_app_Branch()
    client = Client()
    instance = test_helpers.create_app_Section()
    url = reverse("app_Section_update", args=[instance.pk, ])
    data = {
        "name": "text",
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_invoice_list_view():
    instance1 = test_helpers.create_app_Invoice()
    instance2 = test_helpers.create_app_Invoice()
    client = Client()
    url = reverse("app_Invoice_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_invoice_create_view():
    branch = test_helpers.create_app_Branch()
    client = Client()
    url = reverse("app_Invoice_create")
    data = {
        "name": "text",
        "status": "text",
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_invoice_detail_view():
    client = Client()
    instance = test_helpers.create_app_Invoice()
    url = reverse("app_Invoice_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_invoice_update_view():
    branch = test_helpers.create_app_Branch()
    client = Client()
    instance = test_helpers.create_app_Invoice()
    url = reverse("app_Invoice_update", args=[instance.pk, ])
    data = {
        "name": "text",
        "status": "text",
        "branch": branch.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_returndeliverproduct_list_view():
    instance1 = test_helpers.create_app_ReturnDeliverProduct()
    instance2 = test_helpers.create_app_ReturnDeliverProduct()
    client = Client()
    url = reverse("app_ReturnDeliverProduct_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_returndeliverproduct_create_view():
    product = test_helpers.create_app_Product()
    client = Client()
    url = reverse("app_ReturnDeliverProduct_create")
    data = {
        "comment": "text",
        "amount": 1,
        "product": product.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_returndeliverproduct_detail_view():
    client = Client()
    instance = test_helpers.create_app_ReturnDeliverProduct()
    url = reverse("app_ReturnDeliverProduct_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_returndeliverproduct_update_view():
    product = test_helpers.create_app_Product()
    client = Client()
    instance = test_helpers.create_app_ReturnDeliverProduct()
    url = reverse("app_ReturnDeliverProduct_update", args=[instance.pk, ])
    data = {
        "comment": "text",
        "amount": 1,
        "product": product.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_currency_list_view():
    instance1 = test_helpers.create_app_Currency()
    instance2 = test_helpers.create_app_Currency()
    client = Client()
    url = reverse("app_Currency_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_currency_create_view():
    client = Client()
    url = reverse("app_Currency_create")
    data = {
        "readl_currency": 1.0,
        "selling_currency": 1.0,
        "ball_price": 1.0,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_currency_detail_view():
    client = Client()
    instance = test_helpers.create_app_Currency()
    url = reverse("app_Currency_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_currency_update_view():
    client = Client()
    instance = test_helpers.create_app_Currency()
    url = reverse("app_Currency_update", args=[instance.pk, ])
    data = {
        "readl_currency": 1.0,
        "selling_currency": 1.0,
        "ball_price": 1.0,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_shop_list_view():
    instance1 = test_helpers.create_app_Shop()
    instance2 = test_helpers.create_app_Shop()
    client = Client()
    url = reverse("app_Shop_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_shop_create_view():
    branch = test_helpers.create_app_Branch()
    seller = test_helpers.create_app_Staff()
    client = test_helpers.create_app_Client()
    section = test_helpers.create_app_Section()
    url = reverse("app_Shop_create")
    data = {
        "traded_at": datetime.now(),
        "card": 1.0,
        "loan_sum": 1.0,
        "cash_sum": 1.0,
        "discount_sum": 1.0,
        "loan_dollar": 1.0,
        "discount_dollar": 1.0,
        "transfer": 1.0,
        "cash_dollar": 1.0,
        "branch": branch.pk,
        "seller": seller.pk,
        "client": client.pk,
        "section": section.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_shop_detail_view():
    client = Client()
    instance = test_helpers.create_app_Shop()
    url = reverse("app_Shop_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_shop_update_view():
    branch = test_helpers.create_app_Branch()
    seller = test_helpers.create_app_Staff()
    client = test_helpers.create_app_Client()
    section = test_helpers.create_app_Section()
    instance = test_helpers.create_app_Shop()
    url = reverse("app_Shop_update", args=[instance.pk, ])
    data = {
        "traded_at": datetime.now(),
        "card": 1.0,
        "loan_sum": 1.0,
        "cash_sum": 1.0,
        "discount_sum": 1.0,
        "loan_dollar": 1.0,
        "discount_dollar": 1.0,
        "transfer": 1.0,
        "cash_dollar": 1.0,
        "branch": branch.pk,
        "seller": seller.pk,
        "client": client.pk,
        "section": section.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_branch_list_view():
    instance1 = test_helpers.create_app_Branch()
    instance2 = test_helpers.create_app_Branch()
    client = Client()
    url = reverse("app_Branch_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_branch_create_view():
    client = Client()
    url = reverse("app_Branch_create")
    data = {
        "address": "text",
        "is_b2b": True,
        "is_b2c": True,
        "name": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_branch_detail_view():
    client = Client()
    instance = test_helpers.create_app_Branch()
    url = reverse("app_Branch_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_branch_update_view():
    client = Client()
    instance = test_helpers.create_app_Branch()
    url = reverse("app_Branch_update", args=[instance.pk, ])
    data = {
        "address": "text",
        "is_b2b": True,
        "is_b2c": True,
        "name": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_category_list_view():
    instance1 = test_helpers.create_app_Category()
    instance2 = test_helpers.create_app_Category()
    client = Client()
    url = reverse("app_Category_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_category_create_view():
    client = Client()
    url = reverse("app_Category_create")
    data = {
        "name": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_category_detail_view():
    client = Client()
    instance = test_helpers.create_app_Category()
    url = reverse("app_Category_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_category_update_view():
    client = Client()
    instance = test_helpers.create_app_Category()
    url = reverse("app_Category_update", args=[instance.pk, ])
    data = {
        "name": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_deliver_list_view():
    instance1 = test_helpers.create_app_Deliver()
    instance2 = test_helpers.create_app_Deliver()
    client = Client()
    url = reverse("app_Deliver_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_deliver_create_view():
    client = Client()
    url = reverse("app_Deliver_create")
    data = {
        "load_dollar": 1.0,
        "load_sum": 1.0,
        "name": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_deliver_detail_view():
    client = Client()
    instance = test_helpers.create_app_Deliver()
    url = reverse("app_Deliver_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_deliver_update_view():
    client = Client()
    instance = test_helpers.create_app_Deliver()
    url = reverse("app_Deliver_update", args=[instance.pk, ])
    data = {
        "load_dollar": 1.0,
        "load_sum": 1.0,
        "name": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_differproductrecievehistory_list_view():
    instance1 = test_helpers.create_app_DifferProductRecieveHistory()
    instance2 = test_helpers.create_app_DifferProductRecieveHistory()
    client = Client()
    url = reverse("app_DifferProductRecieveHistory_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_differproductrecievehistory_create_view():
    product = test_helpers.create_app_Product()
    inventory = test_helpers.create_app_Inventory()
    client = Client()
    url = reverse("app_DifferProductRecieveHistory_create")
    data = {
        "old_price": 1.0,
        "traded_at": datetime.now(),
        "product": product.pk,
        "inventory": inventory.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_differproductrecievehistory_detail_view():
    client = Client()
    instance = test_helpers.create_app_DifferProductRecieveHistory()
    url = reverse("app_DifferProductRecieveHistory_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_differproductrecievehistory_update_view():
    product = test_helpers.create_app_Product()
    inventory = test_helpers.create_app_Inventory()
    client = Client()
    instance = test_helpers.create_app_DifferProductRecieveHistory()
    url = reverse("app_DifferProductRecieveHistory_update", args=[instance.pk, ])
    data = {
        "old_price": 1.0,
        "traded_at": datetime.now(),
        "product": product.pk,
        "inventory": inventory.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_staff_list_view():
    instance1 = test_helpers.create_app_Staff()
    instance2 = test_helpers.create_app_Staff()
    client = Client()
    url = reverse("app_Staff_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_staff_create_view():
    branch = test_helpers.create_app_Branch()
    section = test_helpers.create_app_Section()
    client = Client()
    url = reverse("app_Staff_create")
    data = {
        "address": "text",
        "phone": "text",
        "birth_date": datetime.now(),
        "role": "text",
        "branch": branch.pk,
        "section": section.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_staff_detail_view():
    client = Client()
    instance = test_helpers.create_app_Staff()
    url = reverse("app_Staff_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_staff_update_view():
    branch = test_helpers.create_app_Branch()
    section = test_helpers.create_app_Section()
    client = Client()
    instance = test_helpers.create_app_Staff()
    url = reverse("app_Staff_update", args=[instance.pk, ])
    data = {
        "address": "text",
        "phone": "text",
        "birth_date": datetime.now(),
        "role": "text",
        "branch": branch.pk,
        "section": section.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302
