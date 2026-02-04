from app.database.repositorios import RepositorioEstacionamento
from app.models.pessoa import Pessoa
from app.models.veiculo import Veiculo
from app.utils.validadores import ValidadorCPF, ValidadorPlaca
import csv

class ControleEstacionamento:
    def __init__(self):
        self.repo = RepositorioEstacionamento()

    def exportar_historico_csv(self):
        """Gera um arquivo CSV com todo o histórico."""
        historico = self.repo.listar_historico_completo()
        if not historico:
            return {"sucesso": False, "mensagem": "Histórico vazio."}
        
        try:
            with open('data/relatorio_acessos.csv', 'w', newline='', encoding='utf-8-sig') as f:
                escritor = csv.DictWriter(f, fieldnames=["data_hora", "tipo", "placa"])
                escritor.writeheader()
                escritor.writerows(historico)
            return {"sucesso": True, "mensagem": "Arquivo 'data/relatorio_acessos.csv' gerado!"}
        except Exception as e:
            return {"sucesso": False, "mensagem": f"Erro ao exportar: {e}"}

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
        from app.utils.validadores import ValidadorPlaca, ValidadorCPF
        
        # Se for PLACA
        if ValidadorPlaca.validar(termo_busca):
            veiculo = self.repo.buscar_veiculo_por_placa(termo_busca)
            if not veiculo: return {"encontrado": False, "mensagem": "Placa não cadastrada."}
            dono = self.repo.buscar_pessoa_por_cpf(veiculo.proprietario_cpf)
            return {
                "encontrado": True, "liberado": veiculo.autorizado,
                "mensagem": "Veículo Identificado",
                "detalhes": f"Modelo: {veiculo.modelo} | Dono: {dono.nome if dono else '???'}",
                "placa_direta": veiculo.placa
            }

        # Se for CPF
        elif ValidadorCPF.validar(termo_busca):
            pessoa = self.repo.buscar_pessoa_por_cpf(termo_busca)
            if not pessoa: return {"encontrado": False, "mensagem": "CPF não cadastrado."}
            
            # Busca todos os carros desse CPF
            veiculos_do_dono = []
            dados = self.repo.listar_todos_veiculos()
            for v in dados:
                if v['proprietario_cpf'] == pessoa.cpf:
                    veiculos_do_dono.append(v)
            
            return {
                "encontrado": True,
                "liberado": any(v.get('autorizado') for v in veiculos_do_dono),
                "mensagem": f"Pessoa: {pessoa.nome}",
                "detalhes": f"Possui {len(veiculos_do_dono)} veículo(s) cadastrado(s).",
                "lista_veiculos": veiculos_do_dono # Passa a lista para a tela
            }
        
        return {"encontrado": False, "mensagem": "Formato inválido (Use Placa ou CPF)."}

    def relatorio_veiculos_internos(self):
        """Identifica quais veículos entraram e ainda não saíram."""
        historico = self.repo.listar_historico_completo()
        status_atual = {} # Placa: ultimo_movimento

        for reg in historico:
            status_atual[reg['placa']] = reg['tipo']

        # Filtra apenas os que o último registro foi ENTRADA
        placas_dentro = [p for p, tipo in status_atual.items() if tipo == 'ENTRADA']
        
        resultado = []
        for placa in placas_dentro:
            v = self.repo.buscar_veiculo_por_placa(placa)
            if v:
                dono = self.repo.buscar_pessoa_por_cpf(v.proprietario_cpf)
                resultado.append({
                    "placa": v.placa,
                    "modelo": v.modelo,
                    "dono": dono.nome if dono else "Desconhecido"
                })
        return resultado

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