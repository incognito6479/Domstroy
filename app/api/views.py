from datetime import datetime, timedelta
from operator import itemgetter

from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django_filters import rest_framework as filters
from rest_framework import viewsets, status, generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.compat import coreapi, coreschema
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema, coreapi as coreapi_schema
from rest_framework.views import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from django.db.models import Q

from rest_framework.views import APIView
from app import models, paginations
from app import serializers
from app.api import filter_params
from app.api.serializer import PageModelSerializer
from app.filters import ShopFilter

"""
SWAGGER DOCs

swagger: '2.0'
info:
  version: 0.0.0
  title: Markdown 
  description: |
    # Heading

    Text attributes _italic_, *italic*, __bold__, **bold**, `monospace`.

    Horizontal rule:

    ---

    Bullet list:

      * apples
      * oranges
      * pears

    Numbered list:

      1. apples
      2. oranges
      3. pears

    A [link](http://example.com).

    An image:
    ![Swagger logo](https://raw.githubusercontent.com/swagger-api/swagger-ui/master/dist/favicon-32x32.png)

    Code block:

    ```
    {
      "message": "Hello, world!"
    }
    ```

    Tables:

    | Column1 | Column2 |
    | ------- | --------|
    | cell1   | cell2   |
paths:
  /:
    get:
      responses:
        200:
          description: OK

"""


class GetActionApiView(APIView):
    """
    Page uchun Actionlarni ko'rsatadi
    """

    def get(self, request):
        actions = models.Action.objects.all().values('id', 'name')
        return Response({'actions': actions})


class GetPageApiView(APIView):
    """
    Permission uchun pagelarni ko'rsatadi
    """

    def get(self, request):
        pages = models.Page.objects.filter(parent=None)
        serializer = PageModelSerializer(pages, many=True)
        return Response({'pages': serializer.data})


# class PermissionViewSet(viewsets.ModelViewSet):
#     model = models.Permission


class DiscountCardViewSet(viewsets.ModelViewSet):
    """Klientlar uchun chegirma kartasini yaratish hamda ro'yhatini olish"""

    queryset = models.DiscountCard.objects.all()
    pagination_class = paginations.CustomPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'card': ['exact'],
        'client': ['exact'],
        'client__type': ['exact'],
        'percentage': ['exact'],
        'created_at': ['gte', 'lte'],
        'last_updated': ['gte', 'lte']
    }
    search_fields = ['client__first__name', 'client__last_name',
                     'card', 'bonus_dollar', 'bonus_sum']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.DiscountCardDetailSerializer
        return serializers.DiscountCardSerializer


class CartViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'shop__id': ['exact'],
        'shop__branch__id': ['exact'],
        'status': ['exact'],
        'created_at': ['gte', 'lte'],
        'shop__traded_at': ['exact'],
    }
    search_fields = ['cartitem__product__name', 'shop__seller__first_name',
                     'shop__seller__last_name', 'shop__client__first_name',
                     'shop__client__last_name']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.CartDetailSerializer
        return serializers.CartSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.CartItem.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        'cart': ['exact'],
        'product__category__is_mobile': ['exact'],
        'cart__shop__branch': ['exact'],
        'cart__status': ['exact'],
        'created_at': ['gte', 'lte'],
    }

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.CartItemDetailSerializer
        return serializers.CartItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MakePurchaseViewSet(viewsets.ModelViewSet):
    """ Xarid tugagach CartItem, Cart va Shop haqidagi barcha ma'lumotlarni
        bitta request da yuborish orqali kerakli ma'lumotlarni bazada saqlash 
        uchun endpoint. """
    queryset = models.CartItem.objects.all()
    serializer_class = serializers.PurchaseSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        client_id = serializer.data['client']
        card = serializer.data['card']
        cash_sum = serializer.data['cash_sum']
        shop = models.Shop.objects.filter(client__id=client_id, seller=request.user,
                                          card=card, cash_sum=cash_sum).order_by('-created_at').first()
        # bonus from purchase will be added to discount card
        if shop.client and shop.client.discount_card:
            discount_card = shop.client.discount_card
            discount_card.bonus_sum += shop.total_sum * discount_card.percentage
            discount_card.bonus_dollar += shop.total_dollar * discount_card.percentage
            discount_card.save()
            # also balls computed & added to client balans
            shop.client.ball += shop.total_ball
            shop.client.save()

        data = serializers.ShopDetailSerializer(shop).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class RealizeViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.Realize.objects.all()
    serializer_class = serializers.ReleaseSerializer


class ProductRequestViewSet(viewsets.ModelViewSet):
    """ Tovar uchun so'rov yuborish. Avval so'rov yaratiladi va unga
        tovarlar qo'shiladi. STATUS => ('requested', 'accepted', 'finished', 'rejected').
    """

    queryset = models.ProductRequest.objects.all()
    serializer_class = serializers.ProductRequestSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def partial_update(self, request, *args, **kwargs):
        """Tovar so'rovidagi tovarlar qabul qilib olingach so'rov statusi
           'finished' ga o'zgartirilishi lozim.
        """
        instance = self.queryset.get(pk=kwargs.get('pk'))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        status = request.data.get('status', 'requested')
        updated_ins = serializer.save()

        if status in ['finished', 'accepted', 'rejected']:
            updated_ins.reviewed_by = request.user
            updated_ins.save()
            # remove product from branch warehouse if status = finished
            # from_branch = updated_ins.from_branch
            # to_branch = updated_ins.to_branch
            # for item in updated_ins.productrequestitem_set.all():
            #     product = item.product
            #     amount = item.amount
            #     expire_date = item.expire_date
            #     pro_through_bra_1 = models.ProductThroughBranch.objects.filter(
            #                                 branch=from_branch, product=product).first()
            #     pro_meta_1 = models.ProductMeta.objects.filter(
            #             product_through_branch=pro_through_bra_1, expire_date=expire_date
            #             ).first()
            #     pro_meta_1.amount -= amount
            #     pro_meta_1.save()
            #     pro_through_bra_2, created = models.ProductThroughBranch.objects.get_or_create(
            #                                                   branch=to_branch, product=product)
            #     if created:
            #         pro_through_bra_2.selling_price = item.selling_price
            #     pro_meta_2, created = models.ProductMeta.objects.get_or_create(
            #             product_through_branch=pro_through_bra_2, expire_date=expire_date)
            #     pro_meta_2.amount += amount
            #     pro_meta_2.save()

        return Response(self.serializer_class(instance=updated_ins).data)


class ProductRequestItemViewSet(viewsets.ModelViewSet):
    """ Tovar so'roviga tovarlarni qo'shish uchun endpoint. """

    queryset = models.ProductRequestItem.objects.all()
    serializer_class = serializers.ProductRequestItemSerializer


class InvoiceItemViewSet(viewsets.ModelViewSet):
    """Invoice(faktura) ichidagi invoiceitem uchun api"""

    queryset = models.InvoiceItem.objects.all()
    serializer_class = serializers.InvoiceItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'invoice': ['exact'],
        'product': ['exact'],
        'status': ['exact'],
    }
    search_fields = ['invoice__name', 'product__name', 'product__producer__name',
                     'product__barcode']


class BrokenProductViewSet(viewsets.ModelViewSet):
    """
    Tovarlarni biror sababga ko'ra (singan, muddati tugagan, yaroqsiz
    holga kelgan ...) hisobdan chiqarish. Ushbu endpointga kerakli ma'lumotlarni
    post qilish orqali tovarni hisobdan chiqarish uchun so'rov yaratiladi. 
    PS: status, created_by va reviewed_by ni post qilish shart emas. 
    STATUS ==>
        ('pending', 'pending') # yaratlgandagi status
        ('approved', 'approved') # tasdiqlangandagi status
        ('rejected', 'rejected') # rad etilgandagi status
    """

    queryset = models.BrokenProduct.objects.all()
    serializer_class = serializers.BrokenProductSerializer
    # permission_classes =
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'branch__id': ['exact'],
        'status': ['exact'],
    }
    search_fields = ['branch__name', 'created_by__name', 'product__name', 'reviewed_by__name']
    http_method_names = ['get', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        """Tovarni hisobdan chiqarishni tasdiqlash. 
           Ushbu amaliyotni faqatgina filial boshlig'i yoki undan ham yuqori
           lavozimdagi xodimlar bajara olishadi(head_of_branch, director, ceo).
           PATCH status ==> ('pending', 'approved', 'rejected')
        """
        instance = self.queryset.get(pk=kwargs.get('pk'))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        status = request.data.get('status', 'pending')
        if request.user.role in ('ceo', 'director') or (
                request.user.role == 'head_of_branch' and request.user in instance.branch.staff_set.all()):

            updated_ins = serializer.save()
            updated_ins.reviewed_by = request.user
            updated_ins.save()

            if status == 'approved':
                # remove product from branch warehouse
                branch = updated_ins.branch
                product = updated_ins.product
                amount = updated_ins.amount
                expire_date = updated_ins.expire_date
                pro_through_branch = models.ProductThroughBranch.objects.filter(branch=branch,
                                                                                product=product).first()
                pro_meta = models.ProductMeta.objects.filter(product_through_branch=pro_through_branch,
                                                             expire_date=expire_date).first()

                pro_meta.amount -= amount
                pro_meta.save()

            return Response(self.serializer_class(instance=updated_ins).data)
        else:
            raise PermissionDenied()


class ProviderInvoiceViewSet(viewsets.ModelViewSet):
    """ Ta'minotchi zayavka(faktura) yaratishi va uni qabul qilganda tasdiqlashi uchun endpoint
        STATUS => ('preparing', 'finished').
    """

    queryset = models.ProviderInvoice.objects.all()
    pagination_class = paginations.CustomPagination
    serializer_class = serializers.ProviderInvoiceSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'status': ['exact'],
        'to_branch': ['exact'],
    }
    search_fields = ['name', 'deliver__name']
    http_method_names = ['get', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        """Ta'minotchi zayavkadagi tovarlani qabul qilib olgach zayavka statusi
           'finished' ga o'zgartirilishi lozim.
        """
        instance = self.queryset.get(pk=kwargs.get('pk'))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        status = request.data.get('status', 'finished')
        updated_ins = serializer.save()

        if status == 'finished':
            # add product to branch warehouse
            to_branch = updated_ins.to_branch
            for item in updated_ins.items.all():
                product = item.product
                amount = item.amount
                expire_date = item.expire_date
                pro_through_branch, created = models.ProductThroughBranch.objects.get_or_create(
                    branch=to_branch, product=product)
                pro_meta, created = models.ProductMeta.objects.get_or_create(
                    product_through_branch=pro_through_branch, expire_date=expire_date)
                pro_meta.amount += amount
                pro_meta.save()
                if created:
                    pro_through_branch.selling_price = item.selling_price
        return Response(self.serializer_class(instance=updated_ins).data)


class ProviderInvoiceItemViewSet(viewsets.ModelViewSet):
    """ Ta'minotchi zayavkasiga tovarlarni qo'shish. """

    queryset = models.ProviderInvoiceItem.objects.all()
    serializer_class = serializers.ProviderInvoiceItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'invoice': ['exact'],
        'product': ['exact']
    }
    search_fields = ['invoice__name', 'product__name', 'product__producer__name',
                     'product__barcode']


class MinimalCreateAPIViewViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.Minimal.objects.all()
    serializer_class = serializers.MinimalSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        """
        Tovar uchun minimal miqdor qo'shish,
        Tovarni minimal miqdorini o'zgartirish, tovar va o'zgartiriladigan miqdor yuboriladi

        """
        product = request.data.get('product')
        amount = request.data.get('amount')
        month = request.data.get('month')
        if minimal := models.Minimal.objects.filter(month=month, product=product).first():
            minimal.amount = amount
            minimal.save()
            serializer = self.get_serializer(minimal)
            return Response(serializer.data)

        return super().create(request, *args, **kwargs)


class ClientViewSet(viewsets.ModelViewSet):
    """Mijozlar ro'yhatini ko'rish  """
    queryset = models.Client.objects.filter(Q(type="b2c") | (Q(type="b2b") & Q(is_active=True)))
    serializer_class = serializers.ClientSerializer

    pagination_class = paginations.CustomPagination
    permission_classes = [permissions.IsAuthenticated, ]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'id': ['exact'],
        'type': ['exact'],
        'first_name': ['icontains'],
        'address': ['icontains'],
        'phone_1': ['icontains'],
        'discount_card__card': ['exact'],
        # 'status': ['exact']
    }
    search_fields = ['first_name', 'last_name', 'phone_1', 'phone_2']

    def get_serializer_class(self):
        if self.action == 'status':
            return serializers.ClientStatusSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(manual_parameters=filter_params.get_client_params())
    @action(methods=['get'], detail=False)
    def status(self, request, *args, **kwargs):
        """
        imminent_payment(to'lovi yaqinlashib qolgan qarzdorlar)
        amissed_payment(to'lovi o'tib ketganlar)
        """
        status_ = request.GET.get('status')
        # if status_ in ['imminent_payment', 'missed_payment']:
        branch = request.user.branch
        if status_ == "imminent_payment":
            # query = models.Client.objects.filter(client_loan__return_date__gte=datetime.today())
            query = models.Client.objects.filter(client_loan__return_date__gte=datetime.today())
        elif status_ == "missed_payment":
            query = models.Client.objects.filter(client_loan__return_date__lte=datetime.today()).order_by(
                '-return_date')
        else:
            query = models.Client.objects.all().order_by('-return_date')
        query = self.filter_queryset(query)
        # query = query.filter(Q(clientloan_set__loan_sum__gt=0) | Q(clientloan_set__loan_dollar__gt=0))
        query = query.filter(Q(client_loan__loan_sum__gte=0) | Q(client_loan__loan_dollar__gte=0))
        if not request.GET.get('limit'):
            self.pagination_class.page_size = 30
            self.pagination_class.default_limit = 30
        page = self.paginate_queryset(query)
        if page is not None:
            serializer = serializers.ClientWithDiscountCardSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ClientWithDiscountCardSerializer(page, many=True)
        return Response(serializer.data)
        # else:
        #     query = models.Client.objects.all().order_by('-return_date')
        # return Response({"data": "status not"})

    @action(methods=['get'], detail=False)
    def history(self, request, *args, **kwargs):
        """
        Mijozning to'lovlar tarixi. Sana bo'yicha filterlash uchun 
        'paid_at_gte' (..dan) va 'paid_at_lte' (..gacha) parametrlaridan foydalaning.
        """

        client_id = request.GET.get('id')
        payment_history = models.ClientPaymentHistory.objects.filter(client_id=client_id
                                                                     ).order_by('-paid_at')
        paid_at_lte = request.GET.get('paid_at_lte')
        paid_at_gte = request.GET.get('paid_at_gte')
        if paid_at_gte:
            payment_history = payment_history.filter(paid_at__gte=paid_at_gte)
        if paid_at_lte:
            payment_history = payment_history.filter(paid_at__lte=paid_at_lte)
        page = self.paginate_queryset(payment_history)
        if page is not None:
            serializer_data = serializers.ClientPaymentHistorySerializer(page, many=True).data
            return self.get_paginated_response(serializer_data)
        serializer_data = serializers.ClientPaymentHistorySerializer(payment_history, many=True).data
        return Response(serializer_data)

    @swagger_auto_schema(manual_parameters=filter_params.get_client_params())
    def list(self, request, *args, **kwargs):
        return super(ClientViewSet, self).list(kwargs)


class ClientLoanViewSet(viewsets.ModelViewSet):
    """Mijozning filiallardan qarzlari """

    queryset = models.ClientLoan.objects.all()
    serializer_class = serializers.ClientLoanSerializer
    pagination_class = paginations.CustomPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'id': ['exact'],
        'client': ['exact'],
        'branch': ['exact'],
        'staff': ['exact'],
        'last_updated': ['gte', 'lte']
    }
    search_fields = ['client__first_name', 'client__last_name',
                     'client__phone_1', 'branch__name', 'loan_dollar',
                     'loan_sum', 'staff__first_name', ]


class InventoryInvoiceViewSet(viewsets.ModelViewSet):
    """
    Inventarizatsiya uchun api
    controller bu nazoratchi
    real_amount - realdagi tovar soni
    """

    queryset = models.InventoryInvoice.objects.all()
    serializer_class = serializers.InventoryInvoiceSerializer
    http_method_names = ['get', 'post']

    def retrieve(self, request, *args, **kwargs):
        """
        Inventarizatsiya ga tegishli mahsulotlar listini olish
        """
        instance = self.get_object()
        query_set = models.InventoryItem.objects.filter(inventory=instance)
        custom_data = serializers.InventoryItemSerializer(query_set, many=True).data
        return Response(custom_data)


