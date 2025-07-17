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

        # If it hasn't roles, I assigh them
        if obj.roles.count() == 0:
            for role_name in STAFF_ROLES:
                role, _ = StaffRole.objects.get_or_create(name=role_name)
                obj.roles.add(role)

admin.site.register(StaffRole)