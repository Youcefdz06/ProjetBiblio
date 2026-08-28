# ProjetBiblio

ProjetBiblio est une application de gestion de bibliotheque en ligne de commande,
developpee en Python avec une base de donnees SQLite. Le projet permet de
pratiquer la programmation modulaire, les requetes SQL, les transactions et le
travail collaboratif avec Git/GitHub.

## Fonctionnalites actuelles

### Authentification

- Connexion avec un nom d'utilisateur et un mot de passe.
- Redirection vers le menu administrateur ou etudiant selon le role du compte.
- Nouvelle tentative lorsque les identifiants sont incorrects.
- Gestion des erreurs d'acces a la base de donnees.

### Administrateur

- Saisie des informations d'un livre : titre, description, auteur, prix d'achat,
  prix de location et stock.
- Validation des valeurs numeriques saisies.
- Confirmation des informations avant l'ajout.
- Ajout du livre dans SQLite.
- Detection des doublons et des donnees invalides.

### Etudiant

- Affichage du catalogue et du stock disponible.
- Affichage des prix d'achat et de location.
- Selection d'un livre par son identifiant.
- Achat d'un livre apres confirmation.
- Verification du stock et du solde avant l'achat.
- Mise a jour atomique du stock et du solde.
- Enregistrement de l'achat dans l'historique.
- Consultation du solde depuis la base de donnees.

## Fonctionnalites prevues

- Location d'un livre.
- Retour d'un livre loue.
- Affichage des locations actives.
- Modification et suppression de livres par un administrateur.
- Statistiques de ventes, de locations et de stock.

## Structure du projet

```text
ProjetBiblio/
|-- main.py             Point d'entree et menus de l'application
|-- auth.py             Authentification des utilisateurs
|-- admin.py            Fonctions reservees aux administrateurs
|-- user.py             Catalogue, solde et achats des etudiants
|-- database.py         Connexion SQLite et creation du schema
|-- utilities.py        Fonctions utilitaires partagees
|-- test_database.py    Tests automatises du schema SQLite
|-- library.db          Base locale generee par l'application
`-- .gitignore          Fichiers locaux ignores par Git
```

## Base de donnees

Le schema SQLite contient quatre tables principales :

- `users` : comptes, roles et soldes.
- `books` : informations, prix et stock des livres.
- `purchases` : historique des achats.
- `rentals` : locations actives et retournees.

Les relations utilisent des cles etrangeres. Des contraintes empechent notamment
les stocks, soldes, prix et quantites negatifs.

## Prerequis

- Python 3.10 ou plus recent (le projet utilise `match` / `case`).
- Aucune dependance externe : `sqlite3` est inclus avec Python.

## Installation

```bash
git clone https://github.com/Youcefdz06/ProjetBiblio.git
cd ProjetBiblio
python database.py
```

La derniere commande cree `library.db` et toutes les tables si elles n'existent
pas. Elle peut etre executee plusieurs fois sans supprimer les donnees existantes.

## Creation d'un compte de test

Les comptes sont actuellement ajoutes manuellement dans la table `users`. Exemple
SQL :

```sql
INSERT INTO users (username, password, role, balance)
VALUES ('student', 'student123', 'student', 100.00);
```

Les roles acceptes sont `admin` et `student`.

## Lancement

```bash
python main.py
```

Connectez-vous ensuite avec un compte present dans la table `users`.

## Tests

```bash
python -m unittest -v
```

Les tests verifient la creation des tables, l'activation des cles etrangeres et
le format de la colonne utilisee pour les mots de passe.

## Notes de securite

Ce projet est destine a l'apprentissage. Les mots de passe sont actuellement
stockes en texte clair dans SQLite. Cette approche ne doit jamais etre utilisee
en production : une application reelle doit stocker des mots de passe haches avec
un algorithme adapte comme Argon2, bcrypt ou scrypt.

La base `library.db` contient des donnees d'execution et est ignoree pour les
nouveaux fichiers par `.gitignore`. Chaque developpeur peut recreer une base vide
avec `python database.py`.
