# 🚗 Sistema de Gerenciamento de Estacionamento

Um sistema em **Python** focado em controle de acesso para eventos, utilizando persistência de dados em **JSON** e arquitetura **MVC (Model-View-Controller)**.

O projeto simula uma portaria inteligente, permitindo validar CPFs e Placas, controlar listas de autorização e registrar histórico de entrada e saída.

---

## 📋 Funcionalidades

* **Cadastro de Pessoas:** Registro de proprietários com validação automática de CPF.
* **Gestão de Veículos:** Vínculo de carros aos donos com validação de Placa (Mercosul e Padrão Antigo).
* **Controle de Acesso (Allowlist):**
    * Sistema de "Lista de Evento": Apenas veículos marcados como *Autorizados* recebem "LIBERADO" na portaria.
    * Busca inteligente por **Placa** ou **CPF**.
* **Registro de Fluxo:** Opção para registrar efetivamente a **Entrada** ou **Saída** (Log de histórico).
* **Relatórios:**
    * Lista de veículos autorizados.
    * Histórico cronológico de movimentações.
* **Reset de Evento:** Funcionalidade de segurança que bloqueia todos os veículos ao fim do evento.

---

## 🛠️ Tecnologias e Arquitetura

O projeto foi construído seguindo boas práticas de Engenharia de Software:

* **Linguagem:** Python 3.x (Nativo, sem bibliotecas externas pesadas).
* **Arquitetura:** MVC (Model - View - Controller).
* **Persistência:** Arquivo JSON (`data/estacionamento.json`) gerenciado via *Repository Pattern*.
* **Validações:** Regex para garantir integridade de dados (CPF e Placas).

### Estrutura de Pastas

```text
estacionamento_system/
│
├── main.py                  # Camada de Visualização (Menu/CLI)
│
├── app/
│   ├── controllers/         # Regras de Negócio
│   │   └── controle_acesso.py
│   │
│   ├── models/              # Classes e Objetos
│   │   ├── pessoa.py
│   │   ├── veiculo.py
│   │   └── registro.py
│   │
│   ├── database/            # Persistência de Dados
│   │   ├── conexao.py       # Gerenciador de Arquivo JSON
│   │   └── repositorios.py  # CRUD e Consultas
│   │
│   └── utils/               # Ferramentas Auxiliares
│       └── validadores.py   # Lógica de validação (CPF/Placa)
│
└── data/                    # Banco de dados (Gerado automaticamente)
    └── estacionamento.json
```

## 🚀 Como Executar

### Pré-requisitos
* Python 3 instalado na máquina.

### Passo a Passo

1.  **Clone o repositório** (ou baixe os arquivos):
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd estacionamento_system
    ```

2.  **Execute o sistema:**
    ```bash
    python main.py
    ```

3.  **Primeiro Acesso:**
    * O sistema criará automaticamente a pasta `data/` e o arquivo `estacionamento.json` na primeira execução.

---

## 📖 Guia de Uso

### 1. Preparação (Antes do Evento)
1.  Acesse a opção **1** para cadastrar as pessoas (Proprietários).
2.  Acesse a opção **2** para cadastrar os veículos.
    * *Importante:* Ao cadastrar o veículo, responda **"S"** (Sim) para autorizar a entrada no evento atual.

### 2. Operação (Durante do Evento)
1.  Vá para a **Portaria (Opção 3)**.
2.  Digite a Placa do carro que chegou.
3.  O sistema informará: `STATUS: LIBERADO` ou `BLOQUEADO`.
4.  Se liberado, você pode digitar **"E"** para registrar a Entrada no histórico.

### 3. Finalização (Pós-Evento)
1.  Acesse a opção **9 (Encerrar Evento)**.
2.  Confirme a operação. Isso removerá a autorização de **todos** os veículos, garantindo que ninguém entre indevidamente no próximo evento sem nova autorização.

---

## 🔒 Regras de Negócio Implementadas

1.  **Integridade:** Não é possível cadastrar um veículo para um CPF inexistente.
2.  **Formatação:** O sistema aceita placas com ou sem traço (ex: `ABC-1234` ou `ABC1234`) e converte automaticamente.
3.  **Segurança:** Apenas existir no banco de dados não garante acesso. O veículo precisa ter a flag `autorizado = True`.
4.  **Histórico:** O registro de entrada/saída salva a data e hora exata do servidor.

---

## ✒️ Autor

Desenvolvido para fins de estudo em Arquitetura de Software e Python Orientado a Objetos.