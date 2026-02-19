from django.db import models
from django.contrib.auth.models import AbstractUser
import hashlib


class User(AbstractUser):
    """Modelo de usuário customizado"""
    full_name = models.CharField(max_length=255, blank=True, default='')
    
    def set_password_sha256(self, raw_password):
        """Define senha usando SHA256 (para compatibilidade com o sistema antigo)"""
        self.password = hashlib.sha256(raw_password.encode()).hexdigest()
    
    def check_password_sha256(self, raw_password):
        """Verifica senha usando SHA256 (para compatibilidade com o sistema antigo)"""
        return self.password == hashlib.sha256(raw_password.encode()).hexdigest()
    
    class Meta:
        db_table = 'users'


class Expense(models.Model):
    """Modelo de lançamentos de gastos"""
    company_code = models.CharField(max_length=50, verbose_name='Código da Empresa')
    company_name = models.CharField(max_length=255, verbose_name='Nome da Empresa')
    description = models.TextField(blank=True, default='', verbose_name='Descrição')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor')
    expense_date = models.DateField(verbose_name='Data do Gasto')
    category = models.CharField(max_length=100, blank=True, default='', verbose_name='Categoria')
    notes = models.TextField(blank=True, default='', verbose_name='Observações')
    created_by = models.CharField(max_length=255, blank=True, default='', verbose_name='Criado Por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    
    class Meta:
        db_table = 'expenses'
        ordering = ['-expense_date']
        verbose_name = 'Lançamento de Gasto'
        verbose_name_plural = 'Lançamentos de Gastos'
    
    def __str__(self):
        return f"{self.company_name} - R$ {self.amount}"


class CompanyAdjustment(models.Model):
    """Modelo de ajustes de valores de empresas"""
    company_code = models.CharField(max_length=50, unique=True, verbose_name='Código da Empresa')
    company_name = models.CharField(max_length=255, verbose_name='Nome da Empresa')
    contract_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Valor do Contrato'
    )
    spent_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Valor Gasto'
    )
    reason = models.TextField(blank=True, default='', verbose_name='Motivo do Ajuste')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    
    class Meta:
        db_table = 'company_adjustments'
        ordering = ['company_name']
        verbose_name = 'Ajuste de Empresa'
        verbose_name_plural = 'Ajustes de Empresas'
    
    def __str__(self):
        return f"{self.company_name} ({self.company_code})"
