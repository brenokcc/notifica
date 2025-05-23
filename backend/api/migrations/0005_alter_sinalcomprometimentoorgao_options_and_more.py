# Generated by Django 5.1.1 on 2025-03-23 10:01

import django.db.models.deletion
import slth.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_apresentacaoclinica_classificacaoinfeccao_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sinalcomprometimentoorgao",
            options={
                "verbose_name": "Sinal de Comprometimento dos Órgãos",
                "verbose_name_plural": "Sinais de Comprometimento dos Órgãos",
            },
        ),
        migrations.AlterModelOptions(
            name="tipoevolucao",
            options={
                "verbose_name": "Tipo de Evolução",
                "verbose_name_plural": "Tipos de Evolução",
            },
        ),
        migrations.AddField(
            model_name="notificacaoindividual",
            name="email",
            field=slth.db.models.CharField(
                blank=True, max_length=255, null=True, verbose_name="E-mail"
            ),
        ),
        migrations.AddField(
            model_name="notificacaoindividual",
            name="telefone",
            field=slth.db.models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Telefone"
            ),
        ),
        migrations.AddField(
            model_name="notificacaoindividual",
            name="zona",
            field=slth.db.models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="api.zona",
                verbose_name="Zona",
            ),
        ),
        migrations.AlterField(
            model_name="notificacaoindividual",
            name="data_inicio_sinais_graves",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Data de Início dos Sinais de Gravidade",
            ),
        ),
    ]
