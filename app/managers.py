from django.db import models
from datetime import datetime
# from .models import Cart, CartItem


class ShopManager(models.Manager):

    def get_branch_total_sum_for_accountant(self, branch):
        # queryset = self.filter((cart__status="finished") and Q(traded_at__day=datetime.today().day) and Q(
        #         traded_at__month=datetime.now().month))
        # for
        # cart_items = CartItem.objects.filter(cart__shop_id=)
        pass


class Warehouse(models.QuerySet):
    pass
