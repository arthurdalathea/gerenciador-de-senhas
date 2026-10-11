import secrets
import hashlib
import time
import os
import json
import hmac
import sys


""" ALGUNS BUGS PARA CORRIGIR COMO A CHAVE DO HMAC E FALTA INPLEMENTAR A SENHA  """

""" FUNÇÕES DO PROGRAMA """
def aviso_tela ():
    limpar_buffer_teclado()
    print("=" * 70)
    print("⚠️  ATENÇÃO: Não altere ou delete a pasta cofre, onde suas senha serão\n" \
    "armazenadas. Caso qualquer modificação externa seja detectada, o cofre\n" \
    "será bloqueado e deletado permanentemente por segurança!")
    print("=" * 70)
    input("\nPressione ENTER para continuar...\n")
    
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
    # Abre o arquivo como leitor
    with open(caminhoArquivo, "r", encoding="utf-8") as arq:
        conteudo = arq.read()
        # Condição para verificar se o arquivo está vazio
        if not conteudo.strip():
            return {}
        # Retorna o JSON en forma de dicionário
        return json.loads(conteudo)

def escrever_json(caminhoArquivo: str, objeto: dict):
    # Abre o arquivo com permissão de escrita
    with open(caminhoArquivo, "w", encoding="utf-8") as arq:
        # Escreve o objeto no JSON
        json.dump(objeto, arq, indent=4, ensure_ascii=False)

