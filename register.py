import sys
import json
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFrame, QSpacerItem, QSizePolicy, QMessageBox,
                               QComboBox)
from PySide6.QtCore import Qt, QSize, Signal, QObject
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette


class ThemeManager(QObject):
    theme_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.dark_mode = False


class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme)
        self.api_url = "http://127.0.0.1:8000/api/users"

        # Setting Window attributes
        self.setWindowTitle("Weight Bridge - Register")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1200, 800)
        self.setWindowFlag(Qt.FramelessWindowHint, False)

        # Set showMaximized
        self.showMaximized()

        # Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create container
        self.container = QWidget()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.addWidget(self.container)

        # Theme toggle
        theme_container = QHBoxLayout()
        theme_container.setContentsMargins(0, 0, 0, 20)

        self.theme_button = QPushButton("🌙 Mode Gelap")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setMinimumWidth(120)
        self.theme_button.clicked.connect(self.toggle_theme)

        theme_container.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        theme_container.addWidget(self.theme_button)

        container_layout.addLayout(theme_container)

        # Create registration form
        self.form_container = QFrame()
        self.form_container.setObjectName("formContainer")
        self.form_container.setFrameShape(QFrame.StyledPanel)
        self.form_container.setFixedWidth(450)
        self.form_container.setMinimumHeight(580)
        self.form_container.setMaximumHeight(680)

        # Center the form in the container
        container_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        container_layout.addWidget(self.form_container, 0, Qt.AlignCenter)
        container_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Form layout
        form_layout = QVBoxLayout(self.form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setText("📝")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setObjectName("logoLabel")

        # Welcome
        self.welcome_label = QLabel("Daftar Akun Baru")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setObjectName("welcomeLabel")

        # Subtitle
        self.subtitle_label = QLabel("Silakan lengkapi data berikut untuk membuat akun")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setObjectName("subtitleLabel")

        # Username
        self.username_label = QLabel("Username")
        self.username_label.setObjectName("fieldLabel")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username Anda")
        self.username_input.setMinimumHeight(40)
        self.username_input.setObjectName("inputField")
        self.username_input.returnPressed.connect(self.register)

        # Password
        self.password_label = QLabel("Password")
        self.password_label.setObjectName("fieldLabel")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Masukkan password Anda")
        self.password_input.setMinimumHeight(40)
        self.password_input.setObjectName("inputField")
        self.password_input.returnPressed.connect(self.register)

        # Confirm Password
        self.confirm_password_label = QLabel("Konfirmasi Password")
        self.confirm_password_label.setObjectName("fieldLabel")

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Masukkan ulang password Anda")
        self.confirm_password_input.setMinimumHeight(40)
        self.confirm_password_input.setObjectName("inputField")
        self.confirm_password_input.returnPressed.connect(self.register)

        # Show/Hide Password
        self.show_password_button = QPushButton("Tampilkan")
        self.show_password_button.setObjectName("showPasswordButton")
        self.show_password_button.setCursor(Qt.PointingHandCursor)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)

        password_container = QHBoxLayout()
        password_container.addWidget(self.password_input)
        password_container.addWidget(self.show_password_button)

        # Register button
        self.register_button = QPushButton("Daftar")
        self.register_button.setMinimumHeight(45)
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setObjectName("registerButton")

        # Login link
        login_layout = QHBoxLayout()
        self.login_label = QLabel("Sudah punya akun?")
        self.login_label.setObjectName("loginLabel")

        self.login_link = QLabel("Masuk sekarang")
        self.login_link.setObjectName("loginLink")
        self.login_link.setCursor(Qt.PointingHandCursor)
        self.login_link.mousePressEvent = self.go_to_login

        login_layout.addWidget(self.login_label)
        login_layout.addWidget(self.login_link)
        login_layout.setAlignment(Qt.AlignCenter)

        # Add widgets to form layout
        form_layout.addWidget(self.logo_label)
        form_layout.addWidget(self.welcome_label)
        form_layout.addWidget(self.subtitle_label)
        form_layout.addItem(QSpacerItem(20, 10))
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addItem(QSpacerItem(20, 5))
        form_layout.addWidget(self.password_label)
        form_layout.addLayout(password_container)
        form_layout.addItem(QSpacerItem(20, 5))
        form_layout.addWidget(self.confirm_password_label)
        form_layout.addWidget(self.confirm_password_input)
        form_layout.addItem(QSpacerItem(20, 5))
        form_layout.addItem(QSpacerItem(20, 10))
        form_layout.addWidget(self.register_button)
        form_layout.addItem(QSpacerItem(20, 5))
        form_layout.addLayout(login_layout)
        form_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Connect signals
        self.register_button.clicked.connect(self.register)

        # Set light theme by default
        self.apply_theme(False)

    def go_to_login(self, event):
        from login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def toggle_theme(self):
        new_mode = not self.theme_manager.dark_mode
        self.theme_manager.dark_mode = new_mode
        self.theme_manager.theme_changed.emit(new_mode)

        # Update button text
        if new_mode:
            self.theme_button.setText("☀️ Mode Terang")
        else:
            self.theme_button.setText("🌙 Mode Gelap")

    def apply_theme(self, dark_mode):
        if dark_mode:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#1e1e1e"))
            self.setPalette(palette)

            # Logo dan Welcome
            self.logo_label.setStyleSheet("font-size: 36px;")
            self.welcome_label.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #ffffff; margin-top: 5px;")

            self.form_container.setStyleSheet("""
                #formContainer {
                    background-color: #2d2d2d;
                    border-radius: 8px;
                    border: 1px solid #3d3d3d;
                }
            """)

            self.theme_button.setStyleSheet("""
                #themeButton {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                #themeButton:hover {
                    background-color: #4d4d4d;
                }
            """)

            self.subtitle_label.setStyleSheet(
                "font-size: 14px; color: #b0b0b0; margin-bottom: 10px;")
            self.username_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d0d0d0;")
            self.password_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d0d0d0;")
            self.confirm_password_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d0d0d0;")

            self.username_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 8px 12px;
                    background-color: #3d3d3d;
                    color: #ffffff;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #007acc;
                    background-color: #333333;
                }
            """)

            self.password_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 8px 12px;
                    background-color: #3d3d3d;
                    color: #ffffff;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #007acc;
                    background-color: #333333;
                }
            """)

            self.confirm_password_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 8px 12px;
                    background-color: #3d3d3d;
                    color: #ffffff;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #007acc;
                    background-color: #333333;
                }
            """)

            self.show_password_button.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    color: #d0d0d0;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                    color: #ffffff;
                }
            """)

            self.register_button.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0088ee;
                }
            """)

            self.login_label.setStyleSheet("color: #b0b0b0; font-size: 13px;")
            self.login_link.setStyleSheet("color: #007acc; font-size: 13px; font-weight: bold;")

        else:
            # Light Theme
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#f5f5f5"))
            self.setPalette(palette)

            # Logo dan Welcome
            self.logo_label.setStyleSheet("font-size: 36px;")
            self.welcome_label.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #333333; margin-top: 5px;")

            self.form_container.setStyleSheet("""
                #formContainer {
                    background-color: #ffffff;
                    border-radius: 8px;
                    border: 1px solid #dddddd;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
            """)

            self.theme_button.setStyleSheet("""
                #themeButton {
                    background-color: #eeeeee;
                    color: #333333;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                #themeButton:hover {
                    background-color: #dddddd;
                }
            """)

            self.subtitle_label.setStyleSheet(
                "font-size: 14px; color: #666666; margin-bottom: 10px;")
            self.username_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")
            self.password_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")
            self.confirm_password_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")

            self.username_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #dddddd;
                    border-radius: 4px;
                    padding: 8px 12px;
                    background-color: #ffffff;
                    color: #333333;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #007acc;
                    background-color: #f8f8f8;
                }
            """)

            self.password_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #dddddd;
                    border-radius: 4px;
                    padding: 8px 12px;
                    background-color: #ffffff;
                    color: #333333;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #007acc;
                    background-color: #f8f8f8;
                }
            """)

            self.confirm_password_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #dddddd;
                    border-radius: 4px;
                    padding: 8px 12px;
                    background-color: #ffffff;
                    color: #333333;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #007acc;
                    background-color: #f8f8f8;
                }
            """)

            self.show_password_button.setStyleSheet("""
                QPushButton {
                    background-color: #eeeeee;
                    color: #555555;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #dddddd;
                    color: #333333;
                }
            """)

            self.register_button.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0088ee;
                }
            """)

            self.login_label.setStyleSheet("color: #666666; font-size: 13px;")
            self.login_link.setStyleSheet("color: #007acc; font-size: 13px; font-weight: bold;")

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_button.setText("Sembunyikan")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            self.show_password_button.setText("Tampilkan")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Validate form data
        if not username:
            QMessageBox.warning(self, "Peringatan", "Username tidak boleh kosong.")
            return

        if not password:
            QMessageBox.warning(self, "Peringatan", "Password tidak boleh kosong.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Peringatan", "Password dan konfirmasi password tidak sama.")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Peringatan", "Password harus minimal 6 karakter.")
            return

        user_data = {
            "username": username,
            "password": password,
        }

        try:
            # Make API request to register user
            headers = {'Content-Type': 'application/json'}
            response = requests.post(self.api_url, data=json.dumps(user_data), headers=headers)

            # Check response status
            if response.status_code == 201 or response.status_code == 200:
                QMessageBox.information(self, "Sukses", "Registrasi berhasil. Silakan login.")
                self.go_to_login(None)
            else:
                error_message = "Registrasi gagal."
                try:
                    response_data = response.json()
                    if "message" in response_data:
                        error_message = response_data["message"]
                    elif "error" in response_data:
                        error_message = response_data["error"]
                except:
                    error_message = f"Status code: {response.status_code}"

                QMessageBox.warning(self, "Peringatan", f"Registrasi gagal: {error_message}")

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error",
                                 "Tidak dapat terhubung ke server. Periksa koneksi Anda atau pastikan server API sedang berjalan.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = RegisterWindow()
    window.show()

    sys.exit(app.exec())