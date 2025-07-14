from .models import Cart

def cart_context(request):
    cart = None
    cart_items_count = 0

    if request.user.is_authenticated and hasattr(request.user, 'customer'):
        try:
            cart = Cart.objects.get(customer=request.user.customer)
            cart_items = cart.cartItems.all()

            for item in cart_items:
                cart_items_count += item.quantity

        except Cart.DoesNotExist:
            pass

    return {
        'cart': cart,
        'cart_items_count': cart_items_count
    }

