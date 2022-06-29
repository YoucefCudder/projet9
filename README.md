# **PROJET 9**

## Développez une application Web en utilisant Django


### Sous Windows

# Installation du  projet 

- Récupérer le projet 
 ```shell
git clone  https://github.com/YoucefCudder/projet9.git
```

- Activer un environnement virtuel pour l'installation du projet
````shell
 cd projet9

python -m venv env

env\Scripts\activate
````

- Récupérer les dépendances nécessaires
````shell
pip install -r requirements.txt
````
# Lancer le projet 

- Activer le serveur Django
````shell
python manage.py runserver
````
- Se rendre à l'adresse [127.0.0.1:8000](http://127.0.0.1:8000)


### Informations 

**Possibilité de :** 
- Se connecter et s'inscrire
- Créer des tickets de demande de critique 
- Créer des critiques, en réponse ou non à des tickets 
- Consulter un flux contenant les tickets et critiques des utilisateurs auxquels on est abonné 
- Suivre d'autres utilisateurs, ou se désabonner.
- Voir ses propres posts, les modifier ou les supprimer 
