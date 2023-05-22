from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Collection
from .serializer import ProductSerializer, CollectionSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}   

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() > 0:
            return Response({'error': 'Product can not be deleted because it is associated with a product item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('product')).all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection can not be deleted because it is associated with a product item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
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
