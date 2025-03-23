from slth.application import Application


class ApiApplication(Application):
    def __init__(self):
        super().__init__()
        self.title = "ArboNotifica"
        self.subtitle = "Sistema de notificação de arboviroses da cidade de Dourados/MS"
        self.icon = "/static/images/logo.png"
        self.logo = "/static/images/logo.png"
        self.brand = "/static/images/brand.png"
        self.groups.add(administrador='Administrador', operador= "Operador", notificante="Notificante")
        self.dashboard.usermenu.add(
            "dev.icons", "user.users", "log.logs", "email.emails",
            "pushsubscription.pushsubscriptions", "job.jobs",
            "deletion.deletions", "auth.logout"
        )
        self.dashboard.boxes.add(
            'notificacaoindividual.notificacoesindividuais',
            'notificacaosurto.notificacoessurto'
        )
        
        self.menu.add({
            'Apresentações Clínicas': 'apresentacaoclinica.apresentacoesclinicas',
            'Classificações de Infecção': 'classificacaoinfeccao.classificacoesinfeccao',
            'Critérios de Confirmação': 'criterioconfirmacao.criteriosconfirmacao',
            'Doenças': 'doenca.doencas',
            'Doenças Pré-Existentes': 'doencapreexistente.doencaspreexistentes',
            'Escolaridades': 'escolaridade.escolaridades',
            'Estados': 'estado.estados',
            'Funções': 'funcao.funcoes',
            'Hospitais': 'hospital.hospitais',
            'Locais de Infecção': 'localinfeccao.locaisinfeccao',
            'Municípios': 'municipio.municipios',
            'Notificações Individuais': 'notificacaoindividual.notificacoesindividuais',
            'Notificações de Surto': 'notificacaosurto.notificacoessurto',
            'Notificantes': 'notificante.notificantes',
            'Ocupações': 'ocupacao.ocupacoes',
            'Países': 'pais.paises',
            'Períodos de Gestação': 'periodogestacao.periodosgestacao',
            'Raças': 'raca.racas',
            'Sexos': 'sexo.sexos',
            'Sinais de Alarme': 'sinalalarme.sinaisalarme',
            'Sinais Clínicos': 'sinalclinico.sinaisclinicos',
            'Sinais de Comprometimento dos Órgãos': 'sinalcomprometimentoorgao.sinaiscomprometimentoorgaos',
            'Sinais de Extravasamento do Plasma': 'sinalextravasamentoplasma.sinaisextravasamentoplasma',
            'Sinais de Sangramento Grave': 'sinalsangramentograve.sinaissangramentograve',
            'Tipos de Evoluação': 'tipoevolucao.tiposevolucao',
            'Tipos de Local': 'tipolocal.tiposlocal',
            'Unidades de Saúde': 'unidadesaude.unidadessaude',
            'Zonas': 'zona.zonas',
            'Sair': 'auth.logout'
        })
        self.theme.light.default.update(color="#033770")
        self.theme.light.primary.update(color="#033770", background="#033770")
        self.theme.light.auxiliary.update(color="#f9c72a", background="#fceab7")