class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    Inventarizatsiya uchun api
    controller bu nazoratchi
    real_amount - realdagi tovar soni
    """

    queryset = models.InventoryItem.objects.all()
    serializer_class = serializers.InventoryItemSerializer


class ClientLoanPaymentViewSet(viewsets.ModelViewSet):
    """ Mijozdan qarzi uchun to'lovni qabul qilib olish. Bunda to'lov miqdori 
    (qaysi usulda to'langaniga qarab, masalan 'card = 1000 000' - karta orqali 1 mln)
    hamda qo'shimcha ma'lumotlar kiritiladi.
    """

    queryset = models.ClientPaymentHistory.objects.all()
    serializer_class = serializers.ClientPaymentHistorySerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        instance = serializer.save(payment_for_loan=True)
        section = self.request.user.section
        print(section)
        client = instance.client
        client.loan_sum -= instance.card
        client.loan_sum -= instance.cash_sum
        client.loan_sum -= instance.transfer
        client.loan_sum -= instance.discount_sum
        client.loan_dollar -= instance.cash_dollar
        client.loan_dollar -= instance.discount_dollar
        client.save()

        section.total_sum += instance.cash_sum
        section.total_dollar += instance.cash_dollar
        section.total_card += instance.card
        section.total_card += instance.transfer
        section.save()


class ProducerViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.Producer.objects.all()
    serializer_class = serializers.ProducerModelSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    """  """
    queryset = models.Warehouse.objects.all()
    serializer_class = serializers.WarehouseSerializer
    http_method_names = ['get']


class ProductViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    http_method_names = ['post', 'get']

    # def list(self, request, *args, **kwargs):


class ProductThroughBranchtViewSet(viewsets.ModelViewSet):
    """Tovar qabul qilib olishga(ta'minotchidan, yetkazib beruvchidan)"""

    queryset = models.ProductThroughBranch.objects.filter(is_valid=True)
    serializer_class = serializers.ProductThroughBranchSerializer
    pagination_class = paginations.CustomPagination
    permission_classes = [permissions.IsAuthenticated, ]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'id': ['exact'],
        'product__name': ['icontains'],
        'branch': ['exact'],
        'product__barcode': ['exact'],
        'product__producer': ['exact'],
        'status': ['exact'],
        'last_updated': ['gte', 'lte'],
        'product__category__is_mobile': ['exact']
    }
    search_fields = ['product__name', 'product__barcode', 'product__producer__name']

    def get_queryset(self):
        queryset = super(ProductThroughBranchtViewSet, self).get_queryset()
        queryparams = self.request.query_params
        category_id = queryparams.get('category_id', None)

        qargs = {}
        if category_id:
            qargs.update({"product__category__id": category_id})
        status_ = queryparams.get("status", None)
        if status_:
            qargs.update({"status": status_})
        return queryset.filter(**qargs)

    @swagger_auto_schema(manual_parameters=filter_params.get_product_params())
    def list(self, request, *args, **kwargs):
        """
        Filialga tegishli bo'lgan mahsulotlar listini olish
        filter bor:
        id (tovar id si yuboriladi)
        product__name__contains (tovar nomi yuboriladi)
        branch (filial idsi yuboriladi)
        product__barcode (tovar shtrix kodi yuboriladi)
        product__producer (tovar ishlab chiqaruvchini id si yuboriladi)

        """

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=filter_params.get_product_params())
    @action(methods=['get'], detail=False)
    def branch_product(self, request, *args, **kwargs):
        """
        Filialga tegishli bo'lgan mahsulotlar listini olish uchun
        branchni id si yuboriladi ({branch: <branch ID si>} kabi).
        Android App uchun: branch IDisi bilan birgalikda {product__category__is_mobile: true}
        ham qo'shib yuborilishi kerak.
        """
        if branch_id := request.query_params.get('branch'):
            queryset = self.filter_queryset(self.get_queryset()).filter(
                branch_id=branch_id, product_meta__amount__gte=0).distinct()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = serializers.ProductThroughBranchWithMetaSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = serializers.ProductThroughBranchWithMetaSerializer(queryset, many=True)
            return Response(serializer.data)
        # status_ = request.query_params.get("status")
        # if status_ := request.query_params.get("status"):
        #     queryset = self.filter_queryset(self.get_queryset().filter(status=status_))
        #     page = self.paginate_queryset(queryset)
        #     if page is not None:
        #         serializer = serializers.ProductThroughBranchWithMetaSerializer(page, many=True)
        #         return self.get_paginated_response(serializer.data)
        #     serializer = serializers.ProductThroughBranchWithMetaSerializer(queryset, many=True)
        #     return Response(serializer.data)
        else:
            return Response({"Error": "Branch id is not found"}, 404)

    @action(methods=['get'], detail=False)
    def categories(self, request, *args, **kwargs):
        """
        Filialga tegishli bo'lgan mahsulotlar turlari (kategoriyalar)ni olish uchun
        branchni id si yuboriladi ({branch: <branch ID si>} kabi).
        Android App uchun: branch IDisi bilan birgalikda {category__is_mobile: true}
        ham qo'shib yuborilishi kerak.
        """

        if branch_id := request.query_params.get('branch'):
            queryset = models.Category.objects.filter(
                product__productthroughbranch__branch__id=branch_id
            )
            if request.query_params.get('is_mobile') == 'true':
                queryset = queryset.filter(is_mobile=True)
            serializer = serializers.CategorySerializer(queryset.distinct(), many=True)
            return Response(serializer.data)
        else:
            return Response({"Error": "Branch id is not found"}, 404)

    @action(methods=['get'], detail=False)
    def product_analysis(self, request, *args, **kwargs):
        """
        Tovar analizi uchun api, tovar nomi, barcode, producer va date(2021-07-24 07:05)
        bo'yicha filter bor.
        """
        branch_id = request.GET.get('branch')
        if branch_id:
            invoices = models.Invoice.objects.filter(to_branch_id=branch_id)
            invoiceitems = models.InvoiceItem.objects.filter(invoice__id__in=invoices.values('id')).distinct()
            self.filterset_fields.pop('branch')
            filtered_invoicesitems = self.filter_queryset(invoiceitems.filter(status='accepted'))
            self.filterset_fields['branch'] = ['exact']
            products = models.Product.objects.filter(
                invoiceitem__id__in=filtered_invoicesitems.values('id')).distinct()
            page = self.paginate_queryset(products)
            context = {'request': request}
            if request.GET.get('last_updated__gte'):
                context['last_updated__gte'] = request.GET.get('last_updated__gte')
            if request.GET.get('last_updated__lte'):
                context['last_updated__lte'] = request.GET.get('last_updated__lte')
            if page is not None:
                serializer = serializers.ProductAnalysisSerializer(page, many=True, context=context)
                return self.get_paginated_response(serializer.data)
            serializer = serializers.ProductAnalysisSerializer(products, many=True, context=context)
            return Response(serializer.data)
        else:
            return Response({"Error": "Branch id is not found"}, 404)

    @action(methods=['get'], detail=False)
    def product_analysis_for_provider(self, request, *args, **kwargs):
        """
        Ta'minotchi uchun tovar analizi. Bu uchun albatta 'branch' (int) - flial IDisi
        yuborilishi shart.
        """
        branch_id = request.GET.get('branch')
        search = request.GET.get('search')
        data = {'product_analysis': []}
        if branch_id:
            branch = models.Branch.objects.get(id=int(branch_id))
            branch_products = branch.productthroughbranch_set.all()
            if search:
                branch_products = branch.productthroughbranch_set.filter(
                    product__name__icontains=search)
            stats = {'gross_income_percentage': 0}
            for branch_product in branch_products.distinct():
                product = branch_product.product
                upto_date = datetime.now()
                from_date = datetime.now() - timedelta(days=30)
                shops = branch.shop_set.filter(traded_at__lt=upto_date, traded_at__gte=from_date)
                cartitems = models.CartItem.objects.filter(cart__shop__id__in=shops.values('id'),
                                                           product=product).distinct()
                overall_sales = sum([item.amount for item in cartitems.all()])
                average_daily_sales = round(overall_sales / 30)
                stats = {
                    'product_name': product.name,
                    'product_id': branch_product.id,
                    'remains_count': branch_product.get_amount,
                    'cost': product.cost,
                    'selling_price': branch_product.selling_price,
                    'average_daily_sales': average_daily_sales,
                    'normative': branch_product.normative,
                    'remains_cost': product.cost * branch_product.get_amount
                }
                if average_daily_sales == 0:
                    stats['remains_day'] = '-'
                else:
                    stats['remains_day'] = round(branch_product.get_amount / average_daily_sales)
                stats['daily_gross_income'] = (stats['selling_price'] - stats['cost']) * average_daily_sales
                if stats['selling_price']:
                    stats['marja'] = (stats['selling_price'] - stats['cost']) / stats['selling_price']
                else:
                    stats['marja'] = '-'
                stats['ustama'] = (stats['selling_price'] - stats['cost']) / stats['cost']
                if stats['remains_day'] == '-':
                    stats['losing'] = '-'
                    stats['freezed_money'] = '-'
                else:
                    stats['losing'] = (stats['remains_day'] - stats['normative']) * stats['daily_gross_income']
                    stats['freezed_money'] = (stats['remains_day'] - stats['normative']) * average_daily_sales * stats[
                        'cost']
                data['product_analysis'].append(stats)
            data['overall_remains_cost'] = sum([item['remains_cost'] for item in data['product_analysis']])
            data['overall_gross_income'] = sum([item['daily_gross_income'] for item in data['product_analysis']])
            data['overall_losing'] = sum(
                [item['losing'] for item in data['product_analysis'] if not isinstance(item['losing'], str)])
            data['overall_freezed_money'] = sum([item['freezed_money'] for item in data['product_analysis'] if
                                                 not isinstance(item['freezed_money'], str)])
            data['freezed_money_percentage'] = data['overall_freezed_money'] / data['overall_remains_cost']
            for item in data['product_analysis']:
                if data['overall_gross_income'] == 0:
                    item['gross_income_percentage'] = 0
                else:
                    item['gross_income_percentage'] = item['daily_gross_income'] / data['overall_gross_income']

            return Response(data)

    @action(methods=['get'], detail=False)
    def product_analysis_2(self, request, *args, **kwargs):
        """
        Tovar analizi olib kelingan/sotilgan tovarlar soni bo'yicha chizilgan grafik uchun.
        {'branch': (Branch IDisi), 'id': (Tovar IDisi)} yuborilishi kerak.
        """
        branch_id = request.GET.get('branch')
        product_id = request.GET.get('id')
        from_date = datetime(datetime.now().year, 1, 1)
        if branch_id and product_id:
            # Buyed products sources
            invoiceitems = models.InvoiceItem.objects.filter(
                invoice__to_branch__id=branch_id, invoice__status='accepted',
                invoice__last_updated__gte=from_date, product__id=product_id
            )
            pmoveitems = models.ProductMoveBranchItem.objects.filter(
                productmovegroup__to_branch__id=branch_id,
                productmovegroup__status='approved',
                productmovegroup__last_updated__gte=from_date,
                product__id=product_id
            )
            preceiptitems = models.ProductReceiptItem.objects.filter(
                receipt__to_branch__id=branch_id, receipt__status='finished',
                receipt__created_at__gte=from_date, product__id=product_id
            )
            # Selled products
            cartitems = models.CartItem.objects.filter(cart__status='finished',
                                                       cart__shop__branch__id=branch_id,
                                                       cart__shop__created_at__gte=from_date,
                                                       product__id=product_id
                                                       )
            # Buyed products with month
            invoiceitems = invoiceitems.annotate(
                month=ExtractMonth('invoice__last_updated')).values('month', 'id')
            pmoveitems = pmoveitems.annotate(
                month=ExtractMonth('productmovegroup__last_updated')).values('month', 'id')
            preceiptitems = preceiptitems.annotate(
                month=ExtractMonth('receipt__created_at')).values('month', 'id')
            # Selled products with month
            cartitems = cartitems.annotate(
                month=ExtractMonth('cart__shop__created_at')).values('month', 'id')

            data = {}
            for m in range(1, 13):
                data[str(m)] = {}
                by_invoices = invoiceitems.filter(month=m).values_list('amount', flat=True)
                by_pmoves = pmoveitems.filter(month=m).values_list('amount', flat=True)
                by_preceipts = preceiptitems.filter(month=m).values_list('amount', flat=True)
                selled = cartitems.filter(month=m).values_list('amount', flat=True)
                data[str(m)]['buyed'] = sum(by_invoices) + sum(by_pmoves) + sum(by_preceipts)
                data[str(m)]['selled'] = sum(selled)
            return Response({'data': data})
        else:
            return Response({"Error": "Branch ID or Product ID is not found"}, 404)


