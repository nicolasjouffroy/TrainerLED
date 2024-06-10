# 🚴‍♂️ Synchronisation de la puissance du Home Trainer avec des LED RGB 💡

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenRGB](https://img.shields.io/badge/OpenRGB-Compatible-green)](https://openrgb.org/)

Ce projet permet de synchroniser la puissance de pédalage d'un home trainer avec des LED RGB en utilisant `OpenRGB` pour le contrôle des LED et `Bleak` pour la communication Bluetooth avec le home trainer.

## 🌟 Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants :

- **Home Trainer Bluetooth** : Compatible avec les services de puissance de cyclisme.
- **PC avec Bluetooth et Windows** : Le script est configuré pour Windows.
- **Contrôleur de LED RGB** : Compatible avec OpenRGB.

## 📥 Installation

### 1. Installer Python

Assurez-vous d'avoir Python 3.8 ou une version ultérieure installée sur votre machine. Vous pouvez le télécharger depuis [python.org](https://www.python.org/downloads/).

### 2. Installer les bibliothèques nécessaires

Utilisez `pip` pour installer les bibliothèques requises :

```sh
pip install bleak openrgb-python
