import datetime


from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from rest_framework.exceptions import NotFound

from . import forms
from . import models


def error400(request, exception):
    raise NotFound("Error 400, Bad Request", 400)


def error403(request, exception):
    raise NotFound("Error 403,  Forbidden", 403)


def error404(request, exception):
    raise NotFound("Error 404, page not found", 404)


def error500(request, exception):
    raise NotFound("Error 500, Internal Server Error", 500)



class Template(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/index.html'

    def get_context_data(self, **kwargs):
        from django.db.models import Sum
        from django.db import connection
        from datetime import datetime
        import datetime as timedate

        ctx = super(Template, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            branches_all = models.Branch.objects.filter(**{
                "created_at__gte": timedate.datetime.now() - timedate.timedelta(days=1),
                "created_at__lte": timedate.datetime.now(),
            })
        elif period == 'weekly':
            branches_all = models.Branch.objects.filter(**{
                "created_at__gte": timedate.datetime.now() - timedate.timedelta(days=7),
                "created_at__lte": timedate.datetime.now(),
            })

        elif period == 'monthly':
            branches_all = models.Branch.objects.filter(**{
                "created_at__gte": timedate.datetime.now() - timedate.timedelta(days=30),
                "created_at__lte": timedate.datetime.now(),
            })
        elif period == 'yearly':
            branches_all = models.Branch.objects.filter(**{
                "created_at__gte": timedate.datetime.now() - timedate.timedelta(days=365),
                "created_at__lte": timedate.datetime.now(),
            })
        else:
            branches_all = models.Branch.objects.filter()

        truncate_date = connection.ops.date_trunc_sql('day', 'created_at')
        company = models.Company.objects.last()
        # B2B
        branch_b2b = models.Branch.objects.filter(type_of_branch='b2b')
        shop_b2b = models.Shop.objects.extra({'day': truncate_date}).values('day').annotate(Sum('cash_sum')).filter(
            branch__in=branch_b2b)

        data_b2b = list(
            map(lambda x: x['cash_sum__sum'],
                shop_b2b))

        b2b_datetime_data = list(
            map(lambda x: datetime.strptime(x['day'], '%Y-%m-%d').strftime('%Y/%m/%d %H:%M:%S'), shop_b2b))

        # Do'llar
        shop_b2b_cash_dollar = models.Shop.objects.extra({'day': truncate_date}).values('day').annotate(
            Sum('cash_dollar')).filter(
            branch__in=branch_b2b)

        data_b2b_cash_dollar = list(
            map(lambda x: x['cash_dollar__sum'],
                shop_b2b_cash_dollar))

        # Card
        shop_b2b_card = models.Shop.objects.extra({'day': truncate_date}).values('day').annotate(
            Sum('card')).filter(
            branch__in=branch_b2b)
        data_b2b_card = list(
            map(lambda x: x['card__sum'],
                shop_b2b_card))

        # Transfer
        shop_b2b_transfer = models.Shop.objects.extra({'day': truncate_date}).values('day').annotate(
            Sum('transfer')).filter(
            branch__in=branch_b2b)

        data_b2b_transfer = list(
            map(lambda x: x['transfer__sum'],
                shop_b2b_transfer))
        """
            B2C
            So'm, do'llar, card, transfer
        """
        # So'm
        branch_b2c = models.Branch.objects.filter(type_of_branch='b2c')

        shop_b2c_cash_sum = models.Shop.objects.extra({'day': truncate_date}).values('day').annotate(
            Sum('cash_sum')).filter(
            branch__in=branch_b2c)
        data_b2c_cash_sum = list(
            map(lambda x: x['cash_sum__sum'],
                shop_b2c_cash_sum))

        # Do'llar
        shop_b2c_cash_dollar = models.Shop.objects.extra({'day': truncate_date}).values('day').annotate(
            Sum('cash_dollar')).filter(
            branch__in=branch_b2c)
        data_b2c_cash_dollar = list(
            map(lambda x: x['cash_dollar__sum'],
                shop_b2c_cash_dollar))

        # Card
        shop_b2b_card = models.Shop.objects.extra({'day': truncate_date}).values('day').annotate(
            Sum('card')).filter(
            branch__in=branch_b2c)
        data_b2c_card = list(
            map(lambda x:
                x['card__sum'],
                shop_b2b_card))

        # Transfer
        shop_b2c_transfer = models.Shop.objects.extra({'day': truncate_date}).values('day').annotate(
            Sum('transfer')).filter(
            branch__in=branch_b2c)
        data_b2c_transfer = list(
            map(lambda x: x['transfer__sum'],
                shop_b2c_transfer))

        # B2B
        # Total statistic for each month
        truncate_date_for_moth_b2b = connection.ops.date_trunc_sql('month', 'created_at')

        monthly_b2b_sum = models.Shop.objects.extra({'month': truncate_date_for_moth_b2b}).values('month').annotate(
            Sum('cash_sum')).filter(branch__in=branch_b2b)
        monthly_b2b_dollar = models.Shop.objects.extra({'month': truncate_date_for_moth_b2b}).values('month').annotate(
            Sum('cash_dollar')).filter(branch__in=branch_b2b)
        monthly_b2b_card = models.Shop.objects.extra({'month': truncate_date_for_moth_b2b}).values('month').annotate(
            Sum('card')).filter(branch__in=branch_b2b)
        monthly_b2b_transfer = models.Shop.objects.extra({'month': truncate_date_for_moth_b2b}).values(
            'month').annotate(Sum('transfer')).filter(branch__in=branch_b2b)

        total_monthly__b2b_sum = list(map(lambda x: x['cash_sum__sum'], monthly_b2b_sum))
        total_monthly__b2b_dollar = list(map(lambda x: x['cash_dollar__sum'], monthly_b2b_dollar))
        total_monthly__b2b_card = list(map(lambda x: x['card__sum'], monthly_b2b_card))
        total_monthly__b2b_transfer = list(map(lambda x: x['transfer__sum'], monthly_b2b_transfer))
        # B2C
        monthly_b2c_sum = models.Shop.objects.extra({'month': truncate_date_for_moth_b2b}).values('month').annotate(
            Sum('cash_sum')).filter(branch__in=branch_b2c)
        monthly_b2c_dollar = models.Shop.objects.extra({'month': truncate_date_for_moth_b2b}).values('month').annotate(
            Sum('cash_dollar')).filter(branch__in=branch_b2c)
        monthly_b2c_card = models.Shop.objects.extra({'month': truncate_date_for_moth_b2b}).values('month').annotate(
            Sum('card')).filter(branch__in=branch_b2c)
        monthly_b2c_transfer = models.Shop.objects.extra({'month': truncate_date_for_moth_b2b}).values(
            'month').annotate(Sum('transfer')).filter(branch__in=branch_b2c)

        total_monthly__b2c_sum = list(map(lambda x: x['cash_sum__sum'], monthly_b2c_sum))
        total_monthly__b2c_dollar = list(map(lambda x: x['cash_dollar__sum'], monthly_b2c_dollar))
        total_monthly__b2c_card = list(map(lambda x: x['card__sum'], monthly_b2c_card))
        total_monthly__b2c_transfer = list(map(lambda x: x['transfer__sum'], monthly_b2c_transfer))

        b2b_datetime_data_by_month = list(
            map(lambda x: datetime.strptime(x['month'], '%Y-%m-%d').strftime('%B'), monthly_b2b_sum))
        b2c_datetime_data_by_month = list(
            map(lambda x: datetime.strptime(x['month'], '%Y-%m-%d').strftime('%B'), monthly_b2c_sum))

        # By month
        # B2B
        ctx['b2b_datetime_data_by_month'] = list(b2b_datetime_data_by_month)
        ctx['total_monthly__b2b_sum'] = list(total_monthly__b2b_sum)
        ctx['total_monthly__b2b_dollar'] = list(total_monthly__b2b_dollar)
        ctx['total_monthly__b2b_card'] = list(total_monthly__b2b_card)
        ctx['total_monthly__b2b_transfer'] = list(total_monthly__b2b_transfer)
        # B2C
        ctx['b2c_datetime_data_by_month'] = list(b2c_datetime_data_by_month)
        ctx['total_monthly__b2c_sum'] = list(total_monthly__b2c_sum)
        ctx['total_monthly__b2c_dollar'] = list(total_monthly__b2c_dollar)
        ctx['total_monthly__b2c_card'] = list(total_monthly__b2c_card)
        ctx['total_monthly__b2c_transfer'] = list(total_monthly__b2c_transfer)

        # By date
        ctx['b2b_datetime_data'] = list(b2b_datetime_data)
        ctx['data_b2b'] = list(data_b2b)
        ctx['data_b2b_cash_dollar'] = list(data_b2b_cash_dollar)
        ctx['data_b2b_card'] = list(data_b2b_card)
        ctx['data_b2b_transfer'] = list(data_b2b_transfer)

        # B2C
        ctx['data_b2c_cash_sum'] = list(data_b2c_cash_sum)
        ctx['data_b2c_cash_dollar'] = list(data_b2c_cash_dollar)
        ctx['data_b2c_card'] = list(data_b2c_card)
        ctx['data_b2c_transfer'] = list(data_b2c_transfer)

        ctx['total_sum'] = company.balance_sum if company.balance_sum >= 0 else 0
        ctx['total_dollar'] = company.balance_dollar if company.balance_dollar >= 0 else 0
        ctx[
            'bank'] = company.balance_transfer + company.balance_card if company.balance_transfer + company.balance_card >= 0 else 0
        ctx['branches'] = branches_all
        return ctx



class DiscountCardListView(LoginRequiredMixin, generic.ListView):
    model = models.DiscountCard
    form_class = forms.DiscountCardForm


class DiscountCardCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.DiscountCard
    form_class = forms.DiscountCardForm


class DiscountCardDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.DiscountCard
    form_class = forms.DiscountCardForm


class DiscountCardUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.DiscountCard
    form_class = forms.DiscountCardForm
    pk_url_kwarg = "pk"


class CartListView(LoginRequiredMixin, generic.ListView):
    model = models.Cart
    form_class = forms.CartForm


class CartCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Cart
    form_class = forms.CartForm


class CartDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Cart
    form_class = forms.CartForm


class CartUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Cart
    form_class = forms.CartForm
    pk_url_kwarg = "pk"


class RealizeListView(LoginRequiredMixin, generic.ListView):
    model = models.Realize
    form_class = forms.RealizeForm


class RealizeCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Realize
    form_class = forms.RealizeForm


class RealizeDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Realize
    form_class = forms.RealizeForm


class RealizeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Realize
    form_class = forms.RealizeForm
    pk_url_kwarg = "pk"


class ProductRequestListView(LoginRequiredMixin, generic.ListView):
    model = models.ProductRequest
    form_class = forms.ProductRequestForm


class ProductRequestCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ProductRequest
    form_class = forms.ProductRequestForm


class ProductRequestDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ProductRequest
    form_class = forms.ProductRequestForm


class ProductRequestUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ProductRequest
    form_class = forms.ProductRequestForm
    pk_url_kwarg = "pk"


class InvoiceItemListView(LoginRequiredMixin, generic.ListView):
    model = models.InvoiceItem
    form_class = forms.InvoiceItemForm


class InvoiceItemCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.InvoiceItem
    form_class = forms.InvoiceItemForm


class InvoiceItemDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.InvoiceItem
    form_class = forms.InvoiceItemForm


class InvoiceItemUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.InvoiceItem
    form_class = forms.InvoiceItemForm
    pk_url_kwarg = "pk"


class BrokenProductListView(LoginRequiredMixin, generic.ListView):
    model = models.BrokenProduct
    form_class = forms.BrokenProductForm


class BrokenProductCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.BrokenProduct
    form_class = forms.BrokenProductForm


class BrokenProductDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.BrokenProduct
    form_class = forms.BrokenProductForm


class BrokenProductUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.BrokenProduct
    form_class = forms.BrokenProductForm
    pk_url_kwarg = "pk"


class MinimalListView(LoginRequiredMixin, generic.ListView):
    model = models.Minimal
    form_class = forms.MinimalForm


class MinimalCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Minimal
    form_class = forms.MinimalForm


class MinimalDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Minimal
    form_class = forms.MinimalForm


class MinimalUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Minimal
    form_class = forms.MinimalForm
    pk_url_kwarg = "pk"


class ClientListView(LoginRequiredMixin, generic.ListView):
    model = models.Client
    form_class = forms.ClientForm


class ClientCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Client
    form_class = forms.ClientForm


class ClientDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Client
    form_class = forms.ClientForm


class ClientUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Client
    form_class = forms.ClientForm
    pk_url_kwarg = "pk"


class InventoryListView(LoginRequiredMixin, generic.ListView):
    model = models.InventoryInvoice
    form_class = forms.InventoryInvoiceForm


class InventoryCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.InventoryInvoice
    form_class = forms.InventoryInvoiceForm


class InventoryDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.InventoryInvoice
    form_class = forms.InventoryInvoiceForm


class InventoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.InventoryInvoice
    form_class = forms.InventoryInvoiceForm
    pk_url_kwarg = "pk"


class ClientPaymentHistoryListView(LoginRequiredMixin, generic.ListView):
    model = models.ClientPaymentHistory
    form_class = forms.ClientPaymentHistoryForm


class ClientPaymentHistoryCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ClientPaymentHistory
    form_class = forms.ClientPaymentHistoryForm


class ClientPaymentHistoryDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ClientPaymentHistory
    form_class = forms.ClientPaymentHistoryForm


class ClientPaymentHistoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ClientPaymentHistory
    form_class = forms.ClientPaymentHistoryForm
    pk_url_kwarg = "pk"


class ProductListView(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/residual-goods/list.html'
    model = models.Product

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(ProductListView, self).get_context_data(**kwargs)
        products = models.ProductThroughBranch.objects.filter(branch__type_of_branch='b2b').order_by('-id')
        branches = models.Branch.objects.filter(type_of_branch='b2b').order_by('-id')
        ctx['products'] = products
        ctx['branches'] = branches
        return ctx


class ProductB2CListView(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/residual-goods/b2c_list.html'
    model = models.Product

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(ProductB2CListView, self).get_context_data(**kwargs)
        products = models.ProductThroughBranch.objects.filter(branch__type_of_branch='b2c').order_by('-id')
        branches = models.Branch.objects.filter(type_of_branch='b2c').order_by('-id')
        ctx['products'] = products
        ctx['branches'] = branches
        return ctx


class ProductCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Product
    form_class = forms.ProductForm


class ProductDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Product
    form_class = forms.ProductForm


class ProductUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Product
    form_class = forms.ProductForm
    pk_url_kwarg = "pk"


class ClientReturnListView(LoginRequiredMixin, generic.ListView):
    model = models.ClientReturn
    form_class = forms.ClientReturnForm


class ClientReturnCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ClientReturn
    form_class = forms.ClientReturnForm


class ClientReturnDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ClientReturn
    form_class = forms.ClientReturnForm


class ClientReturnUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ClientReturn
    form_class = forms.ClientReturnForm
    pk_url_kwarg = "pk"


class SectionListView(LoginRequiredMixin, generic.ListView):
    model = models.Section
    form_class = forms.SectionForm


class SectionCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Section
    form_class = forms.SectionForm


class SectionDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Section
    form_class = forms.SectionForm


class SectionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Section
    form_class = forms.SectionForm
    pk_url_kwarg = "pk"


class InvoiceListView(LoginRequiredMixin, generic.ListView):
    model = models.Invoice
    form_class = forms.InvoiceForm


class InvoiceCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Invoice
    form_class = forms.InvoiceForm


class InvoiceDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Invoice
    form_class = forms.InvoiceForm


class InvoiceUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Invoice
    form_class = forms.InvoiceForm
    pk_url_kwarg = "pk"


class ReturnDeliverProductListView(LoginRequiredMixin, generic.ListView):
    model = models.ReturnDeliverProduct
    form_class = forms.ReturnDeliverProductForm


class ReturnDeliverProductCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ReturnDeliverProduct
    form_class = forms.ReturnDeliverProductForm


class ReturnDeliverProductDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ReturnDeliverProduct
    form_class = forms.ReturnDeliverProductForm


class ReturnDeliverProductUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ReturnDeliverProduct
    form_class = forms.ReturnDeliverProductForm
    pk_url_kwarg = "pk"


class CurrencyListView(LoginRequiredMixin, generic.ListView):
    model = models.Currency
    form_class = forms.CurrencyForm


class CurrencyCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Currency
    form_class = forms.CurrencyForm


class CurrencyDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Currency
    form_class = forms.CurrencyForm


class CurrencyUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Currency
    form_class = forms.CurrencyForm
    pk_url_kwarg = "pk"


class ShopListView(LoginRequiredMixin, generic.ListView):
    model = models.Shop
    form_class = forms.ShopForm


class ShopCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Shop
    form_class = forms.ShopForm


class ShopDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Shop
    form_class = forms.ShopForm


class ShopUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Shop
    form_class = forms.ShopForm
    pk_url_kwarg = "pk"


# Fillial boshqaruvi B2B
class BranchTemplateViewB2B(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/branch/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(BranchTemplateViewB2B, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            shops = models.Shop.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'weekly':
            shops = models.Shop.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'monthly':
            shops = models.Shop.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'yearly':
            shops = models.Shop.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        else:
            shops = models.Shop.objects.filter().order_by('-id')

        total_sum, total_dollar = [], []

        for i in shops:
            total_sum.append(i.cash_sum)
            total_dollar.append(i.cash_dollar)

        ctx['shops'] = shops
        ctx['total_sum'] = sum(total_sum)
        ctx['total_dollar'] = sum(total_dollar)
        branches = models.Branch.objects.filter()
        print(branches)
        ctx['branches'] = branches

        return ctx


# Fillial boshqaruvi B2C
class BranchTemplateViewB2C(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/branch/index_b2c.html'

    def get_context_data(self, **kwargs):
        ctx = super(BranchTemplateViewB2C, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            shops = models.Shop.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'weekly':
            shops = models.Shop.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'monthly':
            shops = models.Shop.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'yearly':
            shops = models.Shop.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        else:
            shops = models.Shop.objects.filter().order_by('-id')
            seller = models.Staff.objects.filter(shop_seller__isnull=False).distinct()

        total_sum, total_dollar = [], []


        for i in shops:
            total_sum.append(i.cash_sum)
            total_dollar.append(i.cash_dollar)


        ctx['shops'] = seller
        ctx['total_sum'] = sum(total_sum)
        ctx['total_dollar'] = sum(total_dollar)
        branches = models.Branch.objects.filter()
        ctx['branches'] = branches

        return ctx


class BranchListView(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/branches/list.html'
    model = models.Branch
    form_class = forms.BranchForm


class BranchCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'app/director/pages/settings/index.html'
    model = models.Branch
    form_class = forms.BranchForm
    success_url = reverse_lazy('settings')

    def form_valid(self, form):
        return super(BranchCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(BranchCreateView, self).form_invalid(form)


class BranchDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Branch
    form_class = forms.BranchForm


class BranchUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Branch
    form_class = forms.BranchForm
    pk_url_kwarg = "pk"


class CategoryListView(LoginRequiredMixin, generic.ListView):
    model = models.Category
    form_class = forms.CategoryForm


class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Category
    form_class = forms.CategoryForm


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Category
    form_class = forms.CategoryForm


class CategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Category
    form_class = forms.CategoryForm
    pk_url_kwarg = "pk"


class DeliverListView(LoginRequiredMixin, generic.ListView):
    model = models.Deliver
    form_class = forms.DeliverForm


class DeliverCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Deliver
    form_class = forms.DeliverForm


class DeliverDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Deliver
    form_class = forms.DeliverForm


class DeliverUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Deliver
    form_class = forms.DeliverForm
    pk_url_kwarg = "pk"


class DifferProductRecieveHistoryListView(LoginRequiredMixin, generic.ListView):
    model = models.DifferProductRecieveHistory
    form_class = forms.DifferProductRecieveHistoryForm


class DifferProductRecieveHistoryCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.DifferProductRecieveHistory
    form_class = forms.DifferProductRecieveHistoryForm


class DifferProductRecieveHistoryDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.DifferProductRecieveHistory
    form_class = forms.DifferProductRecieveHistoryForm


class DifferProductRecieveHistoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.DifferProductRecieveHistory
    form_class = forms.DifferProductRecieveHistoryForm
    pk_url_kwarg = "pk"


class StaffListView(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/staffs/list.html'
    model = models.Staff

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(StaffListView, self).get_context_data(**kwargs)
        branches = models.Branch.objects.all()
        staffs = models.Staff.objects.filter().order_by('-id')
        context['branches'] = branches
        context['staffs'] = staffs
        return context


class StaffDetailTemplateView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/staffs/detail.html'


class StaffCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Staff
    form_class = forms.StaffForm

    def form_valid(self, form):
        return super(StaffCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(StaffCreateView, self).form_invalid(form)


class SettingsCreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = 'app/director/pages/settings/index.html'
    form_class = forms.SettingsModelForm
    model = models.Staff
    success_url = reverse_lazy('settings')
    success_message = "Muvafaqiyatli yaratildi"

    def get_form(self, form_class=None):
        return super().get_form(form_class)

    def get_context_data(self, **kwargs):
        context = super(SettingsCreateView, self).get_context_data(**kwargs)
        context["staff_form"] = context["form"]
        context["branch_form"] = forms.BranchForm(**self.get_form_kwargs())
        return context

    def form_valid(self, form):
        form.save(commit=False)
        return super(SettingsCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SettingsCreateView, self).form_invalid(form)


class StaffDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Staff
    form_class = forms.StaffForm


class StaffUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Staff
    form_class = forms.StaffForm
    success_url = reverse_lazy('app_staff_list')

    def form_valid(self, form):
        form.save(commit=False)
        return super(StaffUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(StaffUpdateView, self).form_invalid(form)


class CashboxTemplateView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/cashbox/index.html'

    def get_context_data(self, **kwargs):
        from django.db import connection
        from django.db.models import Sum, Count
        import datetime

        ctx = super(CashboxTemplateView, self).get_context_data(**kwargs)
        company = models.Company.objects.last()

        truncate_date = connection.ops.date_trunc_sql('day', 'created_at')
        # Income
        incomes = models.Income.objects.extra({'day': truncate_date})
        # Outcome
        outcomes = models.Outcome.objects.extra({'day': truncate_date})

        sum_daily_outcomes = outcomes.values('day').annotate(Sum('sum'), Count('pk')).order_by('day')
        dollar_daily_outcomes = outcomes.values('day').annotate(Sum('dollar'), Count('pk')).order_by('day')
        transfer_daily_outcomes = outcomes.values('day').annotate(Sum('transfer'), Count('pk')).order_by('day')
        card_daily_outcomes = outcomes.values('day').annotate(Sum('card'), Count('pk')).order_by('day')
        report_sum_daily_outcomes, report_dollar_daily_outcomes, report_transfer_daily_outcomes, report_card_daily_outcomes = [], [], [], []

        sum_daily = incomes.values('day').annotate(Sum('sum'), Count('pk')).order_by('day')
        dollar_daily = incomes.values('day').annotate(Sum('dollar'), Count('pk')).order_by('day')
        transfer_daily = incomes.values('day').annotate(Sum('transfer'), Count('pk')).order_by('day')
        card_daily = incomes.values('day').annotate(Sum('card'), Count('pk')).order_by('day')
        report_sum_daily, report_dollar_daily, report_transfer_daily, report_card_daily = [], [], [], []
        """ Output Report """
        # Card
        for i in card_daily_outcomes:
            for x, y in i.items():
                report_card_daily_outcomes.append(y)

        daily_total_card_outcomes = []
        for x in report_card_daily_outcomes:
            if type(x) == float:
                daily_total_card_outcomes.append(x)
        # Dollar
        for i in dollar_daily_outcomes:
            for x, y in i.items():
                report_dollar_daily_outcomes.append(y)

        daily_total_dollar_outcomes = []
        for x in report_dollar_daily_outcomes:
            if type(x) == float:
                daily_total_dollar_outcomes.append(x)

        # Sum

        for i in sum_daily_outcomes:
            for x, y in i.items():
                report_sum_daily_outcomes.append(y)

        daily_total_sum_outcomes = []
        for x in report_sum_daily_outcomes:
            if type(x) == float:
                daily_total_sum_outcomes.append(x)

        # Transfer

        for i in transfer_daily_outcomes:
            for x, y in i.items():
                report_transfer_daily_outcomes.append(y)

        daily_total_transfer_outcomes = []
        for x in report_transfer_daily_outcomes:
            if type(x) == float:
                daily_total_transfer_outcomes.append(x)

        """ Income Report """
        # Card

        for i in card_daily:
            for x, y in i.items():
                report_card_daily.append(y)

        daily_total_card = []
        for x in report_card_daily:
            if type(x) == float:
                daily_total_card.append(x)

        # Transfer

        for i in transfer_daily:
            for x, y in i.items():
                report_transfer_daily.append(y)

        daily_total_transfer = []
        for x in report_transfer_daily:
            if type(x) == float:
                daily_total_transfer.append(x)

        # Dollar
        for i in dollar_daily:
            for x, y in i.items():
                report_dollar_daily.append(y)

        daily_total_dollar = []
        for x in report_dollar_daily:
            if type(x) == float:
                daily_total_dollar.append(x)
        # Sum
        for i in sum_daily:
            for x, y in i.items():
                report_sum_daily.append(y)
        dates, temp = [], []
        for i in report_sum_daily:
            if type(i) == str:
                temp.append(datetime.date.fromisoformat(i))

        for x in temp:
            dates.append(x.strftime('%Y/%m/%d'))

        daily_total_sum = []
        for x in report_sum_daily:
            if type(x) == float:
                daily_total_sum.append(x)

        """ Output Report """

        # Card
        ctx['daily_total_card_outcomes'] = daily_total_card_outcomes
        # Dollar
        ctx['daily_total_dollar_outcomes'] = daily_total_dollar_outcomes
        # Sum
        ctx['daily_total_sum_outcomes'] = daily_total_sum_outcomes
        # Transfer
        ctx['daily_total_transfer_outcomes'] = daily_total_transfer_outcomes

        """ Income Report """
        # Sum
        ctx['daily_total_sum'] = daily_total_sum
        # Dollar
        ctx['daily_total_dollar'] = daily_total_dollar
        # Transfer
        ctx['daily_total_transfer'] = daily_total_transfer
        # Card
        ctx['daily_total_card'] = daily_total_card
        ctx['date'] = dates

        ctx['total_sum'] = company.balance_sum
        ctx['total_dollar'] = company.balance_dollar
        ctx['total_transfer'] = company.balance_transfer
        ctx['total_card'] = company.balance_card
        return ctx


class IncomeAccountTemplateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = 'app/director/pages/income-account/index.html'
    form_class = forms.IncomeModelForm
    model = models.Income
    success_url = reverse_lazy('income_account')
    success_message = "Muvofaqiyatli yaratildi"

    def get_context_data(self, **kwargs):
        ctx = super(IncomeAccountTemplateView, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            income_from_persons = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'weekly':
            income_from_persons = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'monthly':
            income_from_persons = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'yearly':
            income_from_persons = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        else:
            income_from_persons = self.model.objects.filter().order_by('-id')
        ctx['income_from_persons'] = income_from_persons
        return ctx

    def form_valid(self, form):
        company = models.Company.objects.last()
        company.balance_sum += float(form.data.get('sum', 0))
        company.balance_dollar += float(form.data.get('dollar', 0))
        company.balance_transfer += float(form.data.get('transfer', 0))
        company.balance_card += float(form.data.get('card', 0))
        company.save()
        return super(IncomeAccountTemplateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(IncomeAccountTemplateView, self).form_valid(form)


class ExpenseAccountTemplateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = 'app/director/pages/expense-account/index.html'
    form_class = forms.OutcomeModelForm
    model = models.Outcome
    success_url = reverse_lazy('expense_account')
    success_message = "Muvofaqiyatli yaratildi"

    def get_context_data(self, **kwargs):
        ctx = super(ExpenseAccountTemplateView, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            income_from_persons = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'weekly':
            income_from_persons = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'monthly':
            income_from_persons = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        elif period == 'yearly':
            income_from_persons = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            }).order_by('-id')
        else:
            income_from_persons = self.model.objects.filter().order_by('-id')
        ctx['income_from_persons'] = income_from_persons
        print("ctx", ctx)
        return ctx

    def form_valid(self, form):
        company = models.Company.objects.last()
        company.balance_sum -= float(form.data['sum'])
        company.balance_dollar -= float(form.data['dollar'])
        company.balance_transfer -= float(form.data['transfer'])
        company.balance_card -= float(form.data['card'])
        company.save()
        return super(ExpenseAccountTemplateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ExpenseAccountTemplateView, self).form_valid(form)


# Mijozdan qaytuv B2B
class GetBackFromTheCustomerTemplateViewB2B(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/get-back-from-the-customer/index.html'
    model = models.ClientReturn

    def get_context_data(self, **kwargs):
        ctx = super(GetBackFromTheCustomerTemplateViewB2B, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'weekly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        elif period == 'monthly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),

            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            print(cart_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'yearly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        else:
            client_returns = self.model.objects.filter(section__branch__type_of_branch="b2b")
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)
            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        client_price_id_dollar = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='dollar')
        client_price_id_sum = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='sum')
        total_selling_price_in_dollar = []
        total_selling_price_in_sum = []
        for i in client_price_id_dollar:
            for cartitem in i.cartitem_set.all():
                total_selling_price_in_dollar.append(cartitem.selling_price)

        for i in client_price_id_sum:
            for cartitem in i.cartitem_set.all():
                for i in cartitem.product.productthroughbranch_set.filter():
                    total_selling_price_in_sum.append(i.selling_price)

        branch = models.Branch.objects.filter()
        ctx['total_selling_price_in_dollar'] = sum(total_selling_price_in_dollar)
        ctx['total_selling_price_in_sum'] = sum(total_selling_price_in_sum)
        ctx['products'] = product_list
        ctx['branches'] = branch
        return ctx


# Mijozdan qaytuv B2C
class GetBackFromTheCustomerTemplateViewB2C(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/get-back-from-the-customer/index1.html'
    model = models.ClientReturn

    def get_context_data(self, **kwargs):
        ctx = super(GetBackFromTheCustomerTemplateViewB2C, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'weekly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        elif period == 'monthly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),

            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            print(cart_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'yearly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        else:
            client_returns = self.model.objects.filter(section__branch__type_of_branch="b2c")
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)
            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        client_price_id_dollar = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='dollar')
        client_price_id_sum = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='sum')
        total_selling_price_in_dollar = []
        total_selling_price_in_sum = []
        for i in client_price_id_dollar:
            for cartitem in i.cartitem_set.all():
                total_selling_price_in_dollar.append(cartitem.selling_price)

        for i in client_price_id_sum:
            for cartitem in i.cartitem_set.all():
                for i in cartitem.product.productthroughbranch_set.filter():
                    total_selling_price_in_sum.append(i.selling_price)

        branch = models.Branch.objects.filter()
        ctx['total_selling_price_in_dollar'] = sum(total_selling_price_in_dollar)
        ctx['total_selling_price_in_sum'] = sum(total_selling_price_in_sum)
        ctx['products'] = product_list
        ctx['branches'] = branch
        return ctx


class GetBackFromTheCustomer1TemplateView(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/get-back-from-the-customer/index1.html'
    model = models.ClientReturn

    def get_context_data(self, **kwargs):
        ctx = super(GetBackFromTheCustomer1TemplateView, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'weekly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        elif period == 'monthly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'yearly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        else:
            client_returns = self.model.objects.filter()
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        client_price_id_dollar = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='dollar')
        client_price_id_sum = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='sum')
        total_selling_price_in_dollar = []
        total_selling_price_in_sum = []
        for i in client_price_id_dollar:
            for cartitem in i.cartitem_set.all():
                total_selling_price_in_dollar.append(cartitem.product.selling_price)

        for i in client_price_id_sum:
            for cartitem in i.cartitem_set.all():
                for i in cartitem.product.productthroughbranch_set.filter():
                    total_selling_price_in_sum.append(i.selling_price)

        branch = models.Branch.objects.filter()
        ctx['total_selling_price_in_dollar'] = sum(total_selling_price_in_dollar)
        ctx['total_selling_price_in_sum'] = sum(total_selling_price_in_sum)
        ctx['products'] = product_list
        ctx['branches'] = branch
        return ctx


class GetBackFromTheCustomer2TemplateView(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/written-off-goods/indexB2C.html'
    model = models.ClientReturn

    def get_context_data(self, **kwargs):
        ctx = super(GetBackFromTheCustomer2TemplateView, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'weekly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        elif period == 'monthly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'yearly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        else:
            client_returns = self.model.objects.filter()
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        client_price_id_dollar = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='dollar')
        client_price_id_sum = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='sum')
        total_selling_price_in_dollar = []
        total_selling_price_in_sum = []
        for i in client_price_id_dollar:
            for cartitem in i.cartitem_set.all():
                total_selling_price_in_dollar.append(cartitem.product.selling_price)

        for i in client_price_id_sum:
            for cartitem in i.cartitem_set.all():
                for i in cartitem.product.productthroughbranch_set.filter():
                    total_selling_price_in_sum.append(i.selling_price)

        branch = models.Branch.objects.filter()
        ctx['total_selling_price_in_dollar'] = sum(total_selling_price_in_dollar)
        ctx['total_selling_price_in_sum'] = sum(total_selling_price_in_sum)
        ctx['products'] = product_list
        ctx['branches'] = branch
        return ctx


class GetBackFromTheCustomer3TemplateView(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/goods-movement-analysis/indexB2C.html'
    model = models.ClientReturn

    def get_context_data(self, **kwargs):
        ctx = super(GetBackFromTheCustomer3TemplateView, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'weekly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        elif period == 'monthly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        elif period == 'yearly':
            client_returns = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)
        else:
            client_returns = self.model.objects.filter()
            cart_id_list = []
            product_list = []
            for client_return in client_returns:
                cart_id_list.append(client_return.cart.id)

            cart_list = models.Cart.objects.filter(id__in=cart_id_list)
            for cart in cart_list:
                for cartitem in cart.cartitem_set.all():
                    product_list.append(cartitem.product)

        client_price_id_dollar = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='dollar')
        client_price_id_sum = models.Cart.objects.filter(id__in=cart_id_list, cartitem__product__currency='sum')
        total_selling_price_in_dollar = []
        total_selling_price_in_sum = []
        for i in client_price_id_dollar:
            for cartitem in i.cartitem_set.all():
                total_selling_price_in_dollar.append(cartitem.product.selling_price)

        for i in client_price_id_sum:
            for cartitem in i.cartitem_set.all():
                for i in cartitem.product.productthroughbranch_set.filter():
                    total_selling_price_in_sum.append(i.selling_price)

        branch = models.Branch.objects.filter()
        ctx['total_selling_price_in_dollar'] = sum(total_selling_price_in_dollar)
        ctx['total_selling_price_in_sum'] = sum(total_selling_price_in_sum)
        ctx['products'] = product_list
        ctx['branches'] = branch
        return ctx


class GoodsReturnedFromDomStroy(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/goods-returned-from-dom-stroy/index.html'


class IncomeAndExpensesOfGoods(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/income-and-expenses-of-goods/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(IncomeAndExpensesOfGoods, self).get_context_data(**kwargs)
        # Product
        #
        products = models.Product.objects.filter()
        total_cost = []
        total_selling_price = []
        for i in products:
            total_cost.append(i.cost)
            total_selling_price.append(i.selling_price)

        ctx['products'] = products
        ctx['total_cost'] = sum(total_cost)
        ctx['total_selling_price'] = sum(total_selling_price)
        return ctx


class WrittenOffGoods(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/written-off-goods/index.html'
    model = models.BrokenProduct

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(WrittenOffGoods, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            broken_product = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'weekly':
            broken_product = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })

            broken_product = self.model.objects.filter(
                Q(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7)) & Q(
                    created_at__lte=datetime.datetime.now()))

        elif period == 'monthly':
            broken_product = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'yearly':
            broken_product = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
        else:
            broken_product = self.model.objects.filter()

        branches = models.Branch.objects.filter()
        selling_price_in_sum = self.model.objects.filter(product__currency='sum')
        selling_price_in_dollar = self.model.objects.filter(product__currency='dollar')
        total_selling_price_in_sum = []
        total_selling_price_in_dollar = []
        for i in selling_price_in_dollar:
            for k in i.product.productthroughbranch_set.all():
                total_selling_price_in_sum.append(k.selling_price)

        for i in selling_price_in_sum:
            for k in i.product.productthroughbranch_set.all():
                total_selling_price_in_sum.append(k.selling_price)

        ctx['total_selling_price_in_sum'] = sum(total_selling_price_in_sum)
        ctx['total_selling_price_in_dollar'] = sum(total_selling_price_in_dollar)
        ctx['branches'] = branches
        ctx['broken_products'] = broken_product
        return ctx


class IncomeAnalysis(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/income-analysis/index.html'
    model = models.Shop

    def post(self):
        pass

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(IncomeAnalysis, self).get_context_data(**kwargs)
        shops = self.model.objects.filter()
        cart_id_list = []
        product_list = []
        # for shop in shops:
        #     cart_id_list.append(shop.card.id)
        # cart = models.Cart.objects.filter(shop)
        cart_item = models.CartItem.objects.filter()
        # CartItem -> product
        # Cart
        # Shop
        ctx['shops'] = shops
        return ctx


class GoodsMovementAnalysis(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/goods-movement-analysis/index.html'
    model = models.ProductThroughBranch

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = forms.NormativeDay(request.POST)
            if form.is_valid():
                models.ProductThroughBranch.objects.filter(id=int(form.data['product_id'])).update(
                    normative=int(form.data['name']))
                return HttpResponse('Form is valid')
        else:
            form = forms.NormativeDay()
            return HttpResponse('Form is not valid')
        return HttpResponse('Form is not valid')

    def get_context_data(self, **kwargs):
        ctx = super(GoodsMovementAnalysis, self).get_context_data(**kwargs)

        product = models.ProductThroughBranch.objects.all()
        branches = models.Branch.objects.all()
        ctx['branches'] = branches
        ctx['products'] = product
        return ctx


class GoodsMovementAnalysisEdit(generic.UpdateView):
    model = models.ProductThroughBranch
    form_class = forms.NormativeDay
    success_url = reverse_lazy('goods_movement_analysis')

    def form_valid(self, form):
        return super(GoodsMovementAnalysisEdit, self).form_valid(form)

    def form_invalid(self, form):
        return super(GoodsMovementAnalysisEdit, self).form_invalid(form)


class RealizedGoods(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/realized-goods/index.html'


class ContractorsTemplateView(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/contractors/index.html'
    model = models.Deliver

    def get_context_data(self, **kwargs):
        ctx = super(ContractorsTemplateView, self).get_context_data(**kwargs)
        deliver = self.model.objects.filter()
        a = models.CartItem.objects.filter(product__deliver__in=deliver)
        ctx['delivers'] = deliver
        return ctx


class ContractorsDetailTemplateView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/contractors/detail.html'
    # model = models.Deliver

    # def get_context_data(self, **kwargs):
    #     ctx = super(ContractorsDetailTemplateView, self).get_context_data(**kwargs)
    #
    #     return ctx


# Molya boshqarivu Postavshik hisobi B2B
class DeliveryReportTemplateViewB2B(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/delivery-report/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(DeliveryReportTemplateViewB2B, self).get_context_data(**kwargs)
        producers = models.Deliver.objects.filter(type="b2b")
        ctx['producers'] = producers
        return ctx


# Molya boshqarivu Postavshik hisobi B2C
class DeliveryReportTemplateViewB2C(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/delivery-report/index_b2c.html'

    def get_context_data(self, **kwargs):
        ctx = super(DeliveryReportTemplateViewB2C, self).get_context_data(**kwargs)
        producers = models.Deliver.objects.filter(type="b2c")
        ctx['producers'] = producers
        print(ctx)
        return ctx


class DeliveryTemplateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'app/financier/deliver/list.html'
    form_class = forms.ProducerModelForm
    model = models.Deliver
    success_url = reverse_lazy('delivery')

    def get_context_data(self, **kwargs):
        ctx = super(DeliveryTemplateView, self).get_context_data(**kwargs)
        producers = self.model.objects.filter()
        ctx['producers'] = producers
        return ctx

    def form_valid(self, form):
        return super(DeliveryTemplateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(DeliveryTemplateView, self).form_invalid(form)


class DeliveryDetailTemplateView(LoginRequiredMixin, generic.DetailView):
    model = models.Deliver
    template_name = 'app/financier/deliver/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DeliveryDetailTemplateView, self).get_context_data(**kwargs)
        context['products'] = models.ProductReceipt.objects.filter(deliver=self.object)
        print(context)
        return context


class OnTheGivenDiscounts(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/on-the-given-discounts/index.html'


class ByAgents(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/by-agents/index.html'


class EmployeeSalaries(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/employee-salaries/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(EmployeeSalaries, self).get_context_data(**kwargs)
        branches = models.Branch.objects.filter()
        staffs = models.Staff.objects.filter()
        total_salary = []
        for i in staffs:
            total_salary.append(i.salary)

        ctx['total_salary'] = sum(total_salary)
        ctx['staffs'] = models.Staff.objects.all()
        ctx['branches'] = branches
        return ctx


class StaffsAdditionalSalary(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    template_name = 'app/director/pages/staffs-additional-salaries/index.html'
    form_class = forms.StaffSalaryModelForm
    success_url = reverse_lazy('staff_additional_salary')
    success_message = 'Muvafaqiyatli yaratildi'

    def get_context_data(self, **kwargs):
        import json
        ctx = super(StaffsAdditionalSalary, self).get_context_data(**kwargs)
        branches = models.Branch.objects.filter()
        staffs = models.Staff.objects.filter()
        ctx['staffs'] = models.Staff.objects.all()
        total_salary = []
        for i in staffs:
            total_salary.append(i.salary)
        ctx['branches'] = branches
        ctx['total_salary'] = sum(total_salary)
        a = [
            {
                'branch_id': branch.id,
                'branch_name': branch.name,
                'staff': [
                    {
                        "id": staff.id,
                        "name": staff.get_full_name(),
                    } for staff in branch.staff_set.all()
                ]
            } for branch in branches
        ]

        ctx['json'] = json.dumps(a)
        return ctx

    def form_valid(self, form):
        return super(StaffsAdditionalSalary, self).form_valid(form)

    def form_invalid(self, form):
        return super(StaffsAdditionalSalary, self).form_invalid(form)


class StaffsAdditionalSalaryDetail(LoginRequiredMixin, generic.DetailView):
    template_name = 'app/director/pages/staffs-additional-salaries/detail.html'
    model = models.Staff
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        staff_salaries = models.StaffSalary.objects.filter(staff_id=int(self.request.path.split('/')[-1]))
        sum_bonus, sum_loan, sum_payment_delay = [], [], []

        for item in staff_salaries:
            sum_bonus.append(item.bonus)
            sum_loan.append(item.loan)
            sum_payment_delay.append(item.payment_delay)

        ctx['staff_salaries'] = staff_salaries
        ctx['sum_bonus'] = sum(sum_bonus)
        ctx['sum_loan'] = sum(sum_loan)
        ctx['sum_payment_delay'] = sum(sum_payment_delay)
        return ctx


class FormTwoOnTheScale(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/form-two-on-the-scale/index.html'


class TheFinalFinancialResult(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/the-final-financial-result/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(TheFinalFinancialResult, self).get_context_data(**kwargs)
        client = models.Client.objects.filter()
        deliver = models.Deliver.objects.filter()
        company = models.Company.objects.last()
        total_deliver_loan_sum, total_deliver_loan_dollar = [], []
        total_client_loan_sum, total_client_loan_dollar = [], []
        for i in client:
            total_client_loan_sum.append(i.loan_sum)
            total_client_loan_dollar.append(i.loan_dollar)
        for i in deliver:
            total_deliver_loan_sum.append(
                i.loans.all().aggregate(Sum("loan_sum"))["loan_sum__sum"] or 0
            )
            total_deliver_loan_dollar.append(
                i.loans.all().aggregate(Sum("loan_dollar"))["loan_dollar__sum"] or 0
            )

        ctx['total_sum'] = company.balance_sum
        ctx['total_dollar'] = company.balance_dollar
        ctx['total_transfer'] = company.balance_transfer
        ctx['total_card'] = company.balance_card

        ctx['total_income_cost_sum'] = sum(
            [i.product.cost for i in models.ProductThroughBranch.objects.filter(product__currency='sum')])
        ctx['total_income_cost_dollar'] = sum(
            [i.product.cost for i in models.ProductThroughBranch.objects.filter(product__currency='dollar')])

        ctx['total_deliver_loan_sum'] = sum(total_deliver_loan_sum)
        ctx['total_deliver_loan_dollar'] = sum(total_deliver_loan_dollar)
        ctx['total_client_loan_sum'] = sum(total_client_loan_sum)
        ctx['total_client_loan_dollar'] = sum(total_client_loan_dollar)
        return ctx


class Revision(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/revision/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['inventory_items'] = models.InventoryItem.objects.all()
        ctx['branches'] = models.Branch.objects.all()
        return ctx


class CustomerDebtB2C(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/customer-debt/index.html'
    model = models.ClientLoan

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(CustomerDebtB2C, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'weekly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })

            clients = self.model.objects.filter(
                Q(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7)) & Q(
                    created_at__lte=datetime.datetime.now()))

        elif period == 'monthly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'yearly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
        else:
            clients = self.model.objects.filter()

        a = self.model.objects.filter(client__type="b2c")
        loan_sum = []
        loan_dollar = []
        for i in a:
            loan_sum.append(i.loan_sum)
            loan_dollar.append(i.loan_dollar)
        branches = models.Branch.objects.filter()
        ctx['loan_sum'] = sum(loan_sum)
        ctx['loan_dollar'] = sum(loan_dollar)
        ctx['branches'] = branches
        ctx['clients'] = clients
        return ctx


class CustomerDebtB2B(LoginRequiredMixin, generic.ListView):
    template_name = 'app/director/pages/customer-debt/index_b2b.html'
    model = models.ClientLoan

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(CustomerDebtB2B, self).get_context_data(**kwargs)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'weekly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })

            clients = self.model.objects.filter(
                Q(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7)) & Q(
                    created_at__lte=datetime.datetime.now()))

        elif period == 'monthly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'yearly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
        else:
            clients = self.model.objects.filter()
            print(clients)
        a = self.model.objects.filter(client__type="b2b")
        loan_sum = []
        loan_dollar = []
        for i in a:
            loan_sum.append(i.loan_sum)
            loan_dollar.append(i.loan_dollar)
        branches = models.Branch.objects.filter()
        ctx['loan_sum'] = sum(loan_sum)
        ctx['loan_dollar'] = sum(loan_dollar)
        ctx['branches'] = branches
        ctx['clients'] = clients
        return ctx


class CustomerDebtDetail(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/director/pages/customer-debt/detail.html'


class RateOfProducts(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/provider/rate-of-products/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(RateOfProducts, self).get_context_data(**kwargs)
        products = models.ProductThroughBranch.objects.filter()
        products_sum = models.ProductThroughBranch.objects.filter(product__currency='sum')
        products_dollar = models.ProductThroughBranch.objects.filter(product__currency='dollar')
        total_cost_sum = []
        total_cost_dollar = []
        for i in products_sum:
            total_cost_sum.append(i.selling_price)
        for i in products_dollar:
            total_cost_dollar.append(i.selling_price)

        branches = models.Branch.objects.filter()
        ctx['branches'] = branches
        ctx['products'] = products
        ctx['total_cost_sum'] = sum(total_cost_sum)
        ctx['total_cost_dollar'] = sum(total_cost_dollar)
        return ctx


class ResidualGoods(LoginRequiredMixin, generic.ListView):
    template_name = 'app/provider/residual-goods/index.html'
    model = models.Product

    def get_context_data(self, **kwargs):
        ctx = super(ResidualGoods, self).get_context_data(**kwargs)
        products = models.ProductThroughBranch.objects.filter()
        products_sum = models.ProductThroughBranch.objects.filter(product__currency='sum')
        products_dollar = models.ProductThroughBranch.objects.filter(product__currency='dollar')

        total_cost_sum = []
        total_cost_dollar = []
        for i in products_sum:
            total_cost_sum.append(i.selling_price)
        for i in products_dollar:
            total_cost_dollar.append(i.selling_price)

        branches = models.Branch.objects.filter()
        ctx['branches'] = branches
        ctx['products'] = products
        ctx['total_cost_sum'] = sum(total_cost_sum)
        ctx['total_cost_dollar'] = sum(total_cost_dollar)
        return ctx


class Report(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/provider/report/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = models.Product.objects.all()
        branch = models.Branch.objects.all()
        ctx['products'] = product
        ctx['branches'] = branch
        return ctx


class Order(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/provider/order/index.html'


class Invoice(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/provider/invoice/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        invoice_items_cost_sum = sum(
            [i.product.cost for i in models.InvoiceItem.objects.filter(product__currency='sum')])
        invoice_items_cost_dollar = sum(
            [i.product.cost for i in models.InvoiceItem.objects.filter(product__currency='dollar')])
        invoice_items_selling_price = sum([i.selling_price for i in models.InvoiceItem.objects.filter()])
        invoice_items = models.InvoiceItem.objects.filter()
        ctx['invoice_items'] = invoice_items
        ctx['invoice_items_cost_sum'] = invoice_items_cost_sum
        ctx['invoice_items_cost_dollar'] = invoice_items_cost_dollar
        ctx['invoice_items_selling_price'] = invoice_items_selling_price
        return ctx


class AnalisisOfGoodsSold(LoginRequiredMixin, generic.TemplateView):
    template_name = 'app/provider/analysis-of-goods-sold/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(AnalisisOfGoodsSold, self).get_context_data(**kwargs)
        """
        period = self.request.GET.get('period', False)
        if period == 'daily':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'weekly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })

            clients = self.model.objects.filter(
                Q(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7)) & Q(
                    created_at__lte=datetime.datetime.now()))

        elif period == 'monthly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'yearly':
            clients = self.model.objects.filter(**{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
        else:
            clients = self.model.objects.filter()
            """
        shop = models.Shop.objects.filter()
        shop_id = []
        for i in shop:
            shop_id.append(i.id)
        cart = models.Cart.objects.filter(shop_id__in=shop_id)
        cart_id = []
        for i in cart:
            cart_id.append(i.id)
        period = self.request.GET.get('period', False)
        if period == 'daily':
            cart_items = models.CartItem.objects.filter(cart_id__in=cart_id, **{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=1),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'weekly':
            cart_items = models.CartItem.objects.filter(cart_id__in=cart_id, **{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=7),
                "created_at__lte": datetime.datetime.now(),
            })

        elif period == 'monthly':
            cart_items = models.CartItem.objects.filter(cart_id__in=cart_id, **{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=30),
                "created_at__lte": datetime.datetime.now(),
            })
        elif period == 'yearly':
            cart_items = models.CartItem.objects.filter(cart_id__in=cart_id, **{
                "created_at__gte": datetime.datetime.now() - datetime.timedelta(days=365),
                "created_at__lte": datetime.datetime.now(),
            })
        else:
            cart_items = models.CartItem.objects.filter(cart_id__in=cart_id)

        # cart_items = models.CartItem.objects.filter(cart_id__in=cart_id)
        cart_items_cost_sum_id = [i.product_id for i in
                                  models.CartItem.objects.filter(cart_id__in=cart_id, product__currency='sum')]
        cart_items_cost_sum = models.ProductThroughBranch.objects.filter(product_id__in=cart_items_cost_sum_id)
        cart_items_cost_dollar_id = [i.product_id for i in
                                     models.CartItem.objects.filter(cart_id__in=cart_id, product__currency='dollar')]
        cart_items_cost_dollar = models.ProductThroughBranch.objects.filter(product_id__in=cart_items_cost_dollar_id)
        cart_items_selling_price_sum_id = [i.product_id for i in
                                           models.CartItem.objects.filter(cart_id__in=cart_id, product__currency='sum')]
        cart_items_selling_price_sum = models.ProductThroughBranch.objects.filter(
            product_id__in=cart_items_selling_price_sum_id)
        cart_items_selling_price_dollar_id = [i.product_id for i in models.CartItem.objects.filter(cart_id__in=cart_id,
                                                                                                   product__currency='dollar')]
        cart_items_selling_price_dollar = models.ProductThroughBranch.objects.filter(
            product_id__in=cart_items_selling_price_dollar_id)
        # Cart - > Shop
        # CartItem -> Cart
        total_cost_sum = []
        total_cost_dollar = []
        total_selling_price_sum = []
        total_selling_price_dollar = []

        for i in cart_items_selling_price_dollar:
            total_selling_price_dollar.append(i.selling_price)

        for i in cart_items_selling_price_sum:
            total_selling_price_sum.append(i.selling_price)

        for i in cart_items_cost_sum:
            total_cost_sum.append(i.product.cost)

        for i in cart_items_cost_dollar:
            total_cost_dollar.append(i.product.cost)

        branches = models.Branch.objects.filter()
        ctx['branches'] = branches
        ctx['total_selling_price_dollar'] = sum(total_selling_price_dollar)
        ctx['total_selling_price_sum'] = sum(total_selling_price_sum)
        ctx['total_cost_sum'] = sum(total_cost_sum)
        ctx['total_cost_dollar'] = sum(total_cost_dollar)
        ctx['cart_items'] = cart_items
        return ctx


class LoginView(generic.FormView):
    form_class = forms.LoginForm
    template_name = 'app/authentications/login/index.html'
    success_url = reverse_lazy('director_home')

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        if self.request.user.is_authenticated:
            return redirect('director_home')
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(self.success_url)
                else:
                    context = {
                        'form': form,
                        'login_error': 'Bu User Faol Emas'
                    }
                    return render(request, self.template_name, context)
            else:
                context = {
                    'form': form,
                    'login_error': "Username yoki parol noto'g'ri"
                }
                return render(request, self.template_name, context)
        else:
            return HttpResponse('Form is not valid')
