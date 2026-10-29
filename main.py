import secrets
import hashlib
import time
import os
import hmac
import sys
from funcoes import *

""" VARIÁVEIS CONSTANTES """
CAMINHO_DADOS_JSON = os.path.join("cofre", "dados.json")
CAMINHO_TIMER_JSON = os.path.join("cofre", "timer.json")
CAMINHO_HMAC_TXT = os.path.join("cofre", "hmac.txt")

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

    senhaMestra = input(
    "Defina sua Senha Mestra. Ela será utilizada para ACESSAR o gerenciador.\n"
    "\nREQUISITOS DA SENHA:\n"
    "- No mínimo 10 caracteres;\n"
    "- Pelo menos uma letra maiúscula;\n"
    "- Pelo menos uma letra minúscula;\n"
    "- Pelo menos um número.\n"
    "\nSenha Mestra: ")
    print()
    
    erros = validar_senha(senhaMestra)

    while erros:
        for erro in erros:
            print(f"- {erro}")
        print()

        senhaMestra = input("Digite uma nova Senha Mestra: ")
        print()
        erros = validar_senha(senhaMestra)

    senhaMestra = senhaMestra.encode("utf-8")
    
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
                print("[ERRO] Nenhuma senha foi cadastrada!\n")
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
                print("[ERRO] Nenhuma senha foi cadastrada!\n")
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