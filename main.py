import os
import sys
from app.controllers.controle_acesso import ControleEstacionamento

# Inicializa o controlador (o cérebro do sistema)
sistema = ControleEstacionamento()

def limpar_tela():
    """Limpa o console de comando (funciona em Windows e Linux/Mac)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_cabecalho():
    print("="*50)
    print("   SISTEMA DE ESTACIONAMENTO & CONTROLE DE ACESSO   ")
    print("="*50)

def menu_principal():
    while True:
        limpar_tela()
        exibir_cabecalho()
        print("\n[ CADASTRO E GESTÃO ]")
        print("1. Cadastrar Pessoa")
        print("2. Gerenciar Veículo (Autorizar)")
        
        print("\n[ OPERAÇÃO ]")
        print("3. PORTARIA (Consulta & Fluxo)")
        print("4. Veículos Presentes (Quem está dentro?)")
        
        print("\n[ RELATÓRIOS ]")
        print("5. Ver Lista de Autorizados")
        print("6. Ver Histórico Completo")
        print("7. Exportar Histórico para Excel (CSV)")
        
        print("\n[ MANUTENÇÃO ]")
        print("9. ENCERRAR EVENTO (Reset)")
        print("0. Sair")
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            tela_cadastro_pessoa()
        elif opcao == '2':
            tela_gestao_veiculo()
        elif opcao == '3':
            tela_consulta_acesso()
        elif opcao == '4':
            tela_veiculos_dentro()
        elif opcao == '5':
            tela_relatorio_autorizados()
        elif opcao == '6':
            tela_relatorio_historico()
        elif opcao == '7':
            res = sistema.exportar_historico_csv()
            input(f"\n>> {res['mensagem']}\nPressione Enter...")
        elif opcao == '9':
            tela_reset_evento()
        elif opcao == '0':
            sys.exit()
        else:
            input("Opção inválida! Enter para continuar...")

# --- TELAS DO SISTEMA ---

def tela_cadastro_pessoa():
    limpar_tela()
    print("--- 1. NOVO CADASTRO DE PESSOA ---")
    print("Preencha os dados do proprietário/funcionário.\n")
    
    nome = input("Nome Completo: ")
    cpf = input("CPF (apenas números ou com pontuação): ")
    contato = input("Contato (Email ou Telefone): ")

    # Chama o controlador
    resultado = sistema.cadastrar_pessoa(nome, cpf, contato)
    
    print(f"\n>> {resultado['mensagem']}")
    input("\nPressione Enter para voltar ao menu...")

def tela_gestao_veiculo():
    limpar_tela()
    print("--- 2. GERENCIAR VEÍCULO (LISTA DO EVENTO) ---")
    print("Use esta opção para processar a lista enviada pela empresa.")
    print("Se o carro já existir, o status de autorização será atualizado.\n")
    
    cpf_dono = input("CPF do Proprietário: ")
    placa = input("Placa do Veículo: ")
    
    print("\n(Opcional: Deixe em branco se o veículo já estiver cadastrado)")
    modelo = input("Modelo (ex: Fiat Uno): ")
    cor = input("Cor: ")
    
    print("-" * 30)
    resp_auth = input("ESTE VEÍCULO ESTÁ AUTORIZADO PARA O EVENTO? (S/N): ").strip().upper()
    autorizado = (resp_auth == 'S')

    # Chama o método inteligente que cria ou atualiza
    resultado = sistema.processar_veiculo_evento(placa, modelo, cor, cpf_dono, autorizado)
    
    print(f"\n>> {resultado['mensagem']}")
    input("\nPressione Enter para voltar ao menu...")

def tela_consulta_acesso():
    while True:
        limpar_tela()
        print("--- 3. PORTARIA (CONSULTA & REGISTRO) ---\n")
        busca = input("Digite a PLACA ou o CPF (ou 'sair'): ").strip()
        if busca.lower() == 'sair': break
        
        resultado = sistema.buscar_acesso(busca)
        print("\n" + "="*40)
        
        if resultado['encontrado']:
            print(f"STATUS: {'[ LIBERADO ]' if resultado['liberado'] else '[ BLOQUEADO ]'}")
            print(f"INFO: {resultado['mensagem']}")
            print(f"DETALHES: {resultado['detalhes']}")
            
            placa_para_registro = None

            # Se buscou por PLACA, já temos a placa
            if 'placa_direta' in resultado:
                placa_para_registro = resultado['placa_direta']
            
            # Se buscou por CPF, mostra os carros dele para o porteiro escolher um
            elif 'lista_veiculos' in resultado:
                print("\nVEÍCULOS DESTA PESSOA:")
                for i, v in enumerate(resultado['lista_veiculos'], 1):
                    auth = "OK" if v.get('autorizado') else "X"
                    print(f"{i}. {v['placa']} - {v['modelo']} [{auth}]")
                
                escolha = input("\nSelecione o número do veículo (ou digite a placa): ")
                if escolha.isdigit() and 1 <= int(escolha) <= len(resultado['lista_veiculos']):
                    placa_para_registro = resultado['lista_veiculos'][int(escolha)-1]['placa']
                else:
                    placa_para_registro = escolha.upper()

            if placa_para_registro:
                print(f"\nREGISTRAR MOVIMENTO PARA: {placa_para_registro}")
                acao = input("[E] Entrada | [S] Saída | [Enter] Cancelar: ").upper()
                if acao in ['E', 'S']:
                    tipo = 'ENTRADA' if acao == 'E' else 'SAIDA'
                    res_reg = sistema.registrar_fluxo(placa_para_registro, tipo)
                    print(f"\n>> {res_reg['mensagem']}")
        else:
            print(f"AVISO: {resultado['mensagem']}")
        
        print("="*40)
        input("\nProxima consulta (Enter)...")

def tela_veiculos_dentro():
    limpar_tela()
    print("--- VEÍCULOS ATUALMENTE NO PÁTIO ---")
    lista = sistema.relatorio_veiculos_internos()
    
    if not lista:
        print("\nO pátio está vazio.")
    else:
        print(f"{'PLACA':<10} | {'VEÍCULO':<20} | {'PROPRIETÁRIO'}")
        print("-" * 50)
        for item in lista:
            print(f"{item['placa']:<10} | {item['modelo']:<20} | {item['dono']}")
    
    input("\nPressione Enter para voltar...")

def tela_relatorio_autorizados():
    limpar_tela()
    print("--- 4. RELATÓRIO: LISTA DE AUTORIZADOS ---")
    print(f"{'PROPRIETÁRIO':<30} | {'PLACA':<10} | {'VEÍCULO':<20}")
    print("-" * 66)
    
    lista = sistema.relatorio_autorizados()
    
    if not lista:
        print(">> Nenhum veículo autorizado no momento.")
    else:
        for item in lista:
            print(f"{item['dono']:<30} | {item['placa']:<10} | {item['modelo']:<20}")
            
    print("-" * 66)
    print(f"Total: {len(lista)} veículos liberados.")
    input("\nPressione Enter para voltar...")

def tela_relatorio_historico():
    limpar_tela()
    print("--- 5. RELATÓRIO: HISTÓRICO DE ACESSOS (Últimos primeiro) ---")
    print(f"{'DATA/HORA':<20} | {'TIPO':<10} | {'PLACA':<10}")
    print("-" * 46)
    
    historico = sistema.relatorio_historico()
    
    if not historico:
        print(">> Nenhum registro de movimentação encontrado.")
    else:
        # Mostra apenas os últimos 20 para não poluir a tela
        for item in historico[:20]:
            print(f"{item['data_hora']:<20} | {item['tipo']:<10} | {item['placa']:<10}")
            
    print("-" * 46)
    input("\nPressione Enter para voltar...")

def tela_reset_evento():
    limpar_tela()
    print("!!!" + "="*40 + "!!!")
    print("       ÁREA DE SEGURANÇA - RESET GERAL       ")
    print("!!!" + "="*40 + "!!!")
    print("\nEsta ação irá remover a autorização de TODOS os veículos.")
    print("Isso deve ser feito APENAS ao final do evento para limpar o banco.")
    print("\nPara confirmar, digite exatamente: CONFIRMAR")
    
    confirmacao = input("\nSua resposta: ")

    if confirmacao == "CONFIRMAR":
        print("\nProcessando...")
        resultado = sistema.encerrar_evento()
        print(f"\n>> {resultado['mensagem']}")
    else:
        print("\n>> Operação CANCELADA. Nenhuma alteração foi feita.")
    
    input("\nPressione Enter para voltar ao menu...")

if __name__ == "__main__":
    # Verifica/Cria a pasta de dados antes de iniciar para evitar erros
    if not os.path.exists('data'):
        try:
            os.makedirs('data')
        except PermissionError:
            print("Erro: Sem permissão para criar a pasta 'data'. Execute como Administrador.")
            sys.exit(1)
            
    menu_principal()