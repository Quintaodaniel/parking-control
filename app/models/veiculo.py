from app.utils.validadores import ValidadorPlaca, ValidadorCPF

class Veiculo:
    def __init__(self, placa: str, modelo: str, cor: str, proprietario_cpf: str, autorizado: bool = False):
        """
        :param autorizado: Define se o veículo pode entrar (padrão False)
        """
        
        # Validações
        if not ValidadorPlaca.validar(placa):
            raise ValueError(f"Placa inválida: {placa}")
        
        self._placa = ValidadorPlaca.limpar(placa)
        self.modelo = modelo
        self.cor = cor
        self.proprietario_cpf = ValidadorCPF.limpar(proprietario_cpf)
        
        # ESTE CAMPO É O IMPORTANTE
        self.autorizado = autorizado 

    @property
    def placa(self):
        return self._placa

    def to_dict(self):
        return {
            "placa": self.placa,
            "modelo": self.modelo,
            "cor": self.cor,
            "proprietario_cpf": self.proprietario_cpf,
            "autorizado": self.autorizado
        }

    @classmethod
    def from_dict(cls, dados):
        """
        Aqui estava o provável erro. Precisamos ler o 'autorizado' do JSON.
        """
        return cls(
            placa=dados["placa"],
            modelo=dados["modelo"],
            cor=dados["cor"],
            proprietario_cpf=dados["proprietario_cpf"],
            autorizado=dados.get("autorizado", False) 
        )

    def __repr__(self):
        status = "LIBERADO" if self.autorizado else "BLOQUEADO"
        return f"<Veiculo: {self.placa} | {status}>"