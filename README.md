# Chatapp
Une application de communication par socket.<br>
Ce projet inclue un système de connection par mot de passe.
Chaque mot de passe et est hasher et saler (grâce à bcrypt) et le serveur vérifie que le mot de passe n'y pas présent sur haveibeenpwnd.com
Attention les message ne sont néamoins pas chiffré. 
Le serveur et le client communique grâce à des dictionnaires python.

### Installation
Installer les dépendances grâce à pip
```
pip install -r /path/to/requirements.txt
```
ou
```
pip3 install -r /path/to/requirements.txt
```
