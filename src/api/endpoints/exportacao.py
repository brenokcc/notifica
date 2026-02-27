import requests
from slth.models import Role
from slth import endpoints
from datetime import date, timedelta
from ..models import *
from ..utils import buscar_endereco
from slth.integrations.google import places
from slth.utils import age
from slth.components import FileViewer
from requests.exceptions import Timeout
from django.core.cache import cache

CAMPOS = [
   'numero',
   'sinan',
   'registrado_sinan',
   'doenca',
   'data',
   'notificante',
   'municipio',
   'unidade',
   'unidade_referencia',
   'data_primeiros_sintomas',
   'semana_epidemiologica',
   'cpf',
   'cartao_sus',
   'nome',
   'data_nascimento',
   'idade',
   'sexo',
   'periodo_gestacao',
   'raca',
   'escolaridade',
   'nome_mae',
   'data_primeiros_sintomas_surto',
   'numero_casos_suspeitos_surto',
   'tipo_local_surto',
   'endereco',
   'pais',
   'cep',
   'municipio_residencia',
   'distrito',
   'zona',
   'bairro',
   'logradouro',
   'codigo_logradouro',
   'numero_residencia',
   'complemento',
   'latitude',
   'longitude',
   'referencia',
   'telefone',
   'email',
   'data_investigacao',
   'ocupacao_investigacao',
   'get_nomes_sinais_clinicos',
   'get_nomes_doencas_pre_existentes',
   'data_primeira_amostra_chikungunya',
   'resultado_primeira_amostra_chikungunya',
   'data_segunda_amostra_chikungunya',
   'resultado_segunda_amostra_chikungunya',
   'data_coleta_exame_prnt',
   'resultado_exame_prnt',
   'data_amostra_dengue',
   'resultado_amostra_dengue',
   'data_exame_ns1',
   'resultado_exame_ns1',
   'data_isolamento',
   'resultado_isolamento',
   'data_rt_pcr',
   'resultado_rt_pcr',
   'sorotipo',
   'histopatologia',
   'imunohistoquimica',
   'vacinado',
   'vacinado2',
   'data_ultima_vacina',
   'hospitalizacao',
   'situacao_hospitalar',
   'data_hospitalizacao',
   'numero_prontuario',
   'hospital',
   'data_alta',
   'autoctone',
   'pais_infeccao',
   'municipio_infeccao',
   'distrito_infeccao',
   'bairro_infeccao',
   'classificacao_infeccao',
   'criterio_confirmacao',
   'apresentacao_clinica',
   'evolucao_caso',
   'data_obito',
   'data_encerramento',
   'resultado_exame',
   'resultado_exame2',
   'resultado_exame3',
   'dengue_com_sinais_de_alarme',
   'get_nomes_sinais_alarme_dengue',
   'data_inicio_sinais_alarme',
   'dengue_grave',
   'get_nomes_sinais_extravasamento_plasma',
   'get_nomes_sinais_sangramento_grave',
   'get_nomes_sinais_comprometimento_orgaos',
   'outros_orgaos_afetados',
   'data_inicio_sinais_graves',
   'observacao',
   'validada',
   'data_validacao',
   'responsavel_validacao',
   'tipo_bloqueio',
   'responsavel_bloqueio',
   'data_atribuicao_bloqueio',
   'data_bloqueio',
   'observacao_bloqueio',
   'latitude_bloqueio',
   'longitude_bloqueio',
   'motivo_perda_prazo_bloqueio',
   'data_perda_prazo_bloqueio',
   'responsavel_perda_prazo_bloqueio',
   'observacao_perda_prazo_bloqueio',
   'data_devolucao_bloqueio',
   'motivo_devolucao_bloqueio',
   'observacao_devolucao_bloqueio',
   'data_envio',
   'responsavel_pelo_envio',
   'devolvida',
   'status_infeccao',
   'status',
   'data_cancelamento',
   'responsavel_pelo_cancelamento',
   'observacao_cancelamento',
]

class NotificacoesIndividuais(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        icon = "file-export"
        verbose_name = "Exportar Notificações Individuais"

    def get(self):
        return (
            super()
            .get()
            .fields('numero', 'doenca', 'unidade', "notificante", "data", "cpf", "nome")
            .xlsx(*CAMPOS)
            .order_by("-numero")
        )

    def check_permission(self):
        return self.check_role("administrador")
