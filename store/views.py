from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    RetrieveModelMixin, UpdateModelMixin, \
        DestroyModelMixin, ListModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import CreateModelMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser


from .models import Product, Collection, Order, OrderItem, Review, Cart, CartItem, Customer
from .serializer import ProductSerializer, CollectionSerializer, \
    ReviewSerializer, CartSerializer, CartItemSerializer, \
        AddCartItemSerializer, UpdateCartItemSerializer, \
        CustomerSerializer, OrderSerializer, OrderItemSerializer, \
        CreateOrderSerializer, UpdateOrderSerializer
from .filters import ProductFilter, CartFilter
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermission, ViewCustomerHistoryPermission


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    # filtersets_fields = ['collection_id']

    # def get_queryset(self):
    #     queryset = Product.objects.all()

    #     collection_id = self.request.query_params.get('collection_id')

    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)

    #     return queryset
    
    def get_serializer_context(self):
        return {'request': self.request}   
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count > 0:
            return Response({'error': 'Product can not be deleted because it is associated with a product item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
  
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('product')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection can not be deleted because it is associated with a product item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'request': self.request}   

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

class CartViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
    
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    # permission_classes = [FullDjangoModelPermission]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)

        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'optionos']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, 
                                           context = {'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer        
        return OrderSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        
        customer_id = Customer.objects.only('id').get(user_id = self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
        
# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(product_count=Count('product')).all()
#     serializer_class = CollectionSerializer

# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(product_count=Count('product')).all()
#     serializer_class = CollectionSerializer

# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
    
#     def get_serializer_context(self):
#         return {'request': self.request}

# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitem_set.count() > 0:
#             return Response({'error': 'Product can not be deleted because it is associated with a product item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class ProductList(APIView):
#     def get(self, request):
#         query_set = Product.objects.all()
#         serializer = ProductSerializer(query_set, many=True, context={'request': request})
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# @api_view(['GET', 'POST'])
# def product_list(request):
#     if request.method == 'GET':
#         query_set = Product.objects.all()
#         serializer = ProductSerializer(query_set, many=True, context={'request': request})
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         # serializer = ProductSerializer(data=request.data)

#         # if serializer.is_valid():
#         #     serializer.validated_data
            
#         #     return Response('Raja')
#         # else:
#         #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         # serializer.validated_data            
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET', 'PUT', 'DELETE'])
# def product(request, id):
#     # try:
#     #     product = Product.objects.get(pk=id)
#     #     serializer = ProductSerializer(product)

#     #     return Response(serializer.data)
#     # except Product.DoesNotExist:
#     #     return Response(status=status.HTTP_404_NOT_FOUND)
#     product = get_object_or_404(Product, pk=id)

#     if request.method == 'GET':        
#         serializer = ProductSerializer(product)

#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if product.orderitem_set.count() > 0:
#             return Response({'error': 'Product can not be deleted because it is associated with a product item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
