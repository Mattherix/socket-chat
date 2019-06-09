# -- IMPORT -- #
import json
import select
import socket
import sys

import bcrypt
import passpwnedcheck.pass_checker as passwordcheck

# -- CONSTANTES, VARIABLE ET PARAMS -- #
# Compte par défaut, admin chatappadmin
# Si vous l'utilisé, CHANGER LE MOT DE PASSE, merci.
TYPE_REQUEST = ['MSG', 'LOGIN', 'REGISTER'] # Type de requete accepté

connections = [] # Liste de toutes les connection au serveur
adr = {} # Adresse des connections, adr[une_connection] -> ('X.X.X.X', PORT)
login_liste = [] # Liste des connections des utilisateur connecté
conn_login = {} # Info des utilisateur connecté, conn_login[une_connection]['username'] -> 'username'

# -- FONCTIONS -- #
def verif_request(data):
    """ Permet de verifier une requete. """
    try:
        # Obtention dico
        data = json.loads(data.decode())
    except:
        request = {'type': 'ERROR', 'code': 1}
        return request
    try:
        type = data['type']
        if type in TYPE_REQUEST:
            pass
        else:
            request = {'type': 'ERROR', 'code': 3}
            return request
    except:
        request = {'type': 'ERROR', 'code': 2}
        return request
    if type == 'MSG':
        try:
            var = data['msg']
        except:
            request = {'type': 'ERROR', 'code': 4}
            return request
    elif type == 'LOGIN' or type == 'REGISTER':
        try:
            var = data['username']
        except:
            request = {'type': 'ERROR', 'code': 5}
            return request
        try:
            var = data['password']
        except:
            request = {'type': 'ERROR', 'code': 6}
            return request
    return data

def afficher_request(request):
    """ Affiche les requetes """
    if request['type'] == 'MSG':
        if conn in login_liste:
            username = conn_login[conn]['username']
            if len(login_liste) == 1:
                username = '(seul)' + username
        else:
            username = adr[conn]
        print(username, ': ', request['msg'])
    elif request['type'] == 'LOGIN' or request['type'] == 'REGISTER':
        print({'type': request['type'], 'username': request['username'], 'password': '***'})

# -- INIT -- #
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('', 6060))
    s.listen(5)
except socket.error as error:
    print("Impossible d'ouvrir le port 6060\n{}".format(error))
    sys.exit()

