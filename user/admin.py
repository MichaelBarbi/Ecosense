from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Customer)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):

        # Save normally
        super().save_model(request, obj, form, change)

        # Assign default roles only if exist, but never create them qui!
        if obj.roles.count() == 0:
            for role_name in STAFF_ROLES:
                try:
                    role = StaffRole.objects.get(name=role_name)
                    obj.roles.add(role)
                except StaffRole.DoesNotExist:
                    pass  # oppure log a warning

admin.site.register(StaffRole)