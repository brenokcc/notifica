from slth import endpoints
from ..models import *
from slth.models import Email
from django.core import signing
from django.conf import settings
from django.contrib.auth.models import User
from slth.endpoints.auth import login_response


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
                "solicitacaocadastro.cancelaravaliacao",
            )
        )

    def check_permission(self):
        return self.check_role("gm", "gu", "administrador")


class SolicitacoesCadastroPendentes(endpoints.ListEndpoint[SolicitacaoCadastro]):

    class Meta:
        modal = False
        verbose_name = "Solicitações de cadastro pendentes"

    def get_queryset(self):
        return super().get_queryset().filter(aprovada__isnull=True).actions("solicitacaocadastro.visualizar", "solicitacaocadastro.avaliar", "solicitacaocadastro.excluir")
    
    def check_permission(self):
        return self.check_role("gm", "gu", "administrador") and super().get_queryset().exists()


class RedefinirSenha(endpoints.AddEndpoint[SolicitacaoCadastro]):
    cpf = endpoints.forms.CharField(label="CPF")
    email = endpoints.forms.CharField(label="E-mail")
    senha = endpoints.forms.CharField(label="Senha")

    class Meta:
        icon = "user-lock"
        verbose_name = "Redefinir Senha"

    def get(self):
        token = self.request.GET.get('token')
        if token:
            dados = signing.loads(token)
            user = User.objects.filter(email=dados['email'], username=dados['cpf']).first()
            user.set_password(dados['password'])
            user.save()
            return login_response(user)
        return self.formfactory().fields('cpf', 'email', 'senha').info("Você receberá um e-mail contendo o link para confirmar a alteração da senha.")

    def check_permission(self):
        return not self.request.user.is_authenticated
    
    def post(self):
        to = self.cleaned_data['email']
        cpf = self.cleaned_data['cpf']
        password = self.cleaned_data['senha']
        if User.objects.filter(email=to, username=cpf).exists():
            token = signing.dumps(dict(email=to, password=password, cpf=cpf))
            url = f'{settings.SITE_URL}/app/solicitacaocadastro/redefinirsenha/?token={token}'
            content = "Acesse o link abaixo para confirmar a alteração de sua senha."
            email = Email(to=to, subject="Arbonotifica - Redefinição de senha.", content=content, action="Confirmar", url=url)
            email.send()
            return super().post()
        else:
            raise ValidationError("Usuário não localizado")


class Cadastrar(endpoints.AddEndpoint[SolicitacaoCadastro]):
    class Meta:
        icon = "user-plus"
        verbose_name = "Solicitar Acesso"

    def get(self):
        return super().get().initial(municipio=Municipio.objects.first())

    def check_permission(self):
        return not self.request.user.is_authenticated
    
    def get_municipio_queryset(self, queryset):
        return queryset.nolookup()

    def get_unidade_queryset(self, queryset):
        return queryset.nolookup().filter(municipio=self.form.controller.get('municipio'))

    def post(self):
        qs = SolicitacaoCadastro.objects.filter(
            cpf=self.instance.cpf,
            papel=self.instance.papel,
            municipio=self.instance.municipio,
            unidade=self.instance.unidade,
        ).exclude(pk=self.instance.pk).exclude(aprovada=False)
        if qs.exists():
            raise ValidationError('Já existe uma solicitação para o CPF e papel informados pendente de avaliação ou aprovada.')
        if self.instance.papel == 'notificante':
            if not self.instance.unidade:
                raise ValidationError('Informe a unidade.')
        else:
            if self.instance.unidade:
                raise ValidationError('Não é necessário informar a unidade.')
        content = 'Sua solicitação de acesso foi registrada e será avaliada em breve.'
        email = Email(to=self.instance.email, subject="Arbonotifica - Solicitação de Acesso", content=content)
        email.send()
        if self.instance.unidade:
            for gestor in self.instance.unidade.gestores.all():
                content = 'Uma nova solicitação de acesso foi castrada para sua unidade.'
                email = Email(to=gestor.email, subject="Arbonotifica - Solicitação de Acesso", content=content)
                email.send()
        else:
            for gestor in self.instance.municipio.gestores.all():
                content = 'Uma nova solicitação de acesso foi castrada para seu município.'
                email = Email(to=gestor.email, subject="Arbonotifica - Solicitação de Acesso", content=content)
                email.send()
        return super().post()


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
    
    def clean(self, data):
        equipe = data.get('equipe')
        if self.instance.papel == "notificante" and not equipe:
            raise ValidationError("Informe a equipe do notificante")

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

    def check_permission(self):
        return self.check_role("gm", "gu", "administrador") and self.instance.aprovada is None


class CancelarAvaliacao(endpoints.InstanceEndpoint[SolicitacaoCadastro]):
    class Meta:
        icon = "x"
        verbose_name = "Cancelar Avaliação"

    def get(self):
        return self.formfactory(self.instance).fields()
    
    def post(self):
        self.instance.aprovada = None
        self.instance.avaliador = None
        self.instance.data_avaliacao = None
        self.instance.save()
        return super().post()
    
    def check_permission(self):
        return self.instance.data_avaliacao # and self.request.user.is_superuser
    
