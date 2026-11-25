# 🔐 Gerenciador de Senhas

### Gerenciamento seguro de credenciais utilizando mecanismos criptográficos

## Sobre o projeto

Este projeto consiste no desenvolvimento de um gerenciador de senhas em Python, executado pelo terminal, que permite cadastrar, consultar, alterar e excluir credenciais de diferentes serviços.

O programa utiliza mecanismos criptográficos para proteger as informações armazenadas localmente, buscando preservar a confidencialidade e a integridade dos dados.

## Funcionalidades

- Cadastro de novas credenciais.
- Consulta das credenciais cadastradas.
- Alteração e exclusão de credenciais.
- Criptografia e descriptografia dos dados armazenados.
- Autenticação por meio de uma senha mestra.
- Bloqueio temporário após tentativas incorretas de autenticação.
- Verificação da integridade dos dados armazenados.
- Armazenamento local das informações.

## Tecnologias e mecanismos utilizados

- **Python:** linguagem de programação utilizada no desenvolvimento do projeto.
- **PyCryptodome:** biblioteca utilizada na implementação dos mecanismos criptográficos.
- **AES-256-CBC:** algoritmo de criptografia simétrica utilizado para proteger as credenciais.
- **Scrypt:** função de derivação de chaves utilizada na geração de chaves criptográficas a partir da senha mestra.
- **HMAC-SHA256:** mecanismo utilizado para verificar a integridade e autenticidade dos dados armazenados.
- **JSON:** formato utilizado para organizar e armazenar as informações do programa.

## ▶️ Como executar o programa

Para executar o gerenciador de senhas, é necessário ter o **Python** instalado e a biblioteca **PyCryptodome**.

**1. Clone o repositório:**

```bash
git clone https://github.com/arthurdalathea/gerenciador-de-senhas.git
```

**2. Acesse a pasta do projeto:**

```bash
cd gerenciador-de-senhas
```

**3. Instale a biblioteca PyCryptodome:**

```bash
pip install pycryptodome
```

**4. Execute o programa:**

```bash
python main.py
```

Na primeira execução, o programa solicitará a criação de uma senha mestra e criará automaticamente uma pasta chamada `cofre`, contendo três arquivos responsáveis pelo armazenamento e pela segurança das informações:

- **`dados.json`:** armazena as informações de segurança e as credenciais criptografadas.
- **`timer.json`:** armazena os dados referentes às tentativas incorretas de autenticação e aos bloqueios temporários.
- **`hmac.txt`:** armazena o código HMAC utilizado na verificação da integridade dos dados.

Nas execuções seguintes, o programa utilizará esses arquivos para recuperar as informações e realizar os procedimentos de autenticação e verificação de integridade.

## Objetivo

O projeto tem como objetivo estudar os impactos dos avanços da computação quântica sobre os mecanismos criptográficos utilizados atualmente, relacionando a pesquisa teórica ao desenvolvimento de uma aplicação prática.

Por meio da construção do gerenciador de senhas, buscamos aplicar conceitos de segurança da informação e compreender a importância da utilização de mecanismos criptográficos na proteção de dados.

## Pesquisa teórica

Como parte do projeto, foi desenvolvido um artigo científico intitulado **"O Impacto dos Computadores Quânticos na Segurança da Internet"**.

O artigo aborda os fundamentos da criptografia, os impactos dos algoritmos quânticos de Shor e Grover sobre os mecanismos criptográficos atuais e as possibilidades oferecidas pela criptografia pós-quântica, com destaque para os algoritmos baseados em reticulados.

A pesquisa serviu como fundamentação teórica para o desenvolvimento prático do gerenciador de senhas.

**[📄 Acessar o artigo completo (PDF)](documentacao/artigo.pdf)**