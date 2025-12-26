from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from cart.views import MyCartViewSet
from orders.views import MyOrdersViewSet
from payments.views import MyOrderPaymentViewSet, PaymentAdminActionsViewSet
from payments.views import PaymentAdminActionsViewSet
from core.views import UserViewSet
from catalog.views import CategoryViewSet, ProductViewSet 
from payments.webhooks import prontu_general_callback
from django.http import JsonResponse

router = DefaultRouter()

router.register(r'usuarios', UserViewSet, basename='usuarios')

# E-commerce (catalog)
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'products', ProductViewSet, basename='products')

router.register(r"my-cart", MyCartViewSet, basename="my-cart")
router.register(r"my-orders", MyOrdersViewSet, basename="my-orders")


#router.register(r"my-orders", MyOrdersViewSet, basename="my-orders")  # já existe
router.register(r"my-orders", MyOrderPaymentViewSet, basename="my-order-pay")
router.register(r"payments", PaymentAdminActionsViewSet, basename="payments")



def health(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", health),

    # OpenAPI 3
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc',
    ),

    # Auth JWT
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API
    path('api/', include(router.urls)),

    path("api/webhooks/prontu/<str:secret>/", prontu_general_callback),
]
