import secrets
import hashlib
import time
import os
import json
import hmac
import sys

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
    input("\nPressione ENTER para continuar...")
    print()

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


""" MENU PRINCIPAL """
print("Carregando Menu Principal...")
print()
time.sleep(2)

print("="*30)
print("      PAINEL DE AÇÕES")
print("="*30)
print(" 1 - Cadastrar nova senha")
print(" 2 - Listar senha")
print(" 3 - Excluir senha")
print(" 4 - Alterar senha")
print(" 5 - Sair")
print("="*30)
while True:
    acao = input("Digite qual ação você deseja: ")
    while acao not in ["1","2","3","4","5"]:
        acao = input("DIgite uma opção válida: ")
    match acao:
        case "1":
            # Cadastrar senha:
            pass
            cofre = ler_json(CAMINHO_DADOS_JSON)
            app = input("Digite qual aplicativo pertence").lower()
            if app not in cofre["servicos"]:
                cofre["servicos"][app] = {}
            usuario = input(f"Digite seu usuário do {app} : ")
            senha = input(f"Digite a senha do usuário {usuario} : ")
            cofre["servicos"][app][usuario] = senha
            escrever_json(CAMINHO_HMAC_TXT, cofre)
            hmacResultado = calcular_hmac(CAMINHO_DADOS_JSON, senhaMestra.encode("utf-8"))
            salvar_hmac(CAMINHO_HMAC_TXT, hmacResultado)
            print("Senha Cadastrada com sucesso.\n")

        case "2":
            # Listar cofre:
            pass
            cofre = ler_json(CAMINHO_DADOS_JSON)
            if not cofre["servicos"]:
                print("Nenhuma senha cadastrada o momento.\n")
            else:
                for appNome, App in cofre["servicos"].items():
                    print("="*15)
                    print(f"Senhas do {appNome}")
                    print("="*15)
                    for usuario, senha in App.items():
                        print(f"{usuario} : {senha}")
                    print()
                escrever_json(CAMINHO_DADOS_JSON, senhaMestra.encode("utf-8"))
        case "3":
            # Excluir cofre:
            pass
            cofre = ler_json(CAMINHO_DADOS_JSON)
            if not cofre["servicos"]:
                print("Nenhuma senha cadastrada no momento.\n")
            else:
                app = input("Digite de qual app pertence a senha: ").lower()
                while app not in cofre["servicos"]:
                    app = input("Digite um app válido: ").lower()
                usuario = input("Digite o usuário que você deseja excluir: ")
                while usuario not in cofre["servicos"][app]:
                    usuario = input("Digite um usuário válido")
                # Decisão se o usuário realmente quer apagar a senha
                escolha = input("Digite se você realmente quer apagar a senha (s/n): ").lower()
                if escolha == "s":
                    del cofre["servicos"][app][usuario]
                    print("Usuário e senha deletados com sucesso.\n")
                else:
                    print("Senha e usuário não foram deletados\n")
                escrever_json(CAMINHO_DADOS_JSON, cofre)
                hmacResultado = calcular_hmac(CAMINHO_DADOS_JSON, senhaMestra.encode("utf-8"))
                salvar_hmac(CAMINHO_HMAC_TXT,hmacResultado)
        case "4":
            # Alterar senha:
            pass
            cofre = ler_json(CAMINHO_DADOS_JSON)
            if not cofre["servicos"]:
                print("Nenhuma senha cadastrada no momento.")
            else:
                app = input("Digite de qual app pertence a senha: ").lower()
                while app not in cofre["servicos"]:
                    app = input("Digite um app válido: ").lower()
                usuario = input("Digite qual usuário você quer trocar: ")
                while usuario not in cofre["servicos"]:
                    usuario = input("Digite um usuario válido: ")
                novoUsuario = input("Digite o novo nome de usuario: ")
                while novoUsuario == usuario:
                    novoUsuario = input("Digite um novo usuário diferente do anterior: ")
                senhaNova = input("Digite a nova senha: ")
                while senhaNova == cofre["servico"][app][usuario]:
                    senhaNova = input("Digite uma senha diferente da anterior: ")
                del cofre["servicos"][app][usuario]
                cofre["servicos"][app][novoUsuario] = senhaNova
            escrever_json(CAMINHO_DADOS_JSON, cofre)
            hmacResultado = calcular_hmac(CAMINHO_DADOS_JSON, senhaMestra.encode("utf-8"))
            salvar_hmac(CAMINHO_HMAC_TXT, hmacResultado)
            print("Senha alterada com sucesso.\n")
        case "5":
            # Parar execução do programa: 
            print("Programa encerrado.")
            break

    
        

    


""" ESSE É O CÓDIGO BASE, SERÁ USADO COMO INFLUENCIA PARA A CONSTRUÇÃO DO GERENCIADOR """

# senhaM = "12345"
# tentativas = 0
# def limpar_buffer_teclado():
#     """Limpa a fila de teclas digitadas, funcionando em Windows, Linux e Mac."""
#     import os

#     if os.name == 'nt':  # Se for Windows
#         import msvcrt
#         while msvcrt.kbhit(): # comandos para limpar os dados de entrada do terminal
#             msvcrt.getch()  
#     else:  # Se for Linux ou Mac (Unix)
#         import termios
#         termios.tcflush(sys.stdin, termios.TCIFLUSH) # comando para limpar os dados de entrada do terminal