class ClientReturnCartViewSet(viewsets.ModelViewSet):
    """Klientdan qaytgan tovarlar uchun API. Avval ushbu endpoint ga kerakli
     ma'lumotlar 'post' qilinib vozvrat qilinayotgan tovarlar uchun cart yaratiladi. 
     Ushbu cart status 'processing' holatida bo'ladi. So'ng unga qaytarilayotgan tovarlar qo'shiladi.
     Barcha tovarlar qo'shilgach cart statusi 'finished' ga o'zgatiriladi."""

    queryset = models.ClientReturn.objects.select_related("client", "staff", "cart", "branch", "section")
    serializer_class = serializers.ClientReturnCartSerializer
    pagination_class = paginations.CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        'created_at': ['gte', 'lte'],
        'cart': ['exact'],
        'branch': ['exact']
    }
    http_method_names = ['post', 'get', 'patch']

    @action(methods=['get'], detail=False)
    def buyed_cart(self, request, *args, **kwargs):
        """
        Klient sotib olgan kartga tegishli tovarlar listini olish.
        """
        cart = self.request.GET.get('cart')
        cart = models.Cart.objects.get(id=int(cart))
        data = serializers.ShopDetailSerializer(cart.shop, context={'request': request}).data
        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        """Vozvratni yakunlash uchun vozvrat qilinayotgan tovarlar uchun yaratilgan
         cart statusini 'finished' ga o'zgartirish uchun endpoint."""
        instance = self.queryset.get(pk=kwargs.get('pk'))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        status = request.data.get('status', 'processing')
        instance = serializer.save()
        client = instance.client
        section = instance.section
        # update branch products if clientreturn is approved
        if status == 'finished':
            for item in instance.clientreturnitem_set.all():
                product = item.product
                pro_through_branch = models.ProductThroughBranch.objects.filter(
                    branch=instance.branch, product=product).first()
                if item.expire_date:
                    product_meta = pro_through_branch.product_meta.filter(
                        expire_date=item.expire_date).first()
                    product_meta.amount += item.amount
                    product_meta.save()

                else:
                    product_meta = pro_through_branch.productmeta_set.first()
                    product_meta.amount += item.amount
                    product_meta.save()

                # change client loan
                if instance.client:
                    if product.currency == 'sum':
                        client.loan_sum -= item.amount * pro_through_branch.selling_price
                    if product.currency == 'dollar':
                        client.loan_dollar -= item.amount * pro_through_branch.selling_price
                # client qaytarib berilgan pul miqdorini kassadan ayirish
                if instance.section:
                    if product.currency == "sum":
                        section.total_sum -= item.amount * pro_through_branch.selling_price
                        section.save()
                    if product.currency == "dollar":
                        section.total_dollar -= item.amount * pro_through_branch.selling_price
                        section.save()
        return Response(self.serializer_class(instance).data)

    @action(methods=['get'], detail=False)
    def report(self, request, *args, **kwargs):
        """
        Hisobot: Otkaz. Ikki sana oralig'i bo'yicha filterlash mumkin.
        Bu uchun "created_at_after" va "created_at_before" hamda "branch" query parameterlaridan
        foydalanish lozim. (Sana formati: YYYY-MM-DD). Agar "branch" ID isi berilmasa umumiy 
        statistika chiqariladi. Qidirish uchun "search" parametridan,
        Pagination uchun "offset" va "limit" query parametrlaridan foydalanish lozim. 
        """

        queryset = self.get_queryset().filter(status='finished')
        if search := request.query_params.get('search'):
            queryset = queryset.filter(
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search)
            ).distinct()
        if branch := request.query_params.get('branch'):
            queryset = queryset.filter(branch__id=branch)
        if created_after := request.query_params.get('created_at_after'):
            created_after = datetime.strptime(created_after, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gt=created_after)
        if created_before := request.query_params.get('created_at_before'):
            created_before = datetime.strptime(created_before, '%Y-%m-%d')
            created_before += timedelta(hours=23, minutes=59)
            queryset = queryset.filter(created_at__lte=created_before)

        page = self.paginate_queryset(queryset)
        serializer = serializers.ClientReturnReportSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ClientReturnCartItemViewSet(viewsets.ModelViewSet):
    """Klientdan qaytgan tovarlar savatchasiga tovar qo'shish"""

    queryset = models.ClientReturnItem.objects.select_related("return_cart", "product")
    serializer_class = serializers.ClientReturnCartItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        'product': ['exact'],
    }
    http_method_names = ['post', 'get']


class SectionViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.Section.objects.select_related("branch")
    serializer_class = serializers.SectionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        'branch__id': ['exact'],
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductMoveBranchItemViewSet(viewsets.ModelViewSet):
    """
    Tovarni boshqa filialga ko'chirish.
    """

    queryset = models.ProductMoveBranchItem.objects.all()
    serializer_class = serializers.ProductMoveBranchItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'productmovegroup__id': ['exact'],
        'product__name': ['icontains'],
        'amount': ['exact'],
        'selling_price': ['exact'],
        'expire_date': ['exact'],
    }
    http_method_names = ['get', 'post', 'patch']


class ProductMoveBranchGroupViewSet(viewsets.ModelViewSet):
    """
    Bir qancha tovarlarni bir filialdan boshqa filialga ko'chirish
    uchun, tovarlar shunday guruhlarga birlashtiriladi va ko'chiriladi.
    STATUS ==>
        ('pending', 'pending') # yaratilgandagi status
        ('approved', 'approved') # tasdiqlangandagi status
        ('rejected', 'rejected') # rad etilgandagi status
    """

    queryset = models.ProductMoveBranchGroup.objects.all()
    serializer_class = serializers.ProductMoveBranchGroupSerializer
    pagination_class = paginations.CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        'from_branch__id': ['exact'],
        'to_branch__id': ['exact'],
        'status': ['exact'],
        'items__product__name': ['icontains']
    }
    http_method_names = ['get', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        """Tovarlarni ko'chirishilishini tasdiqlash. 
           Ushbu amaliyotni faqatgina qabul qiluvchi filial xodimi 
           (masalan omborchisi) yoki ceo/director amalga oshira oladi.
        """
        instance = self.queryset.get(pk=kwargs.get('pk'))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        status = request.data.get('status', 'pending')
        if request.user in instance.to_branch.staff_set.all() or request.user.role in ('ceo', 'director'):
            # update instance and set user as instance reviewer
            updated_ins = serializer.save()
            updated_ins.reviewed_by = request.user
            updated_ins.save()

            # update branch products if productmove is approved
            if status == 'approved':
                for item in updated_ins.items.all():
                    product = item.product
                    from_branch = models.ProductThroughBranch.objects.filter(
                        branch=updated_ins.from_branch, product=product).first()
                    to_branch, created = models.ProductThroughBranch.objects.get_or_create(
                        branch=updated_ins.to_branch, product=product)
                    to_branch.selling_price = item.selling_price
                    to_branch.save()
                    if item.expire_date:
                        product_meta = from_branch.productmeta_set.filter(
                            expire_date=item.expire_date).first()
                        product_meta.amount -= item.amount
                        product_meta.save()

                        product_meta_to_branch = to_branch.productmeta_set.filter(
                            expire_date=item.expire_date).first()
                        if not product_meta_to_branch:
                            product_meta_to_branch = models.ProductMeta.objects.create(
                                product_through_branch=to_branch, expire_date=item.expire_date
                            )
                        product_meta_to_branch.amount += item.amount
                        product_meta_to_branch.save()
                    else:
                        product_metas = from_branch.productmeta_set.all()
                        needed_amount = item.amount
                        new_expire_date = None
                        for pr_meta in product_metas:
                            if needed_amount > 0 and pr_meta.amount > 0:
                                if pr_meta.amount > needed_amount:
                                    pr_meta.amount -= needed_amount
                                    needed_amount = 0
                                    new_expire_date = pr_meta.expire_date
                                else:
                                    needed_amount -= pr_meta.amount
                                    pr_meta.amount = 0
                                    new_expire_date = pr_meta.expire_date
                                pr_meta.save()

                        product_meta_to_branch = models.ProductMeta.objects.filter(
                            product_through_branch=to_branch).first()
                        if not product_meta_to_branch:
                            product_meta_to_branch = models.ProductMeta.objects.create(
                                product_through_branch=to_branch)
                        product_meta_to_branch.amount += item.amount
                        product_meta_to_branch.expire_date = new_expire_date
                        product_meta_to_branch.save()

            return Response(self.serializer_class(instance=updated_ins).data)
        else:
            raise PermissionDenied()


class ProductReceiptViewSet(viewsets.ModelViewSet):
    """
    Tovar prixod. Bu uchun avval yangi 'prixod' (receipt) create qilinib,
    qabul qilinayotgan tovarlar shunga qo'shib qo'yiladi.
    """

    queryset = models.ProductReceipt.objects.select_related("staff", "deliver", "currency", "price_type", "warehouse")
    serializer_class = serializers.ProductReceiptSerializer
    pagination_class = paginations.CustomPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        # 'from_branch__id': ['exact'],
        # 'to_branch__id': ['exact'],
        'deliver__id': ['exact'],
        'created_at': ['gte', 'lte'],
        "status": ['exact']
    }
    search_fields = ['name', 'comment', 'deliver__name']
    http_method_names = ['get', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        """Prixodni yakunlash. Bu uchun {'status': 'finished'} ni patch qilish kerak.
           Bu ishni faqatgina filial xodimi yoki yoki ceo/director amalga oshira oladi.
        """
        instance = self.queryset.get(pk=kwargs.get('pk'))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        status = request.data.get('status', 'processing')
        if request.user in instance.to_branch.staff_set.all() or request.user.role in ('ceo', 'director'):
            # update instance and set user as instance reviewer
            updated_ins = serializer.save()
            updated_ins.staff = request.user
            updated_ins.save()

            # update branch products if receipt is finished
            if status == 'accepted':
                for item in updated_ins.items.all():
                    product = item.product
                    pro_through_branch, created = models.ProductThroughBranch.objects.get_or_create(
                        branch=updated_ins.to_branch, product=product)
                    pro_through_branch.selling_price = item.selling_price
                    pro_through_branch.save()
                    pro_meta, created = models.ProductMeta.objects.get_or_create(
                        product_through_branch=pro_through_branch,
                        cost=item.cost
                    )
                    print("item.amount", item.amount)
                    pro_meta.amount += item.amount
                    pro_meta.save()
                if updated_ins.deliver:
                    deliver_loan, created = models.DeliverLoan.objects.get_or_create(
                        branch=updated_ins.to_branch, deliver=updated_ins.deliver
                    )
                    deliver_loan.loan_sum += updated_ins.summa_sum_selling_price
                    deliver_loan.loan_dollar += updated_ins.summa_dollar_selling_price
                    deliver_loan.save()
            return Response(self.serializer_class(instance=updated_ins).data)
        else:
            raise PermissionDenied()


class PriceTypeProductReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.PriceType.objects.select_related("deliver", "client")
    serializer_class = serializers.PriceTypeProductReceiptSerializer


class ProductReceiptItemViewSet(viewsets.ModelViewSet):
    """
    Qabul qilinayotgan tovarni "prixod" (receipt)ga qo'shish."""

    queryset = models.ProductReceiptItem.objects.select_related("receipt", "product")
    serializer_class = serializers.ProductReceiptItemSerializer
    pagination_class = paginations.CustomPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'receipt': ['exact'],
        'receipt__deliver__id': ['exact']
    }
    search_fields = ['product__name', 'receipt__name']
    http_method_names = ['get', 'post']


class DiscountProductReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.DiscountProductReceipt.objects.all()
    serializer_class = serializers.DiscountProductReceiptSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Faktura yaratish uchun, name(faktura nomi),
    status(faktura holati [preparing, send, accepted, cancelled] ),
    staff_id(fakturani yaratayotgan xodim idsi),
    deliver_id(yetkazib beruvchining idsi)

    invoice ichida 2ta branch bor

    1) branch - bu faktura yuborilayotgan filial yani qabul qilib oladigan
    2) staff ichidagi branch esa qaysi filial yuborayotgani, jo'natayotgan

    tovar qabul qilish (branch orqali)

    tovar jo'natish (staff ichidagi branch statusi orqal)

    sana bo'yicha filter qilish uchun bular qo'shib yuboriladi
    created_at__gte (..dan)
    created_at__lte (..gacha)
    vaqt formati (YYYY-MM-DD HH:MM)
    example: 2021-07-24 07:05
    """

    queryset = models.Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    pagination_class = paginations.CustomPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'from_branch': ['exact'],
        'to_branch': ['exact'],
        'status': ['exact'],
        'created_at': ['gte', 'lte'],
        'staff__role': ['exact'],
    }
    search_fields = ['name', 'deliver__name']

    def get_serializer_class(self):

        if self.action == 'accept_invoice':
            return serializers.InvoiceAcceptListSerializer
        return super().get_serializer_class()

    @action(methods=['post'], detail=False)
    def accept_invoice(self, request, *args, **kwargs):
        """
        Fakturani qabul qilish uchun invoiceitemlarni ro'yhatini list qilib yuboring,
        status ni esa accept qilib yuboring
        """
        invoice_list = request.data['invoice_list']
        invoice_id = request.data['invoice_id']
        expense = request.data['expense']
        invoice = models.Invoice.objects.get(pk=invoice_id)
        invoice.expense = expense
        invoice.save()

        if not invoice:
            return Response({"error": "Invoice id not found"}, 404)
        invoiceitem_list = invoice.invoiceitem_set.all()
        accepted_invoiceitems = []

        for invoiceitem in invoiceitem_list:
            if not (invoiceitem.id in invoice_list):
                invoiceitem.status = models.InvoiceItem.STATUS[3][0]
            else:
                accepted_invoiceitems.append(invoiceitem)
                invoiceitem.status = models.InvoiceItem.STATUS[2][0]
            invoiceitem.save()
        for invoiceitem in accepted_invoiceitems:
            product = invoiceitem.product
            # from_branch dan amount ni ayirish
            product_through_branch, created = models.ProductThroughBranch.objects.get_or_create(
                product=product,
                branch=invoice.from_branch,
            )
            product.branch.add(invoice.to_branch)
            for product_branch_meta in product_through_branch.productmeta_set.all():
                if product_branch_meta.expire_date is None:
                    product_branch_meta.amount -= invoiceitem.amount
                elif product_branch_meta.expire_date == invoiceitem.expire_date:
                    product_branch_meta.amount -= invoiceitem.amount
                product_branch_meta.save()
                product_through_branch.save()

            product.save()

            # productni yangi branchga qo'shish
            product_through_branch = models.ProductThroughBranch.objects.get(
                product=product,
                branch=invoice.to_branch,
            )
            if product_through_branch:
                product_through_branch.selling_price = invoiceitem.selling_price
                product_through_branch.save()
                product_branch_meta, created = product_through_branch.productmeta_set.get_or_create(
                    expire_date=invoiceitem.expire_date
                )
                product_branch_meta.amount += invoiceitem.amount
                product_branch_meta.save()

        if invoiceitem_list.filter(status=models.InvoiceItem.STATUS[2][0]).count() == invoiceitem_list.count():
            invoice.status = models.Invoice.STATUS[2][0]
            invoice.save()

        data = serializers.InvoiceItemSerializer(invoiceitem_list, many=True,
                                                 context={'request': request}).data
        return Response({"status": "Success", "data": data})

    def list(self, request, *args, **kwargs):
        branch = request.user.branch
        query_set = models.Invoice.objects.filter(Q(to_branch=branch) | Q(from_branch=branch))
        queryset = self.filter_queryset(query_set)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Invoice ga tegishli tovalar listini olish
        tovar ichidagi selling_price tovarning sotilish narxi
        """
        invoice_id = kwargs.get('pk')
        query_set = models.InvoiceItem.objects.filter(invoice_id=invoice_id)
        custom_data = serializers.InvoiceItemWithoutIdSerializer(query_set, many=True,
                                                                 context={'request': request}).data
        return Response(custom_data)

    def partial_update(self, request, *args, **kwargs):
        """Invoice ni jo'natdag status: send qilinadi, shunda invoice 
           va undagi barcha itemlar statusi 'send' ga o'zgaradi."""
        instance = self.queryset.get(pk=kwargs.get('pk'))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        status = request.data.get('status', 'preparing')
        instance = serializer.save()
        if status == 'send':
            for item in instance.invoiceitem_set.all():
                item.status = 'send'
                item.save()
        elif status == 'cancelled':
            for item in instance.invoiceitem_set.all():
                item.status = 'rejected'
                item.save()
        return Response(self.serializer_class(instance).data)

    @action(methods=['get'], detail=False)
    def all_invoice(self, request):
        branch = request.user.branch
        status = request.GET.get('status')
        if status:
            query_set = models.Invoice.objects.filter(status=status, branch=branch)
        else:
            query_set = models.Invoice.objects.filter(branch=branch)
        invoice_serializers = serializers.InvoiceSerializer(query_set, many=True)
        return Response(invoice_serializers.data)

    @action(methods=['get'], detail=False)
    def accepting_product(self, request, *args, **kwargs):
        """Ta’minotchidan tovar kelganda ma’lumot shu url dan olinadi"""

        models.Invoice.objects.filter(status=models.Invoice.STATUS[1][0])
        return Response('data')

    @action(methods=['get'], detail=False)
    def list_provider(self, request, *args, **kwargs):
        """Ta’minotchidan kelgan fakturalarni ro'yhatini olish"""

        queryset = self.filter_queryset(self.get_queryset())
        invoice_list = queryset.filter(staff__role=models.Staff.ROLE[8][0])
        invoice_serializers = serializers.InvoiceSerializer(invoice_list, many=True)
        return Response(invoice_serializers.data)

    @action(methods=['get'], detail=False)
    def in_processing_invoice(self, request, *args, **kwargs):
        """Xodimning tayyorlayotgan preparing statusidagi fakturani ichidagi tovarlarni olish"""

        invoice = models.Invoice.objects.filter(status=models.Invoice.STATUS[0][0], staff=request.user).first()
        invoice_items = models.InvoiceItem.objects.filter(invoice=invoice)
        data = serializers.InvoiceItemWithoutIdSerializer(invoice_items, many=True).data
        return Response(data)