def salvar_hmac(caminhoArquivo: str, hmac: str):
    # Abre o arquivo txt com permissão de escrita
    with open(caminhoArquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(hmac) 

def calcular_hmac(caminhoArquivo: str, chaveHMAC: bytes):
    # Abre o arquivo como leitor (em bytes)
    with open(caminhoArquivo, "rb") as arq:
        dados = arq.read()
    # Calcula o HMAC
    return hmac.new(chaveHMAC, dados, hashlib.sha256).hexdigest()

""" VARIÁVEIS CONSTANTES """
CAMINHO_DADOS_JSON = os.path.join("cofre", "dados.json")
CAMINHO_TIMER_JSON = os.path.join("cofre", "timer.json")
CAMINHO_HMAC_TXT = os.path.join("cofre", "hmac.txt")


""" PROGRAMA """
pastaExiste = os.path.exists("cofre")
arquivoExiste = os.path.exists(path=CAMINHO_DADOS_JSON)

# Verificação se o cofre existe
if pastaExiste and arquivoExiste:
    """ FLUXO DE LOGIN """
    aviso_tela()

    # Pegando o horario de bloqueio do usuário e o horário atual, para verificarmos se o usuário ainda está bloqueado
    dados = ler_json(caminhoArquivo=CAMINHO_TIMER_JSON)
    bloqueadoAte = dados["bloqueadoAte"]
    horarioAtual = int(time.time())
    tempoBloqueado = bloqueadoAte - horarioAtual # Se o resultado for positivo, esse é o tempo em segundos que o usuário está bloqueado

    if tempoBloqueado > 0:
        # Mostrar que o usuário ainda está bloqueado
        print(f"Você ainda está bloqueado por {tempoBloqueado} segundos!")
        for i in range(tempoBloqueado-1, -1, -1):
            time.sleep(1)
            if i == 0:
                print(f"\rRestam {i} segundos...    ")  # Não retirem esses espaços, faz parte do print
                print()
            else:
                print(f"\rRestam {i} segundos...    ", end="", flush=True) # Aqui também não retirem os espaços
        
        limpar_buffer_teclado()
    
    else:
        # """ FALTA FAZER ESSA PARTE DO FLUXO DE LOGIN """

        # Vai faltar a parte do controle de tentativas ainda
        # Algumas partes estão comentadas pois estão dando errando então comentei para não dar problemas.
        tentativas = ler_json(CAMINHO_TIMER_JSON)
        dados = ler_json(CAMINHO_DADOS_JSON)
        senhaM = input("Digite sua senha Mestra: ")
        tentativas["tentativasErradas"] += 1
        while hashlib.scrypt(password=senhaM, salt=dados["seguranca"]["saltCofre"], n=16384, r=8, p=1,dklen=32).hex() != dados["segurança"]["hashAutenticacao"].hex():
            senhaM = input("Digite a senha correta: ")
            tentativas["tentativasErradas"] += 1
            if tentativas["tentativasErradas"] % 5 == 0:
                print()
                print(f"ACESSO BLOQUEADO POR {tentativas*6} SEGUNDOS!")
                tentativas["bloqueadoAté"] += tentativas["tentativasErradas"]*6
                for i in range(tentativas*6-1, -1, -1):
                    time.sleep(1)
                    if i == 0:
                        print(f"\rRestam {i} segundos...      ")  # Não retirem esses espaços, faz parte do print
                        print()
                    else:
                        print(f"\rRestam {i} segundos...      ", end="", flush=True) # Aqui também não retirem os espaços
            else: 
                print("ACESSO NEGADO!")
                print()
                senhaM = input("Digite a senha correta: ")
                tentativas["tentativasErradas"] += 1
            limpar_buffer_teclado()


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
                    # hmacResultado = calcular_hmac(CAMINHO_DADOS_JSON, chaveHMAC)
                    salvar_hmac(CAMINHO_HMAC_TXT, hmacResultado)
                    escrever_json(CAMINHO_DADOS_JSON, cofre)
                    print("Senha Cadastrada com sucesso.\n")

                case "2":
                    # Listar cofre:
                    pass
                    cofre = ler_json(CAMINHO_DADOS_JSON)
                    if not cofre["servicos"]:
                        print("Nenhuma senha cadastrada o momento.\n")
                    else:
                        for appNome, dictApp in cofre["servicos"].items():
                            print("="*15)
                            print(f"Senhas do {appNome}")
                            print("="*15)
                            for usuario, senha in cofre["servicos"][dictApp].items():
                                print(f"{usuario} : {senha}")
                            print()
                        escrever_json(CAMINHO_DADOS_JSON, cofre)
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
                        while usuario not in cofre["servicos"]:
                            usuario = input("Digite um usuário válido")
                        # Decisão se o usuário realmente quer apagar a senha
                        escolha = input("Digite se você realmente quer apagar a senha (s/n): ").lower()
                        if escolha == "s":
                            del cofre["servicos"][app][usuario]
                            print("Usuário e senha deletados com sucesso.\n")
                        else:
                            print("Senha e usuário não foram deletados\n")
                        # hmacResultado = calcular_hmac(CAMINHO_DADOS_JSON, chaveHMAC)
                        salvar_hmac(hmacResultado)
                        escrever_json(CAMINHO_DADOS_JSON, cofre)
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
                    hmacResultado = calcular_hmac(CAMINHO_DADOS_JSON)
                    salvar_hmac(CAMINHO_HMAC_TXT, hmacResultado)
                    print("Senha alterada com sucesso.\n")
                case "5":
                    # Parar execução do programa: 
                    print("Programa encerrado.")
                    break


    
else:
    """ FLUXO DE CRIAÇÃO DO COFRE """
    # Criando a pasta cofre
    os.makedirs("cofre", exist_ok=True)

    aviso_tela()

    senhaMestra = input("Defina a sua Senha Mestra (Essa senha você utilizará para entrar no\n" \
    "gerenciador, ESCOLHA COM CUIDADO): ")
    print()
    
    # Geração dos 2 salts utilizando a biblioteca secrets
    saltCofre = secrets.token_bytes(16)
    saltHMAC = secrets.token_bytes(16)

    senhaMestra = senhaMestra.encode("utf-8")

    # Utilizando do algoritmo de kdf scrypt para gerar as chaves e o hash 
    chaveCofre = hashlib.scrypt(password=senhaMestra, salt=saltCofre, n=16384, r=8, p=1,dklen=32)
    chaveHMAC = hashlib.scrypt(password=senhaMestra, salt=saltHMAC, n=16384, r=8, p=1,dklen=32)
    hashAutenticacao = hashlib.sha256(string=chaveCofre).digest()

    # Criando os arquivos da pasta cofre
    arquivos = ["dados.json", "timer.json", "hmac.txt"]
    for arquivo in arquivos:
        caminho = os.path.join("cofre", arquivo)
        if not os.path.exists(caminho):
            with open(caminho, "w", encoding="utf-8") as arq:
                arq.write(caminho)
        else:
            pass
                
    # Criando a estrutura do dados.json
    if os.path.getsize(filename=CAMINHO_DADOS_JSON) == 0:
        estrutura = {
            "seguranca": {},
            "servicos": {}
        }

        escrever_json(caminhoArquivo=CAMINHO_DADOS_JSON, objeto=estrutura)

    # Enviando as informações necessárias para o dados.json
    seguranca = {
        "saltCofre": saltCofre.hex(),
        "saltHMAC": saltHMAC.hex(),
        "hashAutenticacao": hashAutenticacao.hex()
    }

    dados = ler_json(CAMINHO_DADOS_JSON)
    dados["seguranca"] = seguranca
    escrever_json(caminhoArquivo=CAMINHO_DADOS_JSON, objeto=dados)

    # Enviando as informações necessárias para o timer.json
    dados = ler_json(CAMINHO_TIMER_JSON)
    
    dados =  {
        "tentativasErradas": 0,
        "bloqueadoAte": 0,
        "multiplicadorBloqueio": 1
    }

    escrever_json(caminhoArquivo=CAMINHO_TIMER_JSON, objeto=dados)

    # Calculando o HMAC do dados.json
    assinatura = calcular_hmac(caminhoArquivo=CAMINHO_DADOS_JSON, chaveHMAC=chaveHMAC)

    # Salvando o HMAC no hmac.txt
    salvar_hmac(caminhoArquivo=CAMINHO_HMAC_TXT, hmac=assinatura)








""" MENU PRINCIPAL """
print("Carregando Menu Principal...")
time.sleep(2)

    
        

    


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
