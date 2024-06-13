import sys
import asyncio
import threading
import time
import json
import logging
from collections import deque
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider,
                             QFrame, QColorDialog, QGridLayout, QLineEdit, QMessageBox, QDialog, QListWidget, QTextEdit,
                             QMenuBar, QAction, QMainWindow, QComboBox, QWidgetAction)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
from bleak import BleakClient, BleakScanner
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import gettext
import os
from logging.handlers import RotatingFileHandler  # Import the RotatingFileHandler

# Configuration du logging avec RotatingFileHandler
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler("trainer_led.log", maxBytes=200*1024, backupCount=5)  # 200KB per file, keep 5 backups
log_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        log_handler,
        console_handler
    ]
)

print("Configuration du logging terminée")

# Chemin du fichier de configuration
CONFIG_FILE = 'config.json'

# Variable globale pour arrêter le script
running = True

# Déclaration des variables pour la puissance et la couleur
power_values = deque(maxlen=10)
last_update_time = time.time()
current_color = RGBColor(0, 0, 0)
color_lock = threading.Lock()

# UUID du service et de la caractéristique pour les notifications de puissance
SERVICE_UUID = '00001818-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC_UUID = '00002a63-0000-1000-8000-00805f9b34fb'

# Fonction pour changer la langue
def set_language(lang_code):
    global current_language
    print(f"Changement de langue : {lang_code}")
    localedir = os.path.join(os.path.dirname(__file__), 'translations')
    translation = gettext.translation('translations', localedir, languages=[lang_code], fallback=True)
    translation.install()
    current_language = lang_code
    global _
    _ = translation.gettext

# Classe pour gérer les notifications de puissance
class PowerNotificationHandler(QObject):
    power_updated = pyqtSignal(int)
    color_updated = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        print("Initialisation du gestionnaire de notifications de puissance")
        self.zone_thresholds, self.zone_colors, self.default_device, self.default_language = self.load_config()
        set_language(self.default_language)  # Initialiser la langue par défaut
        print("Configuration chargée")

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                zone_thresholds = config['thresholds']
                zone_colors = [tuple(color) for color in config['colors']]
                default_device = config.get('default_device', '')
                default_language = config.get('default_language', 'fr')
                return zone_thresholds, zone_colors, default_device, default_language
        except (FileNotFoundError, KeyError, ValueError) as e:
            logging.error("Erreur lors du chargement de la configuration", exc_info=True)
            return [106, 146, 175, 205, 234, 293], [
                (255, 255, 255),  # Default color for zone 1
                (0, 0, 255),      # Default color pour zone 2
                (0, 255, 0),      # Default color pour zone 3
                (255, 255, 0),    # Default color pour zone 4
                (255, 165, 0),    # Default color pour la zone 5
                (255, 0, 0),      # Default color pour la zone 6
                (128, 0, 128)     # Default color pour la zone 7
            ], '', 'fr'

    def save_config(self):
        config = {
            'thresholds': self.zone_thresholds,
            'colors': [list(color) for color in self.zone_colors],
            'default_device': self.default_device,
            'default_language': current_language  # Enregistrer la langue actuelle
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            logging.error("Erreur lors de la sauvegarde de la configuration", exc_info=True)

    def restore_default_config(self):
        self.zone_thresholds = [106, 146, 175, 205, 234, 293]
        self.zone_colors = [
            (255, 255, 255),  # Default color for zone 1
            (0, 0, 255),      # Default color pour zone 2
            (0, 255, 0),      # Default color pour zone 3
            (255, 255, 0),    # Default color pour zone 4
            (255, 165, 0),    # Default color pour la zone 5
            (255, 0, 0),      # Default color pour la zone 6
            (128, 0, 128)     # Default color pour la zone 7
        ]
        self.default_device = ''
        self.default_language = 'fr'
        set_language(self.default_language)  # Réinitialiser la langue par défaut
        self.save_config()

    def set_default_device(self, device_address):
        self.default_device = device_address
        self.save_config()

    def get_zone_ranges(self):
        ranges = []
        lower_bound = 0
        for threshold in self.zone_thresholds:
            ranges.append((lower_bound, threshold))
            lower_bound = threshold + 1
        ranges.append((lower_bound, float('inf')))  # La dernière plage est ouverte
        return ranges

    def set_zone_threshold(self, index, value):
        self.zone_thresholds[index] = value
        self.save_config()

    def set_zone_color(self, index, color):
        self.zone_colors[index] = color
        self.save_config()

    def handle_notification(self, sender, data):
        global last_update_time
        try:
            puissance = int.from_bytes(data[2:4], byteorder='little')
            last_update_time = time.time()
            power_values.append(puissance)

            if len(power_values) == power_values.maxlen:
                avg_puissance = sum(power_values) / len(power_values)
                self.power_updated.emit(int(avg_puissance))

                for i, threshold in enumerate(self.zone_thresholds):
                    if avg_puissance <= threshold:
                        new_color = self.zone_colors[i]
                        zone = i + 1
                        break
                else:
                    new_color = self.zone_colors[-1]
                    zone = len(self.zone_colors)

                self.color_updated.emit((new_color, zone))
                threading.Thread(target=set_led_color_with_transition, args=new_color).start()
        except Exception as e:
            logging.error("Erreur lors de la gestion des données de puissance", exc_info=True)

def set_led_color_with_transition(r, g, b, steps=10, delay=0.01):
    global current_color
    try:
        client = OpenRGBClient('localhost', 6742)
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
        logging.error("Erreur de connexion à OpenRGB", exc_info=True)

async def main(notification_handler, device_address, service_uuid, characteristic_uuid, status_label):
    global last_update_time, running
    retry_attempts = 5
    status_label.setText(_("En attente de connexion au périphérique"))
    for attempt in range(retry_attempts):
        try:
            async with BleakClient(device_address) as client:
                status_label.setText(_("Périphérique {device_address} connecté").format(device_address=device_address))
                await client.start_notify(characteristic_uuid, notification_handler.handle_notification)
                try:
                    while running:
                        if time.time() - last_update_time > 10:
                            logging.warning("Aucune donnée reçue depuis 10 secondes, attente de nouvelles données...")
                        await asyncio.sleep(1)
                except asyncio.CancelledError:
                    logging.info("Tâche annulée.")
                except KeyboardInterrupt:
                    running = False
                    logging.info("Interruption reçue, arrêt du script...")
                finally:
                    await client.stop_notify(characteristic_uuid)
                break
        except Exception as e:
            logging.error(f"Tentative {attempt + 1}/{retry_attempts} échouée", exc_info=True)
            if attempt < retry_attempts - 1:
                await asyncio.sleep(2)
            else:
                logging.error("Échec de la connexion après plusieurs tentatives, arrêt du script.")
                status_label.setText(_("Échec de la connexion après plusieurs tentatives"))

class AsyncThread(QThread):
    def __init__(self, notification_handler, device_address, service_uuid, characteristic_uuid, status_label):
        super().__init__()
        self.notification_handler = notification_handler
        self.device_address = device_address
        self.service_uuid = service_uuid
        self.characteristic_uuid = characteristic_uuid
        self.status_label = status_label

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main(self.notification_handler, self.device_address, self.service_uuid, self.characteristic_uuid, self.status_label))

