from django.db import connection

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Obtém o schema da organização do usuário
                # Para esta implementação, priorizamos o schema vinculado no perfil
                schema = request.user.organization_profile.organizacao.schema
            except Exception:
                # Fallback para public caso ocorra erro ao buscar o perfil
                schema = 'public'
        else:
            schema = 'public'

        # Seta o search_path de forma global para a requisição
        # SEMPRE mantendo o schema public acessível para as tabelas do Django
        with connection.cursor() as cursor:
            cursor.execute(f'SET search_path TO "{schema}", public')

        response = self.get_response(request)
        return response
