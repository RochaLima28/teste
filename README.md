# Dashboard de Controle de Pagamentos 2025 - Django

Sistema Django com interface web para monitorar contratos e gastos de empresas em tempo real.

## 🎯 Migração de Flask para Django

Este projeto foi migrado de Flask para Django, mantendo **todas as funcionalidades** originais:
- ✅ Processamento automático de arquivos Excel
- ✅ Monitoramento em tempo real de arquivos
- ✅ Dashboard elegante e responsivo
- ✅ Autenticação de usuários com JWT
- ✅ Gestão de lançamentos e ajustes
- ✅ Exportação de relatórios em Excel
- ✅ Atualizações em tempo real via WebSocket (Django Channels)

## 📋 Características

- **Processamento de Excel**: Leitura automática de planilhas VALIDAÇÕES e LIQUIDAÇÃO 2025
- **Dashboard Interativo**: Visualização de contratos, gastos e estatísticas
- **Tempo Real**: Atualizações automáticas via WebSocket quando arquivo Excel é modificado
- **Autenticação**: Sistema de login/registro com tokens JWT
- **Gestão de Lançamentos**: Adicionar, visualizar e remover lançamentos de gastos
- **Ajustes de Valores**: Possibilidade de ajustar valores de contratos e gastos
- **Exportação**: Gerar relatórios em Excel por empresa
- **Admin Django**: Interface administrativa completa

## 🔧 Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🚀 Instalação Rápida

### 1. Clone o repositório (ou extraia os arquivos)

```bash
cd /caminho/para/o/projeto
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crie um superusuário (para acessar o admin)

```bash
python manage.py createsuperuser
```

### 6. Execute o servidor

#### Desenvolvimento (servidor simples):
```bash
python manage.py runserver
```

#### Produção (com suporte a WebSocket):
```bash
daphne -p 8000 projeto_django.asgi:application
```

### 7. Acesse a aplicação

- **Dashboard**: http://localhost:8000/
- **Login**: http://localhost:8000/login
- **Admin**: http://localhost:8000/admin/

## 📁 Estrutura do Projeto

```
projeto/
├── manage.py                       # Gerenciador Django
├── projeto_django/                 # Configurações do projeto
│   ├── __init__.py
│   ├── settings.py                # Configurações
│   ├── urls.py                    # URLs principais
│   ├── asgi.py                    # ASGI para WebSocket
│   └── wsgi.py                    # WSGI para deploy
├── dashboard/                      # App principal
│   ├── models.py                  # Modelos (User, Expense, CompanyAdjustment)
│   ├── views.py                   # Views (rotas/endpoints)
│   ├── urls.py                    # URLs do dashboard
│   ├── admin.py                   # Configuração do admin
│   ├── apps.py                    # Configuração do app
│   ├── consumers.py               # WebSocket consumers
│   ├── routing.py                 # Routing WebSocket
│   ├── migrations/                # Migrações do banco
│   └── utils/                     # Utilitários
│       ├── excel_processor.py     # Processamento de Excel
│       ├── export_excel.py        # Exportação para Excel
│       └── file_monitor.py        # Monitoramento de arquivos
├── templates/                      # Templates HTML
│   ├── index.html                 # Dashboard principal
│   └── login.html                 # Página de login
├── static/                         # Arquivos estáticos
│   ├── style.css                  # Estilos
│   ├── script.js                  # JavaScript
│   └── logo.png                   # Logo
├── downloads/                      # Arquivos gerados
├── dashboard.db                    # Banco de dados SQLite
└── requirements.txt                # Dependências Python
```

## ⚙️ Configuração

### ⚠️ IMPORTANTE: Configurações Obrigatórias

Antes de executar em produção, você **DEVE** configurar:

#### 1. Chave Secreta (SECRET_KEY)

**NUNCA use a chave padrão em produção!** Gere uma chave segura:

```python
# Em settings.py
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'sua-chave-super-segura-aqui')
```

Para gerar uma chave aleatória:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### 2. Pasta de Monitoramento (WATCH_FOLDER)

**Ajuste o caminho para seu ambiente!** Não deixe caminhos com nomes de usuários específicos.

Edite o arquivo `projeto_django/settings.py`:

```python
# Opção 1: Usar variável de ambiente (RECOMENDADO)
WATCH_FOLDER = os.environ.get('EXCEL_WATCH_FOLDER', '/caminho/padrao')

# Opção 2: Hardcoded (apenas para desenvolvimento)
WATCH_FOLDER = r"C:\Users\SEU_USUARIO\Desktop\Nova pasta"  # Ajuste o caminho

