from django.contrib import admin
from .models import User, Expense, CompanyAdjustment


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'company_code', 'amount', 'expense_date', 'created_by', 'created_at']
    list_filter = ['expense_date', 'category', 'company_name']
    search_fields = ['company_name', 'company_code', 'description']
    date_hierarchy = 'expense_date'
    ordering = ['-expense_date']


@admin.register(CompanyAdjustment)
class CompanyAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'company_code', 'contract_value', 'spent_value', 'updated_at']
    list_filter = ['company_name']
    search_fields = ['company_name', 'company_code']
    ordering = ['company_name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'full_name']
    ordering = ['username']
