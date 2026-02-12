"""
Views para o dashboard de pagamentos
Convertido de Flask para Django
"""

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from django.conf import settings
from django.db.models import Sum
from datetime import datetime, timedelta
from functools import wraps
import jwt
import logging
import os

from .models import User, Expense, CompanyAdjustment
from .utils.excel_processor import ExcelProcessor
from .utils.export_excel import ExcelExporter

logger = logging.getLogger(__name__)

# Inicializar processador e exporter
processor = ExcelProcessor()
exporter = ExcelExporter()

# Dados atuais (em memória)
current_data = {
    'companies': [],
    'statistics': {},
    'last_update': None,
    'file_path': None
}


def token_required(f):
    """Decorator para verificar token JWT"""
    @wraps(f)
    def decorated(request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'error': 'Token ausente'}, status=401)
        
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            request.user_id = data['user_id']
            request.username = data['username']
            request.full_name = data['full_name']
        except:
            return JsonResponse({'error': 'Token inválido'}, status=401)
        
        return f(request, *args, **kwargs)
    
    return decorated


def apply_adjustments_to_companies(companies):
    """Aplica ajustes do banco de dados aos dados das empresas"""
    for company in companies:
        try:
            adjustment = CompanyAdjustment.objects.filter(company_code=company['code']).first()
            if adjustment:
                # Aplicar ajustes se existirem
                if adjustment.contract_value is not None:
                    company['contract_value'] = float(adjustment.contract_value)
                if adjustment.spent_value is not None:
                    company['spent_value'] = float(adjustment.spent_value)
                else:
                    # Se não há ajuste de spent_value, usar soma de lançamentos
                    total_expenses = Expense.objects.filter(
                        company_code=company['code']
                    ).aggregate(total=Sum('amount'))['total'] or 0
                    if total_expenses > 0:
                        company['spent_value'] = float(total_expenses)
            else:
                # Se não há ajuste, usar soma de lançamentos
                total_expenses = Expense.objects.filter(
                    company_code=company['code']
                ).aggregate(total=Sum('amount'))['total'] or 0
                if total_expenses > 0:
                    company['spent_value'] = float(total_expenses)
            
            # Recalcular percentual
            if company['contract_value'] > 0:
                company['percentage'] = round((company['spent_value'] / company['contract_value']) * 100, 2)
            else:
                company['percentage'] = 0
            
            # Recalcular status
            if company['percentage'] > 90:
                company['status'] = 'critical'
            elif company['percentage'] > 70:
                company['status'] = 'warning'
            else:
                company['status'] = 'ok'
        except Exception as e:
            logger.error(f"Erro ao aplicar ajustes para empresa {company['code']}: {e}")
    
    return companies