class ReturnDeliverProductViewSet(viewsets.ModelViewSet):
    """ Tovarni yetkazib beruvchiga qaytarish. Bunda qaysi tovar (product) qaysi
        yetkazib beruvchiga (deliver) yetkazib berilyatgani va tovar haqidagi qo'shimcha
        ma'lumotlar kiritilishi kerak. Jumladan tovar qabul qilingan narx (cost), uning srogi
        (expire_date agar mavjud bo'lsa) hamda necha dona (amount) qaytarilayotgani. Bundan tashqari kim
        tomonidan qaytarilgani ham (staff) kiritilishi kerak.
        [GET] methodida 'search' key orqali qidirish imkoniyati va filter mavjud."""

    queryset = models.ReturnDeliverProduct.objects.all()
    serializer_class = serializers.ReturnDeliverProductSerializer
    http_method_names = ['get', 'post']
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'deliver__id': ['exact'],
        'from_branch__id': ['exact'],
        'amount': ['exact'],
        'expire_date': ['exact'],
        'created_at': ['gte', 'lte'],
    }
    search_fields = ['product__name', 'staff__name', 'from_branch__name', 'deliver__name']


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    ball_price - Ball narxi
    real_currency - dollarning ayni vaqtdagi kursi
    selling_price - tovarni sotishdagi kurs narxi
    """

    queryset = models.Currency.objects.all()
    serializer_class = serializers.CurrencySerializer
    http_method_names = ['GET']


class ShopViewSet(viewsets.ModelViewSet):
    """
    Savdo api
    2ta vaqt oralig'i uchun date-format (2021-10-12)
    """

    queryset = models.Shop.objects.all()
    serializer_class = serializers.ShopSerializer
    pagination_class = paginations.CustomPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = ShopFilter
    search_fields = ('cart__cartitem__product__name',
                     'cart__cartitem__product__barcode',
                     'cart__cartitem__product__producer__name')

    def create(self, request, *args, **kwargs):
        """
        Savdo qilish api, seller(sotuvchini yuborish shartmas),
        branch(filial) buni ham yuborish shartmas, o'zim aniqlab olaman ularni avtomatik
        """

        request.data['seller'] = request.user.id
        request.data['branch'] = request.user.branch.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shop = serializer.save()
        if shop.loan_dollar != 0:
            shop.client.loan_dollar += shop.loan_dollar
            shop.client.save()

        if shop.loan_sum != 0:
            shop.client.loan_sum += shop.loan_sum
            shop.client.save()

        for cart_item in shop.cart.cartitem_set.all():
            product = cart_item.product
            products_meta = product.product_meta.all()
            for product_meta in products_meta:
                product_meta.amount -= cart_item.amount
                product_meta.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Methods for various Reports and Statistics
    # @action(methods=['get'], detail=False)
    # def report_sales_today(self, request, *args, **kwargs):
    #     """
    #      Hisobot. Bu Endpointda kunlik Hisobotlar chiqadi. hisobotlar bo'limiga kirilganda
    #      dasturda default holatda kunlik  hisobotlar chiqib turadi
    #     """
    #     queryset = self.get_queryset().filter(
    #         Q(cart__status="finished") and Q(traded_at__day=datetime.today().day) and Q(
    #             traded_at__month=datetime.now().month))
    #     client_loan_paid = models.ClientPaymentHistory.objects.filter(
    #         Q(paid_at__month=datetime.now().month) and Q(paid_at__day=datetime.today().day))
    #
    #     # Hisobot umumiy summalar
    #     print(client_loan_paid)
    #     total_cash_summ = 0
    #     total_cash_dollar = 0
    #     total_card = 0
    #     total_loan_sum = 0
    #     total_transfer = 0
    #     total_loan_dollar = 0
    #     print(queryset.values("cash_sum"))
    #     for i in queryset.values():
    #         total_cash_summ += i["cash_sum"]
    #         total_cash_dollar += i["cash_dollar"]
    #         total_card += i['card']
    #         total_loan_sum += i["loan_sum"]
    #         total_transfer += i['transfer']
    #         total_loan_dollar += i['loan_dollar']
    #     serializer = serializers.ShopSerializerForToday(queryset, many=True)
    #     return Response(
    #         {"total_cash_summ": total_cash_summ, "total_cash_dollar": total_cash_dollar, "total_card": total_card,
    #          "total_loan_sum": total_loan_sum,
    #          "total_loan_dollar": total_loan_dollar, "total_transfer": total_transfer, })

    @action(methods=['get'], detail=False)
    def report_sales(self, request, *args, **kwargs):
        """
        Eng ko'p sotilgan tovarlar hisoboti. Ikki sana oralig'i bo'yicha filterlash mumkin.
        Bu uchun "created_at_after" va "created_at_before" hamda "branch" query parameterlaridan
        foydalanish lozim. (Sana formati: YYYY-MM-DD). Agar "branch" ID isi berilmasa umumiy 
        statistika chiqariladi. Qidirish uchun "search" parametridan,
        Pagination uchun "offset" va "limit" query parametrlaridan foydalanish lozim. 
        """
        queryset = self.get_queryset().filter(cart__status='finished')
        queryparams = self.request.query_params
        created_at_after = queryparams.get("created_at_after")
        created_at_before = queryparams.get("created_at_before")
        today = queryparams.get("today")
        weekly = queryparams.get("weekly")
        monthly = queryparams.get("monthly")
        if search := request.query_params.get('search'):
            queryset = queryset.filter(
                Q(cart__cartitem__product__name__icontains=search) |
                Q(cart__cartitem__product__barcode__icontains=search) |
                Q(cart__cartitem__product__producer__name__icontains=search)
            ).distinct()
        if branch := request.query_params.get('branch'):
            queryset = queryset.filter(branch__id=branch)
        if created_at_after and created_at_before:
            created_after = datetime.strptime(created_at_after, '%Y-%m-%d')
            created_before = datetime.strptime(created_at_before, '%Y-%m-%d')
            queryset = queryset.filter(Q(traded_at__gt=created_after) and Q(traded_at__lte=created_before))
        if today:
            queryset = self.get_queryset().filter(Q(traded_at__day=datetime.today().day) and Q(
                traded_at__month=datetime.now().month))
        if weekly:
            one_week_ago = datetime.today() - timedelta(days=7)
            queryset = queryset.filter(traded_at__gte=one_week_ago)
        if monthly:
            one_month_ago = datetime.today() - timedelta(days=30)
            queryset = queryset.filter(traded_at__gte=one_month_ago)
        cartitems = models.CartItem.objects.filter(
            cart__shop__in=queryset
        ).distinct()
        products = cartitems.values('product').annotate(count=Sum('amount'))
        data = []
        for item in products:
            product = models.Product.objects.get(id=item['product'])
            if branch:
                product_through_branch = models.ProductThroughBranch.objects.filter(
                    product=item['product'], branch=branch)
            else:
                product_through_branch = models.ProductThroughBranch.objects.filter(
                    product=item['product'])
            total_summa = item['count'] * product_through_branch.first().selling_price
            remains = sum([obj.get_amount for obj in product_through_branch])
            last_receipt = models.ProductReceiptItem.objects.filter(
                product=product).order_by('-created_at').first()
            last_branchmove = models.ProductMoveBranchItem.objects.filter(
                product=product).order_by('-created_at').first()
            last_receipt_date = last_receipt.created_at if last_receipt else None
            last_branchmove_date = last_branchmove.created_at if last_branchmove else None
            if last_receipt_date and last_branchmove_date:
                last_deliver_on = last_branchmove_date
                if last_receipt_date > last_branchmove_date:
                    last_deliver_on = last_receipt_date
            else:
                last_deliver_on = last_branchmove_date or last_receipt_date
            data.append({
                'id': item['product'],
                'name': product.name,
                'barcode': product.barcode,
                'producer': product.producer.name if product.producer else None,
                'measurement': product.measurement,
                'count': item['count'],
                'total_summa': total_summa,
                'remains': remains,
                'last_deliver_on': last_deliver_on
            })
        data = sorted(data, key=itemgetter('total_summa'), reverse=True)
        cash_sum, cash_dollar, loan_sum, loan_dollar, transfer, card, returns = [0] * 7
        # cash_sum += total_summa
        # Custom Pagination
        count = products.count()
        return Response({
            "count": count,
            # "next": next_url,
            # "previous": prev_url,
            "results": data,
            "overall_stats": {
                "cash_sum": cash_sum,
                "cash_dollar": cash_dollar,
                "card": card,
                "transfer": transfer,
                "loan_sum": loan_sum,
                "loan_dollar": loan_dollar,
                "returns": returns
            }
        })

    @action(methods=['get'], detail=False)
    def report_cashiers(self, request, *args, **kwargs):
        """
        Xodimlar aktivligi bo'yicha hisobot. Ikki sana oralig'i bo'yicha filterlash mumkin.
        Bu uchun "created_at_after" va "created_at_before" hamda "branch" query parameterlaridan
        foydalanish lozim. (Sana formati: YYYY-MM-DD). Agar "branch" ID isi berilmasa umumiy 
        statistika chiqariladi. Qidirish uchun "search" parametridan,
        Pagination uchun "offset" va "limit" query parametrlaridan foydalanish lozim. 
        """

        queryset = self.get_queryset().filter(cart__status='finished')
        queryparams = self.request.query_params
        today = queryparams.get("today")
        weekly = queryparams.get("weekly")
        monthly = queryparams.get("monthly")
        if search := request.query_params.get('search'):
            queryset = queryset.filter(
                Q(seller__first_name__icontains=search) |
                Q(seller__last_name__icontains=search)
            ).distinct()
        if branch := request.query_params.get('branch'):
            queryset = queryset.filter(branch__id=branch)
        if created_after := request.query_params.get('created_at_after'):
            created_after = datetime.strptime(created_after, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gt=created_after)
        if created_before := request.query_params.get('created_at_before'):
            created_before = datetime.strptime(created_before, '%Y-%m-%d')
            created_before += timedelta(hours=23, minutes=59)
            queryset = queryset.filter(created_at__lte=created_before)
        if today:
            queryset = self.get_queryset().filter(Q(traded_at__day=datetime.today().day) and Q(
                traded_at__month=datetime.now().month))
        if weekly:
            one_week_ago = datetime.today() - timedelta(days=7)
            queryset = queryset.filter(traded_at__gte=one_week_ago)
        if monthly:
            one_month_ago = datetime.today() - timedelta(days=30)
            queryset = queryset.filter(traded_at__gte=one_month_ago)
        sellers = queryset.values('seller').annotate(card=Sum('card'),
                                                     loan_sum=Sum('loan_sum'),
                                                     loan_dollar=Sum('loan_dollar'),
                                                     cash_sum=Sum('cash_sum'),
                                                     cash_dollar=Sum('cash_dollar'),
                                                     transfer=Sum('transfer'))
        sellers = sellers.order_by('-cash_sum')
        page = self.paginate_queryset(sellers)
        for i in page:
            i['seller_name'] = models.Staff.objects.get(id=i['seller']).get_full_name()
        return self.get_paginated_response(page)

    @action(methods=['get'], detail=False)
    def report_products(self, request, *args, **kwargs):
        """
        Hisobot: Mahsulot. Ikki sana oralig'i bo'yicha filterlash mumkin.
        Bu uchun "created_at_after" va "created_at_before" hamda "branch" query parameterlaridan
        foydalanish lozim. (Sana formati: YYYY-MM-DD). Agar "branch" ID isi berilmasa umumiy 
        statistika chiqariladi. Qidirish uchun "search" parametridan,
        Pagination uchun "offset" va "limit" query parametrlaridan foydalanish lozim. 
        """

        queryset = self.get_queryset().filter(cart__status='finished')
        queryparams = self.request.query_params
        today = queryparams.get("today")
        weekly = queryparams.get("weekly")
        monthly = queryparams.get("monthly")
        if search := request.query_params.get('search'):
            queryset = queryset.filter(
                Q(cart__cartitem__product__name__icontains=search) |
                Q(cart__cartitem__product__barcode__icontains=search) |
                Q(cart__cartitem__product__producer__name__icontains=search)
            ).distinct()
        if branch := request.query_params.get('branch'):
            queryset = queryset.filter(branch__id=branch)
        if created_after := request.query_params.get('created_at_after'):
            created_after = datetime.strptime(created_after, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gt=created_after)
        if created_before := request.query_params.get('created_at_before'):
            created_before = datetime.strptime(created_before, '%Y-%m-%d')
            created_before += timedelta(hours=23, minutes=59)
            queryset = queryset.filter(created_at__lte=created_before)
        if today:
            queryset = self.get_queryset().filter(Q(traded_at__day=datetime.today().day) and Q(
                traded_at__month=datetime.now().month))
        if weekly:
            one_week_ago = datetime.today() - timedelta(days=7)
            queryset = queryset.filter(traded_at__gte=one_week_ago)
        if monthly:
            one_month_ago = datetime.today() - timedelta(days=30)
            queryset = queryset.filter(traded_at__gte=one_month_ago)
        cartitems = models.CartItem.objects.filter(
            cart__shop__in=queryset
        ).distinct()
        products = cartitems.values('product').annotate(count=Sum('amount'))
        data = []
        for item in products:
            product = models.Product.objects.get(id=item['product'])
            if branch:
                product_through_branch = models.ProductThroughBranch.objects.filter(
                    product=item['product'], branch=branch)
            else:
                product_through_branch = models.ProductThroughBranch.objects.filter(
                    product=item['product'])
            total_summa = item['count'] * product_through_branch.first().selling_price
            remains = sum([obj.get_amount for obj in product_through_branch])
            data.append({
                'id': item['product'],
                'name': product.name,
                'measurement': product.measurement,
                'count': item['count'],
                'cost': product_through_branch.first().product_meta.first(
                ).cost if product_through_branch.first().product_meta.first() else None,
                'selling_price': product_through_branch.first().selling_price,
                'currecy': product.currency,
                'category': product.category.name if product.category else None,
                'remains': remains,
                'total_summa': total_summa,
            })
        data = sorted(data, key=itemgetter('total_summa'), reverse=True)
        # Custom Pagination
        count = products.count()
        # offset = int(request.query_params.get('offset', 0))
        # limit = int(request.query_params.get('limit', 20))
        # url = self.request.build_absolute_uri()
        # url = replace_query_param(url, 'limit', limit)
        prev_url = None
        next_url = None
        # if offset > count - 1:
        #     return Response({'error': 'offset is too big'}, status=400)
        # elif offset > 0:
        #     prev_offset = offset - limit if offset - limit >= 0 else 0
        #     prev_url = replace_query_param(url, 'offset', prev_offset)
        # elif offset < 0:
        #     return Response({'error': 'offset must be greater then 0'}, status=400)
        # if offset + limit < count:
        #     next_url = replace_query_param(url, 'offset', offset + limit)
        return Response({
            "count": count,
            "next": next_url,
            "previous": prev_url,
            "results": data
        })

    # Methods for Mobile API
    @action(methods=['get'], detail=False)
    def active_checks(self, request, *args, **kwargs):
        """
        Android App uchun klientga berib yuborilishi kerak bo'lgan tovarlar checklari.
        """
        if request.query_params.get('branch'):
            queryset = self.filter_queryset(self.get_queryset()).filter(
                cart__cartitem__product__category__is_mobile=True,
                cart__status='waiting_loading').distinct()
            if search := request.query_params.get('search'):
                queryset = queryset.filter(Q(seller__first_name__icontains=search) |
                                           Q(seller__last_name__icontains=search) |
                                           Q(client__first_name__icontains=search) |
                                           Q(client__last_name__icontains=search) |
                                           Q(cart__cartitem__product__name__icontains=search) |
                                           Q(cart__cartitem__product__category__name__icontains=search)
                                           ).distinct()
            # page = self.paginate_queryset(queryset)
            # if page is not None:
            #     serializer = serializers.ProductThroughBranchWithMetaSerializer(page, many=True)
            #     return self.get_paginated_response(serializer.data)
            serializer = serializers.ActiveCheckSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"Error": "Branch id is not found"}, 404)

    @action(methods=['get'], detail=False)
    def check_detail(self, request, *args, **kwargs):
        """
        Android App uchun klientga berib yuborilishi kerak bo'lgan tovarlar ro'yxati
        (Check ichidagi tovarlar). Bu listni olish uchun {check: <check_IDisi>} yuborilishi kerak.
        """
        if check_id := request.query_params.get('check'):
            shop = models.Shop.objects.filter(id=check_id).first()
            if not shop:
                return Response({"Error": "Check not found with given ID"}, 404)
            # page = self.paginate_queryset(queryset)
            # if page is not None:
            #     serializer = serializers.ProductThroughBranchWithMetaSerializer(page, many=True)
            #     return self.get_paginated_response(serializer.data)
            serializer = serializers.ActiveCheckDetailSerializer(shop)
            return Response(serializer.data)
        else:
            return Response({"Error": "Check id is not found"}, 404)

    @action(methods=['get'], detail=False)
    def close_check(self, request, *args, **kwargs):
        """
        Android App uchun: Active Check ni yopish (tasdiqlash). 
        Bu uchun {check: <check_IDisi>} yuborilishi kerak.
        """
        if check_id := request.query_params.get('check'):
            shop = models.Shop.objects.filter(id=check_id, cart__status='waiting_loading').first()
            if not shop:
                return Response({"Error": "Active Check not found with given ID"}, 404)
            cart = shop.cart
            cart.status = 'finished'
            cart.save()
            # page = self.paginate_queryset(queryset)
            # if page is not None:
            #     serializer = serializers.ProductThroughBranchWithMetaSerializer(page, many=True)
            #     return self.get_paginated_response(serializer.data)
            data = serializers.ActiveCheckDetailSerializer(shop).data
            data['status'] = 'finished'
            return Response(data)
        else:
            return Response({"Error": "Check id is not found"}, 404)

    @action(methods=['get'], detail=False)
    def closed_checks(self, request, *args, **kwargs):
        """
        Android App uchun: Tasdiqlanga Checklar ro'yxatini olish (Hisobot). 
        Bu uchun {branch: <branch_IDisi>} yuborilishi kerak.
        """
        if branch := request.query_params.get('branch'):
            queryset = self.get_queryset().filter(branch__id=branch,
                                                  cart__status='finished',
                                                  cart__cartitem__product__category__is_mobile=True
                                                  ).distinct()
            if created_after := request.query_params.get('created_at_after'):
                created_after = datetime.strptime(created_after, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gt=created_after)
            if created_before := request.query_params.get('created_at_before'):
                created_before = datetime.strptime(created_before, '%Y-%m-%d')
                created_before += timedelta(hours=23, minutes=59)
                queryset = queryset.filter(created_at__lte=created_before)
            if search := request.query_params.get('search'):
                queryset = queryset.filter(Q(seller__first_name__icontains=search) |
                                           Q(seller__last_name__icontains=search) |
                                           Q(client__first_name__icontains=search) |
                                           Q(client__last_name__icontains=search) |
                                           Q(cart__cartitem__product__name__icontains=search) |
                                           Q(cart__cartitem__product__category__name__icontains=search)
                                           ).distinct()
            # page = self.paginate_queryset(queryset)
            # if page is not None:
            #     serializer = serializers.ProductThroughBranchWithMetaSerializer(page, many=True)
            #     return self.get_paginated_response(serializer.data)
            serializer = serializers.ActiveCheckSerializer(queryset.distinct(), many=True)
            return Response(serializer.data)
        else:
            return Response({"Error": "Branch id is not found"}, 404)


