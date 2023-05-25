from typing import Any, List, Optional, Tuple
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models
from tags.models import TaggedItem


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
    
class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [TagInline]
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', InventoryFilter]
    search_fields = ['title']

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'
    
    def collection_title(self, product):
        return product.collection.title
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)

        self.message_user(
            request,
            f"{updated_count} products were successfully updated.",
            messages.ERROR
        )

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    ordering = ['user__first_name', 'user__last_name']
    list_select_related = ['user']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    list_per_page = 10

class OrderItemInLine(admin.TabularInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    extra = 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInLine]
    list_display = ['id', 'placed_at', 'customer']

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title', 'product_count']

    @admin.display(ordering='product_count')
    def product_count(self, collection):
        # Format is -> reverse('admin:app_model_page')
        url = (
                reverse('admin:store_product_changelist')
                + '?'
                + urlencode({
                    'collection__id': str(collection.id)
                }))
        return format_html('<a href="{}">{}</a>', url, collection.product_count)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(product_count=Count('product'))
