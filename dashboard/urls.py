"""
URLs para o dashboard app
"""

from django.urls import path
from . import views

# Wrapper views para combinar GET e POST na mesma rota
def expenses_view(request):
    if request.method == 'GET':
        return views.get_expenses(request)
    elif request.method == 'POST':
        return views.add_expense(request)
    
def adjustments_view(request):
    if request.method == 'GET':
        return views.get_adjustment(request)
    elif request.method == 'POST':
        return views.set_adjustment(request)

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
    path('api/expenses', expenses_view, name='api_expenses'),
    path('api/expenses/<int:expense_id>', views.delete_expense, name='api_delete_expense'),
    path('api/download/expenses/<str:company_code>', views.download_expenses, name='api_download_expenses'),
    
    # API - Adjustments
    path('api/company/adjustment', adjustments_view, name='api_adjustments'),
]
