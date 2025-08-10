from slth import endpoints
from ..models import *


class SolicitacoesCadastro(
    endpoints.ListEndpoint[SolicitacaoCadastro]
):
    class Meta:
        verbose_name = "Solicitações de Cadastro"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .actions(
                "solicitacaocadastro.cadastrar",
                "solicitacaocadastro.visualizar",
                "solicitacaocadastro.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("gm", "gu", "administrador")


class SolicitacoesCadastroPendentes(endpoints.ListEndpoint[SolicitacaoCadastro]):

    class Meta:
        modal = False
        verbose_name = "Solicitações de Cadastro Pendentes"

    def get_queryset(self):
        return super().get_queryset().filter(aprovada__isnull=True).actions("solicitacaocadastro.visualizar")
    
    def check_permission(self):
        return self.check_role("gm", "gu", "administrador")


class Cadastrar(endpoints.AddEndpoint[SolicitacaoCadastro]):
    class Meta:
        icon = "user-plus"
        verbose_name = "Solicitar Acesso"

    def get(self):
        return super().get().initial(municipio=Municipio.objects.first())

    def check_permission(self):
        return not self.request.user.is_authenticated
    
    def get_unidade_queryset(self, queryset):
        return queryset.nolookup().filter(municipio=self.form.controller.get('municipio'))


class Visualizar(endpoints.ViewEndpoint[SolicitacaoCadastro]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Solicitação de Cadastro"

    def check_permission(self):
        return self.check_role("gu", "gm", "administrador") and self.check_instance()


class Avaliar(endpoints.InstanceEndpoint[SolicitacaoCadastro]):
    class Meta:
        icon = "check"
        verbose_name = "Avaliar"

    def get(self):
        fields = "aprovada", "observacao"
        if self.instance.papel == "notificante":
            fields = "aprovada", "equipe", "observacao"
        return self.formfactory(self.instance).fieldset("", fields)

    def post(self):
        self.instance.avaliador = self.request.user
        self.instance.data_avaliacao = datetime.now()
        self.instance.save()
        self.instance.processar()
        return super().post()

    def check_permission(self):
        return self.check_role("gu", "gm") and self.instance.aprovada is None
    
    def get_equipe_queryset(self, queryset):
        return queryset.filter(unidade=self.instance.unidade)


class Excluir(endpoints.DeleteEndpoint[SolicitacaoCadastro]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Solicitação de Cadastro"
