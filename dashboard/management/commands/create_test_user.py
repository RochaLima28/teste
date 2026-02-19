"""
Management command para criar usuário de teste
"""

from django.core.management.base import BaseCommand
from dashboard.models import User


class Command(BaseCommand):
    help = 'Cria um usuário de teste para a aplicação'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin123'
        full_name = 'Administrador'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Usuário "{username}" já existe!')
            )
            return
        
        user = User(
            username=username,
            full_name=full_name,
            is_staff=True,
            is_superuser=True
        )
        user.set_password_sha256(password)
        user.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Usuário "{username}" criado com sucesso!')
        )
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
