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
            "deletion.deletions", "settings.settings", "auth.logout"
        )
        self.dashboard.boxes.add(
            'notificacaoindividual.notificacoesindividuais',
            'notificacaosurto.notificacoessurto',
            'estatistica.painel',
            'notificacaoindividual.aguardandovalidacao',
        )
        
        self.menu.add({
            'list-ul:Cadastros Gerais': {
                'Funções': 'funcao.funcoes',
                'Períodos de Gestação': 'periodogestacao.periodosgestacao',
                'Raças': 'raca.racas',
                'Sexos': 'sexo.sexos',
                'Escolaridades': 'escolaridade.escolaridades',
                'Ocupações': 'ocupacao.ocupacoes',
            },
            'users:Gestores': 'gestor.gestores',
            'thermometer-quarter:Doenças': {
                'Cadastro de Doenças': 'doenca.doencas',
                'Doenças Pré-Existentes': 'doencapreexistente.doencaspreexistentes',
                'Sinais de Alarme': 'sinalalarme.sinaisalarme',
                'Sinais Clínicos': 'sinalclinico.sinaisclinicos',
                'Sinais de Comprometimento dos Órgãos': 'sinalcomprometimentoorgao.sinaiscomprometimentoorgaos',
                'Sinais de Extravasamento do Plasma': 'sinalextravasamentoplasma.sinaisextravasamentoplasma',
                'Sinais de Sangramento Grave': 'sinalsangramentograve.sinaissangramentograve',
                'Tipos de Evoluação': 'tipoevolucao.tiposevolucao',
            },
            'map-marker-alt:Locais': {
                'Países': 'pais.paises',
                'Estados': 'estado.estados',
                'Municípios': 'municipio.municipios',
                'Zonas': 'zona.zonas',
                'Tipos de Local': 'tipolocal.tiposlocal',
                'Locais de Infecção': 'localinfeccao.locaisinfeccao',
            },
            'book-medical:Infeção': {
                'Apresentações Clínicas': 'apresentacaoclinica.apresentacoesclinicas',
                'Classificações': 'classificacaoinfeccao.classificacoesinfeccao',
                'Critérios de Confirmação': 'criterioconfirmacao.criteriosconfirmacao',
            },
            'hospital-symbol:Hospitais': 'hospital.hospitais',
            
            'person:Notificações Individuais': 'notificacaoindividual.notificacoesindividuais',
            'people-line:Notificações de Surto': 'notificacaosurto.notificacoessurto',
            'contact-book:Notificantes': 'notificante.notificantes',
            'building:Unidades de Saúde': 'unidadesaude.unidadessaude',
            'sign-out-alt:Sair': 'auth.logout'
        })
        self.theme.light.default.update(color="#033770")
        self.theme.light.primary.update(color="#033770", background="#033770")
        self.theme.light.auxiliary.update(color="#f9c72a", background="#fceab7")
        self.theme.light.success.update(color="#033770", background="#FFCC29")