try:
    # -- MAIN -- #
    c = True
    while c:
        # - Nouveaux - #
        nouvelles_connections, wlist, xlist = select.select([s], [], [], 0.05)

        for connection in nouvelles_connections:
            conn, address = connection.accept()
            connections.append(conn)
            adr[conn] = address
            print(f"{address} connecté")

        # - A lire - #
        try:
            connections_a_lire, wlist, xlist = select.select(connections, [], [], 0.05)
        except select.error:
            pass
        else:
            for conn in connections_a_lire:
                try:
                    data = conn.recv(1024)
                except:
                    conn.close()
                    connections.remove(conn)
                else:
                    request = verif_request(data)
                    afficher_request(request)
                    # Traitement
                    if request['type'] == 'MSG':
                        try:
                            username = conn_login[conn]['username']
                            if len(login_liste) == 1:
                                # Une seul personne connecté
                                conn.sendall(bytes(json.dumps({'type':'ERROR', 'code':10}), 'utf-8'))
                            else:
                                request['username'] = username
                                # Envoie du msg aux autres
                                for autre_conn in connections:
                                    if autre_conn != conn:
                                        autre_conn.sendall(bytes(json.dumps(request), 'utf-8'))
                        except:
                            # Vous devez etre connecté
                            conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 12}), 'utf-8'))

                    elif request['type'] == 'REGISTER':
                        try:
                            # JSON load
                            print('[*]: [REGISTER] JSON load')
                            f = open('user.json', 'r')
                            dico = json.load(f)
                            f.close()
                            print('[OK]: [REGISTER] JSON load')
                            # Verification
                            print('[*]: [REGISTER] Verification')
                            rep = False
                            try:
                                username = dico[request['username']]
                                # L'utilisateur existe deja
                                conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 7}), 'utf-8'))
                                print("[ERROR]: [REGISTER] L'utilisateur {} existe deja".format(request['username']))
                            except:
                                # Verification de la taille du mot de passe et du fait qu'il soit leak ou pas
                                password_checker = passwordcheck.PassChecker()
                                is_leak, nbr_fois = password_checker.is_password_compromised(request['password'])
                                if len(request['password']) <= 6:
                                    print('[*]: [REGISTER] Mot de passe trop court')
                                    # Mot de passe trop court
                                    conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 13}), 'utf-8'))
                                elif is_leak:
                                    # Mot de passe leak
                                    conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 14, 'data':nbr_fois}), 'utf-8'))
                                else:
                                    dico[request['username']] = {}
                                    dico[request['username']]['username'] = request['username']
                                    salt = bcrypt.gensalt()
                                    dico[request['username']]['password'] = str(bcrypt.hashpw(bytes(request['password'], 'utf-8'), salt), 'utf-8')
                                    # JSON dump
                                    try:
                                        print('[*]: [REGISTER] JSON dump')
                                        f = open('user.json', 'w')
                                        json.dump(dico, f)
                                        f.close()
                                        print('[OK]: [REGISTER] JSON dump')
                                        # Message de bienvenue
                                        conn.sendall(bytes(json.dumps({'type': 'INFO', 'code': 2}), 'utf-8'))
                                        print('[+]: [REGISTER] User {}'.format(request['username']))
                                    except Exception as ex:
                                        print('JSON dump (error)', ex)
                                        f.close()
                                        # Erreur interne au serveur
                                        conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 11}), 'utf-8'))
                        except Exception as ex:
                            print('JSON load (error)', ex)
                            f.close()
                            # Erreur interne au serveur
                            conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 11}), 'utf-8'))

                    elif request['type'] == 'LOGIN':
                        try:
                            # JSON load
                            print('[*]: [LOGIN] JSON load')
                            f = open('user.json', 'r')
                            dico = json.load(f)
                            f.close()
                            print('[OK]: [LOGIN] JSON load')
                            # Verification
                            print('[*]: [LOGIN] Verification')
                            try:
                                password = bytes(dico[request['username']]['password'], 'utf8')
                                if bcrypt.checkpw(request['password'].encode('utf-8'), password):
                                    login_liste.append(conn)
                                    conn_login[conn] = {}
                                    conn_login[conn]['username'] = request['username']
                                    # Message Connection
                                    conn.sendall(bytes(json.dumps({'type': 'INFO', 'code': 1}), 'utf-8'))
                                    # Message de connection pour les autres personne connecte
                                    for autre_conn in login_liste:
                                        if autre_conn != conn:
                                            # Info connection
                                            autre_conn.sendall(bytes(json.dumps({'type':'INFO', 'code':3, 'data':request['username']}), 'utf-8'))
                                    print('[OK]: [LOGIN] Connection de {}\n'.format(request['username']))
                                else:
                                    # Mauvais mot de passe
                                    conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 9}), 'utf-8'))
                                    print("[ERROR]: [LOGIN] l'utilisateur {} a taper un mot de passe faux".format(request['username']))
                            except:
                                print("[ERROR]: [LOGIN] l'utilisateur {} n'existe pas".format(request['username']))
                                # Mauvais Username
                                conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 8}), 'utf-8'))
                        except Exception as ex:
                            print('JSON load (error)', ex)
                            f.close()
                            # Erreur interne au serveur
                            conn.sendall(bytes(json.dumps({'type': 'ERROR', 'code': 11}), 'utf-8'))

                    elif request['type'] == 'ERROR':
                        conn.sendall(bytes(json.dumps(request), 'utf-8'))

finally:
    # -- Fin du programme -- #
    for conn in connections:
        conn.close()
    s.close()