# Versão apenas para testes
from random import *
from hashlib import *
from time import *
from sys import *

senhaM = "12345"
tentativas = 0
senhas = {}

print("=======Gerenciador de Senhas========")
senhaMestra = input("Digite sua senha mestra: ")
tentativas += 1
while senhaMestra != senhaM:
    print("Acesso negado.")
    print()
    senhaMestra = input("Digite a senha correta : ")
    tentativas += 1
    if tentativas %5 == 0:
        print(f"Acesso bloqueado por {tentativas*6} segundos")
        for i in range(tentativas*6-1, 0, -1):
            sleep(1)
            print(f"Restam {i} segundos")
    else:
        pass
print("\nAcesso Liberado\n")
while True:
    print("Ações:")
    print("1-Cadastrar nova senha")
    print("2-Listar senhas")
    print("3-Excluir senha")
    print("4-Alterar senha")
    print("5-Sair")
    while True:
        try:
            ação = int(input("Digite qual ação deseja: "))
            while ação > 5 or ação < 1:
                ação = int(input("Digite uma ação válida"))
            break
        except ValueError:
            print("Digite um número no formato correto")
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