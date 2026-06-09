from django.db import models
from django.contrib.auth.models import User

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

class UserOrganization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organization_profile')
    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.username} - {self.organizacao.nome}"