class BranchViewSet(viewsets.ModelViewSet):
    """Filial api  """

    queryset = models.Branch.objects.all()
    serializer_class = serializers.BranchSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['id']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MinimalViewSet(generics.CreateAPIView,
                     generics.RetrieveUpdateDestroyAPIView,
                     viewsets.GenericViewSet):
    """  """

    queryset = models.Minimal.objects.all()
    serializer_class = serializers.MinimalSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['id']
    http_method_names = ['get', 'patch', 'post']

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CustomMinimalUpdateSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """Product ga tegishli bo'lgan barcha oylik miqdorlar listi (__product id__ sini yuboring)"""
        product_id = kwargs.get('pk')
        instance = models.Minimal.objects.filter(product_id=product_id)
        serializer = serializers.MinimalWithoutSerializer(instance, many=True)
        data = {
            "product_id": product_id,
            "minimals": serializer.data
        }
        return Response(data)

    def update(self, request, *args, **kwargs):
        """bunga minimalga tegishli bo'lgan id yuboriladi update qilish uchun"""
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
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
        {
        "product": 118,
        "minimals": [
            "amount": 50,
            "month": "january"
        ]
        }
        """

        product_id = request.data['product']
        minimals = request.data['minimals']
        for minimal in minimals:
            amount = minimal.get('amount')
            month = minimal.get('month')
            minimal, created = models.Minimal.objects.get_or_create(product_id=product_id, month=month)
            minimal.amount = amount
            minimal.save()
        return Response({"Successfully created"})


class CategoryViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer


class CheckViewSet(viewsets.ModelViewSet):
    """  """
    queryset = models.Check.objects.all()
    serializer_class = serializers.CheckModelSerializer


class CheckItemViewSet(viewsets.ModelViewSet):
    """  """
    permission_classes = [AllowAny]
    queryset = models.CheckItem.objects.all()
    serializer_class = serializers.CheckItemModelSerializer


class DeliverViewSet(viewsets.ModelViewSet):
    """Yetkazib beruvchilar ro'yhatini olish"""

    queryset = models.Deliver.objects.all()
    pagination_class = paginations.CustomPagination
    serializer_class = serializers.DeliverSerializer
    filter_backends = (SearchFilter,)
    search_fields = ['name', 'director_name', 'address', 'phone_1', 'phone_2']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DeliverLoanViewSet(viewsets.ModelViewSet):
    """Yetkazib beruvchilar ro'yhatini olish"""

    queryset = models.DeliverLoan.objects.all()
    pagination_class = paginations.CustomPagination
    serializer_class = serializers.DeliverLoanSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'branch': ['exact'],
        'deliver': ['exact']
    }
    search_fields = ['deliver__name', 'branch__name', 'loan_sum', 'loan_dollar']


