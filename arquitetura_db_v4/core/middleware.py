from django.db import connection

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Obtém o schema da organização da sessão ou usa o padrão public
        schema = request.session.get('tenant_schema', 'public')

        # Seta o search_path de forma global para a requisição
        # Mantemos o schema public acessível para tabelas globais
        with connection.cursor() as cursor:
            cursor.execute(f'SET search_path TO "{schema}", public')

        response = self.get_response(request)
        return response
