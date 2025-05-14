from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon, QImage, QKeySequence,
                           QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform, QAction)
from PySide6.QtWidgets import (QApplication, QHeaderView, QMainWindow, QMenuBar,
                               QPushButton, QSizePolicy, QStatusBar, QTableWidget, QTableWidgetItem,
                               QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox)
from Settings import Ui_Settings
from database_handler import DatabaseHandler



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")

        MainWindow.showFullScreen()
        MainWindow.setWindowTitle("Vehicle Transaction System")
        self.db_handler = DatabaseHandler()

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setStyleSheet("""
                        QMenuBar {
                            background-color: #2c3e50;
                            color: white;
                            font-size: 14px;
                        }
                        QMenuBar::item {
                            padding: 5px 15px;
                            spacing: 3px;
                            background: transparent;
                        }
                        QMenuBar::item:selected {
                            background: #34495e;
                            border-radius: 5px;
                        }
                        QMenu {
                            background-color: white;
                            border: 1px solid #bdc3c7;
                        }
                        QMenu::item:selected {
                            background: #3498db;
                            color: white;
                        }
                    """)
        MainWindow.setMenuBar(self.menubar)

        self.menuFile = self.menubar.addMenu("File")
        self.actionExit = QAction(QIcon(), "Exit", MainWindow)
        self.actionExit.setShortcut("Ctrl+Q")
        self.actionExit.triggered.connect(MainWindow.close)
        self.menuFile.addAction(self.actionExit)

        self.menuSettings = self.menubar.addMenu("⚙ Settings")
        self.actionOpenSettings = QAction(QIcon("settings-icon.png"), "Open Settings", MainWindow)
        self.actionOpenSettings.setShortcut("Ctrl+S")
        self.menuSettings.addAction(self.actionOpenSettings)

        self.menuSettings.setToolTip("Configure application settings (required for NEW TICKET)")

        self.actionOpenSettings.triggered.connect(self.show_settings_with_warning)

        # Add this after the existing menu definitions (after the Help menu)
        self.menuLogin = self.menubar.addMenu("Login")
        self.actionLogin = QAction("User Login", MainWindow)
        self.actionLogin.setShortcut("Ctrl+L")
        self.menuLogin.addAction(self.actionLogin)

        self.menuLogout = self.menubar.addMenu("Logout")
        self.actionLogout = QAction("User Logout", MainWindow)
        self.actionLogout.setShortcut("Ctrl+O")
        self.menuLogout.addAction(self.actionLogout)
        # Connect the logout action to the logout function
        self.actionLogout.triggered.connect(self.logout)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        self.actionOpenSettings.triggered.connect(self.open_settings_window)

        self.header_layout = QHBoxLayout()
        # Removed the header label with "Transaction List" text
        self.header_layout.addStretch()

        self.btnNew = QPushButton(self.centralwidget)
        self.btnNew.setObjectName(u"btnNew")
        self.btnNew.setMinimumSize(QSize(200, 50))
        self.btnNew.setText("NEW TICKET")
        self.btnNew.setEnabled(False)
        self.btnNew.setToolTip("Please configure Settings first (⚙ Settings menu)")
        self.btnNew.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.header_layout.addWidget(self.btnNew)

        self.main_layout.addLayout(self.header_layout)

        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setAlternatingRowColors(True)

        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F5F5F5;
                selection-background-color: #E3F2FD;  /* Light blue selection */
                selection-color: #0D47A1;  /* Dark blue text when selected */
                gridline-color: #E0E0E0;
                border: 1px solid #BDBDBD;
                border-radius: 6px;
                color: #212121 !important;
                font-size: 13px;
                margin: 5px;
            }
            QHeaderView::section {
                background-color: #ECEFF1;
                padding: 10px;
                border: none;
                border-right: 1px solid #CFD8DC;
                border-bottom: 2px solid #90A4AE;
                font-weight: bold;
                color: #37474F;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F0F0F0;
                color: #212121 !important;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;  /* Light blue selection */
                color: #0D47A1 !important;  /* Dark blue text when selected */
            }
            QTableWidget QTableWidgetItem {
                color: #212121;
            }
            QTableWidget::item:hover {
                background-color: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
        """)

        headers = {
            "ID": Qt.AlignCenter,
            "Transaction Number": Qt.AlignCenter,
            "Vehicle No.": Qt.AlignCenter,
            "Driver Name": Qt.AlignCenter,
            "IN": Qt.AlignCenter,
            "OUT": Qt.AlignCenter,
            "Net": Qt.AlignCenter,
            "Transaction Date": Qt.AlignCenter,
            "Status": Qt.AlignCenter
        }

        for col, (header, alignment) in enumerate(headers.items()):
            item = QTableWidgetItem(header)
            item.setTextAlignment(alignment)
            self.tableWidget.setHorizontalHeaderItem(col, item)

        self.main_layout.addWidget(self.tableWidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #F5F5F5;
                color: #424242;
            }
        """)
        MainWindow.setStatusBar(self.statusbar)

        MainWindow.setCentralWidget(self.centralwidget)

        QMetaObject.connectSlotsByName(MainWindow)

    def add_transaction(self, data):
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)

        # Column alignments
        alignments = {
            0: Qt.AlignCenter,  # ID
            1: Qt.AlignLeft | Qt.AlignVCenter,
            2: Qt.AlignLeft | Qt.AlignVCenter,
            3: Qt.AlignLeft | Qt.AlignVCenter,
            4: Qt.AlignRight | Qt.AlignVCenter,
            5: Qt.AlignRight | Qt.AlignVCenter,
            6: Qt.AlignRight | Qt.AlignVCenter,
            7: Qt.AlignCenter,
            8: Qt.AlignCenter
        }

        status_colors = {
            "NEW": "#FFF8E1",  # Lighter amber
            "IN": "#E8F5E9",   # Lighter green
            "OUT": "#E3F2FD",  # Lighter blue
            "COMPLETED": "#ECEFF1"  # Lighter gray
        }

        for col, value in enumerate(data.values()):
            item = QTableWidgetItem()

            if col in [4, 5, 6]:
                try:
                    formatted_value = f"{int(value):,}"
                except (ValueError, TypeError):
                    formatted_value = str(value)
                item.setText(formatted_value)
            else:
                item.setText(str(value))

            # Set alignment
            item.setTextAlignment(alignments[col])

            if col == 8:
                status = str(value).upper()
                item.setBackground(QColor(status_colors.get(status, "#FFFFFF")))
                font = item.font()
                font.setBold(True)
                item.setFont(font)

            self.tableWidget.setItem(row_position, col, item)

    def update_transaction_status(self, row, status):
        status_colors = {
            "NEW": "#FFF3CD",
            "IN": "#D4EDDA",
            "OUT": "#CCE5FF",
            "COMPLETED": "#E2E3E5"
        }

        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter)
        status_item.setBackground(QColor(status_colors.get(status, "#FFFFFF")))

        # Make status text bold
        font = status_item.font()
        font.setBold(True)
        status_item.setFont(font)

        self.tableWidget.setItem(row, 8, status_item)

    def logout(self):
        # Close the current main window
        QApplication.instance().closeAllWindows()

        # Import and start the login window
        from login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()

    def open_settings_window(self):
        self.settings_window = QMainWindow()
        self.ui_settings = Ui_Settings()
        self.ui_settings.setupUi(self.settings_window)
        self.settings_window.setWindowModality(Qt.ApplicationModal)

        # Connect settings changed signal to button update
        self.ui_settings.signals.settingsChanged.connect(self.update_new_ticket_button_state)

        self.settings_window.show()

    def load_active_transaction(self):
        active_transaction = self.db_handler.get_active_transaction()

        if active_transaction and active_transaction.get("active_transaction"):
            transaction_data = active_transaction.get("transaction_data")
            self.load_transaction_to_form(transaction_data)

    def update_new_ticket_button_state(self):
        is_enabled = Ui_Settings.are_settings_valid()
        self.btnNew.setEnabled(is_enabled)

        if is_enabled:
            self.btnNew.setToolTip("Create a new transaction")
            QMessageBox.information(
                None,
                "Settings Saved",
                "Settings have been saved successfully!\n"
                "The NEW TICKET button is now enabled."
            )
        else:
            self.btnNew.setToolTip("Please configure Settings first (⚙ Settings menu)")

    def show_settings_with_warning(self):
        if not Ui_Settings.are_settings_valid():
            QMessageBox.warning(
                None,
                "Settings Required",
                "Please configure the Settings first!\n\n"
                "You need to set both Comcode and Bacode values\n"
                "to enable the NEW TICKET functionality."
            )

        self.open_settings_window()