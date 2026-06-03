from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Motor, Rental

# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Motor)
class MotorAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'plate_number', 'price_per_day', 'status')
    list_filter = ('status', 'brand')
    search_fields = ('name', 'brand', 'plate_number')

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'motor', 'start_date', 'end_date', 'total_price', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('user__username', 'motor__name', 'motor__plate_number')
