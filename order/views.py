from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from user.views import customer_login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, View
from .models import Cart, CartItem, Order, OrderStatus, OrderItem
from django.contrib import messages
from shipping.forms import *
from payment.forms import *
from shipping.forms import *
from sensor.models import SensorItem

@method_decorator(customer_login_required, name="dispatch")
class CustomerOrderView(View):
    
    template_name = "order/order.html"

    # Return the order requested
    def get(self, request, order_id):

        customer = request.user.customer
        order = get_object_or_404(Order, customer=customer, order_id=order_id)

        context = {
            "order": order,
            "shippingAddressForm": ShippingAddressForm(
                instance=order.customer.shippingAddress,
                disabled=True,
                required=False
            )
        }

        return render(request, self.template_name, context)
    
    # Delete that order = Set status cancelled and delete all relations between the order and SensorItems
    def post(self, request, order_id):

        customer = request.user.customer
        order = get_object_or_404(Order, customer=customer, order_id=order_id)

        if order.status >= OrderStatus.SHIPPED:
            messages.warning(request, "Order cannot be refunded.")
        else:
            order.status = OrderStatus.CANCELLED
            order.save()

            sensorItemsOfOrder = SensorItem.objects.filter(order=order)
            for sensorItem in sensorItemsOfOrder:

                sensorItem.order = None
                sensorItem.save()

            messages.success(request, f"Order n. {order.order_id} refunded.")

        return redirect(request.META.get("HTTP_REFERER", reverse("order", kwargs={"order_id": order_id})))

# To show all orders of a customer
@method_decorator(customer_login_required, name='dispatch')
class CustomerOrdersListView(ListView):
    model = Order
    template_name = 'order/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user.customer).order_by('-created_at')


# GET => Get checkout page
# POST => Comlpete an order
@customer_login_required
def checkoutView(request):

    customer = request.user.customer

    if request.method == "GET":
        try:            

            # Get the cart from customer
            cart = customer.cart
            if not cart:
                raise ValueError("The cart is absent")

            # Get the user's shipping address
            shippingAddress = customer.shippingAddress
            if not shippingAddress:
                raise ValueError("The user's shipping address is absent")

            # Create the shippingAddressform
            shippingAddressForm = ShippingAddressForm(instance=shippingAddress, disabled=True, required=False)

            # Create the CreditCardForm
            creditCardForm = CreditCardForm()

            return render(request, "order/checkout.html", {
                "title": "Checkout",
                "shippingAddressForm": shippingAddressForm,
                "creditCardForm": creditCardForm
            })

        except Exception as e:
            messages.error(request, f"Checkout error: {str(e)}")
            return redirect("cart")

    elif request.method == "POST":
        
        try:

            cart = customer.cart
            if not cart:
                raise ValueError("The cart is absent")

            # Verify is crediCardForm is valid
            creditCardForm = CreditCardForm(request.POST)
            if not creditCardForm.is_valid():
                raise ValueError("Credit card form is invalid.")
            
            # Get or create the CreditCard object
            creditCardFormData = creditCardForm.cleaned_data
            credit_card, _ = CreditCard.objects.get_or_create(
                card_number = creditCardFormData["card_number"],
                exp_month = creditCardFormData["exp_month"],
                exp_year = creditCardFormData["exp_year"]
            )
            
            # Get customer's shipping address
            shippingAddress = customer.shippingAddress
            if not shippingAddress:
                raise ValueError("Shipping address is invalid")

            # Create the order and its orderItems
            order = Order.objects.create(
                customer=customer,
                #created_at is automatically set
                total_price=cart.total_price,
                status=OrderStatus.AWAITING_SHIPMENT,
                credit_card=credit_card
            )

            if not order:
                raise ValueError("The order has not been created")
            
            for cartItem in cart.cartItems.all():

                OrderItem.objects.create(
                    order=order,
                    quantity=cartItem.quantity,
                    sensor=cartItem.sensor,
                    amount=cartItem.amount
                )

                # For each orderItem, I need to link n sensorItem still not shipped to the order                
                for _ in range(0, cartItem.quantity):
                    
                    sensorItem = SensorItem.objects.filter(sensor=cartItem.sensor, order=None).first()
                    
                    if not sensorItem:
                        raise ValueError("Sensor item not found")

                    sensorItem.order = order

                    sensorItem.save()                    
            
            # Delete the customer's cart
            cart.delete()

            return redirect("home")

        except Exception as e:
            messages.error(request, f"Checkout submission error: {str(e)}")
            return redirect("checkout")


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