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

    class Meta:
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitais'

    def __str__(self):
        return self.nome


class Endereco(models.Model):
    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE)
    distrito = models.CharField(verbose_name='Distrito', null=True, blank=True)
    bairro = models.CharField(verbose_name='Bairro')
    logradouro = models.CharField(verbose_name='Logradouro')
    codigo = models.CharField(verbose_name='Código do Logradouro', null=True, blank=True)
    numero = models.CharField(verbose_name='Número')
    complemento = models.CharField(verbose_name='Complemento', null=True, blank=True)
    latitude = models.CharField(verbose_name='Latitude', null=True, blank=True)
    longitude = models.CharField(verbose_name='Latitude', null=True, blank=True)
    referencia = models.CharField(verbose_name='Ponto de Referência', null=True, blank=True)
    cep = models.CharField(verbose_name='CEP')
    telefone = models.CharField(verbose_name='Telefone')
    
    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f'Endereço {self.id}'


class DetalhamentoNotificacaoIndividual(models.Model):
    # Dados do Paciente
    nome = models.CharField(verbose_name='Nome')
    data_nascimento = models.DateField(verbose_name='Data de Nascimento', null=True, blank=True)
    idade = models.IntegerField(verbose_name='Idade', blank=True)
    sexo = models.ForeignKey(Sexo, verbose_name='Sexo', on_delete=models.CASCADE, pick=True)
    periodo_gestacao = models.ForeignKey(PeriodoGestacao, verbose_name='Período de Gestação', on_delete=models.CASCADE, pick=True)
    raca = models.ForeignKey(Raca, verbose_name='Raça', on_delete=models.CASCADE, pick=True)
    escolaridade = models.ForeignKey(Escolaridade, verbose_name='Escolaridade', on_delete=models.CASCADE, pick=True)
    cartao_sus = models.CharField(verbose_name='Cartão SUS')
    nome_mae = models.CharField(verbose_name='Nome da Mãe')
    # Detalhamento
    data_primeiros_sintomas = models.DateField(verbose_name='Data dos Primeiros Sintomas')
    sinais_clinicos = models.ManyToManyField(SinalClinico, verbose_name='Sinais Clínicos', pick=True, blank=True)
    doencas_pre_existentes = models.ManyToManyField(DoencaPreExistente, verbose_name='Doenças Pré-Existentes', pick=True, blank=True)
    data_coleta_primeira_amostra = models.DateField(verbose_name='Data da Coleta da 1ª Amostra da Sorologia', null=True, blank=True)
    data_coleta_outra_amostra = models.DateField(verbose_name='Data da Coleta da 1ª Amostra de Outra Amostra', null=True, blank=True)
    tipo_exame = models.CharField(verbose_name='Tipo de Exame', null=True, blank=True)
    obito = models.BooleanField(verbose_name='Óbito')
    contato_caso_semelhante = models.BooleanField(verbose_name='Contato com Caso Semelhante', null=True)
    presenca_exantema = models.BooleanField(verbose_name='Presença de Exantema', null=True)
    data_inicio_exantema = models.DateField(verbose_name='Data de Início da Exantema', blank=True, null=True)
    presenca_petequias_ou_sufusoes = models.BooleanField(verbose_name='Presença de Petéquias ou Sufusões Hemorrágicas', null=True)
    realizado_liquor = models.BooleanField(verbose_name='Realizado Líquor', null=True)
    resultado_bacterioscopia = models.CharField(verbose_name='Resultado da Bacterioscopia', null=True, blank=True)
    # Vacinação
    vacinado = models.BooleanField(verbose_name='Vacinado contra Doença', null=True)
    data_ultima_vacina = models.DateField(verbose_name='Data da Última Dose da Vacina', null=True, blank=True)
    # Hospitalização
    hospitalizacao = models.BooleanField(verbose_name='Ocorreu Hospitalização', null=True)
    data_hospitalizacao = models.DateField(verbose_name='Data da Hospitalização', null=True, blank=True)
    municio_hospitalizacao = models.ForeignKey(Municipio, verbose_name='Município da Hospitalização', on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        verbose_name = 'Detalhamento de Notificação Individual'
        verbose_name_plural = 'Detalhamentos de Notificação Individual'


class DetalheNotificacaoSurto(models.Model):
    data_primeiros_sintomas = models.DateField(verbose_name='Data dos 1º Sintomas do 1º Caso Suspeito')
    numero_casos_suspeitos = models.CharField(verbose_name='Número de Casos Suspeitos/Expostos')
    tipo_local = models.ForeignKey(TipoLocal, verbose_name='Local Inicial da Ocorrência', on_delete=models.CASCADE, pick=True)
    hipotese_diagnostica_1 = models.ForeignKey(Doenca, verbose_name='1ª Hipótese Diagnóstica', on_delete=models.CASCADE, null=True, blank=True, related_name='s1')
    hipotese_diagnostica_2 = models.ForeignKey(Doenca, verbose_name='1ª Hipótese Diagnóstica', on_delete=models.CASCADE, null=True, blank=True, related_name='s2')

    class Meta:
        verbose_name = 'Detalhamento de Notificação de Surto'
        verbose_name_plural = 'Detalhamentos de Notificação de Surto'


class LocalInfeccao(models.Model):
    pais = models.CharField(verbose_name='País', default='Brasil')
    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE, null=True, blank=True)
    distrito = models.CharField(verbose_name='Distrito', null=True, blank=True)
    bairro = models.CharField(verbose_name='Bairro', null=True, blank=True)

    class Meta:
        verbose_name = 'Local de Infecção'
        verbose_name_plural = 'Locais de Infecção'


class Notificacao(models.Model):
    tipo = models.ForeignKey(TipoNotificacao, verbose_name='Tipo', on_delete=models.CASCADE, pick=True)
    doenca = models.ForeignKey(Doenca, verbose_name='Doença', on_delete=models.CASCADE, pick=True)
    data = models.DateField(verbose_name='Data')
    notificante = models.ForeignKey(Notificante, verbose_name='Notificante', on_delete=models.CASCADE)
    unidade = models.ForeignKey(UnidadeSaude, verbose_name='Unidade de Saúde', on_delete=models.CASCADE)
    
    detalhamento_individual = models.OneToOneField(DetalhamentoNotificacaoIndividual, verbose_name='Dados do Indivíduo', on_delete=models.CASCADE, null=True, blank=True)
    detalhamento_surto = models.OneToOneField(DetalheNotificacaoSurto, verbose_name='Dados do Surto', on_delete=models.CASCADE, null=True, blank=True)
    
    endereco = models.OneToOneField(Endereco, verbose_name='Local da Notificação', on_delete=models.CASCADE, null=True, blank=True)
    possivel_local_infecao = models.OneToOneField(LocalInfeccao, verbose_name='Possível Local da Infecção', on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        icon = 'user-tag'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'


    def __str__(self):
        return f'Notificação {self.id}'
