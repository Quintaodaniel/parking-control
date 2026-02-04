import json
import shutil
import os

class BancoDeDadosJson:
    def __init__(self, arquivo="data/estacionamento.json"):
        """
        Gerencia a leitura e escrita no arquivo JSON.
        :param arquivo: Caminho do arquivo (padrão: data/estacionamento.json)
        """
        self.arquivo = arquivo
        self._verificar_diretorio()
        self._verificar_arquivo()

    def _verificar_diretorio(self):
        """Garante que a pasta 'data' exista."""
        pasta = os.path.dirname(self.arquivo)
        if pasta and not os.path.exists(pasta):
            os.makedirs(pasta)

    def _verificar_arquivo(self):
        """
        Se o arquivo não existir, cria um JSON vazio com a estrutura básica.
        Isso impede erros de leitura na primeira execução.
        """
        if not os.path.exists(self.arquivo):
            dados_iniciais = {
                "pessoas": [],
                "veiculos": [],
                "historico": [] # Futuramente podemos guardar logs de entrada/saída aqui
            }
            self.salvar(dados_iniciais)

    def ler(self):
        """
        Lê o arquivo JSON e retorna como um dicionário Python.
        """
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Se o arquivo estiver corrompido ou vazio, reseta para evitar crash
            return {"pessoas": [], "veiculos": [], "historico": []}

    def salvar(self, dados):
            """Salva com backup de segurança."""
            # Se o arquivo existe, cria uma cópia .bak antes de sobrescrever
            if os.path.exists(self.arquivo):
                shutil.copyfile(self.arquivo, self.arquivo + ".bak")
                
            with open(self.arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)