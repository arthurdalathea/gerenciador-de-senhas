import secrets
import hashlib
import time
import os
import json
import hmac
import sys
import subprocess

""" VARIÁVEIS CONSTANTES """
CAMINHO_DADOS_JSON = os.path.join("cofre", "dados.json")
CAMINHO_TIMER_JSON = os.path.join("cofre", "timer.json")
CAMINHO_HMAC_TXT = os.path.join("cofre", "hmac.txt")

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
    print("[ERRO] Um arquivo obrigatório do cofre foi removido!\n")
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
    # Se o arquivo não existir
    if not os.path.exists(caminhoArquivo):
        mensagem_arquivo_removido()

    # Usamos um arquivo temporário para salvar os dados. Caso de um erro ao salvar os dados, o arquivo principal não é afetado
    caminhoTemporario = caminhoArquivo + ".tmp"

    try:
        with open(caminhoTemporario, "w", encoding="utf-8") as arq:
            json.dump(objeto, arq, indent=4, ensure_ascii=False)

        os.replace(caminhoTemporario, caminhoArquivo)

    except (OSError, TypeError, ValueError) as erro:
        print(f"[ERRO] Não foi possível salvar os dados: {erro}")

        if os.path.exists(caminhoTemporario):
            os.remove(caminhoTemporario)

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

# Essas funções embaixo servem para validar os dados dos arquivos antes da execução do programa
def validar_dados_json(dados: dict):
    # Armazenará todos os erros que derem no arquivo, para serem printados depois
    erros = []

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


""" PROGRAMA """
limpar_terminal()

pastaExiste = os.path.isdir("cofre")
arquivosExistem = all([
    os.path.isfile(CAMINHO_DADOS_JSON),
    os.path.isfile(CAMINHO_TIMER_JSON),
    os.path.isfile(CAMINHO_HMAC_TXT)
])

# Verificação se o cofre existe
if pastaExiste:
    # Se todos os arquivos existirem, iremos para o fluxo de login. Caso contrario, será exibido um aviso e o programa encerrado
    if arquivosExistem:
        """ FLUXO DE LOGIN """
        aviso_tela()

        timer = ler_json(CAMINHO_TIMER_JSON)
        dados = ler_json(CAMINHO_DADOS_JSON)
        hmacTxt = ler_txt(CAMINHO_HMAC_TXT)

        validar_arquivos(dados, timer, hmacTxt)

        # Pegando o horario de bloqueio do usuário e o horário atual, para verificarmos se o usuário ainda está bloqueado
        bloqueadoAte = timer["bloqueadoAte"]
        horarioAtual = int(time.time())
        tempoBloqueado = bloqueadoAte - horarioAtual # Se o resultado for positivo, esse é o tempo em segundos que o usuário está bloqueado

        if tempoBloqueado > 0:
            # Mostrar que o usuário ainda está bloqueado
            print(f"VOCÊ AINDA ESTÁ BLOQUEADO POR {tempoBloqueado} SEGUNDOS!")
            for i in range(tempoBloqueado - 1, -1, -1):
                time.sleep(1)
                if i == 0:
                    print(f"\rRestam {i} segundos...    ")  # Não retirem esses espaços, faz parte do print
                    print()
                else:
                    print(f"\rRestam {i} segundos...    ", end="", flush=True) # Aqui também não retirem os espaços
            limpar_buffer_teclado()
            limpar_terminal()
        
        # Seguindo o fluxo de login
        saltCofre = dados["seguranca"]["saltCofre"]
        saltCofreBytes = bytes.fromhex(saltCofre)
        senhaMestra = input("Digite sua senha Mestra: ").encode("utf-8")
        print()
        chaveCofre = hashlib.scrypt(password=senhaMestra, salt=saltCofreBytes, n=16384, r=8, p=1,dklen=32)
        hashAutenticacao = hashlib.sha256(chaveCofre).hexdigest()

        # Enquanto a senha do usuário não estiver correta
        while hashAutenticacao != dados["seguranca"]["hashAutenticacao"]:
            # Contando uma tentativa errada e armazenando no timer.json
            timer["tentativasErradas"] += 1
            escrever_json(CAMINHO_TIMER_JSON, objeto=timer)
            
            # Verificando se o usuário errou a senha 5 vezes seguidas
            if timer["tentativasErradas"] % 5 == 0:
                penalidade = 30 * timer["multiplicadorBloqueio"]
                # Recalculando as variáveis e enviando para o timer.json
                timer["multiplicadorBloqueio"] *= 2
                timer["bloqueadoAte"] = penalidade + int(time.time())
                
                escrever_json(CAMINHO_TIMER_JSON, timer)

                # Aplicando o loop de bloqueio ao usuário
                print(f"ACESSO BLOQUEADO POR {penalidade} SEGUNDOS!")
                for i in range(penalidade - 1, -1, -1):
                    time.sleep(1)
                    if i == 0:
                        print(f"\rRestam {i} segundos...      ")  # Não retirem esses espaços, faz parte do print
                        print()
                    else:
                        print(f"\rRestam {i} segundos...      ", end="", flush=True) # Aqui também não retirem os espaços
                limpar_buffer_teclado()
                limpar_terminal()
            else: 
                print("ACESSO NEGADO!")
                print()
            
            senhaMestra = input("Digite a senha correta: ").encode("utf-8")
            print()
            
            # Calculando novo hash
            chaveCofre = hashlib.scrypt(password=senhaMestra, salt=saltCofreBytes, n=16384, r=8, p=1,dklen=32)
            hashAutenticacao = hashlib.sha256(chaveCofre).hexdigest()

        # Senha validada, calculando o hmac do dados.json para ver se não houve alterações externas
        saltHMAC = dados["seguranca"]["saltHMAC"]
        saltHMACBytes = bytes.fromhex(saltHMAC)
        chaveHMAC = hashlib.scrypt(password=senhaMestra, salt=saltHMACBytes, n=16384, r=8, p=1,dklen=32)
        
        hmacDados = calcular_hmac(CAMINHO_DADOS_JSON, chaveHMAC)

        # Verificando se o hmac do dados.json é o mesmo do hmac.txt
        if hmac.compare_digest(hmacDados, hmacTxt):
            # Cada atributo do timer irá resetar e o timer será atualizado no json
            timer["tentativasErradas"] = 0
            timer["bloqueadoAte"] = 0
            timer["multiplicadorBloqueio"] = 1
            escrever_json(CAMINHO_TIMER_JSON, timer)
        else:
            print("[ERRO] Alteração externa detectada no JSON!\n")
            print("Por motivos de segurança, o acesso ao cofre será bloqueado!\n")
            time.sleep(2)
            print("Encerrando o programa...")
            time.sleep(2)
            sys.exit()
    else:
        aviso_tela()
        mensagem_arquivo_removido()
