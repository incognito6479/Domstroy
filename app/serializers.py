import datetime
from datetime import datetime as today
from random import randint

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from . import models


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Branch
        fields = [
            "id",
            "name",
            "address",
            "type_of_branch"
            # "created_at",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = [
            "id",
            "name",
            # "created_at",
        ]


class DeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Deliver
        fields = [
            "id",
            "name",
            "director_name",
            "address",
            "bank_hr",
            "inn",
            "mfo",
            "state",
            "region",
            "phone_1",
            "phone_2",
            "created_at",
            "last_updated"
        ]


class DeliverLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliverLoan
        fields = [
            "id",
            "branch",
            "deliver",
            "loan_dollar",
            "loan_sum",
            "created_at",
            "last_updated"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['branch'] = BranchSerializer(instance.branch).data
        rep['deliver'] = DeliverSerializer(instance.deliver).data
        return rep


class StaffDataForShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Staff
        fields = [
            "id",
            "first_name",
            "last_name",
            "address",
            "phone",
        ]


class CheckStaffModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Staff
        fields = [
            "id",
            "first_name",
            "branch",
            "section",
            "role",
        ]


class DiscountCardSerializer(serializers.ModelSerializer):
    card = serializers.CharField(max_length=20, required=False)
    client = PrimaryKeyRelatedField(queryset=models.Client.objects.all())

    class Meta:
        model = models.DiscountCard
        fields = [
            "id",
            "card",
            "client",
            "percentage",
            "bonus_sum",
            "bonus_dollar",
            "last_updated",
            "created_at",
        ]

    def create(self, validated_data):
        card = validated_data.get('card')
        valid = True
        try:
            card = int(card)
            if len(card) < 16:
                valid = False
        except:
            valid = False
        if not valid:
            validated_data['card'] = generate_number(16)
        client = validated_data['client']
        if client.discount_card:
            raise serializers.ValidationError('This client has discount card')
        instance = super().create(validated_data)
        client.discount_card = instance
        client.save()
        return instance

    def update(self, instance, validated_data):
        old_owner = instance.client
        cur_owner = validated_data['client']
        if cur_owner != old_owner:
            old_owner.discount_card = None
            old_owner.save()
            cur_owner.discount_card = instance
            cur_owner.save()
        return super().update(instance, validated_data)


class DiscountCardDetailSerializer(serializers.ModelSerializer):
    card = serializers.CharField(max_length=20, required=False)

    class Meta:
        model = models.DiscountCard
        fields = [
            "id",
            "card",
            "percentage",
            "bonus_dollar",
            "bonus_sum",
            "last_updated",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        try:
            rep['client'] = ClientSerializer(instance.client).data
        except:
            rep['client'] = None
        return rep


class CustomMinimalUpdateSerializer(serializers.Serializer):
    class MonthlyMinimal(serializers.Serializer):
        month = serializers.ChoiceField(
            choices=[
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
            ]
        )
        amount = serializers.FloatField()

    product = serializers.IntegerField()
    minimals = serializers.ListField(child=MonthlyMinimal())

    def save(self, **kwargs):
        cart_id = self.data.get('cart')
        if models.Cart.objects.filter(pk=cart_id).exists():
            items = self.data.get('items')
            for item in items:
                product_id = item.get('product')
                if not models.Product.objects.filter(pk=product_id).exists():
                    raise ValidationError({'error': f"{product_id} - Product topilmadi"})

                amount = item.get('amount')
                models.CartItem.objects.create(cart_id=cart_id, amount=amount, product_id=product_id)
        else:
            raise ValidationError({'error': "Cart topilmadi"})


class ReturnPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReturnPrice
        fields = ("price", "currency", "description")


class PurchaseSerializer(serializers.Serializer):
    """ Ushbu serializer CartItem, Cart va Shop larni bitta
        requestda yaratish uchun foydalaniladi """

    class ReturnPriceSerializer(serializers.Serializer):
        price = serializers.FloatField()
        currency = serializers.ChoiceField(choices=models.ReturnPrice.Currency)
        description = serializers.CharField(max_length=250, allow_null=True, required=False)

    class PurchaseItem(serializers.Serializer):

        product = serializers.IntegerField()
        amount = serializers.FloatField()
        expire_date = serializers.DateField(required=False, allow_null=True)

    items = serializers.ListField(child=PurchaseItem())
    return_price = serializers.ListField(child=ReturnPriceSerializer(), required=False, allow_null=True)
    client = PrimaryKeyRelatedField(queryset=models.Client.objects.all(),
                                    required=False, allow_null=True)
    check_number = serializers.IntegerField()
    card = serializers.FloatField()
    loan_sum = serializers.FloatField()
    cash_sum = serializers.FloatField()
    discount_sum = serializers.FloatField()
    discount_dollar = serializers.FloatField()
    loan_dollar = serializers.FloatField()
    cash_dollar = serializers.FloatField()
    transfer = serializers.FloatField()
    traded_at = serializers.DateTimeField()

    def save(self, **kwargs):
        user = self.context['request'].user
        # creating Cart
        cart = models.Cart.objects.create(status="finished")
        items = self.data.get('items')
        cart_item_id = 0
        for item in items:
            product_id = item.get('product')
            expire_date = item.get('expire_date')
            amount = item.get('amount')
            if not models.Product.objects.filter(pk=product_id).exists():
                cart.delete()
                raise ValidationError({'error': f"{product_id} - Product topilmadi"})

            cartitem = models.CartItem.objects.create(cart=cart, amount=amount, product_id=product_id)
            cartitem.expire_date = expire_date
            cartitem.save()
            if cartitem.product.category and cartitem.product.category.is_mobile:
                cart.status = 'waiting_loading'
                cart.save()
            # cart_item_id = cartitem.get("id")
            # print(cart_item_id)
        return_price = self.data.get("return_price")
        print(return_price)
        # creating CartItems and adding them to the Cart
        if return_price is not None:
            for item in return_price:
                price = item.get("price")
                currency = item.get("currency")
                description = item.get("description")
                returnprice = models.ReturnPrice.objects.create(cart_item=cartitem, price=price, currency=currency,
                                                                description=description)
                returnprice.save()
            # creating Shop ...
        shop = models.Shop.objects.create(
            seller=user,
            branch=user.branch,
            section=user.section,
            client_id=self.data.get('client', None),
            check_number=self.data.get('check_number', 0),
            card=self.data.get('card'),
            loan_sum=self.data.get('loan_sum'),
            cash_sum=self.data.get('cash_sum'),
            discount_sum=self.data.get('discount_sum'),
            discount_dollar=self.data.get('discount_dollar'),
            loan_dollar=self.data.get('loan_dollar'),
            cash_dollar=self.data.get('cash_dollar'),
            transfer=self.data.get('transfer'),
            traded_at=self.data.get('traded_at')
        )
        # ... associating it with Cart
        cart.shop = shop
        cart.save()
        # check if there is a loan and add it to client loan
        if shop.client:
            if shop.loan_dollar != 0:
                shop.client.loan_dollar += shop.loan_dollar
                shop.client.save()

            if shop.loan_sum != 0:
                shop.client.loan_sum += shop.loan_sum
                shop.client.save()
        # remove product from branch warehouse
        for cart_item in shop.cart.cartitem_set.all():
            product = cart_item.product
            pro_through_branch = models.ProductThroughBranch.objects.filter(product=product,
                                                                            branch=user.branch).first()
            products_meta = pro_through_branch.product_meta.filter(product_through_branch_id=pro_through_branch)
            for product_meta in products_meta:
                product_meta.amount -= cart_item.amount
                product_meta.save()


class CartItemSerializer(serializers.Serializer):
    class Item(serializers.Serializer):
        product = serializers.IntegerField()
        amount = serializers.FloatField()
        is_bonus = serializers.BooleanField(default=False)
        percent = serializers.FloatField(allow_null=True)
        commit = serializers.CharField(max_length=250, allow_null=True, allow_blank=True)
        expire_date = serializers.DateField(required=False, allow_null=True)

    cart = serializers.IntegerField()
    items = serializers.ListField(child=Item())

    def save(self, **kwargs):
        cart_id = self.data.get('cart')
        if models.Cart.objects.filter(pk=cart_id).exists():
            items = self.data.get('items')
            for item in items:
                product_id = item.get('product')
                expire_date = item.get('expire_date')
                amount = item.get('amount')
                if not models.Product.objects.filter(pk=product_id).exists():
                    raise ValidationError({'error': f"{product_id} - Product topilmadi"})

                cartitem = models.CartItem.objects.create(cart_id=cart_id,
                                                          amount=amount, product_id=product_id)
                cartitem.expire_date = expire_date
                cartitem.save()
        else:
            raise ValidationError({'error': "Cart topilmadi"})


class CartItemDetailSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.CartItem
        fields = [
            "id",
            "amount",
            "expire_date",
            "selling_price",
            "product",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductWithoutDetailSerializer(instance.product).data
        rep['cart'] = instance.cart.id
        rep['cart_status'] = instance.cart.status
        return rep


class CartSerializer(serializers.ModelSerializer):
    shop = PrimaryKeyRelatedField(queryset=models.Shop.objects.all(), allow_null=True)

    class Meta:
        model = models.Cart
        fields = [
            "id",
            "shop",
            "status",
            "created_at",
        ]


class CartDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = [
            "id",
            "status",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['items'] = CartItemDetailSerializer(instance.cartitem_set.all(), many=True).data
        rep['seller'] = StaffDataForShopSerializer(instance.shop.seller).data if instance.shop else None
        rep['client'] = ClientSerializer(instance.shop.client).data if instance.shop else None
        return rep


class ShopSerializerForToday(serializers.ModelSerializer):
    class Meta:
        model = models.Shop
        fields = ("id", "card", "cash_sum", "cash_dollar", "loan_sum", "loan_dollar", "transfer", "traded_at")


class ShopSerializer(serializers.ModelSerializer):
    client = PrimaryKeyRelatedField(queryset=models.Client.objects.all())
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())
    section = PrimaryKeyRelatedField(queryset=models.Section.objects.all())
    seller = PrimaryKeyRelatedField(queryset=models.Staff.objects.all())
    cart_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.Shop
        fields = [
            "id",
            "check_number",
            "cart_id",
            "client",
            "branch",
            "section",
            "seller",
            "traded_at",
            "card",
            "loan_sum",
            "loan_dollar",
            "discount_sum",
            "discount_dollar",
            "cash_sum",
            "cash_dollar",
            "change_sum",
            "change_dollar",
            "transfer",
            "created_at",
        ]

    def create(self, validated_data):
        cart_id = self.initial_data.get('cart_id')
        print("cart_id", cart_id)
        section = validated_data['section']
        cash_sum = validated_data['cash_sum']
        section.total_sum += cash_sum
        section.total_dollar += validated_data['cash_dollar']
        section.total_card += validated_data['card']
        section.total_loan_sum += validated_data['loan_sum']
        section.total_loan_dollar += validated_data['loan_dollar']
        section.total_card += validated_data['transfer']
        section.save()
        if models.Cart.objects.filter(pk=cart_id).exists():
            print("cart", cart_id)
            cart = models.Cart.objects.get(id=cart_id)
            shop = super().create(validated_data)
            cart.shop = shop
            cart.save()
            return shop
        else:
            raise ValidationError({'error': "Cart topilmadi"})

    def validate(self, attrs):
        del attrs['cart_id']
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['client'] = ClientSerializer(instance.client).data if instance.client else None
        ret['branch'] = BranchSerializer(instance.branch).data
        ret['seller'] = StaffDataForShopSerializer(instance.seller).data
        ret['section'] = SectionSerializer(instance.section).data
        return ret


class ShopDetailSerializer(serializers.ModelSerializer):
    client = PrimaryKeyRelatedField(queryset=models.Client.objects.all())
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())
    seller = PrimaryKeyRelatedField(queryset=models.Staff.objects.all())

    class Meta:
        model = models.Shop
        fields = [
            "id",
            "cart",
            "check_number",
            "client",
            "branch",
            "seller",
            "traded_at",
            "card",
            "loan_sum",
            "cash_sum",
            "discount_sum",
            "loan_dollar",
            "discount_dollar",
            "transfer",
            "cash_dollar",
            "change_sum",
            "change_dollar",
            "created_at",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['client'] = ClientSerializer(instance.client).data
        ret['branch'] = BranchSerializer(instance.branch).data
        ret['seller'] = StaffDataForShopSerializer(instance.seller).data
        ret['cart'] = CartDetailSerializer(instance.cart).data
        return ret


class BranchSerializerForAccountant(serializers.ModelSerializer):
    class Meta:
        model = models.Branch
        fields = ("id",)

    def to_representation(self, instance):
        data = super(BranchSerializerForAccountant, self).to_representation(instance)
        shops = instance.shops_in_branch.filter(traded_at__day=today.today().day)
        data['cash_sum'] = 0
        data["cash_dollar"] = 0
        data["card"] = 0
        data['loan_sum'] = 0
        data['loan_dollar'] = 0
        data['discount_sum'] = 0
        data['discount_dollar'] = 0
        data['transfer'] = 0
        data['change_sum'] = 0
        data['change_dollar'] = 0
        for i in shops:
            data['cash_sum'] += i.cash_sum
            data['cash_dollar'] += i.cash_dollar
            data["card"] += i.card
            data['loan_sum'] += i.loan_sum
            data['loan_dollar'] += i.loan_dollar
            data['discount_sum'] += i.discount_sum
            data['discount_dollar'] += i.discount_dollar
            data['transfer'] += i.transfer
            data['change_sum'] += i.change_sum
            data["change_dollar"] += i.change_dollar
        return_prices = models.ReturnPrice.objects.filter(cart_item__cart__shop__in=shops)
        for i in return_prices:
            if i.currency == "sum":
                data["cash_sum"] -= i.price
            elif i.currency == "dollar":
                data["cash_dollar"] -= i.price
        return data


class AccountantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Accountant
        fields = "__all__"

    # def create(self, validated_data):
    #     company = validated_data['company']
    #     company.balance_sum += validated_data['cash_sum']
    #     company.balance_dollar += validated_data['cash_dollar']
    #     company.balance_card += validated_data['card']
    #     company.balance_transfer += validated_data['transfer']
    #     company.save()
    #     data = super(AccountantSerializer, self).create(validated_data)
    #     return data


class ShopReportSerializer(serializers.ModelSerializer):
    client = PrimaryKeyRelatedField(queryset=models.Client.objects.all())

    class Meta:
        model = models.Shop
        fields = [
            "id",
            "client",
            "check_number",
            "traded_at",
            "card",
            "loan_sum",
            "created_at",
            "cash_sum",
            "discount_sum",
            "loan_dollar",
            "discount_dollar",
            "transfer",
            "cash_dollar",
            "change_sum",
            "change_dollar",
        ]


class ActiveCheckSerializer(serializers.ModelSerializer):
    seller = StaffDataForShopSerializer()

    class Meta:
        model = models.Shop
        fields = [
            "id",
            "seller",
            "total_summa",
            "created_at"
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['status'] = instance.cart.status
        return ret


class ActiveCheckDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Shop
        fields = [
            "id"
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        products = instance.cart.cartitem_set.all()
        ret['products'] = [
            {
                'name': item.product.name,
                'amount': item.amount,
                'price': item.selling_price,
                'summa': item.total_summa
            } for item in products
        ]
        return ret


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Realize
        fields = [
            "id",
            "purpose",
            "created_at",
        ]


class ProductRequestSerializer(serializers.ModelSerializer):
    created_by = PrimaryKeyRelatedField(queryset=models.Staff.objects.all())
    reviewed_by = PrimaryKeyRelatedField(queryset=models.Deliver.objects.all(),
                                         required=False)
    from_branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())
    to_branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all(),
                                       required=False)

    class Meta:
        model = models.ProductRequest
        fields = [
            "id",
            "from_branch",
            "to_branch",
            "created_by",
            "reviewed_by",
            "status",
            "comment",
            "created_at",
            "last_updated"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['from_branch'] = BranchSerializer(instance.from_branch).data
        rep['to_branch'] = BranchSerializer(instance.to_branch
                                            ).data if instance.to_branch else None
        rep['created_by'] = StaffWithNameSerializer(instance.created_by).data
        rep['reviewed_by'] = StaffWithNameSerializer(instance.reviewed_by).data
        rep['products'] = ProductRequestItemSerializer(
            instance.productrequestitem_set.all(), many=True).data
        return rep

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['status'] = "requested"
        validated_data['from_branch'] = self.context['request'].user.branch
        data = super().create(validated_data)
        return data


class ProductRequestItemSerializer(serializers.ModelSerializer):
    product_request = PrimaryKeyRelatedField(queryset=models.ProductRequest.objects.all())
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())
    cost = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = models.ProductRequestItem
        fields = [
            "id",
            "product_request",
            "product",
            "amount",
            "selling_price",
            "cost",
            "expire_date"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductWithoutDetailSerializer(instance.product)
        return rep

    # def create(self, validated_data):
    #     product = validated_data['product']
    #     amount = validated_data['amount']
    #     expire_date = validated_data.get('expire_date', None)
    #     branch = validated_data['from_branch']
    #     pro_through_branch = models.ProductThroughBranch.objects.filter(branch=branch,
    #                                                                     product=product).first()
    #     if not pro_through_branch:
    #         raise ValidationError({'error': "Ushbu filialda bunday tovar yo'q."})
    #     pro_meta = models.ProductMeta.objects.filter(product_through_branch=pro_through_branch,
    #                                                   expire_date=expire_date).first()
    #     if not pro_meta:
    #         raise ValidationError({'error': "Ushbu filialda bunday srokli tovar yo'q."})
    #     if pro_meta.amount < amount:
    #         raise ValidationError({'error': 
    #             f"Ushbu filialda srogi {expire_date} bo'lgan {amount} ta tovar mavjud emas."})
    #     data = super().create(validated_data)
    #     return data


class ProviderInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProviderInvoice
        fields = [
            "id",
            "deliver",
            "to_branch",
            "created_by",
            "name",
            "status",
            "comment",
            "delivery_date",
            "created_at",
            "last_updated"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['deliver'] = DeliverSerializer(instance.to_branch).data
        rep['to_branch'] = BranchSerializer(instance.to_branch).data
        rep['created_by'] = StaffWithNameSerializer(instance.created_by).data
        rep['products'] = ProviderInvoiceItemSerializer(instance.items.all(),
                                                        many=True).data
        return rep

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['status'] = "preparing"
        data = super().create(validated_data)
        return data


class ProviderInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProviderInvoiceItem
        fields = [
            "id",
            "invoice",
            "product",
            "amount",
            "selling_price",
            "cost",
            "expire_date",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductWithoutDetailSerializer(instance.product).data
        return rep


class PriceTypeProductReceiptSerializer(serializers.ModelSerializer):
    deliver = serializers.PrimaryKeyRelatedField(queryset=models.Deliver.objects.all(), required=False, allow_null=True)
    # client = serializers.PrimaryKeyRelatedField(allow_null=True, many=True, queryset=models.Client.objects.all())

    class Meta:
        model = models.PriceType
        fields = ("id", "title", 'deliver', "client")


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Warehouse
        fields = ("id", "title", "staff", "branch")


class ProductReceiptSerializer(serializers.ModelSerializer):
    # staff = PrimaryKeyRelatedField(queryset=models.Staff.objects.all())
    # deliver = PrimaryKeyRelatedField(queryset=models.Deliver.objects.all(),
    #                                  required=False, allow_null=True)
    # to_branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all(), required=False, allow_null=True)
    # price_type = PrimaryKeyRelatedField(queryset=models.PriceType.objects.all(), required=False, allow_null=True)
    # warehouse = PrimaryKeyRelatedField(queryset=models.Warehouse.objects.all(), required=False, allow_null=True)
    # currency = PrimaryKeyRelatedField(queryset=models.Currency.objects.all())

    class Meta:
        model = models.ProductReceipt
        fields = [
            "id",
            "deliver",
            # "from_branch",
            # "to_branch",
            "staff",
            "price_type",
            "warehouse",
            "currency",
            "name",
            "comment",
            "status",
            "summa_sum_selling_price",
            "summa_dollar_selling_price",
            "summa_sum_arrival_price",
            "summa_dollar_arrival_price",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['deliver'] = DeliverSerializer(instance.deliver
                                           ).data if instance.deliver else None
        # rep['from_branch'] = BranchSerializer(instance.from_branch
        #                                       ).data if instance.from_branch else None
        # rep['to_branch'] = BranchSerializer(instance.to_branch).data
        rep['staff'] = StaffWithNameSerializer(instance.staff).data
        rep['price_type'] = PriceTypeProductReceiptSerializer(instance.price_type).data
        rep['warehouse'] = WarehouseSerializer(instance.warehouse).data
        rep['products'] = ProductReceiptItemSerializer(instance.items.all(),
                                                       many=True).data
        return rep

    def create(self, validated_data):
        validated_data['staff'] = self.context['request'].user
        validated_data['to_branch'] = self.context['request'].user.branch
        print("validated_data")
        data = super().create(validated_data)
        return data
    

class ProductReceiptItemSerializer(serializers.ModelSerializer):
    receipt = PrimaryKeyRelatedField(queryset=models.ProductReceipt.objects.all())
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.ProductReceiptItem
        fields = [
            "id",
            "receipt",
            "product",
            "amount",
            "selling_price",
            "cost",
            "comment",
            "percent",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductWithoutDetailSerializer(instance.product).data
        return rep

    def create(self, validated_data):
        cost = validated_data['cost']
        product_receipt_item = None
        if cost == float(0):
            product_receipt_item = self.Meta.model.objects.create(**validated_data, is_bonus=True)
            product_receipt_item.save()
        else:
            selling_price = validated_data.pop("selling_price")

            if selling_price != float(0):
                percent = (selling_price - cost) / 100
                product_receipt_item = self.Meta.model.objects.create(**validated_data, is_bonus=False)
                product_receipt_item.percent = percent
                product_receipt_item.save()
            if selling_price == float(0):
                percent = validated_data['percent']
                selling_price = cost + (cost * percent / 100)
                product_receipt_item = self.Meta.model.objects.create(**validated_data, is_bonus=False)
                product_receipt_item.selling_price = selling_price
                product_receipt_item.save()
        return product_receipt_item


class DiscountProductReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DiscountProductReceipt
        fields = "__all__"


class InvoiceAcceptListSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField()
    invoice_list = serializers.ListField(child=serializers.IntegerField())
    expense = serializers.FloatField()


class InvoiceSerializer(serializers.ModelSerializer):
    staff = PrimaryKeyRelatedField(queryset=models.Staff.objects.all())
    deliver = PrimaryKeyRelatedField(queryset=models.Deliver.objects.all(), required=False)
    to_branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all(), write_only=True)
    from_branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all(), write_only=True)
    section = PrimaryKeyRelatedField(queryset=models.Section.objects.all(),
                                     required=False, write_only=True)

    class Meta:
        model = models.Invoice
        fields = [
            "id",
            "staff",
            "deliver",
            "from_branch",
            "to_branch",
            "section",
            "expense",
            "summa_sum",
            "summa_dollar",
            "name",
            "status",
            "created_at",
            "last_updated",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['to_branch'] = BranchSerializer(instance.to_branch
                                                       ).data if instance.to_branch else None
        representation['from_branch'] = BranchSerializer(instance.from_branch).data
        representation['staff'] = StaffWithNameSerializer(instance.staff).data
        representation['section'] = StaffWithNameSerializer(instance.section
                                                            ).data if instance.section else None
        return representation
    #
    # def update(self, instance, validated_data):
    #     if validated_data.get('status') == 'accepted':
    #         for invoiceitem in instance.invoiceitem_set.all():
    #             product = invoiceitem.product
    #             product.selling_price = invoiceitem.selling_price
    #             product.save()
    #     return super().update(instance, validated_data)


class BrokenProductSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())
    section = PrimaryKeyRelatedField(queryset=models.Section.objects.all(), required=False)
    created_by = PrimaryKeyRelatedField(queryset=models.Staff.objects.all(), required=False)
    reviewed_by = PrimaryKeyRelatedField(queryset=models.Staff.objects.all(), required=False)

    class Meta:
        model = models.BrokenProduct
        fields = [
            "id",
            "product",
            "branch",
            "section",
            "comment",
            "created_by",
            "broken_date",
            "amount",
            "expire_date",
            "status",
            "reviewed_by",
            "created_at",
            "last_updated"
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['status'] = "pending"
        branch = validated_data['branch']
        product = validated_data['product']
        amount = validated_data['amount']
        expire_date = validated_data.get('expire_date', None)
        pro_through_branch = models.ProductThroughBranch.objects.filter(branch=branch,
                                                                        product=product).first()
        if not pro_through_branch:
            raise ValidationError({'error': "Ushbu filialda bunday tovar yo'q."})
        pro_meta = models.ProductMeta.objects.filter(product_through_branch=pro_through_branch,
                                                     expire_date=expire_date).first()
        if not pro_meta:
            raise ValidationError({'error': "Ushbu filialda bunday srogli tovar yo'q."})
        if pro_meta.amount < amount:
            raise ValidationError({'error':
                                       f"Ushbu filialda srogi {expire_date} bo'lgan {amount} ta tovar mavjud emas."})
        data = super().create(validated_data)
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductWithoutDetailSerializer(instance.product).data
        representation['branch'] = BranchSerializer(instance.branch).data
        if instance.section:
            representation['section'] = SectionSerializer(instance.section).data
        representation['created_by'] = StaffWithNameSerializer(instance.created_by).data
        if instance.reviewed_by:
            representation['reviewed_by'] = StaffWithNameSerializer(instance.reviewed_by).data
        return representation


class MinimalWithoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Minimal
        fields = [
            "id",
            "amount",
            "month",
        ]


class MinimalSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.Minimal
        fields = [
            "id",
            "product",
            "amount",
            "month",
            "created_at",
        ]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = [
            "id",
            "type",
            "first_name",
            "last_name",
            "address",
            "birth_date",
            "phone_1",
            "phone_2",
            "loan_sum",
            "loan_dollar",
            "return_date",
            "discount_card",
            "ball",
            "created_at",
            "is_active"
        ]


class ClientWithDiscountCardSerializer(serializers.ModelSerializer):
    discount_card = PrimaryKeyRelatedField(queryset=models.DiscountCard.objects.all())

    class Meta:
        model = models.Client
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_1",
            "phone_2",
            "address",
            "return_date",
            "loan_dollar",
            "loan_sum",
            "ball",
            "discount_card",
            "created_at",
            "is_active",

        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['discount_card'] = None
        if instance.discount_card:
            representation['discount_card'] = DiscountCardSerializer(
                instance.discount_card).data
        return representation


class ClientLoanSerializer(serializers.ModelSerializer):
    client = PrimaryKeyRelatedField(queryset=models.Client.objects.all())
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())
    staff = PrimaryKeyRelatedField(queryset=models.Staff.objects.all(),
                                   required=False, allow_null=True)

    class Meta:
        model = models.ClientLoan
        fields = [
            "client",
            "branch",
            "staff",
            "loan_dollar",
            "loan_sum",
            "return_date",
            "last_updated",
        ]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['client'] = ClientSerializer(instance.client).data
        repr['branch'] = BranchSerializer(instance.branch).data
        if instance.staff:
            repr['staff'] = StaffWithNameSerializer(instance.staff).data
        return repr


class InventoryInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InventoryInvoice
        fields = [
            "id",
            "status",
            "created_at",
        ]

    def validate(self, attrs):
        request = self.context['request']
        attrs['controller'] = request.user
        attrs['branch'] = request.user.branch
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['controller'] = StaffWithNameSerializer(instance.controller).data
        ret['branch'] = BranchSerializer(instance.branch).data
        return ret


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InventoryItem
        fields = [
            "id",
            "product",
            "inventory",
            "real_amount",
            "in_program_amount",
            "difference_sum",
            "difference_dollar",
            "created_at",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['product'] = ProductSerializer(instance.product).data
        return ret


class ProductMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductMeta
        fields = [
            "id",
            "amount",
            "cost",
        ]


class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Producer
        fields = [
            "id",
            "name",
            "address",
            "country"
        ]


class ClientStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            "imminent_payment",
            "missed_payment",
        ]
    )


def generate_number(n):
    def prefill(num):
        return [1, 3, 2, 0], num - 4

    def finalize(nums):
        check_sum = 0
        check_offset = (len(nums) + 1) % 2

        for i, num in enumerate(nums):
            if (i + check_offset) % 2 == 0:
                n_ = num * 2
                check_sum += n_ - 9 if n_ > 9 else n_
            else:
                check_sum += num
        return nums + [10 - (check_sum % 10)]

    initial, rem = prefill(n)
    so_far = initial + [randint(1, 9) for x in range(rem - 1)]
    card_number = "".join(map(str, finalize(so_far)))

    return card_number


class ProductThroughBranchSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all(), required=False)
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())

    class Meta:
        model = models.ProductThroughBranch
        fields = [
            "product",
            "branch",
            "selling_price",
            "normative",
            "get_cost",
            "get_amount",
            "status",
            "created_at",

        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['product'] = ProductWithoutDetailSerializer(instance.product).data
        return ret


class ProductThroughBranchWithMetaSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all(), required=False)
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())

    class Meta:
        model = models.ProductThroughBranch
        fields = [
            "product",
            "branch",
            "selling_price",
            "normative",
            "get_cost",
            "get_amount",
            "status",
            "created_at",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['product'] = ProductWithoutDetailSerializer(instance.product).data
        ret['variants'] = ProductMetaSerializer(instance.product_meta.filter(amount__gt=0), many=True).data
        return ret


class SectionSerializerForProductWithoutDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = [
            "id",
            "name",
            "branch",
            # "created_at",
        ]


class ProductWithoutDetailSerializer(serializers.ModelSerializer):
    deliver = PrimaryKeyRelatedField(queryset=models.Deliver.objects.all())
    producer = PrimaryKeyRelatedField(queryset=models.Producer.objects.all())
    section = SectionSerializerForProductWithoutDetailSerializer()
    category = CategorySerializer()

    class Meta:
        model = models.Product
        fields = [
            "id",
            "category",
            "section",
            "deliver",
            "producer",
            "currency",
            "name",
            "ball",
            "measurement",
            "monthly_minimal_amout",
            "cost",
            "barcode",
            "created_at",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.producer:
            ret['producer'] = ProducerSerializer(instance.producer).data
        return ret


class ProductMeta(serializers.ModelSerializer):
    class Meta:
        model = models.ProductMeta
        fields = ("id", "amount", "cost", "expire_date")


class BranchSerializerForProduct(serializers.ModelSerializer):
    class Meta:
        model = models.Branch
        fields = [
            "id",
        ]


class BarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Barcode
        fields = ("id", "barcode",)


class ProductSerializer(serializers.ModelSerializer):
    section = PrimaryKeyRelatedField(queryset=models.Section.objects.all(), required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=models.Branch.objects.all(),
                                                many=True, required=False)
    category = PrimaryKeyRelatedField(queryset=models.Category.objects.all())
    # deliver = PrimaryKeyRelatedField(queryset=models.Deliver.objects.all(), required=False)
    producer = PrimaryKeyRelatedField(queryset=models.Producer.objects.all(), required=False)
    product_meta = ProductMetaSerializer()
    barcode = BarcodeSerializer(many=True)

    class Meta:
        model = models.Product
        fields = [
            "id",
            "category",
            "branch",
            "section",
            "deliver",
            "producer",
            "currency",
            "name",
            "ball",
            "measurement",
            "monthly_minimal_amout",
            "cost",
            "barcode",
            "product_meta",
            "created_at",
        ]

    def to_representation(self, instance):
        ret = super(ProductSerializer, self).to_representation(instance=instance)

        print(self.context['request'].user)
        if instance.category:
            ret['category'] = CategorySerializer(instance.category).data
        branch = self.context['request'].user.branch
        section = self.context['request'].user.section
        if section:
            ret['section'] = SectionSerializer(section).data
        if branch and branch in instance.branch.all():
            ret['branch'] = BranchSerializer(branch).data
            product_though_branch = instance.productthroughbranch_set.filter(branch=branch).first()
            if product_though_branch:
                ret['selling_price'] = product_though_branch.selling_price
                product_meta = product_though_branch.product_meta.all()
                product_amount = sum([productmeta['amount'] for productmeta in product_meta.values('amount')])
                serializer_product_meta_data = ProductMetaSerializer(product_meta, many=True).data
                ret['expire_dates'] = serializer_product_meta_data
                ret['all_amount'] = product_amount
        if instance.producer:
            ret['producer'] = ProducerSerializer(instance.producer).data
        return ret

    # def validate(self, attrs):
    #     print(attrs)
    #     card = attrs.get('barcode')
    #     if not card:
    #         attrs['barcode'] = generate_number(13)
    #     return super().validate(attrs)

    def create(self, validated_data):
        branch = validated_data.pop("branch")
        barcode = validated_data.pop("barcode")
        print(barcode)
        product_meta = validated_data.pop("product_meta")

        product = self.Meta.model.objects.create(**validated_data)
        for i in barcode:
            create_barcode = models.Barcode.objects.create(barcode=i.get("barcode"))
            product.barcode.add(create_barcode)
            product.save()
        for b in branch:
            product.branch.add(b)
        product.save()
        product_through_branch = models.ProductThroughBranch.objects.filter(product=product).first()
        product_meta = models.ProductMeta.objects.create(**product_meta, product=product,
                                                         product_through_branch_id=product_through_branch.id)
        return product


class ClientReturnCartSerializer(serializers.ModelSerializer):
    section = PrimaryKeyRelatedField(queryset=models.Section.objects.all(),
                                     required=False, allow_null=True)
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all(), required=False)
    staff = PrimaryKeyRelatedField(queryset=models.Staff.objects.all(), required=False)
    client = PrimaryKeyRelatedField(queryset=models.Client.objects.all(),
                                    required=False, allow_null=True)
    cart = PrimaryKeyRelatedField(queryset=models.Cart.objects.all())

    class Meta:
        model = models.ClientReturn
        fields = [
            "id",
            "section",
            "branch",
            "staff",
            "client",
            "cart",
            "comment",
            "status",
            "return_date",
            "took_date",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['section'] = SectionSerializer(instance.section).data
        rep['branch'] = BranchSerializer(instance.branch).data
        rep['staff'] = StaffWithNameSerializer(instance.staff).data
        rep['client'] = ClientSerializer(instance.client).data
        rep['cart'] = CartDetailSerializer(instance.cart).data
        rep['items'] = ClientReturnCartItemSerializer(instance.clientreturnitem_set.all(),
                                                      many=True).data
        return rep

    def create(self, validated_data):
        validated_data['section'] = self.context['request'].user.section
        validated_data['branch'] = self.context['request'].user.branch
        validated_data['staff'] = self.context['request'].user
        validated_data['status'] = 'processing'
        data = super().create(validated_data)
        return data


class ClientReturnCartItemSerializer(serializers.ModelSerializer):
    return_cart = PrimaryKeyRelatedField(queryset=models.ClientReturn.objects.all())
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.ClientReturnItem
        fields = [
            "id",
            "return_cart",
            "product",
            "amount",
            "expire_date",
            "comment",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductWithoutDetailSerializer(instance.product).data
        return rep

    def create(self, validated_data):
        cart = validated_data['return_cart'].cart
        branch = self.context['request'].user.branch
        product = validated_data['product']
        expire_date = validated_data.get('expire_date', None)
        amount = validated_data['amount']
        buyed_product = cart.cartitem_set.filter(product=product,
                                                 expire_date=expire_date).first()
        if not buyed_product:
            raise serializers.ValidationError('Mijoz ushbu tovarni sotib olmagan.')
        elif buyed_product.amount < amount:
            raise serializers.ValidationError('Mijoz sotib olgan tovarlar soni bundan kam.')
        data = super().create(validated_data)
        return data


class ClientReturnReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientReturn
        fields = [
            "id",
            "client",
            "total_sum",
            "total_dollar",
            "comment",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['client'] = {
            'id': instance.client.id,
            'name': instance.client.full_name,
            'phone_number': instance.client.phone_1,
            'address': instance.client.address
        }
        return rep


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = [
            "id",
            "name",
            # "created_at",
        ]


class ProductMoveBranchItemSerializer(serializers.ModelSerializer):
    productmovegroup = PrimaryKeyRelatedField(queryset=models.ProductMoveBranchGroup.objects.all())
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())
    expire_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = models.ProductMoveBranchItem
        fields = [
            "id",
            "productmovegroup",
            "product",
            "amount",
            "expire_date",
            "selling_price",
            "get_summa",
            "last_updated",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductWithoutDetailSerializer(instance.product).data
        return rep

    def create(self, validated_data):
        pm_group = validated_data.get('productmovegroup')
        product = validated_data.get('product')
        expire_date = validated_data.get('expire_date', None)
        amount = validated_data.get('amount')
        from_branch = pm_group.from_branch
        product_through_branch = models.ProductThroughBranch.objects.filter(
            branch=from_branch, product=product).first()
        if expire_date:
            if not product_through_branch.productmeta_set.filter(expire_date=expire_date).exists():
                raise serializers.ValidationError('Bunday expire date li tovar mavjud emas')
            elif product_through_branch.productmeta_set.filter(
                    expire_date=expire_date).first().amount < int(amount):
                raise serializers.ValidationError('Ushbu filialda bunday (expire date li) tovarlar yetarli emas.')
        data = super().create(validated_data)
        return data


class ProductMoveBranchGroupSerializer(serializers.ModelSerializer):
    from_branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())
    to_branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())
    created_by = PrimaryKeyRelatedField(queryset=models.Staff.objects.all(), required=False)
    reviewed_by = PrimaryKeyRelatedField(queryset=models.Staff.objects.all(), required=False)

    class Meta:
        model = models.ProductMoveBranchGroup
        fields = [
            "id",
            "name",
            "status",
            "from_branch",
            "to_branch",
            "created_by",
            "reviewed_by",
            "summa_sum",
            "summa_dollar",
            "created_at",
            "last_updated"
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        data = super().create(validated_data)
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.to_branch:
            representation['to_branch'] = BranchSerializer(instance.to_branch).data
        if instance.from_branch:
            representation['from_branch'] = BranchSerializer(instance.from_branch).data
        if instance.created_by:
            representation['created_by'] = StaffWithNameSerializer(instance.created_by).data
        if instance.reviewed_by:
            representation['reviewed_by'] = StaffWithNameSerializer(instance.reviewed_by).data
        representation['products'] = ProductMoveBranchItemSerializer(instance.items, many=True).data
        return representation


class ReturnDeliverProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReturnDeliverProduct
        fields = [
            "id",
            "product",
            "deliver",
            "from_branch",
            "staff",
            "comment",
            "amount",
            "cost",
            "expire_date",
            "overall_summa",
            "created_at",
            "last_updated"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductWithoutDetailSerializer(instance.product).data
        rep['staff'] = StaffWithNameSerializer(instance.staff).data
        rep['from_branch'] = BranchSerializer(instance.from_branch).data
        rep['deliver'] = DeliverSerializer(instance.deliver).data
        return rep

    def create(self, validated_data):
        deliver = validated_data.get('deliver')
        branch = validated_data.get('from_branch')
        product = validated_data.get('product')
        expire_date = validated_data.get('expire_date', None)
        amount = validated_data.get('amount')
        cost = validated_data.get('cost')
        product_through_branch = models.ProductThroughBranch.objects.filter(branch=branch, product=product).first()
        if not product_through_branch.productmeta_set.filter(expire_date=expire_date).exists():
            raise serializers.ValidationError('Bunday expire date li tovar mavjud emas')
        elif product_through_branch.productmeta_set.filter(expire_date=expire_date).first().amount < int(amount):
            raise serializers.ValidationError('Ushbu filialda bunday (expire date li) tovarlar yetarli emas.')
        data = super().create(validated_data)
        # update branch products if productmove is approved
        if expire_date:
            product_meta = product_through_branch.productmeta_set.filter(expire_date=expire_date).first()
            product_meta.amount -= amount
            product_meta.save()

        if product.currency == 'sum':
            deliver.loan_sum -= amount * cost if cost > 0 else amount * product.cost
        else:
            deliver.loan_dollar -= amount * cost if cost > 0 else amount * product.cost
        deliver.save()

        return data


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = [
            "id",
            "real_currency",
            "created_at",
            "selling_currency",
            "ball_price",
        ]


class DifferProductRecieveHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DifferProductRecieveHistory
        fields = [
            "old_price",
            "traded_at",
            "created_at",
        ]


class ProductPriceChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductPriceChange
        fields = [
            "old_price",
            "new_price",
            "product",
            "amount",
            "created_at",
        ]


class ShowcaseSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.Showcase
        fields = [
            "product",
            "amount",
            "expire_date",
            "last_updated",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductWithoutDetailSerializer(instance.product).data
        rep['branch'] = BranchSerializer(instance.branch).data
        rep['dollar_summa'] = instance.dollar_summa
        rep['sum_summa'] = instance.sum_summa

    def create(self, validated_data):
        validated_data['branch'] = self.context['request'].user.branch
        product = validated_data['product']
        amount = validated_data['amount']
        expire_date = validated_data.get('expire_date', None)
        pro_through_branch = models.ProductThroughBranch.objects.filter(branch=validated_data['branch'],
                                                                        product=product).first()
        if not pro_through_branch:
            raise ValidationError({'error': "Ushbu filialda bunday tovar yo'q."})
        pro_meta = models.ProductMeta.objects.filter(product_through_branch=pro_through_branch,
                                                     expire_date=expire_date).first()
        if not pro_meta:
            raise ValidationError({'error': "Ushbu filialda bunday srogli tovar yo'q."})
        if pro_meta.amount < amount:
            raise ValidationError({'error':
                                       f"Ushbu filialda srogi {expire_date} bo'lgan {amount} ta tovar mavjud emas."})
        pro_meta.amount -= amount
        pro_meta.save()
        data = super().create(validated_data)
        return data


class StaffWithNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Staff
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


from django.contrib.auth.hashers import make_password


class StaffSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField('get_permissions')
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    branches = serializers.PrimaryKeyRelatedField(queryset=models.Branch.objects.all(),
                                                  many=True, required=False)
    # providers = BranchSerializer(many=True, required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=models.Branch.objects.all(),
                                                required=False, allow_null=True)
    section = serializers.PrimaryKeyRelatedField(queryset=models.Section.objects.all(),
                                                 required=False, allow_null=True)

    class Meta:
        model = models.Staff
        fields = (
            'password1', 'branch', 'password2', 'section', 'first_name', 'last_name',
            'username', "branches", "address", 'phone', 'birth_date', "status", 'role', 'permissions')
        # exclude = ['password']
        read_only_fields = ['date_joined', 'groups', 'user_permissions', 'is_staff', 'last_login', 'email',
                            'salary', 'is_superuser', ]

    def validate(self, data):
        if data.get('password1') and data.get('password2'):
            if data['password1'] != data['password2']:
                raise serializers.ValidationError('Passwords must match.')
        return data

    def create(self, validated_data):
        branches = validated_data.pop("branches")
        data = {
            key: value for key, value in validated_data.items()
            if key not in ('password1', 'password2')
        }
        data['password'] = validated_data['password1']
        data['username'] = data['username']
        user = self.Meta.model.objects.create_user(**data)
        for b in branches:
            user.branches.add(b)
        user.is_active = True
        # user.is_superuser = True
        user.save()
        request = self.context.get('request', None)
        if request and request.data.get('action') and request.data.get('page'):
            user_permission_obj = models.Permission.objects.create(user=user)
            for i in request.data['page']:
                user_permission_obj.page.add(i)
            for i in request.data['action']:
                user_permission_obj.action.add(i)
        return user

    def get_permissions(self, obj):
        return models.Permission.objects.filter(user_id=obj.id).values('page', 'action')


class StaffDataSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()
    branches = BranchSerializer(read_only=True, many=True)
    section = SectionSerializer()

    class Meta:
        model = models.Staff
        fields = [
            "id",
            "first_name",
            "last_name",
            "branch",
            "section",
            "branches",
            "address",
            "phone",
            "status",
            "role",
        ]


class BonusProductSerializer(serializers.ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.BonusProduct
        fields = [
            "id",
            "product",
            "cost",
            "amount",
            "created_at",
        ]


class ProducerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Producer
        fields = [
            "id",
            "name",
            "address",
            "country",
        ]


class ClientPaymentHistorySerializer(serializers.ModelSerializer):
    staff = PrimaryKeyRelatedField(queryset=models.Staff.objects.all(), required=False)
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all(), required=False)
    client = PrimaryKeyRelatedField(queryset=models.Client.objects.all(), required=False)

    class Meta:
        model = models.ClientPaymentHistory
        fields = [
            "staff",
            "branch",
            "client",
            "paid_at",
            "card",
            "cash_sum",
            "cash_dollar",
            "discount_sum",
            "discount_dollar",
            "transfer",
            "from_ball",
            "comment",
            "payment_for_loan",
            "created_at",

        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['client'] = ClientSerializer(instance.client).data
        ret['staff'] = StaffSerializer(instance.staff).data
        ret['branch'] = BranchSerializer(instance.branch).data
        return ret


class CheckModelSerializer(serializers.ModelSerializer):
    staff = CheckStaffModelSerializer()

    class Meta:
        model = models.Check
        fields = [
            "id",
            "staff",
            "get_all_sum",
            "status",
            "created_at",
        ]


class CheckItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CheckItem
        fields = [
            "id",
            "product_name",
            "amount",
            "created_at",
        ]


class InvoiceItemWithoutIdSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = models.InvoiceItem
        fields = [
            "id",
            "product",
            "get_summa",
            "amount",
            "selling_price",
            "expire_date",
            "status",
            "last_updated",
            "created_at",
        ]


class InvoiceItemSerializer(serializers.ModelSerializer):
    invoice = PrimaryKeyRelatedField(queryset=models.Invoice.objects.all())
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.InvoiceItem
        fields = [
            "id",
            "invoice",
            "product",
            "get_summa",
            "amount",
            "expire_date",
            "selling_price",
            "status",
            "last_updated",
            "created_at",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['product'] = ProductSerializer(instance.product, context=self.context).data
        return ret


class InvoiceItemForProductAnalysisSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer(read_only=True)
    product = PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.InvoiceItem
        fields = [
            "id",
            "invoice",
            "product",
            "get_summa",
            "amount",
            "expire_date",
            "selling_price",
            "status",
            "last_updated",
            "created_at",
        ]


class ProductAnalysisSerializer(serializers.ModelSerializer):
    section = PrimaryKeyRelatedField(queryset=models.Section.objects.all(), required=False)
    category = PrimaryKeyRelatedField(queryset=models.Category.objects.all())
    deliver = PrimaryKeyRelatedField(queryset=models.Deliver.objects.all())
    producer = PrimaryKeyRelatedField(queryset=models.Producer.objects.all(), required=False)

    class Meta:
        model = models.Product
        fields = [
            "id",
            "category",
            "branch",
            "section",
            "deliver",
            "producer",
            "currency",
            "name",
            "ball",
            "measurement",
            "monthly_minimal_amout",
            "cost",
            "barcode",
            "created_at",
            "last_updated"
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.category:
            ret['category'] = CategorySerializer(instance.category).data
        branch = self.context['request'].user.branch
        section = self.context['request'].user.section
        if section:
            ret['section'] = SectionSerializer(section).data
        if branch:
            ret['branch'] = BranchSerializer(branch).data
        product_though_branch = instance.productthroughbranch_set.filter(branch=branch).first()
        ret['selling_price'] = product_though_branch.selling_price
        product_meta = product_though_branch.productmeta_set.all()
        product_amount = sum([productmeta['amount'] for productmeta in product_meta.values('amount')])
        ret['current_amount'] = product_amount
        if instance.producer:
            ret['producer'] = ProducerSerializer(instance.producer).data
        if instance.deliver:
            ret['deliver'] = {'id': instance.deliver.id, 'name': instance.deliver.name}
        invoiceitems = instance.invoiceitem_set.filter(status="accepted").all()
        if from_day := self.context.get('last_updated__gte'):
            invoiceitems = invoiceitems.filter(last_updated__gte=from_day)
        if to_day := self.context.get('last_updated__lte'):
            invoiceitems = invoiceitems.filter(last_updated__lte=to_day)
        ret['recieved'] = InvoiceItemForProductAnalysisSerializer(invoiceitems, many=True).data
        ret['overall_recieved_amount'] = sum([item.amount for item in invoiceitems])
        return ret


class OutcomeSerializer(serializers.ModelSerializer):
    type = PrimaryKeyRelatedField(queryset=models.OutcomeType.objects.all())
    branch = PrimaryKeyRelatedField(queryset=models.Branch.objects.all())
    section = PrimaryKeyRelatedField(queryset=models.Section.objects.all())

    class Meta:
        model = models.Outcome
        fields = [
            "id",
            "branch",
            "section",
            "type",
            "status",
            "whom",
            "card",
            "sum",
            "dollar",
            "transfer",
            "comment",
            "created_at",
            "last_updated"
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['type'] = OutcomeTypeSerializer(instance.type).data
        ret['section'] = SectionSerializer(instance.section).data
        if instance.branch:
            ret['branch'] = BranchSerializer(instance.branch).data
        return ret

    def create(self, validated_data):
        branch = validated_data['branch']
        section = validated_data['section']
        print("section", section)
        sum = validated_data['sum']
        card = validated_data['card']
        dollar = validated_data['dollar']
        transfer = validated_data['transfer']
        print(validated_data)
        if branch.get_total_branch_shop_sum() >= sum and branch.get_total_branch_shop_card() >= card and branch.get_total_branch_shop_dollar() >= dollar and branch.get_total_branch_shop_transfer() >= transfer:
            outcome = models.Outcome.objects.create(**validated_data)
            outcome.save()
            section.total_sum -= sum
            section.total_dollar -= dollar
            section.total_card -= card
            section.total_card -= transfer
            section.save()
            return outcome
        else:
            raise serializers.ValidationError("Kiritilgan summa midori katta")


class OutcomeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OutcomeType
        fields = ["id", 'name']


class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        password = attrs.get('password')
        username = attrs.get("username")
        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            print("user", user)
            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = "Bunday user topilmadi, parolni tekshirib ko'ring"
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "password" and "username".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class TokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = StaffDataSerializer(instance=self.user, context=self.context).data
        return data


# class ChangeCurrencySerializer(serializers.ModelSerializer):
#
#     # chang_sum = serializers.SerializerMethodField()
#
#     class Meta:
#         model = models.Branch
#         fields = ("id", "chang_sum", "chang_dollar", "get_total_branch_shop_sum", "get_total_branch_shop_dollar")


class ChangeCurrencySerializer(serializers.ModelSerializer):
    # branch = serializers.PrimaryKeyRelatedField(queryset=models.Branch.objects.all(), required=False)
    # section = serializers.PrimaryKeyRelatedField(queryset=models.Section.objects.all(), required=False)

    class Meta:
        model = models.ChangeCurrency
        fields = ("id", "from_sum", "from_dollar", "currency", "changed_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        branch = self.context['request'].user.branch
        section = self.context['request'].user.section
        data['branch'] = BranchSerializer(instance.branch).data
        data['section'] = SectionSerializer(instance.section).data

        return data

    def create(self, validated_data):
        branch = self.context['request'].user.branch
        section = self.context['request'].user.section
        print(section)
        currency = validated_data['currency']
        from_dollar = validated_data['from_dollar']
        from_sum = validated_data["from_sum"]
        if section is not None:
            if currency == "dollar":
                if section.total_sum >= from_sum:
                    section.total_dollar += from_dollar
                    section.total_sum -= from_sum
                    section.save()
                else:
                    raise serializers.ValidationError("Kassadagi pul miqdori kam")
            else:
                if section.total_dollar >= from_dollar:
                    section.total_sum += from_sum
                    section.total_dollar -= from_dollar
                    section.save()
                else:
                    raise serializers.ValidationError("Kassada pul miqori kam")
        else:
            raise serializers.ValidationError("User kassaga biriktirilmagan")
        change_price = models.ChangeCurrency.objects.create(branch=branch, section=section, from_dollar=from_dollar,
                                                            from_sum=from_sum)
        change_price.save()
        return change_price
