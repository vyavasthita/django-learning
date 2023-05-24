from django_filters.rest_framework import FilterSet
from .models import Product, Cart


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt']
        }

class CartFilter(FilterSet):
    class Meta:
        model = Cart
        fields = {
            'created_at': ['exact']
        }