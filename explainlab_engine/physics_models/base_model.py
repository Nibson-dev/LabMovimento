from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def solve(self, **kwargs):
        """
        Método obrigatório. 
        Recebe os parâmetros físicos do frontend e retorna um dicionário
        com o modelo detectado, os passos explicativos e os dados da simulação.
        """
        pass