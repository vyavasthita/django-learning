from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Max, Min, Avg
from django.db import transaction
from store.models import Product, OrderItem, Order, Customer, Collection


# Create your views here.
@transaction.atomic
def home(request):
    # query_set = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    # query_set = Order.objects.select_related('customer').prefatch_related('orderitem_set').order_by('-placed_at')[:5]

    # result = Product.objects.aaggregate(count=Count('id'))

    query_set = Customer.objects.annotate(new_id=Value(True))
    full_name = Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT')
    full_name_2 = Concat('first_name', Value(' '), 'last_name')

    discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())

    collection = Collection()
    collection.title = 'Book'
    collection.feature_product = Product(pk=1)
    collection.save()

    Collection.objects.filter(pk=11).update(featured_product=None)

    with transaction.atomic():
        order = Order()
        order.customer_id = 1
        order.save()

        item = OrderItem()
        item.order = order
        item.product_id = 1
        item.quantity = 1
        item.unit_price = 10
        item.save()

    # return render(request, 'home.html', 
    #               {'names': ['Lali Devi Sharma', 'Raja', 'Bhoomi', 'Samskriti', 'Sabhyata'], 
    #                'result': result})
    return render(request, 'home.html', 
                  {'names': ['Lali Devi Sharma', 'Raja', 'Bhoomi', 'Samskriti', 'Sabhyata'], 
                   'result': list(query_set)})