from slth.db import models, role, meta
from slth.components import Image


class Funcao(models.Model):
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Função'
        verbose_name_plural = 'Funções'

    def __str__(self):
        return self.nome


class Notificante(models.Model):
    cpf = models.CharField(verbose_name='CPF')
    nome = models.CharField(verbose_name='Nome')
    funcao = models.ForeignKey(Funcao, verbose_name='Função', on_delete=models.CASCADE)


    class Meta:
        verbose_name = 'Notificante'
        verbose_name_plural = 'Notificantes'

    def __str__(self):
        return self.nome



class TipoNotificacao(models.Model):
    codigo = models.CharField(verbose_name='Código')
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Tipo de Notificação'
        verbose_name_plural = 'Tipos de Notificação'

    def __str__(self):
        return self.nome


class Doenca(models.Model):
    nome = models.CharField(verbose_name='Nome')
    cid10 = models.CharField(verbose_name='CID10')

    class Meta:
        verbose_name = 'Doença'
        verbose_name_plural = 'Doenças'

    def __str__(self):
        return self.nome


class Estado(models.Model):
    codigo = models.CharField(verbose_name='Código IBGE', max_length=2, unique=True)
    sigla = models.CharField(verbose_name='Sigla', max_length=2, unique=True)
    nome = models.CharField(verbose_name='Nome', max_length=60, unique=True)

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ["nome"]

    @property
    def id(self):
        return self.codigo

    def __str__(self):
        return "%s/%s" % (self.nome, self.sigla)


class Municipio(models.Model):
    estado = models.ForeignKey(Estado, verbose_name='Estado', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=7, verbose_name='Código IBGE', unique=True)
    nome = models.CharField(verbose_name='Nome', max_length=60)

    class Meta:
        verbose_name = "Município"
        verbose_name_plural = "Municípios"

    def __str__(self):
        return "%s/%s" % (self.nome, self.estado.sigla)


class UnidadeSaude(models.Model):
    codigo = models.CharField(verbose_name='Código')
    nome = models.CharField(verbose_name='Nome')

    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Unidade de Saúde'
        verbose_name_plural = 'Unidades de Saúde'


    def __str__(self):
        return self.nome


class Sexo(models.Model):
    codigo = models.CharField(verbose_name='Código')
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Sexo'
        verbose_name_plural = 'Sexos'

    def __str__(self):
        return self.nome


class PeriodoGestacao(models.Model):
    codigo = models.CharField(verbose_name='Código')
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Período de Gestação'
        verbose_name_plural = 'Períodos de Gestação'

    def __str__(self):
        return self.nome 


class Raca(models.Model):
    codigo = models.CharField(verbose_name='Código')
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Raça'
        verbose_name_plural = 'Raças'

    def __str__(self):
        return self.nome

class Escolaridade(models.Model):
    codigo = models.CharField(verbose_name='Código')
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Escolaridade'
        verbose_name_plural = 'Escolaridades'

    def __str__(self):
        return self.nome


class Zona(models.Model):
    codigo = models.CharField(verbose_name='Código')
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'

    def __str__(self):
        return self.nome


class SinalClinico(models.Model):
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Sinal Clínico'
        verbose_name_plural = 'Sinais Clínicos'

    def __str__(self):
        return self.nome
    

class DoencaPreExistente(models.Model):
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Doença Pré-Existente'
        verbose_name_plural = 'Doenças Pré-Existentes'

    def __str__(self):
        return self.nome


class TipoLocal(models.Model):
    codigo = models.CharField(verbose_name='Código')
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Tipo de Local'
        verbose_name_plural = 'Tipos de Locais'

    def __str__(self):
        return self.nome

class Hospital(models.Model):
    nome = models.CharField(verbose_name='Nome')
    codigo = models.CharField(verbose_name='Código')
    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitais'

    def __str__(self):
        return self.nome

class NotificacaoIndividualQuerySet(models.QuerySet):
    def all(self):
        return self.fields('get_numero', 'notificante', 'data', 'notificante').filters('municipio', 'unidade')


