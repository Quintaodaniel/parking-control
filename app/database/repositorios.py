from app.database.conexao import BancoDeDadosJson
from app.utils.validadores import ValidadorCPF
from app.utils.validadores import ValidadorPlaca
from app.models.registro import Registro
from app.models.pessoa import Pessoa
from app.models.veiculo import Veiculo

class RepositorioEstacionamento:
    def __init__(self):
        # Instancia a conexão que criamos antes
        self.db = BancoDeDadosJson()

    def resetar_todas_autorizacoes(self):
        """
        Define autorizado = False para TODOS os veículos cadastrados.
        Usado ao fim do evento.
        """
        dados = self.db.ler()
        total_alterados = 0

        for veiculo in dados["veiculos"]:
            if veiculo.get("autorizado") == True:
                veiculo["autorizado"] = False
                total_alterados += 1
        
        # Só salva se houve alguma mudança para poupar disco
        if total_alterados > 0:
            self.db.salvar(dados)
            
        return total_alterados

    def atualizar_status_veiculo(self, placa: str, novo_status: bool):
        """
        Busca um veículo pela placa e atualiza apenas o campo 'autorizado'.
        """
        dados = self.db.ler()
        
        # Precisamos da placa limpa para comparar
        from app.utils.validadores import ValidadorPlaca
        placa_limpa = ValidadorPlaca.limpar(placa)

        encontrou = False
        for v_dict in dados["veiculos"]:
            if v_dict["placa"] == placa_limpa:
                v_dict["autorizado"] = novo_status # Atualiza o dicionário
                encontrou = True
                break # Para de procurar
        
        if encontrou:
            self.db.salvar(dados) # Salva a lista modificada no arquivo
            return True
        return False
    
    def registrar_movimentacao(self, placa: str, tipo: str):
        try:
            # A validação acontece aqui dentro do construtor Registro()
            novo_registro = Registro(placa, tipo)
            
            dados = self.db.ler()
            if "historico" not in dados:
                dados["historico"] = []
                
            dados["historico"].append(novo_registro.to_dict())
            self.db.salvar(dados)
            return True
        except ValueError as e:
            print(f"Erro grave ao registrar histórico: {e}")
            return False
        
    def listar_todos_veiculos(self):
        """Retorna a lista crua de dicionários de todos os veículos."""
        return self.db.ler()["veiculos"]

    def listar_historico_completo(self):
        """Retorna a lista de movimentações registradas."""
        dados = self.db.ler()
        return dados.get("historico", []) # Retorna lista vazia se não houver histórico

    # --- MÉTODOS PARA PESSOA ---

    def adicionar_pessoa(self, pessoa: Pessoa):
        """Recebe um objeto Pessoa e salva no banco."""
        dados = self.db.ler()
        
        # Converte o objeto para dicionário antes de salvar
        dados["pessoas"].append(pessoa.to_dict())
        
        self.db.salvar(dados)

    def buscar_pessoa_por_cpf(self, cpf: str) -> Pessoa:
        """Busca no JSON e retorna um OBJETOO Pessoa (não um dicionário)."""
        dados = self.db.ler()
        
        # Precisamos limpar o CPF para buscar, pois no banco está salvo limpo
        cpf_limpo = ValidadorCPF.limpar(cpf)

        for p_dict in dados["pessoas"]:
            if p_dict["cpf"] == cpf_limpo:
                # Reconstrói o objeto a partir do dicionário
                return Pessoa.from_dict(p_dict)
        
        return None

    def listar_pessoas(self):
        """Retorna uma lista de objetos Pessoa."""
        dados = self.db.ler()
        return [Pessoa.from_dict(p) for p in dados["pessoas"]]

    # --- MÉTODOS PARA VEÍCULO ---

    def adicionar_veiculo(self, veiculo: Veiculo):
        dados = self.db.ler()
        dados["veiculos"].append(veiculo.to_dict())
        self.db.salvar(dados)

    def buscar_veiculo_por_placa(self, placa: str) -> Veiculo:
        dados = self.db.ler()
        
        placa_limpa = ValidadorPlaca.limpar(placa)

        for v_dict in dados["veiculos"]:
            if v_dict["placa"] == placa_limpa:
                return Veiculo.from_dict(v_dict)
        
        return None