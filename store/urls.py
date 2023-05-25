from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views
from rest_framework_nested import routers


router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)

router.register('carts', views.CartViewSet, basename='carts')
router.register('cartitems', views.CartItemViewSet, basename='cartitems')

router.register('customers', views.CustomerViewSet)

review_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
review_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + review_router.urls + carts_router.urls