class DifferProductRecieveHistoryViewSet(viewsets.ModelViewSet):
    """  """

    queryset = models.DifferProductRecieveHistory.objects.all()
    serializer_class = serializers.DifferProductRecieveHistorySerializer


class ProductPriceChangeViewSet(viewsets.ModelViewSet):
    """Product narxini o'zgartirish"""

    queryset = models.ProductPriceChange.objects.all()
    serializer_class = serializers.ProductPriceChangeSerializer
    http_method_names = ['post']


class ShowcaseViewSet(viewsets.ModelViewSet):
    """Vektrina uchun api"""

    queryset = models.Showcase.objects.all()
    serializer_class = serializers.ShowcaseSerializer
    http_method_names = ['get', 'post', 'put']


class BonusProductViewSet(viewsets.ModelViewSet):
    """Bonusli tovar uchun api"""

    queryset = models.BonusProduct.objects.all()
    serializer_class = serializers.BonusProductSerializer
    http_method_names = ['get', 'post', 'put']


class StaffViewSet(viewsets.ModelViewSet):
    """Xodimlar uchun API. Xodim aktivligini o'zgartirish uchun PATCH metodi orqali
        status -> {active, inactive} yuboriladi."""

    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
        'branch': ['exact'],
        'status': ['exact']
    }
    search_fields = ['username', 'first_name', 'last_name', 'fathers_name',
                     'address', 'phone']

    def get_serializer_context(self):
        context = super(StaffViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(methods=['POST'], detail=False)
    def update_staff_permission(self, request, *args, **kwargs):
        print('working')
        return Response(status.HTTP_200_OK)


class OutcomeViewSet(viewsets.ModelViewSet):
    """ Chiqimlarni CRUD qilish uchun."""

    queryset = models.Outcome.objects.all()
    pagination_class = paginations.CustomPagination
    serializer_class = serializers.OutcomeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryparams = self.request.query_params
        qargs = {}
        branch = queryparams.get("branch", None)
        if branch:
            qargs.update({"branch__name__icontains": branch})
        outcome_status = queryparams.get("status", None)
        if outcome_status:
            qargs.update({"status__icontains": outcome_status})
        whom = queryparams.get("whom", None)
        if whom:
            qargs.update({"whom": whom})
        type_id = queryparams.get("type_id", None)
        if type_id:
            qargs.update({"type__id": type_id})
        return queryset.filter(**qargs)

    @swagger_auto_schema(manual_parameters=filter_params.get_outcome_params())
    def list(self, request, *args, **kwargs):
        return super(OutcomeViewSet, self).list(kwargs)
    # filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    # filterset_fields = {
    #     'branch': ['exact'],
    #     'type': ['exact'],
    #     'status': ['exact'],
    #     'created_at': ['gte', 'lte'],
    # }
    # search_fields = ['whom', 'branch__name', 'type__name', 'comment',
    #                  'sum', 'dollar']


class OutcomeTypeViewSet(viewsets.ModelViewSet):
    """Chiqim turlarini CRUD qilish uchun."""

    queryset = models.OutcomeType.objects.all()
    pagination_class = paginations.CustomPagination
    serializer_class = serializers.OutcomeTypeSerializer
    filter_backends = (SearchFilter,)
    search_fields = ['name']


class CustomObtainAuthToken(ObtainAuthToken):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.CustomAuthTokenSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    )
                )
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        serializer_user = serializers.StaffDataSerializer(user)
        if user.status != models.Staff.STATUS[0][0]:
            return Response({'data': serializer_user.data}, status=403)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'data': serializer_user.data}, status=200)


class CustomObtainAuthTokenMobile(ObtainAuthToken):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.CustomAuthTokenSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="password",
                    required=False,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    )
                )
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        if not serializer.is_valid():
            return Response({'data': {
                'error': 'Bunday foydalanuvchi topilmadi.'
            }}, status=200)
        user = serializer.validated_data['user']
        if user:
            serializer_user = serializers.StaffDataSerializer(user)
            if user.status != models.Staff.STATUS[0][0]:
                return Response({'data': {
                    'error': "Ushbu foydalanuvchi uchun kirish imkoniyati cheklangan."
                }}, status=200)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'data': serializer_user.data}, status=200)


class TokenApiView(ObtainAuthToken):
    serializer_class = serializers.CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        if not serializer.is_valid():
            return Response({"data": {"error": "Bunday user topilmadi"}})
        user = serializer.validated_data['user']
        # if user:
        serializer_user = serializers.StaffDataSerializer(user)
        if user.status != models.Staff.STATUS[0][0]:
            return Response({"data": {"error": "Ushbu foydalanuvchi uchun kirish cheklangan"}})
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "data": serializer_user.data}, status=200)


# class TokenGenerateView(JWTTokenObtainPairView):
#     serializer_class = TokenSerializer
#     post_responses = {
#         rest_status.HTTP_201_CREATED: openapi.Response(description='Token obtained'),
#         rest_status.HTTP_404_NOT_FOUND: openapi.Response(description='User not found'),
#         rest_status.HTTP_400_BAD_REQUEST: openapi.Response(description='Validation error'),
#     }
#
#     def get_serializer_context(self):
#         return {'request': self.request}
#
#     @swagger_auto_schema(operation_id='token_obtain', operation_description='Token obtaining', responses=post_responses)
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#
#         try:
#             serializer.is_valid(raise_exception=True)
#         except TokenError as e:
#             raise InvalidToken(e.args[0])
#         else:
#             data = serializer.validated_data
#         return response.Response(data, status=rest_status.HTTP_201_CREATED)


from rest_framework.viewsets import mixins, GenericViewSet


class AccountantApiView(mixins.RetrieveModelMixin,
                        GenericViewSet):
    serializer_class = serializers.BranchSerializerForAccountant
    queryset = models.Branch.objects.all()
    lookup_field = 'pk'


class AccountantCreateApiView(generics.CreateAPIView):
    queryset = models.Accountant.objects.all()
    serializer_class = serializers.AccountantSerializer


class ChangeCurrency(viewsets.ModelViewSet):
    queryset = models.ChangeCurrency.objects.all()
    serializer_class = serializers.ChangeCurrencySerializer

    def get_serializer_context(self):
        context = super(ChangeCurrency, self).get_serializer_context()
        context.update({"request": self.request})
        return context
