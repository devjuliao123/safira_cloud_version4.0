from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Organizacao, UserOrganization
from django.db import connection

class PessoasCRUDTest(TestCase):
    def setUp(self):
        # We need to manually create the tbl_organizacoes in the public schema for the test database
        # and the tbl_pessoas in the org schemas.
        # Django's test runner creates a fresh test database.

        with connection.cursor() as cursor:
            # Create public.tbl_organizacoes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.tbl_organizacoes (
                    numero INT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    schema TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create org_0001 schema and tbl_pessoas
            cursor.execute('CREATE SCHEMA IF NOT EXISTS org_0001')
            cursor.execute('SET search_path TO org_0001')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tbl_pessoas (
                    id SERIAL PRIMARY KEY,
                    tipo_pessoa VARCHAR(10),
                    nome_razao VARCHAR(150),
                    apelido_fantasia VARCHAR(150),
                    cpf_cnpj VARCHAR(20),
                    tipo_contribuinte INT,
                    inscricao_estadual VARCHAR(30),
                    telefone VARCHAR(20),
                    email VARCHAR(150),
                    cidade VARCHAR(100),
                    estado VARCHAR(2),
                    relacao_comercial VARCHAR(30),
                    cargo VARCHAR(100),
                    criado_em TIMESTAMP
                )
            """)

            # Insert organization
            cursor.execute('SET search_path TO public')
            cursor.execute("INSERT INTO tbl_organizacoes (numero, nome, schema) VALUES (1, 'Org Teste', 'org_0001')")

        self.org = Organizacao.objects.get(numero=1)
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = UserOrganization.objects.create(user=self.user, organizacao=self.org)
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_create_pessoa(self):
        response = self.client.post(reverse('pessoa_create'), {
            'tipo_pessoa': 'F',
            'nome_razao': 'Fulano de Tal',
            'cpf_cnpj': '12345678900',
            'email': 'fulano@example.com'
        })
        self.assertEqual(response.status_code, 302) # Redirect to list

        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO org_0001')
            cursor.execute('SELECT count(*) FROM tbl_pessoas WHERE nome_razao = %s', ['Fulano de Tal'])
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

    def test_list_pessoas(self):
        # Insert a record first
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO org_0001')
            cursor.execute("INSERT INTO tbl_pessoas (nome_razao, tipo_pessoa, cpf_cnpj) VALUES ('Beltrano', 'F', '000')")

        response = self.client.get(reverse('pessoas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beltrano')

    def test_edit_pessoa(self):
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO org_0001')
            cursor.execute("INSERT INTO tbl_pessoas (nome_razao, tipo_pessoa, cpf_cnpj) VALUES ('Original', 'F', '000') RETURNING id")
            pessoa_id = cursor.fetchone()[0]

        response = self.client.post(reverse('pessoa_edit', args=[pessoa_id]), {
            'tipo_pessoa': 'F',
            'nome_razao': 'Editado',
            'cpf_cnpj': '000'
        })
        self.assertEqual(response.status_code, 302)

        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO org_0001')
            cursor.execute('SELECT nome_razao FROM tbl_pessoas WHERE id = %s', [pessoa_id])
            nome = cursor.fetchone()[0]
            self.assertEqual(nome, 'Editado')

    def test_delete_pessoa(self):
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO org_0001')
            cursor.execute("INSERT INTO tbl_pessoas (nome_razao, tipo_pessoa, cpf_cnpj) VALUES ('To Delete', 'F', '000') RETURNING id")
            pessoa_id = cursor.fetchone()[0]

        response = self.client.get(reverse('pessoa_delete', args=[pessoa_id]))
        self.assertEqual(response.status_code, 302)

        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO org_0001')
            cursor.execute('SELECT count(*) FROM tbl_pessoas WHERE id = %s', [pessoa_id])
            count = cursor.fetchone()[0]
            self.assertEqual(count, 0)
