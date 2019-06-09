# -- IMPORT -- #
import getpass
import json
import socket
import sys
import threading

# -- CONSTANTES, VARIABLE ET PARAMS -- #
serveur_ip = '127.0.0.1' # Adresse du serveur
SERVEUR_PORT = 6060 # Port du serveur
INFO_CODE = {
    1:'Vous etes connecté{}',
    2:'Vous avez bien été enregistrer. Vous pouvez maintenant vous connecter avec LOGIN ou log{}',
    3:'{} est maintenant connecte'
} # Code correspondant aux requete de type INFO
ERROR_CODE = {
    1:'Vous devez envoyer un dico{}',
    2:"Le type de requete n'a pas été donnée{}",
    3:"Ce type de requete n'existe pas{}",
    4:'Argument msg absent{}',
    5:'Argument username absent{}',
    6:'Argument password absent{}',
    7:'Cet utilisateur existe déjà{}',
    8:"Cet utilisateur n'existe pas{}",
    9:'Mots de passe incorrect{}',
    10:'Vous êtes seul sur le serveur{}',
    11:'Erreur interne au serveur{}',
    12:'Vous devez etre connecté pour envoyer un message{}',
    13:'Mot de passe trop court (minimum 7 charactères){}',
    14:'Mot de passe trop courant, trouvé {} fois sur haveibeenpwned.com'
} # Code correspondant aux requete de type INFO
TYPE_REQUEST = ['MSG', 'INFO', 'ERROR'] # Type de requete accepté

# -- FONCTIONS -- #
def create_request(type, args):
    if type == 'MSG':
        request = {'type':'MSG', 'msg':args[0]}
        return bytes(json.dumps(request), 'utf-8')
    elif type == 'REGISTER':
        request = {'type':'REGISTER', 'username':args[0], 'password':args[1]}
        return bytes(json.dumps(request), 'utf-8')
    elif type == 'LOGIN':
        request = {'type':'LOGIN', 'username':args[0], 'password':args[1]}
        return bytes(json.dumps(request), 'utf-8')

def reception_msg():
    while True:
        data = s.recv(1024)
        request = verif_request(data)
        if request['type'] == 'MSG':
            print(request['username'], ': ', request['msg'])
        elif request['type'] == 'INFO':
            if request['code'] in [3]:
                data = request['data']
            else:
                data = ''
            print(INFO_CODE[request['code']].format(data))
        elif request['type'] == 'ERROR':
            if request['code'] in [14]:
                data = request['data']
            else:
                data = ''
            print(ERROR_CODE[request['code']].format(data))
        elif request['type'] == 'error':
            print(request['error'])

def verif_request(data):
    try:
        # Obtention dico
        data = json.loads(data.decode())
    except:
        return {'type':'error', 'error':'Impossible de traduire une requete en  provenance du serveur.\nObjet autre que json'}
    try:
        type = data['type']
        if type in TYPE_REQUEST:
            pass
        else:
            return {'type':'error', 'error':'Impossible de traduire une requete en  provenance du serveur\nType de requete inconnue'}
    except:
        return {'type':'error', 'error':'Impossible de traduire une requete en  provenance du serveur\nType de requete absent'}
    if type == 'MSG':
        try:
            var = data['msg']
        except:
            return {'type':'error', 'error':'Impossible de traduire une requete en  provenance du serveur\nMSG  Argument msg absent'}
        try:
            var = data['username']
        except:
            return {'type':'error', 'error':'Impossible de traduire une requete en  provenance du serveur\nMSG  Argument username absent'}
    if type == 'INFO':
        try:
            code = data['code']
        except:
            return {'type':'error', 'error':'Impossible de traduire une requete en  provenance du serveur\nINFO  Argument code absent'}
        if data['code'] in [3]:
            try:
                donnes = data['data']
            except:
                return {'type': 'error', 'error': 'Impossible de traduire un requete en  provenance du serveur\nINFO  Argument data absent'}
    if type == 'ERROR':
        try:
            code = data['code']
        except:
            print('Impossible de traduire la requete en  provenance du serveur\nERROR  Argument code absent')
            return {'type':'error', 'error':''}
    return data

# -- INIT -- #
# Banière
print('     ____    _   _       _        _____       _        ____      ____    \n', '  U /"___|  |', "'| |'|  U  /", '\  u   |_ " _|  U  /"\  u  U|  _"\ u U|  _"\ u \n', '  \| | u   /| |_| |\  \/ _ \/      | |     \/ _ \/   \| |_) |/ \| |_) |/ \n', '   | |/__  U|  _  |u  / ___ \     /| |\    / ___ \    |  __/    |  __/   \n', '    \____|  |_| |_|  /_/   \_\   u |_|U   /_/   \_\   |_|       |_|      \n', '   _// \\\\   //   \\\\   \\\\    >>   _// \\\\_   \\\\    >>   ||>>_     ||>>_    \n', '  (__)(__) (_") ("_) (__)  (__) (__) (__) (__)  (__) (__)__)   (__)__)   \n')
rep = input("Quel est l'adresse IP de votre serveur ?\n [IP]:")
if rep:
    serveur_ip = rep
# Connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((serveur_ip, SERVEUR_PORT))
except socket.error as error:
    print('Une erreur est survenue lors de la connexion à {}:{}\n{}'.format(serveur_ip, SERVEUR_PORT, error))
    sys.exit()

# -- MAIN -- #
try:
    t = threading.Thread(target=reception_msg)
    t.daemon = True
    t.start()
    c = True
    d = False
    while c:
        msg = input('')
        if msg in ['?', 'HELP', 'help', 'H', 'h']:
            print('Pour vous inscrire à un serveur tappé REGISTER ou reg.\nPour vous connecter tappé LOGIN ou log\nPour quitté tappé stop')
        elif not msg and d == False:
            print("Pour obtenir de l'aide tappé help ou ?")
            d = True
        elif msg in ['STOP', 'stop']:
            c = False
        elif msg in ['LOGIN', 'login', 'log', 'LOG']:
            username = input("Nom d'utilisateur: ")
            password = getpass.getpass('Mot de passe: ')
            s.sendall(create_request('LOGIN', [username, password]))
        elif msg in ['REGISTER', 'register', 'reg', 'REG']:
            username = input("Nom d'utilisateur: ")
            password = getpass.getpass('Mot de passe: ')
            s.sendall(create_request('REGISTER', [username, password]))
        else:
            s.sendall(create_request('MSG', [msg]))
finally:
    s.close()