else:
    """ FLUXO DE CRIAÇÃO DO COFRE """
    # Criando a pasta cofre
    os.makedirs("cofre", exist_ok=True)

    aviso_tela()

    senhaMestra = input("Defina a sua Senha Mestra (Essa senha você utilizará para entrar no\n" \
    "gerenciador, ESCOLHA COM CUIDADO): ").encode("utf-8")
    print()
    
    # Geração dos 2 salts utilizando a biblioteca secrets
    saltCofre = secrets.token_bytes(16)
    saltHMAC = secrets.token_bytes(16)

    # Utilizando do algoritmo de kdf scrypt para gerar as chaves e o hash 
    chaveCofre = hashlib.scrypt(password=senhaMestra, salt=saltCofre, n=16384, r=8, p=1,dklen=32)
    chaveHMAC = hashlib.scrypt(password=senhaMestra, salt=saltHMAC, n=16384, r=8, p=1,dklen=32)
    hashAutenticacao = hashlib.sha256(chaveCofre).hexdigest()

    # Criando os arquivos da pasta cofre
    arquivos = ["dados.json", "timer.json", "hmac.txt"]
    
    try:
        for arquivo in arquivos:
            caminho = os.path.join("cofre", arquivo)
            if not os.path.exists(caminho):
                with open(caminho, "w", encoding="utf-8") as arq:
                    pass
    except FileNotFoundError:
        print("[ERRO] A pasta do cofre foi removida durante o cadastro!")
        print()
        time.sleep(2)
        print("Encerrando o programa...")
        sys.exit()
                
    # Criando a estrutura do dados.json
    if os.path.getsize(CAMINHO_DADOS_JSON) == 0:
        estrutura = {
            "seguranca": {},
            "servicos": {}
        }

        escrever_json(caminhoArquivo=CAMINHO_DADOS_JSON, objeto=estrutura)

    # Enviando as informações necessárias para o dados.json
    seguranca = {
        "saltCofre": saltCofre.hex(),
        "saltHMAC": saltHMAC.hex(),
        "hashAutenticacao": hashAutenticacao
    }

    dados = ler_json(CAMINHO_DADOS_JSON)
    dados["seguranca"] = seguranca
    escrever_json(caminhoArquivo=CAMINHO_DADOS_JSON, objeto=dados)

    # Enviando as informações necessárias para o timer.json    
    timer =  {
        "tentativasErradas": 0,
        "bloqueadoAte": 0,
        "multiplicadorBloqueio": 1
    }

    escrever_json(caminhoArquivo=CAMINHO_TIMER_JSON, objeto=timer)

    # Calculando o HMAC do dados.json
    hmacDados = calcular_hmac(caminhoArquivo=CAMINHO_DADOS_JSON, chaveHMAC=chaveHMAC)

    # Salvando o HMAC no hmac.txt
    salvar_hmac(caminhoArquivo=CAMINHO_HMAC_TXT, hmac=hmacDados)

    hmacTxt = ler_txt(CAMINHO_HMAC_TXT)

""" MENU PRINCIPAL """
print("Carregando Menu Principal...")
print()
time.sleep(2)

