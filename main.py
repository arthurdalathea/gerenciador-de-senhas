# Versão apenas para testes
import secrets
import hashlib
import time
import os
import json
import hmac
import sys

senhaM = "12345"
tentativas = 0
def limpar_buffer_teclado():
    """Limpa a fila de teclas digitadas, funcionando em Windows, Linux e Mac."""
    import os

    if os.name == 'nt':  # Se for Windows
        import msvcrt
        while msvcrt.kbhit(): # comandos para limpar os dados de entrada do terminal
            msvcrt.getch()  
    else:  # Se for Linux ou Mac (Unix)
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH) # comando para limpar os dados de entrada do terminal

print("======= Gerenciador de Senhas ========")
senhaMestra = input("Digite sua senha mestra: ")
tentativas += 1

while senhaMestra != senhaM:

    if tentativas % 5 == 0:
        print()
        print(f"ACESSO BLOQUEADO POR {tentativas*6} SEGUNDOS!")
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

    limpar_buffer_teclado()

    senhaMestra = input("Digite a senha correta: ")
    tentativas += 1
print("\nACESSO LIBERADO!\n")

while True:
    print("="*30)
    print("      PAINEL DE AÇÕES")
    print("="*30)
    print(" 1 - Cadastrar nova senha")
    print(" 2 - Listar senhas")
    print(" 3 - Excluir senha")
    print(" 4 - Alterar senha")
    print(" 5 - Sair")
    print("="*30)
    # Estrutura que impede a entrada de uma ação inválida ou de formato errado
    while True:
        try:
            ação = int(input("Digite qual ação deseja (1-5): "))
            while ação > 5 or ação < 1:
                ação = int(input("Digite uma ação válida (1-5): "))
            break
        except ValueError:
            print("Digite um número no formato correto (1-5): ")
    # Estrutura de decisão match, equivalente ao switch em Java
    match ação:
        case 1:
            app = input("Diga qual aplicativo pertence a senha: ").lower() # Função lower() : transforma todos os caracteres de uma String em minúsculo
            usuario = input("Digite qual o nome do usuario: ") 
            senha = input(f"Digite sua senha do {app}: ")
            with open("Dados.json", "r", encoding="utf-8") as arquivo:
                senhas = json.load(arquivo)
            if app not in senhas:
                senhas[app] = {}
                senhas[app][usuario] = senha
            else:
                senhas[app][usuario] = senha
            with open("Dados.json", "w", encoding="utf-8") as arquivo:
                json.dump(senhas, arquivo, indent=4, ensure_ascii= False)
            print("Senha cadatrada com sucesso")
        case 2:
            with open("Dados.json", "r", encoding="utf-8") as arquivo:
                senhas = json.load(arquivo)
            if not senhas:
                print("Nenhuma senha cadastrada.\n")
            else:
                with open("Dados.json", "r", encoding="utf-8") as arquivo:
                    senhas = json.load(arquivo)
                for app, usuarios in senhas.items():
                    print(f"Senhas {app} :")
                    for usuario, Senhas in usuarios.items():
                        print(f"Usuario : {usuario}")
                        print(f"Senha : {Senhas}\n")
        case 3:
            # Validação se dicionário Senhas não está Vazio
            with open("Dados.json", "r", encoding="utf-8") as arquivo:
                senhas = json.load(arquivo)
            if not senhas:
                print("Nenhuma senha cadastrada então não há senhas para excluir\n")
            else:
                app = input("Digite de qual aplicativo você deseja deletar sua senha: ").lower()
                while app not in senhas:
                    app = input("Digite um aplicativo presente : ").lower()
                usuario = input("Digite o nome do usuário: ")
                while usuario not in senhas[app]:
                    usuario = input(f"Digite um usuario presente em {app} : ")
                escolha = input("Você realmente quer apagar a senha: s/n").lower()
                if escolha != "s":
                    print("Senha não foi deletada.\n")
                else:
                    del senhas[app][usuario]
                    print("Senha excluída com sucesso.")
            with open("Dados.json", "w", encoding="utf-8") as arquivo:
                json.dump(senhas, arquivo, indent=4, ensure_ascii=False)
        case 4:
            # Validação se o dicionário Senhas não está Vazio
            with open("Dados.json", "r", encoding="utf-8") as arquivo:
                senhas = json.load(arquivo)
            if not senhas:
                print("Nenhuma senha está cadastrada no momento.")
            else:
                app = input("Digite de qual aplicativo é a senha que deseja alterar: ").lower()
                while app not in senhas:
                    app = input("Digite um aplicativo válido: ").lower()
                usuario = input("Digite o usuário: ")
                while usuario not in senhas[app]:
                    usuario = input("Digite um usuário válido: ")
                senhaNova = input(f"Digite a nova senha : ")
                while senhaNova == senhas[app][usuario]:
                    senhaNova = input("Digite a nova senha diferente da anterior : ")
                senhas[app][usuario] = senhaNova
                print("Senha alterada com sucesso\n")    
            with open("Dados.json", "w", encoding="utf-8") as arquivo:
                json.dump(senhas, arquivo, indent=4, ensure_ascii=False)        
        case 5:
            print("Programa encerrado.")
            break
