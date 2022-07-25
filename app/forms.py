from django import forms

from . import models


class DiscountCardForm(forms.ModelForm):
    class Meta:
        model = models.DiscountCard
        fields = [
            "bonus_dollar",
            "card",
            "bonus_sum",
        ]


class CartForm(forms.ModelForm):
    class Meta:
        model = models.Cart
        fields = [
            "shop",
        ]


class RealizeForm(forms.ModelForm):
    class Meta:
        model = models.Realize
        fields = [
            "purpose",
        ]


class ProductRequestForm(forms.ModelForm):
    class Meta:
        model = models.ProductRequest
        fields = [
            "status",
            "created_by",
            "from_branch",
            "to_branch",
        ]


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = models.InvoiceItem
        fields = [
            "amount",
            "selling_price",
            "invoice",
            "product",
        ]


class BrokenProductForm(forms.ModelForm):
    class Meta:
        model = models.BrokenProduct
        fields = [
            "comment",
            "amount",
            "product",
            "section",
            "branch",
        ]


class MinimalForm(forms.ModelForm):
    class Meta:
        model = models.Minimal
        fields = [
            "amount",
            "month",
            "product",
        ]


class ClientForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = [
            "type",
            "phone_1",
            "loan_dollar",
            "first_name",
            "last_name",
            "address",
            "birth_date",
            "return_date",
            "phone_2",
            "loan_sum",
            "ball",
            "discount_card",
        ]


class InventoryInvoiceForm(forms.ModelForm):
    class Meta:
        model = models.InventoryInvoice
        fields = [
            "controller",
        ]


class ClientPaymentHistoryForm(forms.ModelForm):
    class Meta:
        model = models.ClientPaymentHistory
        fields = [
            "paid_at",
            "client",
            "staff",
        ]


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = [
            "currency",
            "name",
            "ball",
            "measurement",
            "producer",
            "cost",
            "barcode",
            "section",
            "category",
            "deliver",
            "branch",
        ]


class ClientReturnForm(forms.ModelForm):
    class Meta:
        model = models.ClientReturn
        fields = [
            "return_date",
            "took_date",
            "client",
            "staff",
            "cart",
        ]


class SectionForm(forms.ModelForm):
    class Meta:
        model = models.Section
        fields = [
            "name",
            "branch",
        ]


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = models.Invoice
        fields = [
            "name",
            "status",
            "from_branch",
            "to_branch",
        ]


class ReturnDeliverProductForm(forms.ModelForm):
    class Meta:
        model = models.ReturnDeliverProduct
        fields = [
            "comment",
            "amount",
            "product",
        ]


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = models.Currency
        fields = [
            "real_currency",
            "selling_currency",
            "ball_price",
        ]


class ShopForm(forms.ModelForm):
    class Meta:
        model = models.Shop
        fields = [
            "traded_at",
            "card",
            "loan_sum",
            "cash_sum",
            "discount_sum",
            "loan_dollar",
            "discount_dollar",
            "transfer",
            "cash_dollar",
            "branch",
            "seller",
            "client",
            "section",
        ]


class BranchForm(forms.ModelForm):
    class Meta:
        model = models.Branch
        fields = [
            "address",
            "type_of_branch",
            "name",
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = [
            "name",
        ]


class DeliverForm(forms.ModelForm):
    class Meta:
        model = models.Deliver
        fields = [
            # "loan_dollar",
            # "loan_sum",
            "name",
        ]


class DifferProductRecieveHistoryForm(forms.ModelForm):
    class Meta:
        model = models.DifferProductRecieveHistory
        fields = [
            "old_price",
            "traded_at",
            "product",
        ]


class StaffForm(forms.ModelForm):

    def save(self, commit=True):
        staff = super(StaffForm, self).save(commit)
        branch_name = self.data.get('branch')
        branch = models.Branch.objects.filter(name=branch_name).first()
        staff.branch = branch
        staff.save()
        return staff

    class Meta:
        model = models.Staff
        fields = [
            'first_name',
            'last_name',
            'fathers_name',
            'phone',
            'status',
        ]


class SettingsModelForm(forms.ModelForm):
    class Meta:
        model = models.Staff
        fields = [
            'first_name',
            'last_name',
            'fathers_name',
            'role',
            'branch',
            'phone',
            'salary',
            'password',
        ]

    def save(self, commit=True):
        staff = super(SettingsModelForm, self).save(commit)
        staff.username = self.data['first_name'].replace("'", "").replace(" ", "_").lower() + "_" + self.data[
            'last_name'].replace("'", "").replace(" ", "_").lower() + '_' + self.data['fathers_name'].replace("'",
                                                                                                              "").replace(
            " ", "_").lower()
        staff.save()
        return staff


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)


class IncomeModelForm(forms.ModelForm):
    class Meta:
        model = models.Income
        fields = (
            'branch',
            'whom',
            'card',
            'sum',
            'dollar',
            'transfer',
            'comment',
        )
        exclude = (
            'section',
        )
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-control', 'label': 'Title', 'required': True, }),
        }

    def __init__(self, *args, **kwargs):
        super(IncomeModelForm, self).__init__(*args, **kwargs)
        self.fields['card'].required = False
        self.fields['sum'].required = False
        self.fields['dollar'].required = False
        self.fields['transfer'].required = False


class OutcomeModelForm(forms.ModelForm):
    class Meta:
        model = models.Outcome
        fields = (
            'type',
            'whom',
            'card',
            'sum',
            'dollar',
            'transfer',
            'comment',
        )
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control', 'label': 'Turi', 'required': True, }),
        }

    def __init__(self, *args, **kwargs):
        super(OutcomeModelForm, self).__init__(*args, **kwargs)
        self.fields['type'].required = False
        self.fields['card'].required = False
        self.fields['sum'].required = False
        self.fields['dollar'].required = False
        self.fields['transfer'].required = False


class ProducerModelForm(forms.ModelForm):
    class Meta:
        model = models.Producer
        fields = [
            'name',
            'address',
            'country',
        ]


class StaffSalaryModelForm(forms.ModelForm):
    class Meta:
        model = models.StaffSalary
        fields = [
            'staff',
            'payment_delay',
            'loan',
            'bonus',
        ]
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control', 'label': 'Turi', 'required': True, }),
            'payment_delay': forms.NumberInput(attrs={'class': 'form-control', 'label': 'Turi', 'required': True, }),
            'loan': forms.NumberInput(attrs={'class': 'form-control', 'required': True, }),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'required': True, }),
        }


class NormativeDay(forms.Form):
    fields = ['normative']