while True:
    limpar_terminal()

    largura = 70
    print("=" * largura)
    print("GERENCIADOR DE SENHAS".center(largura))
    print("=" * largura)
    print()
    print("  [1]  Cadastrar nova senha")
    print("  [2]  Listar senhas cadastradas")
    print("  [3]  Excluir senha cadastrada")
    print("  [4]  Alterar senha cadastrada")
    print("  [5]  Sair")
    print()
    print("=" * largura)

    acao = input("Digite qual ação você deseja (1-5): ")
    print()

    while acao not in ["1","2","3","4","5"]:
        acao = input("[ERRO] Digite uma opção válida (1-5): ")
        print()

    limpar_terminal()

    match acao:
        case "1":
            # Cadastrar serviço:
            print("=" * largura)
            print("CADASTRAR SENHA".center(largura))
            print("=" * largura)
            print()

            servico = input("Nome do aplicativo ou serviço: ").lower().strip()
            print()
            
            if servico in dados["servicos"]:
                print("[ERRO] Esse serviço já está cadastrado!\n")
            else:
                usuario = input(f"Usuário ou e-mail de acesso do {servico}: ")
                print()
                senha = input(f"Senha de acesso do {servico}: ")
                print()

                if not usuario or not senha:
                    print("[ERRO] O usuário e a senha não podem ficar vazios!\n")
                else:
                    # Precisamos implementar as funções de criptografia dos dados
                    dados["servicos"][servico] = {
                        "usuario": usuario,
                        "senha": senha
                    }
                    escrever_json(CAMINHO_DADOS_JSON, dados)
                    
                    hmacDados = calcular_hmac(CAMINHO_DADOS_JSON, chaveHMAC)
                    salvar_hmac(CAMINHO_HMAC_TXT, hmacDados)

                    print("Serviço cadastrado com sucesso!\n")
            
            print("=" * largura)
            aguardar_enter()
       
        case "2":
            # Listar serviços:
            print("=" * largura)
            print("LISTAR SENHAS".center(largura))
            print("=" * largura)
            print()
            
            if not dados["servicos"]:
                print("[ERRO] Nenhuma senha foi cadastrada.\n")
            else:
                for indice, (appNome, appDados) in enumerate(sorted(dados["servicos"].items()), start=1):
                    print(f"[ {indice} ] {appNome.title()}")
                    print("-" * 45)
                    print(f"      Usuário : {appDados['usuario']}")
                    print(f"      Senha   : {appDados['senha']}")
                    print()
            
            print("=" * largura)
            aguardar_enter()
        
        case "3":
            # Excluir serviço:
            print("=" * largura)
            print("EXCLUIR SENHA".center(largura))
            print("=" * largura)
            print()
            
            if not dados["servicos"]:
                print("[ERRO] Nenhuma senha foi cadastrada.\n")
            else:
                servico = input("Digite o serviço que deseja remover: ").lower().strip()
                print()
                
                if servico not in dados["servicos"]:
                    print("[ERRO] Não foi encontrado nenhum serviço com esse nome!\n")
                else:
                    escolha = input(f"Você realmente deseja remover {servico} (S/N)? ").lower().strip()
                    print()
                
                    while escolha not in ["s", "n"]:
                        escolha = input("[ERRO] Digite uma ação válida (S/N): ").lower().strip()
                        print()

                    if escolha == "s":
                        del dados["servicos"][servico]
                        escrever_json(CAMINHO_DADOS_JSON, dados)
                                        
                        hmacDados = calcular_hmac(CAMINHO_DADOS_JSON, chaveHMAC)
                        salvar_hmac(CAMINHO_HMAC_TXT, hmacDados)
                        
                        print(f"Usuário e senha de {servico} deletados com sucesso!\n")
                    else:
                        print("Remoção cancelada!\n")

            print("=" * largura)
            aguardar_enter()

        case "4":
            # Alterar Serviço
            print("=" * largura)
            print("ALTERAR SENHA".center(largura))
            print("=" * largura)
            print()
            
            if not dados["servicos"]:
                print("[ERRO] Nenhuma senha foi cadastrada!\n")
            else:
                servico = input("Digite o serviço que será alterado: ").lower().strip()
                print()
                
                if servico not in dados["servicos"]:
                    print("[ERRO] Não foi encontrado nenhum serviço com esse nome!\n")
                else:
                    usuario = input(f"Novo usuário ou email de acesso do {servico}: ")
                    print()
                    senha = input(f"Nova senha de acesso do {servico}: ")
                    print()

                    if not usuario or not senha:
                        print("[ERRO] O usuário e a senha não podem ficar vazios!\n")
                    else:
                        # Precisamos implementar as funções de criptografia dos dados
                        dados["servicos"][servico] = {
                            "usuario": usuario,
                            "senha": senha
                        }
                        escrever_json(CAMINHO_DADOS_JSON, dados)
                        
                        hmacDados = calcular_hmac(CAMINHO_DADOS_JSON, chaveHMAC)
                        salvar_hmac(CAMINHO_HMAC_TXT, hmacDados)
        
                        print("Serviço alterado com sucesso!\n")

            print("=" * largura)
            aguardar_enter()

        case "5":
            # Parar execução do programa: 
            print("\nENCERRANDO O PROGRAMA...")
            time.sleep(2)
            break