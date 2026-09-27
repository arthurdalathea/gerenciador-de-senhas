# Versão apenas para testes
from random import *
from hashlib import *
from time import *
from os import *

senhaM = "12345"
tentativas = 0
senhas = {}

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
            sleep(1)
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
            app = input("Diga qual aplicativo pertence a senha: ")
            usuario = input("Digite qual o nome do usuario: ") 
            senha = input(f"Digite sua senha do {app}: ")
            if app not in senhas:
                senhas[app] = {}
                senhas[app][usuario] = senha
            else:
                senhas[app][usuario] = senha
            print("Senha cadatrada com sucesso")
        case 2:
            indice = 1
            if not senhas:
                print("Nenhuma senha cadastrada.\n")
            else:
                for app, usuarios in senhas.items():
                    print(f"Senhas {app} :")
                    for usuario, Senhas in usuarios.items():
                        print(f"Usuario : {usuario}")
                        print(f"Senha : {Senhas}\n")
        case 3:
            if not senhas:
                print("Nenhuma senha cadastrada então não há senhas para excluir\n")
            else:
                app = input("Digite de qual aplicativo você deseja deletar sua senha: ")
                while app not in senhas:
                    app = input("Digite um aplicativo presente : ")
                usuario = input("Digite o nome do usuário: ")
                while usuario not in senhas[app]:
                    usuario = input(f"Digite um usuario presente em {app} : ")
                del senhas[app][usuario]
                print("Senha excluída com sucesso.")
        case 4:
            app = input("Digite de qual aplicativo é a sneha que deseja deletar: ")
            usuario = input("Digite o usuário: ")
            senhaNova = input("Digite a nova senha : ")
            while senhaNova == senhas[app][usuario]:
                senhaNova = input("Digite a nova senha diferente da anterior : ")
            senhas[app][usuario] = senhaNova
        case 5:
            break
