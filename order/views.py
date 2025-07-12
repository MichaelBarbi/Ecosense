from django.shortcuts import render
from django.utils.decorators import method_decorator
from user.views import customer_login_required
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from .models import Cart


@method_decorator(customer_login_required, name='dispatch')
class CartDeleteView(DeleteView):

    model = Cart
    success_url = reverse_lazy("catalog")

    def get_object(self, queryset=None):
        return self.request.user.customer.cart