# print("======= Gerenciador de Senhas ========")
# senhaMestra = input("Digite sua senha mestra: ")
# tentativas += 1

# while senhaMestra != senhaM:

#     if tentativas % 5 == 0:
#         print()
#         print(f"ACESSO BLOQUEADO POR {tentativas*6} SEGUNDOS!")
#         for i in range(tentativas*6-1, -1, -1):
#             time.sleep(1)
#             if i == 0:
#                 print(f"\rRestam {i} segundos...      ")  # Não retirem esses espaços, faz parte do print
#                 print()
#             else:
#                 print(f"\rRestam {i} segundos...      ", end="", flush=True) # Aqui também não retirem os espaços
#     else: 
#         print("ACESSO NEGADO!")
#         print()

#     limpar_buffer_teclado()

#     senhaMestra = input("Digite a senha correta: ")
#     tentativas += 1
# print("\nACESSO LIBERADO!\n")

# while True:
#     print("="*30)
#     print("      PAINEL DE AÇÕES")
#     print("="*30)
#     print(" 1 - Cadastrar nova senha")
#     print(" 2 - Listar cofre")
#     print(" 3 - Excluir senha")
#     print(" 4 - Alterar senha")
#     print(" 5 - Sair")
#     print("="*30)
#     # Estrutura que impede a entrada de uma ação inválida ou de formato errado
#     while True:
#         try:
#             ação = int(input("Digite qual ação deseja (1-5): "))
#             while ação > 5 or ação < 1:
#                 ação = int(input("Digite uma ação válida (1-5): "))
#             break
#         except ValueError:
#             print("Digite um número no formato correto (1-5): ")
#     # Estrutura de decisão match, equivalente ao switch em Java
#     match ação:
#         case 1:
#             app = input("Diga qual aplicativo pertence a senha: ").lower() # Função lower() : transforma todos os caracteres de uma String em minúsculo
#             usuario = input("Digite qual o nome do usuario: ") 
#             senha = input(f"Digite sua senha do {app}: ")
#             with open("Dados.json", "r", encoding="utf-8") as arquivo:
#                 cofre = json.load(arquivo)
#             if app not in cofre:
#                 cofre[app] = {}
#                 cofre[app][usuario] = senha
#             else:
#                 cofre[app][usuario] = senha
#             with open("Dados.json", "w", encoding="utf-8") as arquivo:
#                 json.dump(cofre, arquivo, indent=4, ensure_ascii= False)
#             print("Senha cadatrada com sucesso")
#         case 2:
#             with open("Dados.json", "r", encoding="utf-8") as arquivo:
#                 cofre = json.load(arquivo)
#             if not cofre:
#                 print("Nenhuma senha cadastrada.\n")
#             else:
#                 with open("Dados.json", "r", encoding="utf-8") as arquivo:
#                     cofre = json.load(arquivo)
#                 for app, usuarios in cofre.items():
#                     print(f"Senhas {app} :")
#                     for usuario, Senhas in usuarios.items():
#                         print(f"Usuario : {usuario}")
#                         print(f"Senha : {Senhas}\n")
#         case 3:
#             # Validação se dicionário Senhas não está Vazio
#             with open("Dados.json", "r", encoding="utf-8") as arquivo:
#                 cofre = json.load(arquivo)
#             if not cofre:
#                 print("Nenhuma senha cadastrada então não há cofre para excluir\n")
#             else:
#                 app = input("Digite de qual aplicativo você deseja deletar sua senha: ").lower()
#                 while app not in cofre:
#                     app = input("Digite um aplicativo presente : ").lower()
#                 usuario = input("Digite o nome do usuário: ")
#                 while usuario not in cofre[app]:
#                     usuario = input(f"Digite um usuario presente em {app} : ")
#                 escolha = input("Você realmente quer apagar a senha: s/n").lower()
#                 if escolha != "s":
#                     print("Senha não foi deletada.\n")
#                 else:
#                     del cofre[app][usuario]
#                     print("Senha excluída com sucesso.")
#             with open("Dados.json", "w", encoding="utf-8") as arquivo:
#                 json.dump(cofre, arquivo, indent=4, ensure_ascii=False)
#         case 4:
#             # Validação se o dicionário Senhas não está Vazio
#             with open("Dados.json", "r", encoding="utf-8") as arquivo:
#                 cofre = json.load(arquivo)
#             if not cofre:
#                 print("Nenhuma senha está cadastrada no momento.")
#             else:
#                 app = input("Digite de qual aplicativo é a senha que deseja alterar: ").lower()
#                 while app not in cofre:
#                     app = input("Digite um aplicativo válido: ").lower()
#                 usuario = input("Digite o usuário: ")
#                 while usuario not in cofre[app]:
#                     usuario = input("Digite um usuário válido: ")
#                 senhaNova = input(f"Digite a nova senha : ")
#                 while senhaNova == cofre[app][usuario]:
#                     senhaNova = input("Digite a nova senha diferente da anterior : ")
#                 cofre[app][usuario] = senhaNova
#                 print("Senha alterada com sucesso\n")    
#             with open("Dados.json", "w", encoding="utf-8") as arquivo:
#                 json.dump(cofre, arquivo, indent=4, ensure_ascii=False)        
#         case 5:
#             print("Programa encerrado.")
#             break