class AsyncTaskRunner(QThread):
    result_ready = pyqtSignal(list)

    def __init__(self, coro):
        super().__init__()
        self.coro = coro

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.coro)
        if result is None:
            result = []
        self.result_ready.emit(result)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Initialisation de la fenêtre principale")
        self.notification_handler = PowerNotificationHandler()
        self.notification_handler.power_updated.connect(self.update_power)
        self.notification_handler.color_updated.connect(self.update_color)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.async_thread = None
        self.HOME_TRAINER_MAC = self.notification_handler.default_device

        if self.HOME_TRAINER_MAC:
            self.start_thread()

        self.init_plot()

    def init_ui(self):
        print("Initialisation de l'interface utilisateur")
        self.setWindowTitle('TrainerLED')
        self.layout = QVBoxLayout(self.central_widget)

        self.search_button = QPushButton(_('Rechercher Home Trainer'))
        self.device_list = QListWidget()
        self.start_button = QPushButton(_('Démarrer'))
        self.stop_button = QPushButton(_('Arrêter'))
        self.save_default_button = QPushButton(_('Sauvegarder ce paramètre par défaut'))
        self.restore_default_button = QPushButton(_('Restaurer les paramètres par défaut'))
        self.set_default_device_button = QPushButton(_('Définir comme périphérique par défaut'))
        self.status_label = QLabel(_('En attente de connexion au périphérique'))
        self.power_label = QLabel(_('Puissance: N/A'))
        self.zone_label = QLabel(_('Zone de puissance: N/A'))
        self.color_frame = QFrame()
        self.color_frame.setFixedSize(20, 20)
        self.color_frame.setStyleSheet("background-color: rgb(0, 0, 0);")

        self.search_button.clicked.connect(self.search_devices)
        self.device_list.itemClicked.connect(self.device_selected)
        self.start_button.clicked.connect(self.start_thread)
        self.stop_button.clicked.connect(self.stop_thread)
        self.save_default_button.clicked.connect(self.save_defaults)
        self.restore_default_button.clicked.connect(self.restore_defaults)
        self.set_default_device_button.clicked.connect(self.set_default_device)

        power_zone_layout = QHBoxLayout()
        power_zone_layout.addWidget(self.zone_label)
        power_zone_layout.addWidget(self.color_frame)

        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.device_list)
        self.layout.addWidget(self.set_default_device_button)

        self.info_widget = QWidget()
        info_layout = QVBoxLayout()
        self.service_characteristics = QTextEdit()
        self.service_characteristics.setReadOnly(True)
        info_layout.addWidget(self.service_characteristics)
        self.info_widget.setLayout(info_layout)
        self.info_widget.setVisible(False)

        self.layout.addWidget(self.info_widget)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.save_default_button)
        self.layout.addWidget(self.restore_default_button)
        self.layout.addWidget(self.power_label)
        self.layout.addLayout(power_zone_layout)

        grid_layout = QGridLayout()

        self.sliders = []
        self.color_buttons = []
        self.color_frames = []
        self.threshold_edits = []
        self.range_labels = []

        zone_names = [
            _("Récupération active"), _("Endurance"), _("Tempo"), _("Seuil"),
            _("VO2 max"), _("Anaérobique"), _("Neuromusculaire")
        ]

        for i in range(6):
            range_label = QLabel()
            threshold_edit = QLineEdit(str(self.notification_handler.zone_thresholds[i]))
            threshold_edit.setFixedWidth(50)
            threshold_edit.setValidator(QIntValidator(0, 500))
            threshold_edit.editingFinished.connect(self.create_threshold_edit_handler(i, threshold_edit, range_label))

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(500)
            slider.setValue(self.notification_handler.zone_thresholds[i])
            slider.valueChanged.connect(self.create_slider_change_handler(i, threshold_edit, range_label))

            color_button = QPushButton(_('Sélectionner Couleur Zone {index}').format(index=i + 1))
            color_button.clicked.connect(self.create_color_change_handler(i))

            color_frame = QFrame()
            color_frame.setFixedSize(20, 20)
            color_frame.setStyleSheet(f"background-color: rgb({self.notification_handler.zone_colors[i][0]}, {self.notification_handler.zone_colors[i][1]}, {self.notification_handler.zone_colors[i][2]});")

            self.sliders.append(slider)
            self.color_buttons.append(color_button)
            self.color_frames.append(color_frame)
            self.threshold_edits.append(threshold_edit)
            self.range_labels.append(range_label)

            grid_layout.addWidget(range_label, i, 0, 1, 2)
            grid_layout.addWidget(threshold_edit, i, 2)
            grid_layout.addWidget(slider, i, 3)
            grid_layout.addWidget(color_button, i, 4)
            grid_layout.addWidget(color_frame, i, 5)

        range_label_7 = QLabel()
        threshold_edit_7 = QLineEdit('N/A')
        threshold_edit_7.setFixedWidth(50)
        threshold_edit_7.setEnabled(False)

        color_button_7 = QPushButton(_('Sélectionner Couleur Zone {index}').format(index=7))
        color_button_7.clicked.connect(self.create_color_change_handler(6))

        color_frame_7 = QFrame()
        color_frame_7.setFixedSize(20, 20)
        color_frame_7.setStyleSheet(f"background-color: rgb({self.notification_handler.zone_colors[6][0]}, {self.notification_handler.zone_colors[6][1]}, {self.notification_handler.zone_colors[6][2]});")

        slider_7 = QSlider(Qt.Horizontal)
        slider_7.setMinimum(0)
        slider_7.setMaximum(500)
        slider_7.setValue(0)
        slider_7.setEnabled(False)

        grid_layout.addWidget(range_label_7, 6, 0, 1, 2)
        grid_layout.addWidget(threshold_edit_7, 6, 2)
        grid_layout.addWidget(slider_7, 6, 3)
        grid_layout.addWidget(color_button_7, 6, 4)
        grid_layout.addWidget(color_frame_7, 6, 5)

        self.sliders.append(slider_7)
        self.color_buttons.append(color_button_7)
        self.color_frames.append(color_frame_7)
        self.range_labels.append(range_label_7)
        self.layout.addLayout(grid_layout)

        self.update_ranges()

        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()
        menu_bar.clear()
        about_menu = menu_bar.addMenu(_("À propos"))

        toggle_action = QAction(_("Afficher/Masquer Infos UUID"), self)
        toggle_action.triggered.connect(self.toggle_info)
        about_menu.addAction(toggle_action)

        about_action = QAction(_("À propos de TrainerLED"), self)
        about_action.triggered.connect(self.show_about_dialog)
        about_menu.addAction(about_action)

        language_menu = menu_bar.addMenu(_("Langue"))

        lang_selector = QComboBox(self)
        lang_selector.addItem('Français', 'fr')
        lang_selector.addItem('English', 'en')
        lang_selector.setCurrentIndex(0 if current_language == 'fr' else 1)
        lang_selector.currentIndexChanged.connect(self.change_language)

        language_widget_action = QWidgetAction(self)
        language_widget_action.setDefaultWidget(lang_selector)
        language_menu.addAction(language_widget_action)

    def change_language(self, index):
        lang_code = 'fr' if index == 0 else 'en'
        print(f"Changement de langue demandé : {lang_code}")
        set_language(lang_code)
        self.notification_handler.default_language = lang_code  # Mémoriser la langue par défaut
        self.notification_handler.save_config()  # Sauvegarder la configuration
        self.retranslate_ui()

    def retranslate_ui(self):
        print(f"Retraduction de l'interface utilisateur")
        self.setWindowTitle('TrainerLED')
        self.search_button.setText(_('Rechercher Home Trainer'))
        self.start_button.setText(_('Démarrer'))
        self.stop_button.setText(_('Arrêter'))
        self.save_default_button.setText(_('Sauvegarder ce paramètre par défaut'))
        self.restore_default_button.setText(_('Restaurer les paramètres par défaut'))
        self.set_default_device_button.setText(_('Définir comme périphérique par défaut'))
        self.status_label.setText(_('En attente de connexion au périphérique'))
        self.power_label.setText(_('Puissance: N/A'))
        self.zone_label.setText(_('Zone de puissance: N/A'))

        for i, button in enumerate(self.color_buttons):
            button.setText(_('Sélectionner Couleur Zone {index}').format(index=i + 1))

        self.update_ranges()
        self.create_menu()

    def toggle_info(self):
        self.info_widget.setVisible(not self.info_widget.isVisible())

    async def search_devices_async(self):
        devices = await BleakScanner.discover()
        return [f"{device.name} - {device.address}" for device in devices]

    async def discover_services_and_characteristics(self, device_address):
        async with BleakClient(device_address) as client:
            services = await client.get_services()
            result = []
            for service in services:
                result.append(f"Service: {service.uuid}")
                for char in service.characteristics:
                    result.append(f"  Characteristic: {char.uuid}, Properties: {char.properties}")
            return result

    def search_devices(self):
        coro = self.search_devices_async()
        self.task_runner = AsyncTaskRunner(coro)
        self.task_runner.result_ready.connect(self.update_device_list)
        self.task_runner.start()

    def update_device_list(self, devices):
        self.device_list.clear()
        for device in devices:
            self.device_list.addItem(device)

    def device_selected(self, item):
        address = item.text().split(" - ")[1]
        self.HOME_TRAINER_MAC = address
        QMessageBox.information(self, _("Home Trainer Sélectionné"), f"{_('Adresse MAC')}: {address}")
        coro = self.discover_services_and_characteristics(address)
        self.task_runner = AsyncTaskRunner(coro)
        self.task_runner.result_ready.connect(self.update_service_characteristics)
        self.task_runner.start()

    def update_service_characteristics(self, result):
        self.service_characteristics.clear()
        for line in result:
            self.service_characteristics.append(line)

    def create_slider_change_handler(self, index, threshold_edit, range_label):
        def handler(value):
            threshold_edit.setText(str(value))
            self.notification_handler.set_zone_threshold(index, value)
            self.update_ranges()
        return handler

    def create_threshold_edit_handler(self, index, threshold_edit, range_label):
        def handler():
            value = int(threshold_edit.text())
            self.sliders[index].setValue(value)
            self.notification_handler.set_zone_threshold(index, value)
            self.update_ranges()
        return handler

    def create_color_change_handler(self, index):
        def handler():
            color = QColorDialog.getColor()
            if color.isValid():
                rgb = (color.red(), color.green(), color.blue())
                self.notification_handler.set_zone_color(index, rgb)
                self.color_frames[index].setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
        return handler

    def start_thread(self):
        global running
        if not self.HOME_TRAINER_MAC:
            QMessageBox.warning(self, _("Erreur"), _("Veuillez sélectionner un Home Trainer avant de démarrer."))
            return
        running = True
        self.async_thread = AsyncThread(self.notification_handler, self.HOME_TRAINER_MAC, SERVICE_UUID, CHARACTERISTIC_UUID, self.status_label)
        self.async_thread.start()
        zone_1_color = self.notification_handler.zone_colors[0]
        threading.Thread(target=set_led_color_with_transition, args=zone_1_color).start()

    def stop_thread(self):
        global running
        running = False
        if self.async_thread:
            self.async_thread.quit()
        threading.Thread(target=set_led_color_with_transition, args=(0, 0, 0)).start()

    def update_power(self, power):
        self.power_label.setText(f'{_("Puissance")}: {power} W')
        self.update_plot(power)

    def update_color(self, color_zone):
        color, zone = color_zone
        self.zone_label.setText(f'{_("Zone de puissance")}: {zone}')
        self.color_frame.setStyleSheet(f"background-color: rgb({color[0]}, {color[1]}, {color[2]});")

    def update_ranges(self):
        ranges = self.notification_handler.get_zone_ranges()
        zone_names = [
            _("Récupération active"), _("Endurance"), _("Tempo"), _("Seuil"),
            _("VO2 max"), _("Anaérobique"), _("Neuromusculaire")
        ]
        for i, (low, high) in enumerate(ranges):
            zone_name = zone_names[i]
            if high == float('inf'):
                range_text = _("Zone {index}").format(index=i + 1) + " " + _("({zone_name}): {low} W et plus").format(zone_name=zone_name, low=low)
            else:
                range_text = _("Zone {index}").format(index=i + 1) + " " + _("({zone_name}): {low} - {high} W").format(zone_name=zone_name, low=low, high=high)
            self.range_labels[i].setText(range_text)

    def save_defaults(self):
        self.notification_handler.save_config()

    def restore_defaults(self):
        self.notification_handler.restore_default_config()
        self.update_ranges()
        for i in range(6):
            self.sliders[i].setValue(self.notification_handler.zone_thresholds[i])
            self.color_frames[i].setStyleSheet(f"background-color: rgb({self.notification_handler.zone_colors[i][0]}, {self.notification_handler.zone_colors[i][1]}, {self.notification_handler.zone_colors[i][2]});")
        self.color_frames[6].setStyleSheet(f"background-color: rgb({self.notification_handler.zone_colors[6][0]}, {self.notification_handler.zone_colors[6][1]}, {self.notification_handler.zone_colors[6][2]});")

    def set_default_device(self):
        if self.HOME_TRAINER_MAC:
            self.notification_handler.set_default_device(self.HOME_TRAINER_MAC)
            QMessageBox.information(self, _("Périphérique par défaut"), f"{_('Périphérique par défaut enregistré')} : {self.HOME_TRAINER_MAC}")
        else:
            QMessageBox.warning(self, _("Erreur"), _("Veuillez sélectionner un périphérique avant de définir le périphérique par défaut."))

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(_("À propos de TrainerLED"))
        layout = QVBoxLayout()
        label = QLabel(
            _("<p>TrainerLED</p>"
              "<p>Cette application permet de contrôler la puissance et les LED de votre home trainer via Bluetooth, "
              "et d'afficher différentes zones de puissance avec des couleurs configurables.</p>"
              "<p>Pour plus d'informations, visitez notre dépôt GitHub : "
              "<a href='https://github.com/nicolasjouffroy/TrainerLED'>TrainerLED</a></p>")
        )
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec_()

    def init_plot(self):
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout.addWidget(self.canvas)
        self.xdata, self.ydata, self.colors = [], [], []

        self.ax.set_ylim(0, 300)
        self.ax.set_xlim(0, 50)
        self.ax.grid()

    def update_plot(self, power):
        self.ydata.append(power)
        self.xdata.append(len(self.ydata))
        self.colors.append(self.get_color_for_power(power))

        self.ax.clear()
        self.ax.grid()
        self.ax.set_xlim(max(0, self.xdata[-1] - 50), self.xdata[-1])

        self.ax.set_ylim(min(self.ydata) - 10, max(self.ydata) + 10)

        for i in range(1, len(self.xdata)):
            self.ax.plot(self.xdata[i-1:i+1], self.ydata[i-1:i+1], color=self.colors[i-1], lw=2)

        self.canvas.draw()

    def get_color_for_power(self, power):
        for i, threshold in enumerate(self.notification_handler.zone_thresholds):
            if power <= threshold:
                return [c / 255 for c in self.notification_handler.zone_colors[i]]
        return [c / 255 for c in self.notification_handler.zone_colors[-1]]

if __name__ == '__main__':
    print("Lancement de l'application")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
