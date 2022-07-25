import coreapi
from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend

from app import models


class NameFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [coreapi.Field(
            name='status',
            location='query',
            required=False,
            type='string',
            description="__imminent_payment, missed_payment__"
        )]


class ShopFilter(filters.FilterSet):
    created_at_after = filters.DateFilter(field_name="created_at", lookup_expr='gte')
    created_at_before = filters.DateFilter(field_name="created_at", lookup_expr='lte')
    today = filters.DateFilter(field_name="today")
    weekly = filters.DateFilter(field_name="weekly", lookup_expr="gte")
    monthly = filters.DateFilter(field_name="monthly", lookup_expr="gte")

    class Meta:
        model = models.Shop
        fields = ['id', 'check_number', 'created_at_after', "today", "weekly", "monthly", 'created_at_before', 'branch', 'client']
