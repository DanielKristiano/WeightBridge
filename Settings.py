from PySide6.QtCore import (QCoreApplication, QRect, QMetaObject, Qt, Signal, QObject)
from PySide6.QtGui import (QAction, QIcon)
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
                               QMainWindow, QMenu, QMenuBar, QPushButton,
                               QSizePolicy, QStatusBar, QWidget, QMessageBox,
                               QVBoxLayout, QHBoxLayout, QScrollArea, QComboBox,
                               QCheckBox, QSpinBox, QTabWidget)
import json
import os
import copy
import sys


class SettingsSignals(QObject):
    settingsChanged = Signal(dict)


class DynamicSettingsField:
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECTION = "selection"

    def __init__(self, key, label, field_type, required=False, default_value=None, options=None):
        self.key = key
        self.label = label
        self.field_type = field_type
        self.required = required
        self.default_value = default_value
        self.options = options or []
        self.widget = None

    def create_widget(self, parent):
        if self.field_type == self.TEXT:
            self.widget = QLineEdit(parent)
            if self.default_value:
                self.widget.setText(str(self.default_value))
        elif self.field_type == self.NUMBER:
            self.widget = QSpinBox(parent)
            if self.default_value is not None:
                self.widget.setValue(int(self.default_value))
        elif self.field_type == self.BOOLEAN:
            self.widget = QCheckBox(parent)
            if self.default_value:
                self.widget.setChecked(bool(self.default_value))
        elif self.field_type == self.SELECTION:
            self.widget = QComboBox(parent)
            if self.options:
                self.widget.addItems(self.options)
            if self.default_value and self.default_value in self.options:
                self.widget.setCurrentText(self.default_value)
        return self.widget

    def get_value(self):
        if self.field_type == self.TEXT:
            return self.widget.text()
        elif self.field_type == self.NUMBER:
            return self.widget.value()
        elif self.field_type == self.BOOLEAN:
            return self.widget.isChecked()
        elif self.field_type == self.SELECTION:
            return self.widget.currentText()
        return None

    def set_value(self, value):
        if not self.widget:
            return

        if self.field_type == self.TEXT:
            self.widget.setText(str(value))
        elif self.field_type == self.NUMBER:
            self.widget.setValue(int(value))
        elif self.field_type == self.BOOLEAN:
            self.widget.setChecked(bool(value))
        elif self.field_type == self.SELECTION and value in self.options:
            self.widget.setCurrentText(value)


class SettingsCategory:

    def __init__(self, name, fields=None):
        self.name = name
        self.fields = fields or []

    def add_field(self, field):
        self.fields.append(field)


