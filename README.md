# 🚴‍♂️ TrainerLED 💡: 
## Synchronisation de la puissance du Home Trainer avec des LED RGB 💡

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenRGB](https://img.shields.io/badge/OpenRGB-Compatible-green)](https://openrgb.org/)

## 🚧 En cours de développement 🚧

En cours de développement. Les contributions et suggestions sont les bienvenues !


Ce projet permet de synchroniser la puissance de pédalage d'un home trainer avec des LED RGB en utilisant `OpenRGB` pour le contrôle des LED et `Bleak` pour la communication Bluetooth avec le home trainer.  
L'idée est de visualiser les 7 zones de couleurs pour représenter les différentes plages de puissance lors de votre entrainement.

### Fonctionnalités

- **Contrôle de la puissance** : Mesure en temps réel de la puissance générée par le home trainer.  
- **Visualisation par LED** : Affichage des zones de puissance à l'aide de LEDs colorées pour une meilleure compréhension de l'intensité de l'entraînement.  
- **Personnalisation des zones** : Configuration des seuils de puissance et des couleurs associées à chaque zone.  
- **Langue configurable** : Support multilingue avec mémorisation de la langue préférée.  
- **Sauvegarde et restauration** : Sauvegarde des paramètres personnalisés et restauration des paramètres par défaut en un clic.  
- **Interface intuitive** : Utilisation de PyQt5 pour une interface graphique conviviale et facile à utiliser.  
- **Notifications de puissance** : Gestion des notifications de puissance via Bluetooth pour une intégration fluide avec le home trainer.  
- **Affichage des informations UUID** : Option pour afficher ou masquer les informations des services et caractéristiques UUID du périphérique Bluetooth.  
- **Graphiques en temps réel** : Visualisation en temps réel des données de puissance à l'aide de graphiques interactifs.  

#### Le programme a été testé sur un home trainer Tacx NEO 2T et des pédales Favero Assioma DUO.
#### Pour assurer une compatibilité optimale, il est recommandé d'utiliser la connexion ANT+ pour votre logiciel virtuel (tel qu'IndieVelo, Zwift, Rouvy, etc.) et TrainerLED en Bluetooth.  
#### Laissez tourner TrainerLED en arrière-plan, puis lancez votre logiciel virtuel en utilisant la connexion ANT+

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

Téléchargez le dossier. Dans le dossier où se trouve le fichier **requirements.txt**, utilisez pip pour installer les bibliothèques requises :

```sh
pip install -r requirements.txt
```
### 3. Configuration de OpenRGB

Téléchargez et installez [OpenRGB](https://openrgb.org/). Assurez-vous que OpenRGB fonctionne dans un premier temps.
Ensuite il faut que le serveur OpenRGB soit activé. Pour l'activer il faut aller dans les paramètres de OpenRGB et activer l'option "Enable SDK Server".  

### 🔍 *Facultatif*

*Trouver l'UUID et l'adresse MAC du Home Trainer.*

*Pour que le script fonctionne, vous devez connaître l'UUID du service et de la caractéristique de puissance, ainsi que l'adresse MAC de votre home trainer.* 
*Par défaut, **les UUIDs standard déjà intégrés fonctionnent sans modification** avec un Tacx NEO 2T et des pédales Favero Assioma DUO.*

*Sinon voici comment les trouver :*

***1** - Ouvrez TrainerLED.*  
***2** - Cliquez sur **Rechercher Home Trainer** et selectionnez le bon appareil.*  
***3** - Cliquez sur **À propos" puis** puis **Info***  

*Cela vous fournira les informations nécessaires pour configurer le script correctement.*

*#### Autre méthode*

*Scanner avec un outil Bluetooth :*
*Utilisez un outil comme **Bluetooth LE Scanner** sur Android ou **LightBlue** sur iOS.*
*Recherchez votre home trainer dans la liste des appareils disponibles.*
*Notez l'adresse MAC qui sera dans un format comme XX:XX:XX:XX:XX:XX.*

*#### Trouver l'UUID*

*Utiliser un scanner Bluetooth (l'application Android par exemple):*
*Une fois votre appareil trouvé dans l'application scanner, vous pouvez afficher les services et caractéristiques disponibles.*
*Recherchez les services qui se rapportent à la puissance de cyclisme.* 

*Les UUIDs typiques sont :*

*Service de puissance de cyclisme : 00001818-0000-1000-8000-00805f9b34fb*

*Caractéristique de mesure de puissance : 00002a63-0000-1000-8000-00805f9b34fb*

*## Configuration du Script **si nécessaire***

*Editez le script TrainerLED.py et remplacez les valeurs des variables SERVICE_UUID, et CHARACTERISTIC_UUID par celles de votre home trainer.*

## 🚴‍♂️ Utilisation

### 4. Exécuter le script :
Ouvrez un terminal et exécutez le script :
```
python TrainerLED.py
```

## 📝Configuration

Le fichier config.json contient les paramètres de configuration, y compris :

- Les seuils de puissance (thresholds)  
- Les couleurs des zones (colors)  
- Le périphérique par défaut (default_device)  
- La langue par défaut (default_language)  

Vous pouvez modifier ce fichier pour ajuster les paramètres selon vos besoins.

## Fonctionnalités en détail

- Recherche de périphériques Bluetooth : Trouvez et connectez-vous facilement à votre home trainer via Bluetooth.
- Sauvegarde des paramètres par défaut : Enregistrez vos réglages préférés comme paramètres par défaut.
- Restauration des paramètres par défaut : Réinitialisez les paramètres aux valeurs par défaut en un clic.
- Sélection de couleur intuitive : Choisissez facilement les couleurs des zones de puissance à l'aide d'un sélecteur de couleur.
- Affichage graphique : Visualisez les données de puissance en temps réel avec des graphiques clairs et interactifs.
- Gestion automatique des logs : Les fichiers de log sont automatiquement gérés et rotés pour éviter l'encombrement.

## 📌 Contribution

Les contributions sont les bienvenues ! Si vous avez des idées d'améliorations ou si vous rencontrez des problèmes, n'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.

