from app.database.repositorios import RepositorioEstacionamento
from app.models.pessoa import Pessoa
from app.models.veiculo import Veiculo
from app.utils.validadores import ValidadorCPF, ValidadorPlaca

class ControleEstacionamento:
    def __init__(self):
        self.repo = RepositorioEstacionamento()

    def cadastrar_pessoa(self, nome, cpf, contato):
        """Cadastra um novo proprietário."""
        if self.repo.buscar_pessoa_por_cpf(cpf):
            return {"sucesso": False, "mensagem": "Erro: CPF já cadastrado."}

        try:
            nova_pessoa = Pessoa(nome, cpf, contato)
            self.repo.adicionar_pessoa(nova_pessoa)
            return {"sucesso": True, "mensagem": f"Pessoa '{nome}' cadastrada com sucesso!"}
        except ValueError as e:
            return {"sucesso": False, "mensagem": f"Erro de validação: {str(e)}"}

    def processar_veiculo_evento(self, placa, modelo, cor, cpf_dono, autorizado):
        """
        Cadastra ou Atualiza um veículo.
        Se já existe, atualiza apenas o status de autorização.
        Se não existe, cria um novo.
        """
        # Verifica dono
        dono = self.repo.buscar_pessoa_por_cpf(cpf_dono)
        if not dono:
            return {"sucesso": False, "mensagem": "Erro: Proprietário não encontrado. Cadastre o CPF antes."}

        # Verifica veículo
        veiculo_existente = self.repo.buscar_veiculo_por_placa(placa)

        if veiculo_existente:
            # ATUALIZAÇÃO
            self.repo.atualizar_status_veiculo(placa, autorizado)
            acao = "LIBERADO" if autorizado else "BLOQUEADO"
            return {"sucesso": True, "mensagem": f"Veículo existente atualizado: Acesso {acao}."}
        else:
            # NOVO CADASTRO
            try:
                novo_carro = Veiculo(
                    placa=placa, 
                    modelo=modelo, 
                    cor=cor, 
                    proprietario_cpf=cpf_dono,
                    autorizado=autorizado
                )
                self.repo.adicionar_veiculo(novo_carro)
                status_texto = "AUTORIZADO" if autorizado else "Sem permissão"
                return {"sucesso": True, "mensagem": f"Novo veículo cadastrado e {status_texto}."}
            except ValueError as e:
                return {"sucesso": False, "mensagem": f"Erro de validação: {str(e)}"}

    def buscar_acesso(self, termo_busca):
        """
        Verifica se o VEÍCULO ou CPF está liberado e retorna os detalhes para a tela.
        """
        # CENÁRIO 1: Busca por PLACA (Ideal)
        if ValidadorPlaca.validar(termo_busca):
            veiculo = self.repo.buscar_veiculo_por_placa(termo_busca)
            
            if not veiculo:
                return {"encontrado": False, "mensagem": "Placa não cadastrada."}
            
            dono = self.repo.buscar_pessoa_por_cpf(veiculo.proprietario_cpf)
            nome_dono = dono.nome if dono else "Desconhecido"

            status_str = "LIBERADO" if veiculo.autorizado else "NEGADO"
            
            return {
                "encontrado": True,
                "liberado": veiculo.autorizado, # Aqui está a correção: Pega o valor real do banco
                "mensagem": f"Acesso {status_str}",
                "detalhes": f"Veículo: {veiculo.modelo} ({veiculo.cor}) | Dono: {nome_dono}"
            }

        # CENÁRIO 2: Busca por CPF
        elif ValidadorCPF.validar(termo_busca):
            pessoa = self.repo.buscar_pessoa_por_cpf(termo_busca)
            if not pessoa:
                return {"encontrado": False, "mensagem": "Pessoa não encontrada."}

            # Simula busca de carros deste CPF
            todos_veiculos = self.repo.listar_todos_veiculos()
            carros_autorizados = []
            
            cpf_limpo = pessoa.cpf 
            # Procura nos dicionários crus do repo
            for v_dict in todos_veiculos:
                if v_dict["proprietario_cpf"] == cpf_limpo and v_dict.get("autorizado"):
                    carros_autorizados.append(f"{v_dict['modelo']} ({v_dict['placa']})")

            if carros_autorizados:
                return {
                    "encontrado": True,
                    "liberado": True,
                    "mensagem": "Pessoa possui veículos autorizados.",
                    "detalhes": f"Veículos permitidos: {', '.join(carros_autorizados)}"
                }
            else:
                return {
                    "encontrado": True,
                    "liberado": False,
                    "mensagem": "Pessoa sem veículos autorizados para o evento.",
                    "detalhes": f"Pessoa: {pessoa.nome} (Sem permissão ativa)"
                }

        else:
            return {"encontrado": False, "mensagem": "Formato inválido."}

    def registrar_fluxo(self, placa, tipo):
        """Registra a entrada/saída no histórico."""
        veiculo = self.repo.buscar_veiculo_por_placa(placa)
        if not veiculo:
            return {"sucesso": False, "mensagem": "Erro: Veículo não encontrado."}

        self.repo.registrar_movimentacao(placa, tipo)
        return {"sucesso": True, "mensagem": f"Sucesso: {tipo} registrada para {veiculo.modelo} ({placa})."}

    def relatorio_autorizados(self):
        """Gera lista para o relatório de autorizados."""
        veiculos = self.repo.listar_todos_veiculos()
        resultado = []

        for v in veiculos:
            if v.get("autorizado"):
                dono = self.repo.buscar_pessoa_por_cpf(v["proprietario_cpf"])
                nome_dono = dono.nome if dono else "Dono Desconhecido"
                
                linha = {
                    "dono": nome_dono,
                    "modelo": v["modelo"],
                    "placa": v["placa"],
                    "cor": v.get("cor", "-")
                }
                resultado.append(linha)
        
        resultado.sort(key=lambda x: x["dono"])
        return resultado

    def relatorio_historico(self):
        """Gera lista para o histórico."""
        registros = self.repo.listar_historico_completo()
        return registros[::-1] # Inverte para mostrar mais recente primeiro

    def encerrar_evento(self):
        """Zera as permissões."""
        qtd = self.repo.resetar_todas_autorizacoes()
        if qtd > 0:
            return {"sucesso": True, "mensagem": f"EVENTO ENCERRADO! {qtd} veículos foram bloqueados."}
        else:
            return {"sucesso": True, "mensagem": "Evento encerrado. Todos já estavam bloqueados."}