class Ui_Settings(object):
    def setupUi(self, Settings):
        # Create signals object
        self.signals = SettingsSignals()

        # Store reference to parent window
        self.settings_window = Settings

        # Configuration file path - UPDATED to match database_handler.py
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            self.config_path = os.path.join(base_dir, "config.json")
        else:
            self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

        # Default settings structure
        self.categories = [
            SettingsCategory("General", [
                DynamicSettingsField("comcode", "comcode", DynamicSettingsField.TEXT, required=True),
                DynamicSettingsField("bacode", "bacode", DynamicSettingsField.TEXT, required=True),
            ]),
        ]

        # Konfigurasi utama jendela
        Settings.setObjectName("Settings")
        Settings.resize(800, 600)

        # Widget utama
        self.centralwidget = QWidget(Settings)
        self.centralwidget.setObjectName("centralwidget")

        # Layout utama
        self.main_layout = QVBoxLayout(self.centralwidget)

        # Tab widget untuk kategorisasi
        self.tab_widget = QTabWidget(self.centralwidget)
        self.main_layout.addWidget(self.tab_widget)

        # Setup tab untuk setiap kategori
        for category in self.categories:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            # Scroll area untuk kategori dengan banyak setting
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)

            # Buat field untuk setiap setting
            for field in category.fields:
                field_layout = QHBoxLayout()

                # Label
                label = QLabel(field.label)
                label.setMinimumWidth(150)
                field_layout.addWidget(label)

                # Widget input
                widget = field.create_widget(scroll_content)
                field_layout.addWidget(widget)

                # Indikator required
                if field.required:
                    required_label = QLabel("*")
                    required_label.setStyleSheet("color: red;")
                    field_layout.addWidget(required_label)

                # Tambahkan field ke layout
                scroll_layout.addLayout(field_layout)

            # Spacer di bagian bawah
            scroll_layout.addStretch()

            # Set scroll content
            scroll_area.setWidget(scroll_content)
            tab_layout.addWidget(scroll_area)

            # Tambahkan tab ke widget
            self.tab_widget.addTab(tab, category.name)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Tombol Cancel dan Save
        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.setObjectName("btnCancel")
        self.btnCancel.clicked.connect(self.close_settings)
        button_layout.addWidget(self.btnCancel)

        self.btnSave = QPushButton("Save")
        self.btnSave.setObjectName("btnSave")
        self.btnSave.clicked.connect(self.save_settings)
        button_layout.addWidget(self.btnSave)

        # Tambahkan button layout ke main layout
        self.main_layout.addLayout(button_layout)

        # Set widget utama
        Settings.setCentralWidget(self.centralwidget)

        # Menubar
        self.menubar = QMenuBar(Settings)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))

        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuSettings.setTitle(QCoreApplication.translate("Settings", "Settings"))

        Settings.setMenuBar(self.menubar)

        # Statusbar
        self.statusbar = QStatusBar(Settings)
        self.statusbar.setObjectName("statusbar")
        Settings.setStatusBar(self.statusbar)

        # Add action to menu
        self.actionResetDefaults = QAction(Settings)
        self.actionResetDefaults.setText("Reset to Defaults")
        self.actionResetDefaults.triggered.connect(self.reset_to_defaults)
        self.menuSettings.addAction(self.actionResetDefaults)

        # Add menu to menubar
        self.menubar.addAction(self.menuSettings.menuAction())

        # Load existing settings
        self.load_settings()

    def save_settings(self):
        settings_data = {}
        missing_required = []

        # Load existing settings to preserve comcode and bacode
        existing_settings = {}
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as config_file:
                    existing_settings = json.load(config_file)
        except Exception as e:
            self.statusbar.showMessage(f"Error loading existing settings: {str(e)}", 5000)

        # Collect all settings values
        for category in self.categories:
            for field in category.fields:
                value = field.get_value()

                # Special handling for comcode and bacode - never clear them
                if field.key in ["comcode", "bacode"]:
                    # If current value is empty but there's an existing value, use the existing one
                    if (value is None or (
                            isinstance(value, str) and value.strip() == "")) and field.key in existing_settings and \
                            existing_settings[field.key]:
                        value = existing_settings[field.key]
                    # Still check if it's required and missing
                    elif field.required and (value is None or (isinstance(value, str) and value.strip() == "")):
                        missing_required.append(field.label)
                # Handle other fields normally
                elif field.required and (value is None or (isinstance(value, str) and value.strip() == "")):
                    missing_required.append(field.label)

                settings_data[field.key] = value

        # Validate required fields
        if missing_required:
            QMessageBox.warning(
                self.settings_window,
                "Validation Error",
                f"The following required fields must be filled: {', '.join(missing_required)}"
            )
            return

        # Merge new settings with existing settings
        merged_data = {**existing_settings, **settings_data}

        # Remove last_login if it exists
        if "last_login" in merged_data:
            del merged_data["last_login"]

        # Save to file
        try:
            with open(self.config_path, 'w', encoding='utf-8') as config_file:
                json.dump(merged_data, config_file, indent=4)

            # Show success message
            self.statusbar.showMessage("Settings saved successfully!", 3000)

            # Emit signal that settings changed with new settings
            self.signals.settingsChanged.emit(copy.deepcopy(settings_data))

            # Close the settings window
            self.settings_window.close()
        except Exception as e:
            QMessageBox.critical(
                self.settings_window,
                "Error Saving Settings",
                f"Could not save settings: {str(e)}"
            )

    def remove_settings(self, keys_to_remove):
        try:
            # Baca config.json
            config_data = self.get_settings()

            # Hapus key yang disebutkan
            for key in keys_to_remove:
                config_data.pop(key, None)

            # Simpan kembali config.json tanpa key yang dihapus
            with open(self.config_path, 'w', encoding='utf-8') as config_file:
                json.dump(config_data, config_file, indent=4)

            self.logger.info(f"Removed settings: {keys_to_remove}")
            return True
        except Exception as e:
            self.logger.error(f"Error removing settings: {str(e)}")
            return False

    def load_settings(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as config_file:
                    settings = json.load(config_file)

                    # Apply values to all fields
                    for category in self.categories:
                        for field in category.fields:
                            if field.key in settings:
                                field.set_value(settings[field.key])
        except Exception as e:
            self.statusbar.showMessage(f"Error loading settings: {str(e)}", 5000)

    def close_settings(self):
        self.settings_window.close()

    def reset_to_defaults(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Reset all settings to default values?")
        msg.setInformativeText("This action cannot be undone.")
        msg.setWindowTitle("Confirm Reset")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        if msg.exec() == QMessageBox.Yes:
            # Load existing settings to preserve comcode and bacode
            existing_settings = {}
            try:
                if os.path.exists(self.config_path):
                    with open(self.config_path, 'r', encoding='utf-8') as config_file:
                        existing_settings = json.load(config_file)
            except Exception:
                pass

            for category in self.categories:
                for field in category.fields:
                    # Don't reset comcode and bacode fields
                    if field.key in ["comcode", "bacode"] and field.key in existing_settings:
                        field.set_value(existing_settings[field.key])
                    else:
                        field.set_value(field.default_value)

            self.statusbar.showMessage(
                "Settings have been reset to defaults (except comcode and bacode). Save to apply changes.", 5000)

    @staticmethod
    def get_settings():
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            config_path = os.path.join(base_dir, "config.json")
        else:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as config_file:
                    return json.load(config_file)
            return {}
        except Exception:
            return {}

    @staticmethod
    def are_settings_valid():
        settings = Ui_Settings.get_settings()

        # List of required keys (can be expanded)
        required_keys = ["comcode", "bacode"]

        for key in required_keys:
            if key not in settings or not settings[key]:
                return False

        return True

    @staticmethod
    def add_settings_category(settings_window, category_name, fields):
        if not hasattr(settings_window, 'ui'):
            return False

        ui = settings_window.ui

        # Create new category
        new_category = SettingsCategory(category_name, fields)
        ui.categories.append(new_category)

        # Create tab for the new category
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Create fields
        for field in fields:
            field_layout = QHBoxLayout()

            # Label
            label = QLabel(field.label)
            label.setMinimumWidth(150)
            field_layout.addWidget(label)

            # Widget
            widget = field.create_widget(scroll_content)
            field_layout.addWidget(widget)

            # Required indicator
            if field.required:
                required_label = QLabel("*")
                required_label.setStyleSheet("color: red;")
                field_layout.addWidget(required_label)

            scroll_layout.addLayout(field_layout)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)

        # Add new tab
        ui.tab_widget.addTab(tab, category_name)

        return True