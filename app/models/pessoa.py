from app.utils.validadores import ValidadorCPF

class Pessoa:
    def __init__(self, nome: str, cpf: str, contato: str):
        # Validação
        if not ValidadorCPF.validar(cpf):
            raise ValueError(f"CPF inválido: {cpf}")

        self.nome = nome
        # Limpeza - O atributo _cpf guarda APENAS números
        self._cpf = ValidadorCPF.limpar(cpf) 
        self.contato = contato

    @property
    def cpf(self):
        """Retorna o CPF limpo (apenas números)."""
        return self._cpf

    @property
    def cpf_formatado(self):
        """
        Propriedade extra utilitária para exibir bonito na tela.
        Usa o formatador do Validador.
        """
        return ValidadorCPF.formatar(self._cpf)

    def to_dict(self):
        return {
            "nome": self.nome,
            "cpf": self.cpf, # Salva limpo no JSON
            "contato": self.contato
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(
            nome=dados["nome"],
            cpf=dados["cpf"],
            contato=dados.get("contato", "")
        )

    def __repr__(self):
        return f"<Pessoa: {self.nome} | CPF: {self.cpf_formatado}>"