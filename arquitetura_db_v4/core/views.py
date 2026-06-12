from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import get_tenant_cursor, dictfetchall, dictfetchone, execute_paginated_query, session_login_required
from django.contrib import messages
from datetime import datetime

@session_login_required
def pessoa_list(request):
    search_query = request.GET.get('q', '')
    filtro_tipo = request.GET.get('tipo', '')
    page_number = request.GET.get('page', 1)

    base_query = "SELECT * FROM tbl_pessoas WHERE 1=1"
    params = []

    if search_query:
        base_query += " AND (nome_razao ILIKE %s OR apelido_fantasia ILIKE %s OR cpf_cnpj ILIKE %s)"
        params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])

    if filtro_tipo:
        base_query += " AND tipo_pessoa = %s"
        params.append(filtro_tipo)

    base_query += " ORDER BY nome_razao ASC"

    per_page = 10
    pessoas_list, total_count = execute_paginated_query(
        request, base_query, params, page_number, per_page
    )

    paginator = Paginator(range(total_count), per_page)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    page_obj.object_list = pessoas_list

    context = {
        'pessoas': page_obj,
        'search_query': search_query,
        'filtro_tipo': filtro_tipo,
        'total_registros': total_count,
    }
    return render(request, 'core/pessoa_list.html', context)

@session_login_required
def pessoa_detail(request, pk):
    with get_tenant_cursor(request) as cursor:
        cursor.execute("SELECT * FROM tbl_pessoas WHERE id = %s", [pk])
        pessoa = dictfetchone(cursor)

    if not pessoa:
        messages.error(request, "Pessoa não encontrada.")
        return redirect('pessoas')

    return render(request, 'core/pessoa_detail.html', {'pessoa': pessoa})

@session_login_required
def pessoa_delete(request, pk):
    with get_tenant_cursor(request) as cursor:
        cursor.execute("DELETE FROM tbl_pessoas WHERE id = %s", [pk])

    messages.success(request, "Pessoa excluída com sucesso.")
    return redirect('pessoas')

@session_login_required
def pessoa_create(request):
    if request.method == 'POST':
        data = {
            'tipo_pessoa': request.POST.get('tipo_pessoa'),
            'nome_razao': request.POST.get('nome_razao'),
            'apelido_fantasia': request.POST.get('apelido_fantasia'),
            'cpf_cnpj': request.POST.get('cpf_cnpj'),
            'tipo_contribuinte': request.POST.get('tipo_contribuinte') or None,
            'inscricao_estadual': request.POST.get('inscricao_estadual'),
            'telefone': request.POST.get('telefone'),
            'email': request.POST.get('email'),
            'cidade': request.POST.get('cidade'),
            'estado': request.POST.get('estado'),
            'relacao_comercial': request.POST.get('relacao_comercial'),
            'cargo': request.POST.get('cargo'),
            'criado_em': datetime.now()
        }

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO tbl_pessoas ({columns}) VALUES ({placeholders})"

        with get_tenant_cursor(request) as cursor:
            cursor.execute(query, list(data.values()))

        messages.success(request, "Pessoa inserida com sucesso.")
        return redirect('pessoas')

    return render(request, 'core/pessoa_form.html', {'action': 'Inserir'})

@session_login_required
def pessoa_edit(request, pk):
    with get_tenant_cursor(request) as cursor:
        cursor.execute("SELECT * FROM tbl_pessoas WHERE id = %s", [pk])
        pessoa = dictfetchone(cursor)

    if not pessoa:
        messages.error(request, "Pessoa não encontrada.")
        return redirect('pessoas')

    if request.method == 'POST':
        data = {
            'tipo_pessoa': request.POST.get('tipo_pessoa'),
            'nome_razao': request.POST.get('nome_razao'),
            'apelido_fantasia': request.POST.get('apelido_fantasia'),
            'cpf_cnpj': request.POST.get('cpf_cnpj'),
            'tipo_contribuinte': request.POST.get('tipo_contribuinte') or None,
            'inscricao_estadual': request.POST.get('inscricao_estadual'),
            'telefone': request.POST.get('telefone'),
            'email': request.POST.get('email'),
            'cidade': request.POST.get('cidade'),
            'estado': request.POST.get('estado'),
            'relacao_comercial': request.POST.get('relacao_comercial'),
            'cargo': request.POST.get('cargo'),
        }

        updates = ', '.join([f"{k} = %s" for k in data.keys()])
        params = list(data.values())
        params.append(pk)
        query = f"UPDATE tbl_pessoas SET {updates} WHERE id = %s"

        with get_tenant_cursor(request) as cursor:
            cursor.execute(query, params)

        messages.success(request, "Pessoa atualizada com sucesso.")
        return redirect('pessoas')

    return render(request, 'core/pessoa_form.html', {'pessoa': pessoa, 'action': 'Editar'})

def login_view(request):
    if request.session.get('usuario_id'):
        return redirect('menu')

    if request.method == 'POST':
        usuario_input = request.POST.get('username')
        senha_input = request.POST.get('password')

        # Consulta direta na tbl_usuarios no schema public
        with get_tenant_cursor(request) as cursor:
            # Forçamos public para o login
            cursor.execute('SET search_path TO public')
            cursor.execute("SELECT * FROM tbl_usuarios WHERE usuario = %s AND senha = %s AND ativo = TRUE", [usuario_input, senha_input])
            user = dictfetchone(cursor)

        if user:
            # Cria a sessão manual
            request.session['usuario_id'] = user['id']
            request.session['usuario_nome'] = user['usuario']

            # Busca a organização vinculada no schema public
            with get_tenant_cursor(request) as cursor:
                cursor.execute('SET search_path TO public')
                # Assumimos que o usuário 1 é da org_0001 temporariamente para manter compatibilidade
                request.session['tenant_schema'] = 'org_0001'

            next_url = request.GET.get('next', 'menu')
            return redirect(next_url)
        else:
            messages.error(request, "Usuário ou senha incorretos ou conta inativa.")

    return render(request, 'core/login.html')

def logout_view(request):
    # Limpa a sessão manual
    request.session.flush()
    return redirect('login')

def placeholder(request):
    return render(request, 'core/placeholder.html')
