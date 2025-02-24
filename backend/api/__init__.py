from slth.application import Application


class ApiApplication(Application):
    def __init__(self):
        super().__init__()
        self.title = "Nofica"
        self.subtitle = "Sistema de notificação de casos de dengue e chikungunya"
        self.icon = "/static/images/logo.png"
        self.logo = "/static/images/logo.png"
        self.groups.add(administrador='Administrador', operador= "Operador")
        self.dashboard.usermenu.add(
            "dev.icons", "user.users", "log.logs", "email.emails",
            "pushsubscription.pushsubscriptions", "job.jobs",
            "deletion.deletions", "auth.logout"
        )
        self.dashboard.boxes.add('notificacao.notificacoes')
        
        self.menu.add({
            'Doenças': 'doenca.doencas',
            'Doenças Pré-Existentes': 'doencapreexistente.doencaspreexistentes',
            'Escolaridades': 'escolaridade.escolaridades',
            'Estados': 'estado.estados',
            'Funções': 'funcao.funcoes',
            'Hospitais': 'hospital.hospitais',
            'Locais de Infecção': 'localinfeccao.locaisinfeccao',
            'Municípios': 'municipio.municipios',
            'Notificações': 'notificacao.notificacoes',
            'Notificantes': 'notificante.notificantes',
            'Períodos de Gestação': 'periodogestacao.periodosgestacao',
            'Raças': 'raca.racas',
            'Sexos': 'sexo.sexos',
            'Sinais Clínicos': 'sinalclinico.sinaisclinicos',
            'Tipos de Local': 'tipolocal.tiposlocal',
            'Tipos de Notificação': 'tiponotificacao.tiposnotificacao',
            'Unidades de Saúde': 'unidadesaude.unidadessaude',
            'Zonas': 'zona.zonas',
            'Sair': 'auth.logout'
        })
