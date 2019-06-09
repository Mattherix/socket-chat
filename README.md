# Chatapp
Une application de communication par socket.<br>
Ce projet inclue un système de connection par mot de passe.
Chaque mot de passe est hasher et salé (grâce à bcrypt). Le serveur vérifie que le mot de passe n'est pas présent sur haveibeenpwnd.com
Attention les messages ne sont néamoins pas chiffré. 
Le serveur et le client communique grâce à des dictionnaires python.

## Installation
Installer les dépendances grâce à pip
```
pip install -r /path/to/requirements.txt
```
ou
```
pip3 install -r /path/to/requirements.txt
```

## Liens des github des lib
Ce sont des bibliothéques très pratiques et bien pensées.<br>
N'hésitez pas supporter leurs travail.<br><br>
https://github.com/duongntbk/passpwnedcheck<br>
https://github.com/pyca/bcrypt/

## Note
Quelque comptes sont présent de base dans user.json
