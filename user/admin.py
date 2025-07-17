from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Customer)

class StaffAdmin(admin.ModelAdmin):
    filter_horizontal = ('roles',)

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)
        
        # Se non ha ruoli, aggiungi quelli di default
        if obj.roles.count() == 0:
            for role_name in ('Tecnico', 'Vendita'):
                role, _ = StaffRole.objects.get_or_create(name=role_name)
                obj.roles.add(role)

admin.site.register(Staff, StaffAdmin)
admin.site.register(StaffRole)