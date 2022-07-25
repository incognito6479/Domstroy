import random
import string

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

from app import models as app_models


def random_string(length=10):
    # Create a random string of length length
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def create_User(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_AbstractUser(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return AbstractUser.objects.create(**defaults)


def create_AbstractBaseUser(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return AbstractBaseUser.objects.create(**defaults)


def create_Group(**kwargs):
    defaults = {
        "name": "%s_group" % random_string(5),
    }
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_ContentType(**kwargs):
    defaults = {
    }
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_app_DiscountCard(**kwargs):
    defaults = dict()
    defaults["bonus_dollar"] = ""
    defaults["card"] = ""
    defaults["bonus_sum"] = ""
    defaults.update(**kwargs)
    return app_models.DiscountCard.objects.create(**defaults)


def create_app_Cart(**kwargs):
    defaults = dict()
    defaults["amount"] = ""
    if "shop" not in kwargs:
        defaults["shop"] = create_app_Shop()
    if "product" not in kwargs:
        defaults["product"] = create_app_Product()
    defaults.update(**kwargs)
    return app_models.Cart.objects.create(**defaults)


def create_app_Realize(**kwargs):
    defaults = dict()
    defaults["purpose"] = ""
    defaults.update(**kwargs)
    return app_models.Realize.objects.create(**defaults)


def create_app_ProductRequest(**kwargs):
    defaults = dict()
    defaults["status"] = ""
    if "staff" not in kwargs:
        defaults["staff"] = create_app_Staff()
    if "branch" not in kwargs:
        defaults["branch"] = create_app_Branch()
    defaults.update(**kwargs)
    return app_models.ProductRequest.objects.create(**defaults)


def create_app_InvoiceItem(**kwargs):
    defaults = dict()
    defaults["amount"] = ""
    defaults["selling_price"] = ""
    if "invoice" not in kwargs:
        defaults["invoice"] = create_app_Invoice()
    if "product" not in kwargs:
        defaults["product"] = create_app_Product()
    defaults.update(**kwargs)
    return app_models.InvoiceItem.objects.create(**defaults)


def create_app_BrokenProduct(**kwargs):
    defaults = dict()
    defaults["comment"] = ""
    defaults["count"] = ""
    if "product" not in kwargs:
        defaults["product"] = create_app_Product()
    if "section" not in kwargs:
        defaults["section"] = create_app_Section()
    if "branch" not in kwargs:
        defaults["branch"] = create_app_Branch()
    defaults.update(**kwargs)
    return app_models.BrokenProduct.objects.create(**defaults)


def create_app_Minimal(**kwargs):
    defaults = dict()
    defaults["amount"] = ""
    defaults["month"] = ""
    if "product" not in kwargs:
        defaults["product"] = create_app_Product()
    defaults.update(**kwargs)
    return app_models.Minimal.objects.create(**defaults)


def create_app_Client(**kwargs):
    defaults = dict()
    defaults["phone_1"] = ""
    defaults["loan_dollar"] = ""
    defaults["first_name"] = ""
    defaults["last_name"] = ""
    defaults["address"] = ""
    defaults["birth_date"] = datetime.now()
    defaults["return_date"] = datetime.now()
    defaults["phone_2"] = ""
    defaults["load_sum"] = ""
    defaults["ball"] = ""
    if "discount_card" not in kwargs:
        defaults["discount_card"] = create_app_DiscountCard()
    if "branch" not in kwargs:
        defaults["branch"] = create_app_Branch()
    defaults.update(**kwargs)
    return app_models.Client.objects.create(**defaults)


def create_app_Inventory(**kwargs):
    defaults = dict()
    if "staff" not in kwargs:
        defaults["staff"] = create_app_Staff()
    defaults.update(**kwargs)
    return app_models.Inventory.objects.create(**defaults)


def create_app_ClientPaymentHistory(**kwargs):
    defaults = dict()
    defaults["paid_at"] = datetime.now()
    if "client" not in kwargs:
        defaults["client"] = create_app_Client()
    if "staff" not in kwargs:
        defaults["staff"] = create_app_Staff()
    defaults.update(**kwargs)
    return app_models.ClientPaymentHistory.objects.create(**defaults)


def create_app_Product(**kwargs):
    defaults = dict()
    defaults["currency"] = ""
    defaults["name"] = ""
    defaults["ball"] = 0
    defaults["measurement"] = ""
    defaults["producer"] = None
    defaults["cost"] = 0
    defaults["barcode"] = ""
    if "section" not in kwargs:
        defaults["section"] = create_app_Section()
    if "category" not in kwargs:
        defaults["category"] = create_app_Category()
    if "deliver" not in kwargs:
        defaults["deliver"] = create_app_Deliver()
    # if "branch" not in kwargs:
    #     defaults["branch"] = create_app_Branch()
    defaults.update(**kwargs)
    return app_models.Product.objects.create(**defaults)


def create_app_ClientReturn(**kwargs):
    defaults = dict()
    defaults["return_date"] = datetime.now()
    defaults["took_date"] = datetime.now()
    if "client" not in kwargs:
        defaults["client"] = create_app_Client()
    if "staff" not in kwargs:
        defaults["staff"] = create_app_Staff()
    if "cart" not in kwargs:
        defaults["cart"] = create_app_Cart()
    defaults.update(**kwargs)
    return app_models.ClientReturn.objects.create(**defaults)


def create_app_Section(**kwargs):
    defaults = dict()
    defaults["name"] = ""
    if "branch" not in kwargs:
        defaults["branch"] = create_app_Branch()
    defaults.update(**kwargs)
    return app_models.Section.objects.create(**defaults)


def create_app_Invoice(**kwargs):
    defaults = dict()
    defaults["name"] = ""
    defaults["status"] = ""
    if "branch" not in kwargs:
        defaults["branch"] = create_app_Branch()
    defaults.update(**kwargs)
    return app_models.Invoice.objects.create(**defaults)


def create_app_ReturnDeliverProduct(**kwargs):
    defaults = dict()
    defaults["comment"] = ""
    defaults["amount"] = ""
    if "product" not in kwargs:
        defaults["product"] = create_app_Product()
    defaults.update(**kwargs)
    return app_models.ReturnDeliverProduct.objects.create(**defaults)


def create_app_Currency(**kwargs):
    defaults = dict()
    defaults["readl_currency"] = ""
    defaults["selling_currency"] = ""
    defaults["ball_price"] = ""
    defaults.update(**kwargs)
    return app_models.Currency.objects.create(**defaults)


def create_app_Shop(**kwargs):
    defaults = dict()
    defaults["traded_at"] = datetime.now()
    defaults["card"] = ""
    defaults["loan_sum"] = ""
    defaults["cash_sum"] = ""
    defaults["discount_sum"] = ""
    defaults["loan_dollar"] = ""
    defaults["discount_dollar"] = ""
    defaults["transfer"] = ""
    defaults["cash_dollar"] = ""
    if "branch" not in kwargs:
        defaults["branch"] = create_app_Branch()
    if "seller" not in kwargs:
        defaults["seller"] = create_app_Staff()
    if "client" not in kwargs:
        defaults["client"] = create_app_Client()
    if "section" not in kwargs:
        defaults["section"] = create_app_Section()
    defaults.update(**kwargs)
    return app_models.Shop.objects.create(**defaults)


def create_app_Branch(**kwargs):
    defaults = dict()
    defaults["address"] = ""
    defaults["type_of_branch"] = ""
    defaults["name"] = ""
    defaults.update(**kwargs)
    return app_models.Branch.objects.create(**defaults)


def create_app_Category(**kwargs):
    defaults = dict()
    defaults["name"] = ""
    defaults.update(**kwargs)
    return app_models.Category.objects.create(**defaults)


def create_app_Deliver(**kwargs):
    defaults = dict()
    defaults["loan_dollar"] = 0
    defaults["loan_sum"] = 0
    defaults["name"] = ""
    defaults.update(**kwargs)
    return app_models.Deliver.objects.create(**defaults)


def create_app_DifferProductRecieveHistory(**kwargs):
    defaults = dict()
    defaults["old_price"] = ""
    defaults["traded_at"] = datetime.now()
    if "product" not in kwargs:
        defaults["product"] = create_app_Product()
    if "inventory" not in kwargs:
        defaults["inventory"] = create_app_Inventory()
    defaults.update(**kwargs)
    return app_models.DifferProductRecieveHistory.objects.create(**defaults)


def create_app_Staff(**kwargs):
    defaults = dict()
    defaults["address"] = ""
    defaults["phone"] = ""
    defaults["birth_date"] = datetime.now()
    defaults["role"] = ""
    defaults["username"] = "username"
    defaults["email"] = "username@tempurl.com"
    if "branch" not in kwargs:
        defaults["branch"] = create_app_Branch()
    if "section" not in kwargs:
        defaults["section"] = create_app_Section()
    defaults.update(**kwargs)
    return app_models.Staff.objects.create(**defaults)
