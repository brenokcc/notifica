from slth.application import Application


class ApiApplication(Application):
    def __init__(self):
        super().__init__()
        self.title = "ArboNotifica"
        self.subtitle = "Sistema de notificação de arboviroses da cidade de Dourados/MS"
        self.icon = "/static/images/logo.png"
        self.logo = "/static/images/logo.png"
        self.brand = "/static/images/brand.png"
        self.groups.add(
            administrador="Administrador",
            gu="Gestor de Unidade",
            gm="Gestor Municipal",
            notificante="Notificante",
            agente="Agente",
            supervisor="Supervisor",
            ru="Regulador de Unidade",
            regulador="Regulador",
        )
        self.dashboard.usermenu.add(
            "dev.icons",
            "user.users",
            "log.logs",
            "email.emails",
            "pushsubscription.pushsubscriptions",
            "job.jobs",
            "deletion.deletions",
            "settings.settings",
            "auth.logout",
        )
        self.dashboard.boxes.add(
            "municipio.municipios",
            "unidadesaude.unidadessaude",
            "notificacaoindividual.notificacoesindividuais",
            "notificacaoindividual.bloqueios",
            # 'notificacaosurto.notificacoessurto',
            "estatistica.painel",
            "solicitacaocadastro.solicitacoescadastro",
            "chamado.chamados",
            "exportacao.notificacoesindividuais",
        )
        self.dashboard.center.add(
            "termouso.checar",
        )
        self.dashboard.todo.add(
            "notificacaoindividual.aguardandoenvio",
            "notificacaoindividual.aguardandoresponsavelbloqueio",
            "notificacaoindividual.aguardandobloqueio",
            "notificacaoindividual.aguardandojustificativaperdaprazobloqueio",
            "notificacaoindividual.aguardandodevolucaobloqueio",
            "notificacaoindividual.aguardandocorrecao",
            "notificacaoindividual.aguardandovalidacao",
            "notificacaoindividual.aguardandoregistrosinan",
            "solicitacaocadastro.solicitacoescadastropendentes",
        )
        self.menu.add(
            {
                "list-ul:Cadastros Gerais": {
                    "Funções": "funcao.funcoes",
                    "Períodos de Gestação": "periodogestacao.periodosgestacao",
                    "Raças": "raca.racas",
                    "Sexos": "sexo.sexos",
                    "Escolaridades": "escolaridade.escolaridades",
                    "Municípios": "municipio.municipios",
                    "Motivos para Devolução de Bloqueio": "motivodevolucaobloqueio.motivosdevolucaobloqueio",
                    "Motivos de Perda de Prazo de Bloqueio": "motivoperdaprazobloqueio.motivosperdaprazobloqueio",
                    "Ocupações": "ocupacao.ocupacoes",
                },
                "users:Usuários": {
                    "Administradores": "administrador.administradores",
                    "Agentes de Endemias": "agente.agentes",
                    "Gestores Municipais": "gestormunicipal.gestoresmunicipais",
                    "Reguladores": "regulador.reguladores",
                    "Gestores de Unidade": "gestorunidade.gestoresunidade",
                    "Reguladores de Unidade": "reguladorunidade.reguladoresunidade",
                    "Notificantes": "notificante.notificantes",
                    "Supervisores de Agente de Endemias": "supervisor.supervisores",
                },
                "thermometer-quarter:Doenças": {
                    "Cadastro de Doenças": "doenca.doencas",
                    "Doenças Pré-Existentes": "doencapreexistente.doencaspreexistentes",
                    "Sinais de Alarme": "sinalalarme.sinaisalarme",
                    "Sinais Clínicos": "sinalclinico.sinaisclinicos",
                    "Sinais de Comprometimento dos Órgãos": "sinalcomprometimentoorgao.sinaiscomprometimentoorgaos",
                    "Sinais de Extravasamento do Plasma": "sinalextravasamentoplasma.sinaisextravasamentoplasma",
                    "Sinais de Sangramento Grave": "sinalsangramentograve.sinaissangramentograve",
                    "Tipos de Evoluação": "tipoevolucao.tiposevolucao",
                },
                "map-marker-alt:Locais": {
                    "Países": "pais.paises",
                    "Estados": "estado.estados",
                    "Municípios": "municipio.municipios",
                    "Zonas": "zona.zonas",
                    "Tipos de Local": "tipolocal.tiposlocal",
                    "Locais de Infecção": "localinfeccao.locaisinfeccao",
                    "Endereços Pré-cadastrados": "endereco.enderecos",
                },
                "book-medical:Infeção": {
                    "Apresentações Clínicas": "apresentacaoclinica.apresentacoesclinicas",
                    "Classificações": "classificacaoinfeccao.classificacoesinfeccao",
                    "Critérios de Confirmação": "criterioconfirmacao.criteriosconfirmacao",
                },
                "display:Videos": {
                    "Categorias": "categoriavideo.categoriasvideo",
                    "Videos": "video.videos",
                },
                #"hospital-symbol:Hospitais": "hospital.hospitais",
                # "contact-book:Solicitações de Cadastro": "solicitacaocadastro.solicitacoescadastro",
                #'person:Notificações Individuais': 'notificacaoindividual.notificacoesindividuais',
                #'people-line:Notificações de Surto': 'notificacaosurto.notificacoessurto',
                #"building:Unidades de Saúde": "unidadesaude.unidadessaude",
            }
        )
        self.dashboard.top.add("publico.quemsomos")
        self.dashboard.top.add("publico.videos")
        self.dashboard.top.add("solicitacaocadastro.cadastrar", "solicitacaocadastro.redefinirsenha",)
        self.theme.light.default.update(color="#033770")
        self.theme.light.primary.update(color="#033770", background="#033770")
        self.theme.light.auxiliary.update(color="#f9c72a", background="#fceab7")
        self.theme.light.success.update(color="#033770", background="#FFCC29")
        for imagem in [
            "prefeitura.png",
            "secretaria.png",
            "centro.png",
            "coordenacao.png",
            "fiocruz.png",
        ]:
            self.sponsors.add(f"/static/images/logos/{imagem}")
