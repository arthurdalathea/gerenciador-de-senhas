import hashlib
import time
import os
import json
import hmac
import sys
import subprocess

""" FUNÇÕES DO PROGRAMA """

def aviso_tela():
    limpar_buffer_teclado()
    print("=" * 70)
    print("⚠️  ATENÇÃO: Não altere ou delete a pasta cofre, onde suas senhas serão\n" \
    "armazenadas. Caso qualquer modificação externa seja detectada, o cofre\n" \
    "será bloqueado e deletado permanentemente por segurança!")
    print("=" * 70)
    print()
    aguardar_enter()
    limpar_terminal()

def mensagem_arquivo_removido():
    print("[ERRO] Um ou mais arquivos do cofre foram removidos!\n")
    print("Por motivos de segurança, o acesso ao cofre será bloqueado!\n")
    time.sleep(2)
    print("Encerrando o programa...")
    time.sleep(2)
    sys.exit()

def limpar_buffer_teclado():
    """Limpa os inputs digitados pelo usuário, funcionando em Windows, Linux e Mac."""
    if os.name == 'nt':  # Se for Windows
        import msvcrt
        while msvcrt.kbhit(): # comandos para limpar os dados de entrada do terminal
            msvcrt.getch()  
    else:  # Se for Linux ou Mac (Unix)
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH) # comando para limpar os dados de entrada do terminal

def ler_json(caminhoArquivo: str):
    try:
        with open(caminhoArquivo, "r", encoding="utf-8") as arq:
            return json.load(arq)

    except FileNotFoundError:
        mensagem_arquivo_removido()

    except json.JSONDecodeError:
        print("[ERRO] Um arquivo JSON do cofre está inválido!\n")
        print("Por motivos de segurança, o acesso ao cofre será bloqueado.\n")
        time.sleep(2)
        print("Encerrando o programa...")
        time.sleep(2)
        sys.exit()
        
def escrever_json(caminhoArquivo: str, objeto: dict):
    if not os.path.exists(caminhoArquivo):
        mensagem_arquivo_removido()

    # Abre o arquivo com permissão de escrita
    with open(caminhoArquivo, "w", encoding="utf-8") as arq:
        # Escreve o objeto no json
        json.dump(objeto, arq, indent=4, ensure_ascii=False)

def ler_txt(caminhoArquivo: str):
    try:
        # Abre o arquivo como leitor
        with open(caminhoArquivo, "r", encoding="utf-8") as arq:
            return arq.read()

    except FileNotFoundError:
        mensagem_arquivo_removido()

    except UnicodeDecodeError:
        print("[ERRO] O conteúdo de um arquivo do cofre está inválido.\n")
        print("Por motivos de segurança, o acesso ao cofre será bloqueado.\n")
        time.sleep(2)
        print("Encerrando o programa...")
        time.sleep(2)
        sys.exit()

def salvar_hmac(caminhoArquivo: str, hmac: str):
    if not os.path.exists(caminhoArquivo):
        mensagem_arquivo_removido()

    with open(caminhoArquivo, "w", encoding="utf-8") as arq:
        arq.write(hmac)

def calcular_hmac(caminhoArquivo: str, chaveHMAC: bytes):
    try:
        with open(caminhoArquivo, "rb") as arq:
            dados = arq.read()

    except FileNotFoundError:
        mensagem_arquivo_removido()

    return hmac.new(chaveHMAC, dados, hashlib.sha256).hexdigest()

def limpar_terminal():
    if os.name == "nt":
        subprocess.run("cls", shell=True, check=False)
    else:
        subprocess.run("clear", shell=True, check=False)

def aguardar_enter():
    print("Pressione ENTER para continuar...")

    if os.name == "nt":  
        import msvcrt
        while True:
            tecla = msvcrt.getwch()
            if tecla == "\r":
                break
    else:  
        import termios
        import tty

        fd = sys.stdin.fileno()
        configuracao_anterior = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                tecla = sys.stdin.read(1)
                if tecla in ("\r", "\n"):
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, configuracao_anterior)

