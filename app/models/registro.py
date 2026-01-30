from datetime import datetime
from app.utils.validadores import ValidadorPlaca

class Registro:
    def __init__(self, placa: str, tipo: str = 'ENTRADA', data_hora: str = None):
        """
        Representa uma movimentação no estacionamento.
        :param placa: Placa do veículo
        :param tipo: 'ENTRADA' ou 'SAIDA'
        :param data_hora: String com data e hora. Se None, pega a hora atual.
        """

        if not ValidadorPlaca.validar(placa):
            raise ValueError(f"Tentativa de registrar placa inválida: {placa}")

        self.placa = ValidadorPlaca.limpar(placa)
        self.tipo = tipo.upper()
        
        # Se não informarmos a hora, ele pega a do sistema automaticamente
        if data_hora:
            self.data_hora = data_hora
        else:
            self.data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """Prepara para salvar no JSON"""
        return {
            "placa": self.placa,
            "tipo": self.tipo,
            "data_hora": self.data_hora
        }

    @classmethod
    def from_dict(cls, dados):
        """Reconstrói do JSON"""
        return cls(
            placa=dados["placa"],
            tipo=dados["tipo"],
            data_hora=dados["data_hora"]
        )

    def __repr__(self):
        return f"[{self.data_hora}] {self.tipo}: {self.placa}"