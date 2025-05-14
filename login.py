import sys
import json
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFrame, QSpacerItem, QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, QSize, Signal, QObject, QTimer
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from main import MainWindow


class ThemeManager(QObject):
    theme_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.dark_mode = False


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme)

        # Setting Window properties
        self.setWindowTitle("Weight Bridge")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1200, 800)
        self.setWindowFlag(Qt.FramelessWindowHint, False)

        # Set showMaximized
        self.showMaximized()

        # Widget dan Layout
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

        # Create login
        self.form_container = QFrame()
        self.form_container.setObjectName("formContainer")
        self.form_container.setFrameShape(QFrame.StyledPanel)
        self.form_container.setFixedWidth(450)
        self.form_container.setMinimumHeight(520)
        self.form_container.setMaximumHeight(620)

        # Center the form in the container
        container_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        container_layout.addWidget(self.form_container, 0, Qt.AlignCenter)
        container_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Form layout
        form_layout = QVBoxLayout(self.form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        # logo
        self.logo_label = QLabel()
        self.logo_label.setText("🔐")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setObjectName("logoLabel")

        # Selamat Datang
        self.welcome_label = QLabel("Selamat Datang")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setObjectName("welcomeLabel")

        # Ukuran font
        self.subtitle_label = QLabel("Silakan masuk ke akun Anda")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setObjectName("subtitleLabel")

        # Username
        self.username_label = QLabel("Username")
        self.username_label.setObjectName("fieldLabel")

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username Anda")
        self.username_input.setMinimumHeight(40)
        self.username_input.setObjectName("inputField")
        self.username_input.setEchoMode(QLineEdit.Normal)

        # Trigger login saat Enter ditekan
        self.username_input.returnPressed.connect(self.login)

        # Password
        self.password_label = QLabel("Password")
        self.password_label.setObjectName("fieldLabel")

        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Masukkan password Anda")
        self.password_input.setMinimumHeight(40)
        self.password_input.setObjectName("inputField")

        # Trigger login saat Enter ditekan
        self.password_input.returnPressed.connect(self.login)

        # Show/Hide Password
        self.show_password_button = QPushButton("Tampilkan")
        self.show_password_button.setObjectName("showPasswordButton")
        self.show_password_button.setCursor(Qt.PointingHandCursor)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)

        password_container = QHBoxLayout()
        password_container.addWidget(self.password_input)
        password_container.addWidget(self.show_password_button)

        # Lupa Password
        self.forgot_password = QLabel("Lupa password?")
        self.forgot_password.setObjectName("forgotPassword")
        self.forgot_password.setAlignment(Qt.AlignRight)
        self.forgot_password.setCursor(Qt.PointingHandCursor)

        # Login button
        self.login_button = QPushButton("Masuk")
        self.login_button.setMinimumHeight(45)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setObjectName("loginButton")

        # Register link
        register_layout = QHBoxLayout()
        self.register_label = QLabel("Belum punya akun?")
        self.register_label.setObjectName("registerLabel")

        self.register_link = QLabel("Daftar sekarang")
        self.register_link.mousePressEvent = self.go_to_register
        self.register_link.setObjectName("registerLink")
        self.register_link.setCursor(Qt.PointingHandCursor)

        register_layout.addWidget(self.register_label)
        register_layout.addWidget(self.register_link)
        register_layout.setAlignment(Qt.AlignCenter)

        # tambahan widgets to form layout
        form_layout.addWidget(self.logo_label)
        form_layout.addWidget(self.welcome_label)
        form_layout.addWidget(self.subtitle_label)
        form_layout.addItem(QSpacerItem(20, 10))
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addItem(QSpacerItem(20, 5))
        form_layout.addWidget(self.password_label)
        form_layout.addLayout(password_container)
        form_layout.addWidget(self.forgot_password)
        form_layout.addItem(QSpacerItem(20, 10))
        form_layout.addWidget(self.login_button)
        form_layout.addItem(QSpacerItem(20, 5))
        form_layout.addLayout(register_layout)
        form_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # koneksi sinyal
        self.login_button.clicked.connect(self.login)

        # light theme
        self.apply_theme(False)

        # Show login warning
        QTimer.singleShot(500, self.showLoginWarning)

    def showLoginWarning(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Peringatan")
        msg_box.setText("Anda harus login terlebih dahulu untuk melanjutkan.")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # message box
        if self.theme_manager.dark_mode:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0086e0;
                }
            """)
        else:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                }
                QLabel {
                    color: #202020;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0086f0;
                }
            """)

        msg_box.exec()

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
            # Dark Theme
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

            self.show_password_button.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    color: #b0b0b0;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
            """)

            self.forgot_password.setStyleSheet("font-size: 13px; color: #007acc; text-decoration: none;")

            self.login_button.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0086e0;
                }
                QPushButton:pressed {
                    background-color: #0067a9;
                }
            """)

            self.register_label.setStyleSheet("font-size: 13px; color: #b0b0b0;")
            self.register_link.setStyleSheet("font-size: 13px; color: #007acc; text-decoration: none;")

        else:
            # Light Theme
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#f3f3f3"))
            self.setPalette(palette)

            # Ukuran Logo dan Welcome
            self.logo_label.setStyleSheet("font-size: 36px;")
            self.welcome_label.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #202020; margin-top: 5px;")

            self.form_container.setStyleSheet("""
                #formContainer {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }
            """)

            self.theme_button.setStyleSheet("""
                #themeButton {
                    background-color: #f0f0f0;
                    color: #404040;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                #themeButton:hover {
                    background-color: #e5e5e5;
                }
            """)

            self.subtitle_label.setStyleSheet(
                "font-size: 14px; color: #707070; margin-bottom: 10px;")
            self.username_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #505050;")
            self.password_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #505050;")

            self.username_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 8px 12px;
                    background-color: #fafafa;
                    color: #000000;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #0078d7;
                    background-color: white;
                }
            """)

            self.password_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 8px 12px;
                    background-color: #fafafa;
                    color: #000000;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #0078d7;
                    background-color: white;
                }
            """)

            self.show_password_button.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    color: #505050;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e5e5e5;
                }
            """)

            self.forgot_password.setStyleSheet("font-size: 13px; color: #0078d7; text-decoration: none;")

            self.login_button.setStyleSheet("""
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0086f0;
                }
                QPushButton:pressed {
                    background-color: #006bc7;
                }
            """)

            self.register_label.setStyleSheet("font-size: 13px; color: #707070;")
            self.register_link.setStyleSheet("font-size: 13px; color: #0078d7; text-decoration: none;")

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_button.setText("Sembunyikan")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_button.setText("Tampilkan")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            self.show_message("Peringatan", "Username dan password harus diisi", QMessageBox.Warning)
            return

        try:
            # Tentukan URL API berdasarkan mode login
            if hasattr(self, "login_mode") and self.login_mode == 'desktop':
                api_url = " http://127.0.0.1:8000/api/users/login/desktop"
            else:
                api_url = " http://127.0.0.1:8000/api/users/login/web"

            # Buat payload data
            data = json.dumps({"username": username, "password": password})

            response = requests.post(
                api_url,
                data=data,
                headers={"Content-Type": "application/json"},
                verify=False,
                timeout=10
            )

            print(f"Status Code: {response.status_code}, Response Body: {response.text}")

            # Inisialisasi pesan dengan nilai default
            message = "Login gagal"

            try:
                response_data = response.json()
                if 'message' in response_data:
                    message = response_data['message']
            except json.JSONDecodeError:
                message = "Respons API tidak valid"
                response_data = {}

            if response.status_code == 200:
                # Login berhasil
                from database_handler import DatabaseHandler
                db_handler = DatabaseHandler()

                token = response_data.get('token', '')

                if token:
                    # Simpan hanya token ke config.json
                    token_data = {"token": token}

                    with open(db_handler.config_path, 'w', encoding='utf-8') as config_file:
                        json.dump(token_data, config_file, indent=4)

                    # Directly open main window, no animations
                    self.open_main_window()
                else:
                    self.show_message(
                        "Gagal",
                        "Gagal mendapatkan token autentikasi.",
                        QMessageBox.Warning
                    )
            else:
                self.show_message(
                    "Gagal",
                    f"{message} (Kode {response.status_code})",
                    QMessageBox.Warning if response.status_code < 500 else QMessageBox.Critical
                )

        except requests.exceptions.Timeout:
            self.show_message(
                "Timeout",
                "Server tidak merespon dalam waktu yang ditentukan. Silakan coba lagi nanti.",
                QMessageBox.Critical
            )
        except requests.exceptions.ConnectionError:
            self.show_message(
                "Error Koneksi",
                "Tidak dapat terhubung ke server. Pastikan server berjalan dan Anda terhubung ke jaringan.",
                QMessageBox.Critical
            )
        except Exception as e:
            self.show_message("Error", f"Terjadi kesalahan: {str(e)}", QMessageBox.Critical)

    def get_user_data(self):
        from database_handler import DatabaseHandler
        db_handler = DatabaseHandler()

        # Baca token dari config
        with open(db_handler.config_path, 'r', encoding='utf-8') as f:
            token_data = json.load(f)

        token = token_data.get("token", "")

        if not token:
            print("Token tidak ditemukan, harap login ulang.")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get("http://localhost:5206/api/Users", headers=headers)
            if response.status_code == 200:
                print("Data user:", response.json())
            else:
                print(f"Gagal: {response.status_code} - {response.text}")
        except Exception as e:
            print("Error:", e)

    def open_main_window(self):
        self.main_window = MainWindow(login_window=self)
        self.main_window.show()
        self.hide()

    def go_to_register(self, event):
        from register import RegisterWindow
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()

    def show_message(self, title, message, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.Ok)

        if self.theme_manager.dark_mode:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0086e0;
                }
            """)
        else:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                }
                QLabel {
                    color: #202020;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0086f0;
                }
            """)

        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    app_font = QFont("Segoe UI", 10)
    app.setFont(app_font)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())