def validar_senha(senha: str): 
    erros = []

    # Verificando se a senha contém no mínimo 10 caracteres
    if len(senha) < 10:
        erros.append("Sua senha precisa conter 10 caracteres no mínimo.")
    # Verificando se a senha possui pelo menos uma letra maiuscula
    temMaiuscula = any(char.isupper() for char in senha)
    if not temMaiuscula:
        erros.append("Sua senha precisa conter ao menos uma letra maiúscula.")
    # Verificando se a senha possui pelo menos uma letra minuscula
    temMinuscula = any(char.islower() for char in senha)
    if not temMinuscula:
        erros.append("Sua senha precisa conter ao menos uma letra minúscula.")
    # Verificando se a senha possui pelo menos um número
    temNumero = any(char.isdigit() for char in senha)
    if not temNumero:
        erros.append("Sua senha precisa conter ao menos um número.")

    return erros

# Essas funções embaixo servem para validar os dados dos arquivos antes da execução do programa
def validar_dados_json(dados: dict):
    # Armazenará todos os erros que derem no arquivo, para serem printados depois
    erros = []

    # Verificando se o arquivo é um dicionário
    if not isinstance(dados, dict):
        erros.append("O conteúdo do dados.json está inválido.")
        return erros

    # Verificando se o arquivo possui a chave "seguranca" e "servicos" e se elas são um dicionário
    if not isinstance(dados.get("seguranca"), dict):
        erros.append("Os dados de segurança estão inválidos.")

    if not isinstance(dados.get("servicos"), dict):
        erros.append("A estrutura dos serviços está inválida.")

    # Verificando os campos internos de "seguranca"
    if isinstance(dados.get("seguranca"), dict):
        seguranca = dados["seguranca"]

        campos_seguranca = {
            "saltCofre": 16,
            "saltHMAC": 16,
            "hashAutenticacao": 32
        }

        for campo, tamanhoEsperado in campos_seguranca.items():
            valor = seguranca.get(campo)

            if not isinstance(valor, str):
                erros.append(f"O campo '{campo}' está ausente ou inválido.")
                continue

            try:
                valorHex = bytes.fromhex(valor)

                if len(valorHex) != tamanhoEsperado:
                    erros.append(f"O campo '{campo}' possui um tamanho inválido.")

            except ValueError:
                erros.append(f"O campo '{campo}' possui um formato inválido.")
    
    # Verificando os campos internos de "servicos"
    if isinstance(dados.get("servicos"), dict):
        servicos = dados["servicos"]

        for aplicativo, informacoes in servicos.items():

            if not isinstance(informacoes, dict):
                erros.append(f"As informações do serviço '{aplicativo}' estão inválidas.")
                continue

            for campo in ("usuario", "senha"):
                valor = informacoes.get(campo)

                if not isinstance(valor, str):
                    erros.append(f"O campo '{campo}' do serviço '{aplicativo}' está ausente ou inválido.")

    return erros

def validar_timer_json(timer: dict):
    erros = []

    if not isinstance(timer, dict):
        erros.append("Os dados do temporizador estão inválidos.")
        return erros

    campos = {
        "tentativasErradas": int,
        "bloqueadoAte": int,
        "multiplicadorBloqueio": int
    }

    for campo, tipoEsperado in campos.items():
        valor = timer.get(campo)

        if type(valor) != tipoEsperado:
            erros.append(f"O campo '{campo}' está ausente ou possui um tipo inválido.")
            continue

        if campo in ("tentativasErradas", "bloqueadoAte") and valor < 0:
            erros.append(f"O campo '{campo}' possui um valor inválido.")

        if campo == "multiplicadorBloqueio" and valor < 1:
            erros.append("O campo 'multiplicadorBloqueio' possui um valor inválido.")

    return erros

def validar_hmac_txt(assinatura: str):
    erros = []

    if not isinstance(assinatura, str):
        erros.append("O conteúdo do arquivo HMAC está inválido.")
        return erros

    assinatura = assinatura.strip()

    if len(assinatura) != 64:
        erros.append("A assinatura HMAC possui um tamanho inválido.")
        return erros

    try:
        bytes.fromhex(assinatura)
    except ValueError:
        erros.append("A assinatura HMAC possui um formato inválido.")

    return erros

def validar_arquivos(dados, timer, assinatura):
    erros = []

    erros.extend(validar_dados_json(dados))
    erros.extend(validar_timer_json(timer))
    erros.extend(validar_hmac_txt(assinatura))

    if erros:
        print("[ERRO] Foram encontrados os seguintes problemas nos arquivos do cofre:\n")

        for erro in erros:
            print(f"- {erro}")

        print("\nPor motivos de segurança, o acesso ao cofre será bloqueado!")
        time.sleep(2)
        print()
        print("Encerrando o programa...")
        time.sleep(2)
        sys.exit()