from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from cart.models import CartItem
from user.views import customer_login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib import messages

@customer_login_required
@require_POST
def increase_quantity(request, item_id):
    
    item = get_object_or_404(CartItem, id=item_id)

    if item.cart.customer == request.user.customer:

        if item.sensor.quantity < (item.quantity + 1):

            # Maximum size exceeded
            messages.error(request, f"The quantity has not been increased: Quantity left: {item.sensor.quantity}")
            return redirect("cart:cart")

        item.quantity += 1
        item.save()

    return redirect("cart:cart")

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

    return redirect("cart:cart")

@customer_login_required
@require_POST
def cart_delete_item(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    # Checks that the item belongs to the logged-in user's cart
    if item.cart.customer == request.user.customer:
        item.delete()
    
    return redirect("cart:cart")


@method_decorator(customer_login_required, name='dispatch')
class CartPageView(TemplateView):

    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Cart"

        # Get the cart
        cart = getattr(self.request.user.customer, "cart", None)
        context["cart"] = cart

        items = cart.cartItems.select_related("sensor") if cart else []
        context["items"] = items

        context["total_price"] = sum(item.sensor.price * item.quantity for item in items)

        return context
  
