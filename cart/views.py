from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer
from rest_framework import serializers


class UpdateQtySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class MyCartViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user, is_active=True)
        return cart

    def list(self, request):
        cart = self._get_cart(request.user)
        return Response(CartSerializer(cart).data)

    def create(self, request):
        from .serializers import AddCartItemSerializer
        cart = self._get_cart(request.user)

        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.quantity = quantity if created else (item.quantity + quantity)
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """PATCH /api/my-cart/{item_id}/  body: {"quantity": 3}"""
        cart = self._get_cart(request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)

        serializer = UpdateQtySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item.quantity = serializer.validated_data["quantity"]
        item.save()

        return Response(CartSerializer(cart).data)

    def destroy(self, request, pk=None):
        """DELETE /api/my-cart/{item_id}/"""
        cart = self._get_cart(request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["delete"], url_path="clear")
    def clear(self, request):
        """DELETE /api/my-cart/clear/"""
        cart = self._get_cart(request.user)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)
