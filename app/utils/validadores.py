import re

class ValidadorCPF:
    @staticmethod
    def limpar(cpf: str) -> str:
        """
        Retorna apenas os números do CPF.
        Centraliza a lógica de limpeza (strip, regex, etc).
        """
        if not cpf:
            return ""
        # Remove tudo que não for número
        return re.sub(r'[^0-9]', '', str(cpf))

    @staticmethod
    def validar(cpf: str) -> bool:
        """
        Verifica se um CPF é válido seguindo as regras matemáticas.
        Retorna True se válido, False caso contrário.
        """
        cpf_limpo = ValidadorCPF.limpar(cpf)

        if len(cpf_limpo) != 11:
            return False
        
        # Caso de 11 numeros iguais que passa na matemática mas é invalido (Ex: 111.111.111-11)
        if cpf_limpo == cpf_limpo[0] * 11:
            return False

        # Calcula os dígitos verificadores
        try:
            # Cálculo do primeiro dígito
            soma = 0
            for i in range(9):
                soma += int(cpf_limpo[i]) * (10 - i)
            resto = 11 - (soma % 11)
            digito1 = 0 if resto > 9 else resto

            # Verifica o primeiro dígito
            if digito1 != int(cpf_limpo[9]):
                return False

            # Cálculo do segundo dígito
            soma = 0
            for i in range(10):
                soma += int(cpf_limpo[i]) * (11 - i)
            resto = 11 - (soma % 11)
            digito2 = 0 if resto > 9 else resto

            # Verifica o segundo dígito
            return digito2 == int(cpf_limpo[10])

        except (ValueError, IndexError):
            return False

    @staticmethod
    def formatar(cpf: str) -> str:
        """Retorna o CPF formatado (XXX.XXX.XXX-XX)"""
        cpf_limpo = re.sub(r'[^0-9]', '', str(cpf))
        if len(cpf_limpo) != 11:
            return cpf  # Retorna original se não der para formatar
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    
class ValidadorPlaca:
    @staticmethod
    def limpar(placa: str) -> str:
        """
        Remove traços, espaços e converte para MAIÚSCULO.
        Ex: 'abc-1234' vira 'ABC1234'.
        """
        if not placa:
            return ""
        # Remove tudo que não for letra ou número e joga para UpperCase
        limpa = re.sub(r'[^a-zA-Z0-9]', '', str(placa))
        return limpa.upper()

    @staticmethod
    def validar(placa: str) -> bool:
        """
        Verifica se a placa bate com o padrão Antigo ou Mercosul.
        """
        placa_limpa = ValidadorPlaca.limpar(placa)

        # Regex para Padrão Antigo (3 letras, 4 números): ^[A-Z]{3}[0-9]{4}$
        # Regex para Mercosul (3 letras, 1 num, 1 letra, 2 num): ^[A-Z]{3}[0-9][A-Z][0-9]{2}$
        
        padrao_antigo = re.compile(r'^[A-Z]{3}[0-9]{4}$')
        padrao_mercosul = re.compile(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$')

        if padrao_antigo.match(placa_limpa):
            return True
        if padrao_mercosul.match(placa_limpa):
            return True
            
        return False