class NotificacaoIndividual(models.Model):
    # Dados Gerais
    doenca = models.ForeignKey(Doenca, verbose_name='Doença', on_delete=models.CASCADE, pick=True)
    data = models.DateField(verbose_name='Data')
    notificante = models.ForeignKey(Notificante, verbose_name='Notificante', on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE, related_name='s1')
    unidade = models.ForeignKey(UnidadeSaude, verbose_name='Unidade de Saúde', on_delete=models.CASCADE)
    data_primeiros_sintomas = models.DateField(verbose_name='Data dos Primeiros Sintomas')

    # Dados do Indivíduo
    nome = models.CharField(verbose_name='Nome')
    data_nascimento = models.DateField(verbose_name='Data de Nascimento', null=True, blank=True)
    idade = models.IntegerField(verbose_name='Idade', null=True, blank=True)
    sexo = models.ForeignKey(Sexo, verbose_name='Sexo', on_delete=models.CASCADE, pick=True)
    periodo_gestacao = models.ForeignKey(PeriodoGestacao, verbose_name='Período de Gestação', on_delete=models.CASCADE, pick=True)
    raca = models.ForeignKey(Raca, verbose_name='Raça', on_delete=models.CASCADE, pick=True)
    escolaridade = models.ForeignKey(Escolaridade, verbose_name='Escolaridade', on_delete=models.CASCADE, pick=True)
    cartao_sus = models.CharField(verbose_name='Cartão SUS')
    nome_mae = models.CharField(verbose_name='Nome da Mãe')

    # Dados Residenciais
    pais = models.CharField(verbose_name='País', default='Brasil')
    cep = models.CharField(verbose_name='CEP')
    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE, related_name='s2')
    distrito = models.CharField(verbose_name='Distrito', null=True, blank=True)
    bairro = models.CharField(verbose_name='Bairro')
    logradouro = models.CharField(verbose_name='Logradouro')
    codigo_logradouro = models.CharField(verbose_name='Código do Logradouro', null=True, blank=True)
    numero_residencia = models.CharField(verbose_name='Número da Residência')
    complemento = models.CharField(verbose_name='Complemento', null=True, blank=True)
    latitude = models.CharField(verbose_name='Latitude', null=True, blank=True)
    longitude = models.CharField(verbose_name='Longitude', null=True, blank=True)
    referencia = models.CharField(verbose_name='Ponto de Referência', null=True, blank=True)

    # Investigação
    data_investigacao = models.DateField(verbose_name='Data da Investigação')
    ocupacao_investigacao = models.CharField(verbose_name='Ocupação')

    # Dados Clínicos
    sinais_clinicos = models.ManyToManyField(SinalClinico, verbose_name='Sinais Clínicos', pick=True, blank=True)
    doencas_pre_existentes = models.ManyToManyField(DoencaPreExistente, verbose_name='Doenças Pré-Existentes', pick=True, blank=True)

    # Sorologia (IgM) Chikungunya
    data_primeira_amostra_chikungunya = models.DateField(verbose_name='Coleta da 1ª Amostra', null=True, blank=True)
    resultado_primeira_amostra_chikungunya = models.IntegerField(verbose_name='Resultado da 1ª Amostra', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Reagente', 'Não Reagente', 'Inconclusivo', 'Não Realizado'])], pick=True)
    data_segunda_amostra_chikungunya = models.DateField(verbose_name='Coleta da 2ª Amostra', null=True, blank=True)
    resultado_segunda_amostra_chikungunya = models.IntegerField(verbose_name='Resultado da 2ª Amostra', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Reagente', 'Não Reagente', 'Inconclusivo', 'Não Realizado'])], pick=True)
    # Exame PRNT
    data_coleta_exame_prnt = models.DateField(verbose_name='Coleta Exame PRNT', null=True, blank=True)
    resultado_exame_prnt = models.IntegerField(verbose_name='Resultado do Exame PRNT', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Reagente', 'Não Reagente', 'Inconclusivo', 'Não Realizado'])], pick=True)

    # Sorologia (IgM) Dengue
    data_amostra_dengue = models.DateField(verbose_name='Data da Coleta', null=True, blank=True)
    resultado_amostra_dengue = models.IntegerField(verbose_name='Resultado Coleta', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Positivo', 'Negativo', 'Inconclusivo', 'Não Realizado'])], pick=True)
    
    # Exame NS1
    data_exame_ns1 = models.DateField(verbose_name='Data Exame NS1', null=True, blank=True)
    resultado_exame_ns1 = models.IntegerField(verbose_name='Resultado Exame NS1', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Positivo', 'Negativo', 'Inconclusivo', 'Não Realizado'])], pick=True)
    
    # Isolamento
    data_isolamento = models.DateField(verbose_name='Data da Coleta Isolamento', null=True, blank=True)
    resultado_isolamento = models.IntegerField(verbose_name='Resultado Isolamento', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Positivo', 'Negativo', 'Inconclusivo', 'Não Realizado'])], pick=True)
    
    # RT-PCR
    data_rt_pcr = models.DateField(verbose_name='Data da Coleta RT-PCR', null=True, blank=True)
    resultado_rt_pcr = models.IntegerField(verbose_name='Resultado RT-PCR', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Positivo', 'Negativo', 'Inconclusivo', 'Não Realizado'])], pick=True)
    sorotipo = models.IntegerField(verbose_name='Sorotipo', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['DENV 1', 'DENV 2', 'DENV 3', 'DENV 4'])], pick=True)
    
    # Histopatologia
    histopatologia = models.IntegerField(verbose_name='Histopatologia', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Compatível', 'Incompatível', 'Inconclusivo', 'Não realizado'])], pick=True)

    # Imunohistoquímica
    imunohistoquímica = models.IntegerField(verbose_name='Imunohistoquímica', null=True, blank=True, choices=[[i + 1, x] for i, x in enumerate(['Positivo', 'Negativo', 'Inconclusivo', 'Não Realizado'])], pick=True)

    # Vacinação
    vacinado = models.BooleanField(verbose_name='Vacinado contra Doença', null=True)
    data_ultima_vacina = models.DateField(verbose_name='Data da Última Vacinação', null=True, blank=True)
    
    # Hospitalização
    hospitalizacao = models.BooleanField(verbose_name='Ocorreu Hospitalização', null=True)
    data_hospitalizacao = models.DateField(verbose_name='Data da Hospitalização', null=True, blank=True)
    hospital = models.ForeignKey(Hospital, verbose_name='Hospital', on_delete=models.CASCADE, null=True, blank=True)

    # Infecção
    pais_infeccao = models.CharField(verbose_name='País da Infecção', default='Brasil')
    municipio_infeccao = models.ForeignKey(Municipio, verbose_name='Município da Infecção', on_delete=models.CASCADE, null=True, blank=True, related_name='s3')
    distrito_infeccao = models.CharField(verbose_name='Distrito da Infecção', null=True, blank=True)
    bairro_infeccao = models.CharField(verbose_name='Bairro da Infecção', null=True, blank=True)

    objects = NotificacaoIndividualQuerySet()

    class Meta:
        icon = 'person'
        verbose_name = 'Notificação Individual'
        verbose_name_plural = 'Notificações Individuais'

    @meta('Número')
    def get_numero(self):
        return self.id

    def formfactory(self):
        return (
            super().formfactory()
            .fieldset('Dados Gerais', ('doenca', 'data', ('notificante', 'municipio'), ('unidade', 'data_primeiros_sintomas')))
            .fieldset('Dados do Indivíduo', ('nome', ('data_nascimento', 'idade'), 'sexo', 'periodo_gestacao', 'raca', 'escolaridade', 'cartao_sus', 'nome_mae'))
            .fieldset('Dados Residenciais', ('pais', ('cep', 'municipio'), ('distrito', 'bairro'), ('logradouro', 'codigo_logradouro'), ('numero_residencia', 'complemento'), ('latitude', 'longitude'), 'referencia'))
            .fieldset('Investigação', ('data_investigacao', 'ocupacao_investigacao'))
            .fieldset('Dados Clínicos', ('sinais_clinicos', 'doencas_pre_existentes'))
            .fieldset('Sorologia (IgM) Chikungunya', ('data_primeira_amostra_chikungunya', 'resultado_primeira_amostra_chikungunya', 'data_segunda_amostra_chikungunya', 'resultado_segunda_amostra_chikungunya'))
            .fieldset('Exame PRNT', ('data_coleta_exame_prnt', 'resultado_exame_prnt'))
            .fieldset('Sorologia (IgM) Dengue', ('data_amostra_dengue', 'resultado_amostra_dengue'))
            .fieldset('Exame NS1', ('data_exame_ns1', 'resultado_exame_ns1'))
            .fieldset('Isolamento', ('data_isolamento', 'resultado_isolamento'))
            .fieldset('RT-PCR', ('data_rt_pcr', 'resultado_rt_pcr', 'sorotipo'))
            .fieldset('Histopatologia', ('histopatologia',))
            .fieldset('Imunohistoquímica', ('imunohistoquímica',))
            .fieldset('Vacinação', ('vacinado', 'data_ultima_vacina'))
            .fieldset('Hospitalização', ('hospitalizacao', 'data_hospitalizacao', 'hospital'))
            .fieldset('Infecção', ('pais_infeccao', 'municipio_infeccao', ('distrito_infeccao', 'bairro_infeccao')))
        )


class NotificacaoSurto(models.Model):
    data_primeiros_sintomas = models.DateField(verbose_name='Data dos 1º Sintomas do 1º Caso Suspeito')
    numero_casos_suspeitos = models.CharField(verbose_name='Número de Casos Suspeitos/Expostos')
    tipo_local = models.ForeignKey(TipoLocal, verbose_name='Local Inicial da Ocorrência', on_delete=models.CASCADE, pick=True)
    hipotese_diagnostica_1 = models.ForeignKey(Doenca, verbose_name='1ª Hipótese Diagnóstica', on_delete=models.CASCADE, null=True, blank=True, related_name='s1')
    hipotese_diagnostica_2 = models.ForeignKey(Doenca, verbose_name='1ª Hipótese Diagnóstica', on_delete=models.CASCADE, null=True, blank=True, related_name='s2')

    class Meta:
        icon = 'people-line'
        verbose_name = 'Notificação de Surto'
        verbose_name_plural = 'Notificações de Surto'


    def __str__(self):
        return f'Notificação {self.id}'
