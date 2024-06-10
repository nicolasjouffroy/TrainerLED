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
```
### 3. Configuration de OpenRGB

Téléchargez et installez OpenRGB. Assurez-vous que le serveur OpenRGB est activé. Vous pouvez activer le serveur en allant dans les paramètres de OpenRGB et en activant l'option "Enable SDK Server".

## 📝 Configuration

### 1. Créer et copier le script

Créez un fichier trainled.py et copiez le code suivant :

```
import asyncio
from bleak import BleakClient
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import threading
import time
from collections import deque

power_values = deque(maxlen=10)  # Liste pour stocker les valeurs de puissance sur 1 seconde (10 lectures à 10 Hz)
last_update_time = time.time()  # Temps du dernier update de la puissance
running = True  # Variable de contrôle pour arrêter le script

current_color = RGBColor(0, 0, 0)
color_lock = threading.Lock()

# Fonction pour définir la couleur des LED avec transition
def set_led_color_with_transition(r, g, b, steps=10, delay=0.01):  # Transition plus courte
    global current_color
    try:
        client = OpenRGBClient('localhost', 6742)  # Adresse et port du serveur OpenRGB
        devices = client.devices

        with color_lock:
            current_r = current_color.red
            current_g = current_color.green
            current_b = current_color.blue

        step_r = (r - current_r) / steps
        step_g = (g - current_g) / steps
        step_b = (b - current_b) / steps

        for i in range(steps):
            new_r = int(current_r + step_r * i)
            new_g = int(current_g + step_g * i)
            new_b = int(current_b + step_b * i)
            color = RGBColor(new_r, new_g, new_b)

            with color_lock:
                current_color = color
                for device in devices:
                    device.set_color(color)
            time.sleep(delay)

        final_color = RGBColor(r, g, b)
        with color_lock:
            current_color = final_color
            for device in devices:
                device.set_color(final_color)
    except Exception as e:
        print(f"Erreur de connexion à OpenRGB: {e}")

SERVICE_UUID = '00001818-0000-1000-8000-00805f9b34fb'  # UUID pour le service de puissance de cyclisme
CHARACTERISTIC_UUID = '00002a63-0000-1000-8000-00805f9b34fb'  # UUID pour la caractéristique de mesure de puissance
HOME_TRAINER_MAC = 'AB:CD:EF:GH:IJ:KL'

# Fonction pour gérer les notifications de données de puissance
def notification_handler(sender, data):
    global last_update_time
    print(f"Data brute : {data}")
    try:
        # Extraction de la puissance à partir du troisième et quatrième octet
        puissance = int.from_bytes(data[2:4], byteorder='little')
        print("Puissance :", puissance)
        
        # Mettre à jour le temps de la dernière lecture
        last_update_time = time.time()

        # Ajouter la puissance actuelle à la liste des valeurs
        power_values.append(puissance)

        # Calculer la moyenne des puissances sur les 1 dernières secondes
        if len(power_values) == power_values.maxlen:
            avg_puissance = sum(power_values) / len(power_values)
            print("Puissance moyenne (1s) :", avg_puissance)

            # Déterminer la couleur en fonction de la zone de puissance
            if avg_puissance <= 106:
                new_color = (255, 255, 255)  # Blanc
            elif avg_puissance <= 146:
                new_color = (0, 0, 255)  # Bleu
            elif avg_puissance <= 175:
                new_color = (0, 255, 0)  # Vert
            elif avg_puissance <= 205:
                new_color = (255, 255, 0)  # Jaune
            elif avg_puissance <= 234:
                new_color = (255, 165, 0)  # Orange
            elif avg_puissance <= 293:
                new_color = (255, 0, 0)  # Rouge
            else:
                new_color = (128, 0, 128)  # Violet

            # Appliquer la nouvelle couleur avec transition
            threading.Thread(target=set_led_color_with_transition, args=(new_color,)).start()
        
    except Exception as e:
        print(f"Erreur lors de la gestion des données de puissance: {e}")

# Fonction principale pour se connecter et lire les données de puissance
async def main():
    global last_update_time, running
    async with BleakClient(HOME_TRAINER_MAC) as client:
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        print("Connecté au home trainer. Lecture des données...")
        try:
            while running:
                # Vérifier le temps écoulé depuis la dernière lecture de puissance
                if time.time() - last_update_time > 10:
                    print("Aucune donnée reçue depuis 10 secondes, attente de nouvelles données...")
                await asyncio.sleep(1)  # Garde la connexion active avec un délai
        except asyncio.CancelledError:
            print("Tâche annulée.")
        except KeyboardInterrupt:
            running = False
            print("Interruption reçue, arrêt du script...")
        finally:
            await client.stop_notify(CHARACTERISTIC_UUID)
            print("Notification stoppée, déconnexion.")

# Exécution du script
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Script arrêté par l'utilisateur.")
```
