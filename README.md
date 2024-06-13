# 🚴‍♂️ TrainerLED 💡: 
## Synchronisation de la puissance du Home Trainer avec des LED RGB 💡

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenRGB](https://img.shields.io/badge/OpenRGB-Compatible-green)](https://openrgb.org/)

## 🚧 En cours de développement 🚧

En cours de développement. Les contributions et suggestions sont les bienvenues !


Ce projet permet de synchroniser la puissance de pédalage d'un home trainer avec des LED RGB en utilisant `OpenRGB` pour le contrôle des LED et `Bleak` pour la communication Bluetooth avec le home trainer.
L'idée est de visualiser les 7 zones de couleurs pour représenter les différentes plages de puissance.  

#### Le programme a été testé sur un home trainer Tacx NEO 2T et des pédales Favero Assioma DUO.
#### Pour assurer une compatibilité optimale, il est recommandé d'utiliser la connexion ANT+ pour votre logiciel virtuel (tel qu'IndieVelo, Zwift, Rouvy, etc.) et TrainerLED en Bluetooth.  
#### Laissez TrainerLED tourner en arrière-plan, puis lancez votre logiciel virtuel en utilisant la connexion ANT+

![Description de l'image](TrainerLED.png)  

Voici une vidéo de démonstration (cliquez sur la vignette) :

[![Demo vidéo](https://img.youtube.com/vi/Lh4l7ruDxWw/0.jpg)](https://www.youtube.com/watch?v=Lh4l7ruDxWw)





## 🌟 Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants :

- **Home Trainer Bluetooth** : Home Trainer avec capteur de puissance de cyclisme.
- **PC avec Bluetooth et Windows** : Le script est configuré pour Windows.
- **Contrôleur de LED RGB** : Compatible avec OpenRGB.

## 📥 Installation

### 1. Installer Python

Assurez-vous d'avoir Python 3.8 ou une version ultérieure installée sur votre machine. Vous pouvez le télécharger depuis [python.org](https://www.python.org/downloads/).

### 2. Installer les bibliothèques nécessaires

Utilisez `pip` pour installer les bibliothèques requises :

```sh
pip install -r requirements.txt
```
### 3. Configuration de OpenRGB

Téléchargez et installez [OpenRGB](https://openrgb.org/). Assurez-vous que OpenRGB fonctionne dans un premier temps.
Ensuite il faut que le serveur OpenRGB soit activé. Pour l'activer il faut aller dans les paramètres de OpenRGB et activer l'option "Enable SDK Server".

## 🔍 Facultatif - Trouver l'UUID et l'adresse MAC du Home Trainer.

Pour que le script fonctionne, vous devez connaître l'UUID du service et de la caractéristique de puissance, ainsi que l'adresse MAC de votre home trainer.  
Par défaut, **les UUIDs standard déjà intégrés fonctionnent sans modification** avec un Tacx NEO 2T et des pédales Favero Assioma DUO.

Sinon voici comment les trouver :

**1** - Ouvrez TrainerLED.  
**2** - Cliquez sur **Rechercher Home Trainer** et selectionnez le bon appareil.  
**3** - Cliquez sur **À propos" puis** puis **Info**  

Cela vous fournira les informations nécessaires pour configurer le script correctement.

#### Autre méthode

Scanner avec un outil Bluetooth :
Utilisez un outil comme **Bluetooth LE Scanner** sur Android ou **LightBlue** sur iOS.
Recherchez votre home trainer dans la liste des appareils disponibles.
Notez l'adresse MAC qui sera dans un format comme XX:XX:XX:XX:XX:XX.

#### Trouver l'UUID

Utiliser un scanner Bluetooth (l'application Android par exemple):
Une fois votre appareil trouvé dans l'application scanner, vous pouvez afficher les services et caractéristiques disponibles.
Recherchez les services qui se rapportent à la puissance de cyclisme. 

Les UUIDs typiques sont :

Service de puissance de cyclisme : 00001818-0000-1000-8000-00805f9b34fb

Caractéristique de mesure de puissance : 00002a63-0000-1000-8000-00805f9b34fb

## 📝 Configuration du Script  

### Configurer le script :
Si nécessaire, éditez le script TrainerLED.py et remplacez les valeurs des variables SERVICE_UUID, et CHARACTERISTIC_UUID par celles de votre home trainer.

## 🚴‍♂️ Utilisation

### Exécuter le script :
Ouvrez un terminal et exécutez le script :
```
python TrainerLED.py
```

### ⚡Réglages des Zones de Puissance

L'application permet de définir sept zones de puissance, chacune associée à une couleur différente.

Voici les étapes pour configurer ces zones :  

- **Démarrer l'application** : Cliquez sur le bouton Démarrer.  
- **Arrêter l'application** : Cliquez sur le bouton Arrêter.

Vous pouvez ajuster les seuils de puissance pour chaque zone à l'aide des curseurs ou en entrant manuellement les valeurs :  

- **Zone 1** (Récupération active) : Réglage de 0 à zone 1.  
- **Zone 2** (Endurance) : Réglage zone 1 + à zone 2.  
- **Zone 3** (Tempo) : Réglage de zone 2 +  à zone 3.  
- **Zone 4** (Seuil) : Réglage de zone 3 + 1 à zone 4.  
- **Zone 5** (VO2 max) : Réglage de zone 4 + à zone 5.  
- **Zone 6** (Anaérobique) : Réglage de zone 5 + à zone 6.  
- **Zone 7** (Neuromusculaire) : Réglage de zone 6 + au-delà.  

### 🎨 Couleurs des Zones

Pour chaque zone, vous pouvez choisir une couleur en cliquant sur le bouton Sélectionner Couleur Zone X et en choisissant la couleur souhaitée à partir du sélecteur de couleur.   

Sauvegarder et Restaurer les Paramètres :  

- Sauvegarder ce paramètre par défaut : Cliquez sur ce bouton pour sauvegarder les seuils et les couleurs actuels comme paramètres par défaut.  
- Restaurer les paramètres par défaut : Cliquez sur ce bouton pour restaurer les seuils et les couleurs par défaut.  

### Exemple d'Utilisation

**1** - Cliquez sur **Rechercher Home Trainer** et selectionnez votre appareil.  
**2** - Démarrez l'application en cliquant sur **Démarrer**.  
**3** - Ajustez vos seuils de puissance en utilisant les curseurs ou en entrant les valeurs manuellement.  
**4** - Sélectionnez les couleurs pour chaque zone en cliquant sur les boutons de sélection de couleur.  
**5** - Sauvegardez vos réglages en cliquant sur Sauvegarder ce paramètre par défaut.  
**6** - Arrêtez l'application en cliquant sur **Arrêter**.

Les LED devraient maintenant changer de couleur en fonction de la puissance moyenne sur 1 seconde mesurée par le home trainer.  

## 📌 Contribution

Les contributions sont les bienvenues ! Si vous avez des idées d'améliorations ou si vous rencontrez des problèmes, n'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.

