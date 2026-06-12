from django.db import models

class Organizacao(models.Model):
    numero = models.IntegerField(primary_key=True)
    nome = models.TextField()
    schema = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'public"."tbl_organizacoes'
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'

    def __str__(self):
        return self.nome

class Usuario(models.Model):
    usuario = models.CharField(max_length=50)
    senha = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tbl_usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.usuario
