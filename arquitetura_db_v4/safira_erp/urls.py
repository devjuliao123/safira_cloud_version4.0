from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from core import views as core_views

urlpatterns = [
    path("", lambda request: redirect("menu/")),
    path("admin/", admin.site.urls),
    path("menu/", include("menu.urls")),

    path("empresas", core_views.placeholder, name="empresas"),

    # Cadastros
    path("pessoas", core_views.placeholder, name="pessoas"),
    path("usuarios", core_views.placeholder, name="usuarios"),
    path("cargos", core_views.placeholder, name="cargos"),
    path("permissoes", core_views.placeholder, name="permissoes"),

    # CRM
    path("leads", core_views.placeholder, name="leads"),
    path("interacoes", core_views.placeholder, name="interacoes"),
    path("oportunidades", core_views.placeholder, name="oportunidades"),
    path("orcamentos", core_views.placeholder, name="orcamentos"),

    # Veículos
    path("marcas", core_views.placeholder, name="marcas"),
    path("modelos", core_views.placeholder, name="modelos"),
    path("veiculos", core_views.placeholder, name="veiculos"),
    path("historico-veiculo", core_views.placeholder, name="historico-veiculo"),

    # Oficina
    path("agendamentos", core_views.placeholder, name="agendamentos"),
    path("ordens-servico", core_views.placeholder, name="ordens-servico"),
    path("checklists", core_views.placeholder, name="checklists"),
    path("garantias", core_views.placeholder, name="garantias"),

    # Estoque
    path("categorias", core_views.placeholder, name="categorias"),
    path("produtos", core_views.placeholder, name="produtos"),
    path("fornecedores", core_views.placeholder, name="fornecedores"),
    path("depositos", core_views.placeholder, name="depositos"),
    path("estoque", core_views.placeholder, name="estoque"),
    path("movimentacoes", core_views.placeholder, name="movimentacoes"),

    # Compras
    path("compras", core_views.placeholder, name="compras"),

    # Comercial
    path("vendas", core_views.placeholder, name="vendas"),

    # Financeiro
    path("contas-receber", core_views.placeholder, name="contas-receber"),
    path("contas-pagar", core_views.placeholder, name="contas-pagar"),
    path("caixa", core_views.placeholder, name="caixa"),
    path("movimentacoes-financeiras", core_views.placeholder, name="movimentacoes-financeiras"),

    # Administração
    path("configuracoes", core_views.placeholder, name="configuracoes"),
    path("logs", core_views.placeholder, name="logs"),
    path("auditoria", core_views.placeholder, name="auditoria"),
]
