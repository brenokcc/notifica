# Generated by Django 5.1.1 on 2025-02-26 08:26

import django.db.models.deletion
import slth
import slth.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "api",
            "0008_alter_detalhamentonotificacaoindividual_contato_caso_semelhante_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notificacao",
            name="detalhamento_individual",
        ),
        migrations.RemoveField(
            model_name="detalhenotificacaosurto",
            name="hipotese_diagnostica_1",
        ),
        migrations.RemoveField(
            model_name="detalhenotificacaosurto",
            name="hipotese_diagnostica_2",
        ),
        migrations.RemoveField(
            model_name="detalhenotificacaosurto",
            name="tipo_local",
        ),
        migrations.RemoveField(
            model_name="notificacao",
            name="detalhamento_surto",
        ),
        migrations.RemoveField(
            model_name="endereco",
            name="municipio",
        ),
        migrations.RemoveField(
            model_name="notificacao",
            name="endereco",
        ),
        migrations.RemoveField(
            model_name="localinfeccao",
            name="municipio",
        ),
        migrations.RemoveField(
            model_name="notificacao",
            name="possivel_local_infecao",
        ),
        migrations.RemoveField(
            model_name="notificacao",
            name="doenca",
        ),
        migrations.RemoveField(
            model_name="notificacao",
            name="notificante",
        ),
        migrations.RemoveField(
            model_name="notificacao",
            name="tipo",
        ),
        migrations.RemoveField(
            model_name="notificacao",
            name="unidade",
        ),
        migrations.AddField(
            model_name="hospital",
            name="municipio",
            field=slth.db.models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="api.municipio",
                verbose_name="Município",
            ),
        ),
        migrations.CreateModel(
            name="NotificacaoIndividual",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.DateField(verbose_name="Data")),
                (
                    "data_primeiros_sintomas",
                    models.DateField(verbose_name="Data dos Primeiros Sintomas"),
                ),
                ("nome", slth.db.models.CharField(max_length=255, verbose_name="Nome")),
                (
                    "data_nascimento",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data de Nascimento"
                    ),
                ),
                (
                    "idade",
                    slth.db.models.IntegerField(
                        blank=True, null=True, verbose_name="Idade"
                    ),
                ),
                (
                    "cartao_sus",
                    slth.db.models.CharField(max_length=255, verbose_name="Cartão SUS"),
                ),
                (
                    "nome_mae",
                    slth.db.models.CharField(
                        max_length=255, verbose_name="Nome da Mãe"
                    ),
                ),
                (
                    "pais",
                    slth.db.models.CharField(
                        default="Brasil", max_length=255, verbose_name="País"
                    ),
                ),
                ("cep", slth.db.models.CharField(max_length=255, verbose_name="CEP")),
                (
                    "distrito",
                    slth.db.models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Distrito"
                    ),
                ),
                (
                    "bairro",
                    slth.db.models.CharField(max_length=255, verbose_name="Bairro"),
                ),
                (
                    "logradouro",
                    slth.db.models.CharField(max_length=255, verbose_name="Logradouro"),
                ),
                (
                    "codigo_logradouro",
                    slth.db.models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Código do Logradouro",
                    ),
                ),
                (
                    "numero_residencia",
                    slth.db.models.CharField(
                        max_length=255, verbose_name="Número da Residência"
                    ),
                ),
                (
                    "complemento",
                    slth.db.models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Complemento",
                    ),
                ),
                (
                    "latitude",
                    slth.db.models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Latitude"
                    ),
                ),
                (
                    "longitude",
                    slth.db.models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Latitude"
                    ),
                ),
                (
                    "referencia",
                    slth.db.models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Ponto de Referência",
                    ),
                ),
                (
                    "data_investigacao",
                    models.DateField(verbose_name="Data da Investigação"),
                ),
                (
                    "ocupacao_investigacao",
                    slth.db.models.CharField(max_length=255, verbose_name="Ocupação"),
                ),
                (
                    "data_primeira_amostra_chikungunya",
                    models.DateField(
                        blank=True, null=True, verbose_name="Coleta da 1ª Amostra"
                    ),
                ),
                (
                    "data_segunda_amostra_chikungunya",
                    models.DateField(
                        blank=True, null=True, verbose_name="Coleta da 2ª Amostra"
                    ),
                ),
                (
                    "resultado_primeira_amostra_chikungunya",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Reagente"),
                            (2, "Não Reagente"),
                            (3, "Inconclusivo"),
                            (4, "Não Realizado"),
                        ],
                        null=True,
                        verbose_name="Resultado da 2ª Amostra",
                    ),
                ),
                (
                    "data_coleta_exame_prnt_chikungunya",
                    models.DateField(
                        blank=True, null=True, verbose_name="Coleta Exame PRNT"
                    ),
                ),
                (
                    "resultado_exame_prnt_chikungunya",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Reagente"),
                            (2, "Não Reagente"),
                            (3, "Inconclusivo"),
                            (4, "Não Realizado"),
                        ],
                        null=True,
                        verbose_name="Resultado do Exame PRNT",
                    ),
                ),
                (
                    "data_amostra_dengue",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data da Coleta"
                    ),
                ),
                (
                    "resultado_amostra_dengue",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Positivo"),
                            (2, "Negativo"),
                            (3, "Inconclusivo"),
                            (4, "Não Realizado"),
                        ],
                        null=True,
                        verbose_name="Resultado Coleta",
                    ),
                ),
                (
                    "data_exame_ns1",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data Exame NS1"
                    ),
                ),
                (
                    "resultado_exame_ns1",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Positivo"),
                            (2, "Negativo"),
                            (3, "Inconclusivo"),
                            (4, "Não Realizado"),
                        ],
                        null=True,
                        verbose_name="Resultado Exame NS1",
                    ),
                ),
                (
                    "data_isolamento",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data da Coleta Isolamento"
                    ),
                ),
                (
                    "resultado_isolamento",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Positivo"),
                            (2, "Negativo"),
                            (3, "Inconclusivo"),
                            (4, "Não Realizado"),
                        ],
                        null=True,
                        verbose_name="Resultado Isolamento",
                    ),
                ),
                (
                    "data_rt_pcr",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data da Coleta RT-PCR"
                    ),
                ),
                (
                    "resultado_rt_pcr",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Positivo"),
                            (2, "Negativo"),
                            (3, "Inconclusivo"),
                            (4, "Não Realizado"),
                        ],
                        null=True,
                        verbose_name="Resultado RT-PCR",
                    ),
                ),
                (
                    "sorotipo",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "DENV 1"),
                            (2, "DENV 2"),
                            (3, "DENV 3"),
                            (4, "DENV 4"),
                        ],
                        null=True,
                        verbose_name="Sorotipo",
                    ),
                ),
                (
                    "histopatologia",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Compatível"),
                            (2, "Incompatível"),
                            (3, "Inconclusivo"),
                            (4, "Não realizado"),
                        ],
                        null=True,
                        verbose_name="Histopatologia",
                    ),
                ),
                (
                    "imunohistoquímica",
                    slth.db.models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Positivo"),
                            (2, "Negativo"),
                            (3, "Inconclusivo"),
                            (4, "Não Realizado"),
                        ],
                        null=True,
                        verbose_name="Imunohistoquímica",
                    ),
                ),
                (
                    "vacinado",
                    models.BooleanField(
                        null=True, verbose_name="Vacinado contra Doença"
                    ),
                ),
                (
                    "data_ultima_vacina",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data da Última Vacinação"
                    ),
                ),
                (
                    "hospitalizacao",
                    models.BooleanField(
                        null=True, verbose_name="Ocorreu Hospitalização"
                    ),
                ),
                (
                    "data_hospitalizacao",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data da Hospitalização"
                    ),
                ),
                (
                    "pais_infeccao",
                    slth.db.models.CharField(
                        default="Brasil",
                        max_length=255,
                        verbose_name="País da Infecção",
                    ),
                ),
                (
                    "distrito_infeccao",
                    slth.db.models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Distrito da Infecção",
                    ),
                ),
                (
                    "bairro_infeccao",
                    slth.db.models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Bairro da Infecção",
                    ),
                ),
                (
                    "doenca",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.doenca",
                        verbose_name="Doença",
                    ),
                ),
                (
                    "doencas_pre_existentes",
                    slth.db.models.ManyToManyField(
                        blank=True,
                        to="api.doencapreexistente",
                        verbose_name="Doenças Pré-Existentes",
                    ),
                ),
                (
                    "escolaridade",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.escolaridade",
                        verbose_name="Escolaridade",
                    ),
                ),
                (
                    "hospital",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.hospital",
                        verbose_name="Hospital",
                    ),
                ),
                (
                    "municipio",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="s2",
                        to="api.municipio",
                        verbose_name="Município",
                    ),
                ),
                (
                    "municipio_infeccao",
                    slth.db.models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="s3",
                        to="api.municipio",
                        verbose_name="Município da Infecção",
                    ),
                ),
                (
                    "notificante",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.notificante",
                        verbose_name="Notificante",
                    ),
                ),
                (
                    "periodo_gestacao",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.periodogestacao",
                        verbose_name="Período de Gestação",
                    ),
                ),
                (
                    "raca",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.raca",
                        verbose_name="Raça",
                    ),
                ),
                (
                    "sexo",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.sexo",
                        verbose_name="Sexo",
                    ),
                ),
                (
                    "sinais_clinicos",
                    slth.db.models.ManyToManyField(
                        blank=True,
                        to="api.sinalclinico",
                        verbose_name="Sinais Clínicos",
                    ),
                ),
                (
                    "unidade",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.unidadesaude",
                        verbose_name="Unidade de Saúde",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notificação Individual",
                "verbose_name_plural": "Notificações Individuais",
            },
            bases=(models.Model, slth.ModelMixin),
        ),
        migrations.CreateModel(
            name="NotificacaoSurto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "data_primeiros_sintomas",
                    models.DateField(
                        verbose_name="Data dos 1º Sintomas do 1º Caso Suspeito"
                    ),
                ),
                (
                    "numero_casos_suspeitos",
                    slth.db.models.CharField(
                        max_length=255,
                        verbose_name="Número de Casos Suspeitos/Expostos",
                    ),
                ),
                (
                    "hipotese_diagnostica_1",
                    slth.db.models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="s1",
                        to="api.doenca",
                        verbose_name="1ª Hipótese Diagnóstica",
                    ),
                ),
                (
                    "hipotese_diagnostica_2",
                    slth.db.models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="s2",
                        to="api.doenca",
                        verbose_name="1ª Hipótese Diagnóstica",
                    ),
                ),
                (
                    "tipo_local",
                    slth.db.models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.tipolocal",
                        verbose_name="Local Inicial da Ocorrência",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notificação de Surto",
                "verbose_name_plural": "Notificações de Surto",
            },
            bases=(models.Model, slth.ModelMixin),
        ),
        migrations.DeleteModel(
            name="DetalhamentoNotificacaoIndividual",
        ),
        migrations.DeleteModel(
            name="DetalheNotificacaoSurto",
        ),
        migrations.DeleteModel(
            name="Endereco",
        ),
        migrations.DeleteModel(
            name="LocalInfeccao",
        ),
        migrations.DeleteModel(
            name="Notificacao",
        ),
    ]
