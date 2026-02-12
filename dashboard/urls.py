"""
URLs para o dashboard app
"""

from django.urls import path
from . import views

urlpatterns = [
    # Páginas
    path('', views.index, name='index'),
    path('login', views.login_page, name='login_page'),
    
    # API - Auth
    path('api/login', views.login, name='api_login'),
    path('api/register', views.register, name='api_register'),
    
    # API - Data
    path('api/data', views.get_data, name='api_data'),
    
    # API - Expenses
    path('api/expenses', views.get_expenses, name='api_get_expenses'),
    path('api/expenses', views.add_expense, name='api_add_expense'),
    path('api/expenses/<int:expense_id>', views.delete_expense, name='api_delete_expense'),
    path('api/download/expenses/<str:company_code>', views.download_expenses, name='api_download_expenses'),
    
    # API - Adjustments
    path('api/company/adjustment', views.get_adjustment, name='api_get_adjustment'),
    path('api/company/adjustment', views.set_adjustment, name='api_set_adjustment'),
]
