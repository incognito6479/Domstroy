from django.db.models import Q
from rest_framework import serializers
from app.models import Page


class PageModelSerializer(serializers.ModelSerializer):
    children_obj = serializers.SerializerMethodField('get_children_obj')

    class Meta:
        model = Page
        fields = ["id", "name", "parent", "children_obj"]

    @classmethod
    def get_children_obj(cls, obj):
        return cls(Page.objects.filter(~Q(id=obj.id), tree_id=obj.id), many=True).data