EXCEL_PATTERN = "*.xlsm"  # Padrão de arquivo
CHECK_INTERVAL = 2  # Intervalo de verificação em segundos
```

### Banco de dados

Por padrão, usa SQLite (`dashboard.db`). Para usar PostgreSQL ou MySQL, edite `DATABASES` em `settings.py`.

## 📊 Como Usar

### 1. Login/Registro

- Acesse http://localhost:8000/login
- Crie uma conta ou faça login
- O token JWT é salvo automaticamente

### 2. Processar Arquivo Excel

- Coloque seu arquivo Excel (padrão: `*.xlsm`) na pasta configurada
- O sistema detecta automaticamente e processa
- Dashboard atualiza em tempo real

### 3. Visualizar Dashboard

- Veja estatísticas gerais (total contratado, gasto, etc.)
- Lista de empresas com status (ok, warning, critical)
- Busque empresas pelo nome ou código

### 4. Adicionar Lançamentos

- Clique em uma empresa
- Adicione lançamentos de gastos
- Os valores são atualizados automaticamente

### 5. Ajustar Valores

- Edite valores de contrato ou gastos manualmente
- Adicione um motivo para o ajuste

### 6. Exportar Relatório

- Clique no botão de download na empresa
- Receba um arquivo Excel com todos os movimentos

## 🔌 API Endpoints

### Autenticação

- `POST /api/login` - Login
- `POST /api/register` - Registro

### Dados

- `GET /api/data` - Obter dados atuais
- `GET /api/expenses?company_code=XXX` - Listar lançamentos
- `POST /api/expenses` - Adicionar lançamento (requer token)
- `DELETE /api/expenses/<id>` - Deletar lançamento

### Ajustes

- `GET /api/company/adjustment?company_code=XXX` - Obter ajuste
- `POST /api/company/adjustment` - Salvar ajuste

### Download

- `GET /api/download/expenses/<company_code>` - Baixar relatório

## 🔐 Admin Django

Acesse http://localhost:8000/admin/ com o superusuário criado.

Você pode:
- Gerenciar usuários
- Ver/editar lançamentos
- Ver/editar ajustes de empresas
- Executar queries no banco

## 🧪 Comandos Úteis

```bash
# Criar migrações após alterar models
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar shell interativo
python manage.py shell

# Coletar arquivos estáticos (produção)
python manage.py collectstatic

# Verificar problemas no projeto
python manage.py check
```

## 🐛 Solução de Problemas

### Erro: "Pasta não encontrada"
Ajuste `WATCH_FOLDER` em `settings.py` com o caminho correto.

### Erro: "Port already in use"
Mude a porta:
```bash
python manage.py runserver 8080
```

### WebSocket não funciona
Use `daphne` ao invés de `runserver`:
```bash
daphne -p 8000 projeto_django.asgi:application
```

### Erro de migração
```bash
python manage.py migrate --fake-initial
```

### Permissões de arquivo
```bash
chmod +x manage.py
```

## 🔄 Diferenças do Flask

| Flask | Django |
|-------|--------|
| `app.py` | `views.py` + `urls.py` |
| `@app.route()` | `path()` em urls.py |
| `database.py` | `models.py` (ORM) |
| `Flask-SocketIO` | `Django Channels` |
| `{{ url_for() }}` | `{% url %}` |
| Executar: `python app.py` | Executar: `python manage.py runserver` |

## 📝 Notas Importantes

- O banco de dados existente (`dashboard.db`) foi preservado
- Usuários antigos usam SHA256 para senhas (compatibilidade mantida)
- O monitoramento de arquivo funciona em background
- WebSocket usa Channels com InMemory layer (para produção, use Redis)
- DEBUG=True em desenvolvimento, mude para False em produção

## 🚀 Deploy em Produção

1. Configure `DEBUG = False` em settings.py
2. Defina `ALLOWED_HOSTS = ['seu-dominio.com']`
3. Use PostgreSQL/MySQL ao invés de SQLite
4. Configure Channels com Redis:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```
5. Use servidor ASGI (Daphne, Uvicorn)
6. Configure nginx como proxy reverso
7. Use gunicorn/uwsgi para processos HTTP

## 📄 Licença

Este projeto é de uso interno.

## 👨‍💻 Suporte

Para dúvidas ou problemas:
1. Verifique se Python está instalado: `python --version`
2. Verifique dependências: `pip list`
3. Veja logs do servidor
4. Consulte a documentação do Django: https://docs.djangoproject.com/ 
