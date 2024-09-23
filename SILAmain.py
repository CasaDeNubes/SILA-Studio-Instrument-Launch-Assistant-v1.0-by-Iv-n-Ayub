import sys
import subprocess
import json
import os
import psutil
import ctypes
import csv
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
                             QHBoxLayout, QFrame, QMainWindow, QStatusBar, QTextEdit, 
                             QFileDialog, QScrollArea, QMessageBox, QInputDialog, QDialog, QSpinBox)
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QTimer
import random

class SILAApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.instruments = {}
        self.json_file_path = os.path.join(os.path.expanduser('~'), 'instruments.json')
        self.running_processes = {}
        self.initUI()
        self.load_instruments()

    def initUI(self):
        self.setWindowTitle('Studio Instrument Launch Assistant')
        self.setFixedSize(600, 400)
        self.setWindowIcon(QIcon('icon.png'))
        self.setPalette(self.create_palette())

        layout = QVBoxLayout()
        layout.addWidget(self.create_welcome_label())
        layout.addWidget(self.create_separator_line())

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.instrument_widget = QWidget()
        self.instrument_layout = QVBoxLayout(self.instrument_widget)
        self.instrument_widget.setLayout(self.instrument_layout)
        self.scroll_area.setWidget(self.instrument_widget)
        layout.addWidget(self.scroll_area)

        self.log_area = self.create_log_area()
        layout.addWidget(self.create_scroll_area(self.log_area))
        self.button_layout = self.create_button_layout()
        layout.addLayout(self.button_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.check_processes_timer = QTimer(self)
        self.check_processes_timer.timeout.connect(self.check_running_processes)
        self.check_processes_timer.start(1000)

    def create_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        return palette

    def create_welcome_label(self):
        label = QLabel("SILA V1.0 - Iván Ayub | negroayub97@gmail.com", self)
        label.setFont(QFont('Arial', 13, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: yellow;")
        return label

    def create_separator_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: gray;")
        return line

    def create_log_area(self):
        log_area = QTextEdit(self)
        log_area.setReadOnly(True)
        log_area.setFont(QFont('Consolas', 10))
        log_area.setStyleSheet("background-color: #1C1C1C; color: yellow;")
        return log_area

    def create_scroll_area(self, widget):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget)
        return scroll_area

    def create_button_layout(self):
        button_layout = QHBoxLayout()
        button_style = self.create_button_style()

        add_button = self.create_button("Add Instrument", button_style, self.add_instrument)
        button_layout.addWidget(add_button)

        search_button = self.create_button("Search Instrument", button_style, self.search_instrument)
        button_layout.addWidget(search_button)

        export_button = self.create_button("Export to CSV", button_style, self.export_to_csv)
        button_layout.addWidget(export_button)

        settings_button = self.create_button("Settings", button_style, self.open_settings)
        button_layout.addWidget(settings_button)

        return button_layout

    def create_button_style(self):
        return "QPushButton { background-color: #444444; color: white; padding: 10px; border-radius: 5px; }" \
               "QPushButton:hover { background-color: #666666; }"

    def create_button(self, text, style, callback):
        button = QPushButton(text, self)
        button.setStyleSheet(style)
        button.clicked.connect(lambda: self.indicate_button_press(button, callback))
        return button

    def indicate_button_press(self, button, callback):
        button.setStyleSheet("background-color: #888888; color: white; padding: 10px; border-radius: 5px;")
        callback()
        QTimer.singleShot(200, lambda: self.restore_button(button))

    def restore_button(self, button):
        button.setStyleSheet(self.create_button_style())

    def load_instruments(self):
        if not os.path.exists(self.json_file_path):
            self.instruments = {}
            self.save_instruments()
            return

        try:
            with open(self.json_file_path, 'r') as f:
                self.instruments = json.load(f)
            self.update_instrument_buttons()
        except json.JSONDecodeError:
            self.log_error("Error decoding JSON. Creating a new instruments file.")
            self.instruments = {}
            self.save_instruments()
        except Exception as e:
            self.log_error(f"Error loading instruments: {e}. Creating a new one.")
            self.instruments = {}
            self.save_instruments()

    def update_instrument_buttons(self):
        self.clear_instrument_buttons()
        for instrument_name, exe_path in self.instruments.items():
            self.create_instrument_button(instrument_name, exe_path)

    def clear_instrument_buttons(self):
        while self.instrument_layout.count():
            widget = self.instrument_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

    def create_instrument_button(self, instrument_name, exe_path):
        button_layout = QHBoxLayout()
        
        status_indicator = QLabel()
        status_indicator.setFixedSize(10, 10)
        status_indicator.setStyleSheet("background-color: red; border-radius: 5px;")
        
        display_name = instrument_name.replace('.exe', '')
        button_style = "background-color: #444444; color: white;"

        button = self.create_button(display_name, button_style, lambda: self.launch_instrument(exe_path, display_name, status_indicator))
        button_layout.addWidget(button)
        button_layout.addWidget(status_indicator)

        remove_button = self.create_button("Remove", self.create_button_style(), lambda: self.remove_instrument(instrument_name, button_layout))
        button_layout.addWidget(remove_button)

        self.instrument_layout.addLayout(button_layout)

    def add_instrument(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Instrument Executable', '', 'Executable Files (*.exe)')
        if file_path:
            instrument_name = os.path.basename(file_path)
            if instrument_name not in self.instruments:
                self.instruments[instrument_name] = file_path
                self.log_area.append(f"Instrument added: {instrument_name.replace('.exe', '')}")
                self.save_instruments()
                self.update_instrument_buttons()
            else:
                self.log_area.append(f"The instrument {instrument_name} already exists.")

    def remove_instrument(self, instrument_name, button_layout):
        if instrument_name in self.instruments:
            del self.instruments[instrument_name]
            self.log_area.append(f"Instrument removed: {instrument_name}")
            self.save_instruments()
            self.clear_instrument_buttons()
            self.update_instrument_buttons()

    def launch_instrument(self, path_to_exe, name, indicator):
        if self.is_instrument_running(name):
            self.log_area.append(f"{name} is already running.")
            return

        if not os.path.isfile(path_to_exe):
            self.log_error(f"Executable not found: {path_to_exe}")
            return

        try:
            process = subprocess.Popen([path_to_exe], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running_processes[name] = (process, indicator)
            indicator.setStyleSheet("background-color: green; border-radius: 5px;")
            self.log_area.append(f"{name} launched.")
            self.status_bar.showMessage(f"Instrument {name} launched.")
        except Exception as e:
            self.log_error(f"Error launching {name}: {e}")

    def check_running_processes(self):
        for name, (process, indicator) in list(self.running_processes.items()):
            if process.poll() is not None:
                del self.running_processes[name]
                indicator.setStyleSheet("background-color: red; border-radius: 5px;")
                self.log_area.append(f"{name} has been closed.")

    def is_instrument_running(self, name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == name:
                return True
        return False

    def export_to_csv(self):
        csv_file_path, _ = QFileDialog.getSaveFileName(self, 'Save CSV File', '', 'CSV Files (*.csv)')
        if csv_file_path:
            try:
                with open(csv_file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Instrument Name', 'Path'])
                    for name, path in self.instruments.items():
                        writer.writerow([name, path])
                self.log_area.append("Instruments exported to CSV successfully.")
            except Exception as e:
                self.log_error(f"Error exporting to CSV: {e}")

    def search_instrument(self):
        search_text, ok = QInputDialog.getText(self, 'Search Instrument', 'Enter instrument name:')
        if ok and search_text:
            filtered_instruments = {name: exe for name, exe in self.instruments.items() if search_text.lower() in name.lower()}
            self.clear_instrument_buttons()
            for name, exe in filtered_instruments.items():
                self.create_instrument_button(name, exe)
            self.log_area.append(f"Filtered instruments for: {search_text}")

    def open_settings(self):
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle('Settings')
        layout = QVBoxLayout()
        
        font_size_label = QLabel("Font Size:", self)
        self.font_size_input = QSpinBox(self)
        self.font_size_input.setValue(10)
        
        layout.addWidget(font_size_label)
        layout.addWidget(self.font_size_input)
        
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        settings_dialog.setLayout(layout)
        settings_dialog.exec_()

    def save_settings(self):
        font_size = self.font_size_input.value()
        self.log_area.setFont(QFont('Consolas', font_size))
        self.log_area.append(f"Font size set to {font_size}.")

    def load_instruments(self):
        if not os.path.exists(self.json_file_path):
            self.instruments = {}
            self.save_instruments()
            return

        try:
            with open(self.json_file_path, 'r') as f:
                self.instruments = json.load(f)
            self.update_instrument_buttons()
        except json.JSONDecodeError:
            self.log_error("Error decoding JSON. Creating a new instruments file.")
            self.instruments = {}
            self.save_instruments()
        except Exception as e:
            self.log_error(f"Error loading instruments: {e}. Creating a new one.")
            self.instruments = {}
            self.save_instruments()

    def save_instruments(self):
        try:
            with open(self.json_file_path, 'w') as f:
                json.dump(self.instruments, f, indent=4)
        except Exception as e:
            self.log_error(f"Error saving instruments: {e}")

    def log_error(self, message):
        self.log_area.append(f"Error: {message}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SILAApp()
    ex.show()
    sys.exit(app.exec_())
