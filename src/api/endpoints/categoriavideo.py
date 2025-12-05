from slth import endpoints
from ..models import *


class CategoriasVideo(endpoints.ListEndpoint[CategoriaVideo]):
    class Meta:
        verbose_name = 'Categorias de Video'

    def get(self):
        return (
            super().get()
            .actions('categoriavideo.cadastrar', 'categoriavideo.visualizar', 'categoriavideo.editar', 'categoriavideo.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[CategoriaVideo]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Categoria de Video'

    def check_permission(self):
        return self.check_role('administrador')

        
class Visualizar(endpoints.ViewEndpoint[CategoriaVideo]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Categoria de Video'

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[CategoriaVideo]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Categoria de Video'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[CategoriaVideo]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Categoria de Video'

    def check_permission(self):
        return self.check_role('administrador')

