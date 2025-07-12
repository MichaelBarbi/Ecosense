from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from user.views import customer_login_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView, TemplateView
from .models import Cart, CartItem
from django.contrib import messages
 

@method_decorator(customer_login_required, name='dispatch')
class CartPageView(TemplateView):

    template_name = "order/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the cart
        cart = getattr(self.request.user.customer, "cart", None)
        context["cart"] = cart

        items = cart.cartItems.select_related("sensor") if cart else []
        context["items"] = items

        context["total_price"] = sum(item.sensor.price * item.quantity for item in items)

        return context
    
@customer_login_required
@require_POST
def cart_delete_item(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    # Checks that the item belongs to the logged-in user's cart
    if item.cart.customer == request.user.customer:
        item.delete()
    
    return redirect("cart")

@customer_login_required
@require_POST
def increase_quantity(request, item_id):
    
    item = get_object_or_404(CartItem, id=item_id)

    if item.cart.customer == request.user.customer:

        if item.sensor.quantity < (item.quantity + 1):

            # Maximum size exceeded
            messages.error(request, f"The quantity has not been increased: Quantity left: {item.sensor.quantity}")
            return redirect("cart")

        item.quantity += 1
        item.save()

    return redirect("cart")

@customer_login_required
@require_POST
def decrease_quantity(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    if item.cart.customer == request.user.customer:

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    return redirect("cart")