def login_page(request):
    """Página de login"""
    return render(request, 'login.html')


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """Autentica um usuário"""
    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return JsonResponse({'error': 'Usuário e senha são obrigatórios'}, status=400)
    
    try:
        user = User.objects.get(username=username)
        if user.check_password_sha256(password):
            token = jwt.encode({
                'user_id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'exp': datetime.utcnow() + timedelta(days=7)
            }, settings.SECRET_KEY, algorithm='HS256')
            
            return JsonResponse({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name
                }
            })
        else:
            return JsonResponse({'error': 'Usuário ou senha inválidos'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuário ou senha inválidos'}, status=401)
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return JsonResponse({'error': 'Erro no servidor'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """Cria um novo usuário"""
    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('fullName', '')
    
    if not username or not password:
        return JsonResponse({'error': 'Usuário e senha são obrigatórios'}, status=400)
    
    if len(password) < 6:
        return JsonResponse({'error': 'Senha deve ter pelo menos 6 caracteres'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Usuário já existe'}, status=400)
    
    try:
        user = User(username=username, full_name=full_name)
        user.set_password_sha256(password)
        user.save()
        
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, settings.SECRET_KEY, algorithm='HS256')
        
        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name
            }
        }, status=201)
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        return JsonResponse({'error': 'Erro ao criar usuário'}, status=500)


def index(request):
    """Página principal"""
    return render(request, 'index.html')


def get_data(request):
    """Retorna dados atuais em JSON"""
    return JsonResponse(current_data)


@require_http_methods(["GET"])
def get_expenses(request):
    """Obter lançamentos de gastos"""
    company_code = request.GET.get('company_code')
    
    if company_code:
        expenses = Expense.objects.filter(company_code=company_code).order_by('-expense_date')
    else:
        expenses = Expense.objects.all().order_by('-expense_date')
    
    expenses_list = []
    for expense in expenses:
        expenses_list.append({
            'id': expense.id,
            'company_code': expense.company_code,
            'company_name': expense.company_name,
            'description': expense.description,
            'amount': float(expense.amount),
            'expense_date': expense.expense_date.strftime('%Y-%m-%d'),
            'category': expense.category,
            'notes': expense.notes,
            'created_by': expense.created_by,
            'created_at': expense.created_at.isoformat(),
            'updated_at': expense.updated_at.isoformat(),
        })
    
    return JsonResponse(expenses_list, safe=False)


@csrf_exempt
@token_required
@require_http_methods(["POST"])
def add_expense(request):
    """Adicionar novo lançamento"""
    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    
    try:
        amount = float(data.get('amount', 0))
        company_code = data.get('company_code')
        company_name = data.get('company_name')
        created_by = request.full_name or request.username
        
        expense = Expense.objects.create(
            company_code=company_code,
            company_name=company_name,
            amount=amount,
            description=data.get('description', ''),
            expense_date=data.get('expense_date'),
            category=data.get('category', ''),
            notes=data.get('notes', ''),
            created_by=created_by
        )
        
        # Obter valor total de lançamentos da empresa
        total_spent = Expense.objects.filter(
            company_code=company_code
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Atualizar valor gasto na empresa no banco de dados
        adjustment, created = CompanyAdjustment.objects.get_or_create(
            company_code=company_code,
            defaults={'company_name': company_name}
        )
        adjustment.spent_value = total_spent
        adjustment.save()
        
        # Reprocessar dados para atualizar (se houver arquivo)
        # Isso será feito pelo WebSocket em tempo real
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Erro ao adicionar lançamento: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_expense(request, expense_id):
    """Deletar lançamento"""
    try:
        expense = Expense.objects.get(id=expense_id)
        expense.delete()
        return JsonResponse({'success': True})
    except Expense.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lançamento não encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Erro ao deletar lançamento: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def download_expenses(request, company_code):
    """Baixar relatório de movimentos da empresa"""
    try:
        company = None
        for c in current_data.get('companies', []):
            if c['code'] == company_code:
                company = c
                break
        
        if not company:
            return JsonResponse({'error': 'Empresa não encontrada'}, status=404)
        
        expenses = Expense.objects.filter(company_code=company_code).order_by('-expense_date')
        
        expenses_list = []
        for expense in expenses:
            expenses_list.append({
                'expense_date': expense.expense_date.strftime('%Y-%m-%d'),
                'description': expense.description,
                'category': expense.category,
                'amount': float(expense.amount),
                'created_by': expense.created_by,
                'notes': expense.notes,
                'created_at': expense.created_at.isoformat(),
            })
        
        filepath = exporter.export_company_expenses(
            company_name=company['name'],
            company_code=company_code,
            contract_value=company['contract_value'],
            spent_value=company['spent_value'],
            expenses=expenses_list
        )
        
        if not filepath or not os.path.exists(filepath):
            return JsonResponse({'error': 'Erro ao gerar arquivo'}, status=500)
        
        response = FileResponse(open(filepath, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="Movimentos_{company_code}.xlsx"'
        return response
    
    except Exception as e:
        logger.error(f"Erro ao baixar arquivo: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_adjustment(request):
    """Obter ajuste de valores da empresa"""
    company_code = request.GET.get('company_code')
    
    try:
        adjustment = CompanyAdjustment.objects.get(company_code=company_code)
        return JsonResponse({
            'id': adjustment.id,
            'company_code': adjustment.company_code,
            'company_name': adjustment.company_name,
            'contract_value': float(adjustment.contract_value) if adjustment.contract_value else None,
            'spent_value': float(adjustment.spent_value) if adjustment.spent_value else None,
            'reason': adjustment.reason,
        })
    except CompanyAdjustment.DoesNotExist:
        return JsonResponse({})
    except Exception as e:
        logger.error(f"Erro ao obter ajuste: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def set_adjustment(request):
    """Salvar ajuste de valores da empresa"""
    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    
    try:
        company_code = data.get('company_code')
        company_name = data.get('company_name')
        contract_value = float(data.get('contract_value')) if data.get('contract_value') else None
        spent_value = float(data.get('spent_value')) if data.get('spent_value') else None
        reason = data.get('reason', '')
        
        adjustment, created = CompanyAdjustment.objects.get_or_create(
            company_code=company_code,
            defaults={'company_name': company_name}
        )
        
        if contract_value is not None:
            adjustment.contract_value = contract_value
        if spent_value is not None:
            adjustment.spent_value = spent_value
        if reason:
            adjustment.reason = reason
        
        adjustment.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Erro ao salvar ajuste: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
