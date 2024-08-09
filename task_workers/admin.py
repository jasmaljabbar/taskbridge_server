from django.contrib import admin
from .models import WorkCategory, Tasker, SubscriptionPrice

class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

admin.site.register(WorkCategory, WorkCategoryAdmin)

class TaskerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'aadhar_number', 'city', 'state', 'task', 'task_fee')
    search_fields = ('full_name', 'phone_number', 'aadhar_number', 'city', 'state')
    list_filter = ('city', 'state')

# Check if TaskerAdmin is already registered
if not admin.site.is_registered(Tasker):
    admin.site.register(Tasker, TaskerAdmin)

@admin.register(SubscriptionPrice)
class SubscriptionPriceAdmin(admin.ModelAdmin):
    list_display = ('subscription_type', 'price')
    list_editable = ('price',)
