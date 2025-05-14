import sys
import json
import jwt
import requests
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, QDialog, QPushButton, QWidget, QHBoxLayout,
                               QMessageBox, QToolButton, QLabel, QMenu)
from PySide6.QtGui import QAction, QPalette, QColor, QIcon,Qt
from PySide6.QtCore import QDate, QDateTime, Qt, QPoint,QTimer,Qt
from Depan import Ui_MainWindow
from Halaman2 import Ui_MainWindow as Ui_Halaman2
from database_handler import DatabaseHandler
from Settings import Ui_Settings
from datetime import datetime, timedelta
from login import LoginWindow

class ThemeManager:

    @staticmethod
    def apply_light_theme(app):
        app.setStyle("Fusion")

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 120, 215))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        app.setPalette(palette)

        return """
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 4px;
            border: 1px solid #d0d0d0;
        }
        QTableWidget {
            gridline-color: #d0d0d0;
            selection-background-color: #c2dcf2;
            selection-color: #000000;
        }
        QLCDNumber {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #d0d0d0;
        }
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #d0d0d0;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        QLineEdit, QDateEdit, QComboBox {
            border: 1px solid #d0d0d0;
            padding: 3px;
            background-color: #ffffff;
        }
        QStatusBar {
            background-color: #f0f0f0;
            color: #000000;
        }
        QPlainTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
        }
        """

    @staticmethod
    def apply_dark_theme(app):
        app.setStyle("Fusion")


        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 128, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))


        app.setPalette(palette)

        return """
        QHeaderView::section {
            background-color: #3a3a3a;
            padding: 4px;
            border: 1px solid #505050;
        }
        QTableWidget {
            gridline-color: #505050;
            selection-background-color: #2a547a;
            selection-color: #ffffff;
        }
        QLCDNumber {
            background-color: #252525;
            color: #00ff00;
            border: 1px solid #505050;
        }
        QPushButton {
            background-color: #424242;
            border: 1px solid #505050;
            padding: 5px;
            border-radius: 3px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        QPushButton:pressed {
            background-color: #353535;
        }
        QLineEdit, QDateEdit, QComboBox {
            border: 1px solid #505050;
            padding: 3px;
            background-color: #2a2a2a;
            color: #ffffff;
        }
        QStatusBar {
            background-color: #353535;
            color: #ffffff;
        }
        QPlainTextEdit {
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #505050;
        }
        """
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_url = "http://127.0.0.1:8000/api/tickets"
        self.headers = self.get_headers()

        self.dragPos = None
        self.editing_id = None
        self.current_record = None
        self.current_theme = "light"
        self.window_state_before_fullscreen = None

        self.settings_window = QMainWindow()
        self.settings_ui = Ui_Settings()
        self.settings_ui.setupUi(self.settings_window)
        self.settings_ui.signals.settingsChanged.connect(self.update_new_ticket_button_state)

        self.db_handler = DatabaseHandler()

        self.create_title_bar()
        self.title_bar.show()

        self.ui1 = Ui_MainWindow()
        self.ui1.setupUi(self)

        self.page2 = QMainWindow()
        self.ui2 = Ui_Halaman2()
        self.ui2.setupUi(self.page2)


        if hasattr(self.ui2, 'saved_weights'):
            self.ui2.saved_weights = {'in': None, 'out': None, 'net': None}
        else:
            self.ui2.saved_weights = {'in': None, 'out': None, 'net': None}

        if hasattr(self.ui2, 'transaction_status'):
            self.ui2.transaction_status = "NEW"
        else:
            self.ui2.transaction_status = "NEW"

        self.setMinimumSize(850, 600)

        self.page2.setParent(self)
        self.page2.setWindowFlags(Qt.Window)

        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)

        # Connect buttons with error handling
        self.ui1.btnNew.clicked.connect(self.openHalaman2)
        if hasattr(self.ui2, 'btnSave'):
            self.ui2.btnSave.clicked.connect(self.saveData)
        if hasattr(self.ui2, 'btnCancel'):
            self.ui2.btnCancel.clicked.connect(self.closeHalaman2)

        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_restore.clicked.connect(self.toggle_restore)
        self.btn_close.clicked.connect(self.close)

        # Connect verify button if it exists
        if hasattr(self.ui2, 'btnVerify') and hasattr(self.ui2, 'verify_scan'):
            self.ui2.btnVerify.clicked.connect(self.ui2.verify_scan)

        # Connect double click event
        self.ui1.tableWidget.itemDoubleClicked.connect(self.onTableDoubleClick)

        # Add theme switcher to menubar for both pages
        self.setup_theme_menu()

        # Load existing data
        self.load_data_to_table()

        # Check settings and update NEW TICKET button state
        self.update_new_ticket_button_state()

        self.setWindowTitle("Weight Bridge")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.showMaximized()

        QTimer.singleShot(100, self.load_data_to_table)

        self.apply_theme("light")

    def create_title_bar(self):
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                padding: 5px;
            }
            QToolButton {
                background: transparent;
                padding: 3px;
                border: none;
                border-radius: 3px;
                margin: 2px;
                min-width: 30px;
            }
            QToolButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QToolButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
            #closeButton:hover {
                background: #e74c3c;
                color: white;
            }
            #closeButton:pressed {
                background: #c0392b;
            }
        """)

        # Label judul aplikasi
        self.title_label = QLabel("Weight Bridge", self.title_bar)
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            padding-left: 10px;
            font-weight: bold;
        """)

        # Tombol Minimize
        self.btn_minimize = QToolButton(self.title_bar)
        self.btn_minimize.setText("−")
        self.btn_minimize.setObjectName("minimizeButton")
        self.btn_minimize.setStyleSheet("""
            QToolButton {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.btn_minimize.clicked.connect(self.showMinimized)

        self.btn_restore = QToolButton(self.title_bar)
        self.btn_restore.setText("□")
        self.btn_restore.setObjectName("restoreButton")
        self.btn_restore.setStyleSheet("""
            QToolButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.btn_restore.clicked.connect(self.toggle_restore)

        self.btn_close = QToolButton(self.title_bar)
        self.btn_close.setText("×")
        self.btn_close.setObjectName("closeButton")
        self.btn_close.setStyleSheet("""
            QToolButton {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        layout = QHBoxLayout(self.title_bar)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_restore)
        layout.addWidget(self.btn_close)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setMenuWidget(self.title_bar)

        self.title_bar.mousePressEvent = self.mousePressEvent
        self.title_bar.mouseMoveEvent = self.mouseMoveEvent

    def toggle_restore(self):
        if self.isFullScreen():
            self.showNormal()
            self.title_bar.show()
        else:
            self.title_bar.show()
            self.showFullScreen()

    def update_new_ticket_button_state(self):
        is_enabled = Ui_Settings.are_settings_valid()
        self.ui1.btnNew.setEnabled(is_enabled)

        if not is_enabled:
            self.ui1.btnNew.setToolTip("Settings must be configured before creating new tickets")
        else:
            self.ui1.btnNew.setToolTip("Create a new transaction")

    def setup_theme_menu(self):
        self.menuTheme1 = self.ui1.menubar.addMenu("🎨 Theme")

        self.actionLightTheme1 = QAction("Light Mode", self)
        self.actionLightTheme1.triggered.connect(lambda: self.apply_theme("light"))
        self.menuTheme1.addAction(self.actionLightTheme1)

        self.actionDarkTheme1 = QAction("Dark Mode", self)
        self.actionDarkTheme1.triggered.connect(lambda: self.apply_theme("dark"))
        self.menuTheme1.addAction(self.actionDarkTheme1)

        if hasattr(self.ui2, 'menubar'):
            self.menuTheme2 = self.ui2.menubar.addMenu("🎨 Theme")

            self.actionLightTheme2 = QAction("Light Mode", self.page2)
            self.actionLightTheme2.triggered.connect(lambda: self.apply_theme("light"))
            self.menuTheme2.addAction(self.actionLightTheme2)

            self.actionDarkTheme2 = QAction("Dark Mode", self.page2)
            self.actionDarkTheme2.triggered.connect(lambda: self.apply_theme("dark"))
            self.menuTheme2.addAction(self.actionDarkTheme2)

    def apply_theme(self, theme):
        self.current_theme = theme
        app = QApplication.instance()

        if theme == "light":
            stylesheet = ThemeManager.apply_light_theme(app)
            lcd_stylesheet = "QLCDNumber { background-color: #f0f0f0; color: #000000; }"

            menubar_stylesheet = """
                QMenuBar {
                    background-color: #f0f0f0;
                    color: #000000;
                    border-bottom: 1px solid #d0d0d0;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 6px 10px;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                    border-radius: 4px;
                }
                QMenuBar::item:pressed {
                    background-color: #d0d0d0;
                }
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                }
                QMenu::item {
                    padding: 5px 30px 5px 20px;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
            """

            # Update checkmarks in menu
            if hasattr(self, 'actionLightTheme1'):
                self.actionLightTheme1.setIcon(QIcon.fromTheme("dialog-ok"))
                self.actionDarkTheme1.setIcon(QIcon())
            if hasattr(self, 'actionLightTheme2'):
                self.actionLightTheme2.setIcon(QIcon.fromTheme("dialog-ok"))
                self.actionDarkTheme2.setIcon(QIcon())

        else:
            stylesheet = ThemeManager.apply_dark_theme(app)
            lcd_stylesheet = "QLCDNumber { background-color: #252525; color: #00ff00; }"

            menubar_stylesheet = """
                QMenuBar {
                    background-color: #424242;
                    color: #ffffff;
                    border-bottom: 1px solid #505050;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 6px 10px;
                }
                QMenuBar::item:selected {
                    background-color: #505050;
                    border-radius: 4px;
                }
                QMenuBar::item:pressed {
                    background-color: #353535;
                }
                QMenu {
                    background-color: #353535;
                    border: 1px solid #505050;
                    color: #ffffff;
                }
                QMenu::item {
                    padding: 5px 30px 5px 20px;
                }
                QMenu::item:selected {
                    background-color: #505050;
                }
            """

            if hasattr(self, 'actionLightTheme1'):
                self.actionLightTheme1.setIcon(QIcon())
                self.actionDarkTheme1.setIcon(QIcon.fromTheme("dialog-ok"))
            if hasattr(self, 'actionLightTheme2'):
                self.actionLightTheme2.setIcon(QIcon())
                self.actionDarkTheme2.setIcon(QIcon.fromTheme("dialog-ok"))

        # Apply the main stylesheet first
        app.setStyleSheet(stylesheet)

        # Then apply the menubar-specific stylesheet
        if hasattr(self.ui1, 'menubar'):
            self.ui1.menubar.setStyleSheet(menubar_stylesheet)

        # Apply the same menubar styling to page2 if it exists
        if hasattr(self.ui2, 'menubar'):
            self.ui2.menubar.setStyleSheet(menubar_stylesheet)

        if hasattr(self, 'page2'):
            if hasattr(self.page2, 'setProperty'):
                self.page2.setProperty("current_theme", theme)

        # Apply LCD-specific styling to both windows
        if hasattr(self.ui2, 'lcdIN'):
            self.ui2.lcdIN.setStyleSheet(lcd_stylesheet)
        if hasattr(self.ui2, 'lcdOUT'):
            self.ui2.lcdOUT.setStyleSheet(lcd_stylesheet)

        if theme == "light":
            self.ui1.tableWidget.setAlternatingRowColors(True)
            self.ui1.tableWidget.setStyleSheet("""
                QTableWidget {
                    alternate-background-color: #f5f5f5;
                    background-color: #ffffff;
                }
            """)
        else:
            self.ui1.tableWidget.setAlternatingRowColors(True)
            self.ui1.tableWidget.setStyleSheet("""
                QTableWidget {
                    alternate-background-color: #3a3a3a;
                    background-color: #2a2a2a;
                }
            """)

    def load_data_to_table(self):
        try:
            data = self.db_handler.load_data()

            current_widths = []
            for col in range(self.ui1.tableWidget.columnCount()):
                current_widths.append(self.ui1.tableWidget.columnWidth(col))

            self.ui1.tableWidget.setRowCount(0)

            for row_data in data:
                row = self.ui1.tableWidget.rowCount()
                self.ui1.tableWidget.insertRow(row)

                try:
                    weight_in = float(row_data['weight_in']) if row_data['weight_in'] else 0
                    weight_out = float(row_data['weight_out']) if row_data['weight_out'] else 0
                except (ValueError, TypeError):
                    weight_in = 0
                    weight_out = 0

                if weight_out > 0 and weight_in == 0:
                    status = "OUT"
                elif weight_out > 0:
                    status = "COMPLETED"
                elif weight_in > 0:
                    status = "IN PROGRESS"
                else:
                    status = "NEW"

                items = [
                    str(row_data['id']),
                    row_data.get('ticket_number', ''),
                    row_data.get('vehicle_no', ''),
                    row_data.get('driver_name', ''),
                    str(row_data.get('weight_in', '')),
                    str(row_data.get('weight_out', '')),
                    str(row_data.get('net_weight', '')),
                    row_data.get('TransactionDateIN', row_data.get('transaction_date', '')),
                    status
                ]

                for col, item in enumerate(items):
                    table_item = QTableWidgetItem(str(item))

                    if col == 8:
                        if self.current_theme == "light":
                            if status == "COMPLETED":
                                table_item.setBackground(QColor(200, 255, 200))
                                table_item.setForeground(QColor(0, 100, 0))
                            elif status == "IN PROGRESS":
                                table_item.setBackground(QColor(255, 255, 200))
                                table_item.setForeground(QColor(128, 100, 0))
                            elif status == "OUT":
                                table_item.setBackground(QColor(255, 200, 200))
                                table_item.setForeground(QColor(128, 0, 0))
                            else:
                                table_item.setBackground(QColor(230, 230, 255))
                                table_item.setForeground(QColor(0, 0, 128))
                        else:
                            if status == "COMPLETED":
                                table_item.setBackground(QColor(0, 120, 0))
                                table_item.setForeground(QColor(255, 255, 255))
                            elif status == "IN PROGRESS":
                                table_item.setBackground(QColor(180, 150, 0))
                                table_item.setForeground(QColor(255, 255, 255))
                            elif status == "OUT":
                                table_item.setBackground(QColor(150, 0, 0))
                                table_item.setForeground(QColor(255, 255, 255))
                            else:  # NEW
                                table_item.setBackground(QColor(0, 0, 150))
                                table_item.setForeground(QColor(255, 255, 255))

                    self.ui1.tableWidget.setItem(row, col, table_item)

                if current_widths:
                    for col, width in enumerate(current_widths):
                        if width > 0:
                            self.ui1.tableWidget.setColumnWidth(col, width)
                else:
                    self.ui1.tableWidget.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading data: {str(e)}")

    def enableEditMode(self):
        if hasattr(self.ui2, 'timerIN') and self.ui2.timerIN:
            self.ui2.timerIN.stop()
        if hasattr(self.ui2, 'timerOUT') and self.ui2.timerOUT:
            self.ui2.timerOUT.stop()

        if hasattr(self.ui2, 'enable_edit_mode'):
            self.ui2.enable_edit_mode()

        if hasattr(self.ui2, 'btnIN'):
            self.ui2.btnIN.setEnabled(True)
        if hasattr(self.ui2, 'btnOUT'):
            self.ui2.btnOUT.setEnabled(True)

    def openHalaman2(self):
        try:
            self.editing_id = None
            self.current_record = None

            self.clearForm()

            if hasattr(self.ui2, 'disable_edit_mode'):
                self.ui2.disable_edit_mode()

            if hasattr(self.ui2, 'timerIN') and self.ui2.timerIN:
                self.ui2.timerIN.stop()
            if hasattr(self.ui2, 'timerOUT') and self.ui2.timerOUT:
                self.ui2.timerOUT.stop()

            self.ui2.btnIN.setEnabled(True)
            self.ui2.btnOUT.setEnabled(False)
            self.ui2.lcdIN.setEnabled(True)
            self.ui2.lcdOUT.setEnabled(False)
            self.ui2.comboBoxIN.setEnabled(True)
            self.ui2.comboBoxOUT.setEnabled(False)

            self.ui2.saved_weights = {'in': None, 'out': None, 'net': None}
            if hasattr(self.ui2, 'update_status_display'):
                self.ui2.update_status_display("NEW")

            if hasattr(self.ui2, 'start_auto_in_measurement'):
                self.ui2.start_auto_in_measurement()

            self._set_form_enabled(True)

            if hasattr(self.ui2, 'statusbar'):
                self.ui2.statusbar.showMessage("Ready for new transaction", 3000)

            self.page2.setWindowTitle("New Transaction")
            self.page2.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating new ticket: {str(e)}")

    def _set_form_enabled(self, enabled):
        form_elements = []

        if hasattr(self.ui2, 'lineEditTicketnum'):
            form_elements.append(self.ui2.lineEditTicketnum)
        if hasattr(self.ui2, 'lineEditNopol'):
            form_elements.append(self.ui2.lineEditNopol)
        if hasattr(self.ui2, 'lineEditDriver'):
            form_elements.append(self.ui2.lineEditDriver)
        if hasattr(self.ui2, 'dateEdit'):
            form_elements.append(self.ui2.dateEdit)
        if hasattr(self.ui2, 'lineScan'):
            form_elements.append(self.ui2.lineScan)

        if self.current_theme == "light":
            disabled_bg = "#F0F0F0"
        else:
            disabled_bg = "#3A3A3A"

        for element in form_elements:
            element.setEnabled(enabled)
            element.setStyleSheet("" if enabled else f"background-color: {disabled_bg};")

    def showHalaman1(self):
        self.editing_id = None
        self.current_record = None
        if hasattr(self.ui2, 'disable_edit_mode'):
            self.ui2.disable_edit_mode()

    def clearForm(self):
        for field in ['lineEditTicketnum', 'lineEditNopol', 'lineEditDriver', 'lineScan']:
            if hasattr(self.ui2, field):
                getattr(self.ui2, field).clear()

        # Reset date to current
        if hasattr(self.ui2, 'dateEdit'):
            self.ui2.dateEdit.setDate(QDate.currentDate())
        if hasattr(self.ui2, 'dateTimeIN'):
            self.ui2.dateTimeIN.setDateTime(QDateTime.currentDateTime())
        if hasattr(self.ui2, 'dateTimeEditOUT'):
            self.ui2.dateTimeEditOUT.setDateTime(QDateTime.currentDateTime())

        if hasattr(self.ui2, 'lcdIN'):
            self.ui2.lcdIN.display(0)
        if hasattr(self.ui2, 'lcdOUT'):
            self.ui2.lcdOUT.display(0)
        if hasattr(self.ui2, 'textNet'):
            self.ui2.textNet.setPlainText("0")

        if hasattr(self.ui2, 'comboBoxIN'):
            self.ui2.comboBoxIN.setCurrentIndex(0)
        if hasattr(self.ui2, 'comboBoxOUT'):
            self.ui2.comboBoxOUT.setCurrentIndex(0)

        if hasattr(self.ui2, 'transaction_status'):
            self.ui2.transaction_status = "NEW"
        if hasattr(self.ui2, 'saved_weights'):
            self.ui2.saved_weights = {'in': None, 'out': None, 'net': None}

        # Reset status display
        if hasattr(self.ui2, 'update_status_display'):
            self.ui2.update_status_display("NEW")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos is not None:
            diff = event.globalPosition().toPoint() - self.dragPos
            self.move(self.pos() + diff)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def onTableDoubleClick(self, item):
        try:
            row = item.row()

            cell_item = self.ui1.tableWidget.item(row, 0)
            if cell_item is None:
                raise Exception(f"Item tidak ditemukan di tabel pada baris {row}")

            record_id = int(cell_item.text())
            print(f"Baris dipilih: {row}, ID record: {record_id}")

            # Get data from database
            data = self.db_handler.load_data()
            available_ids = [x['id'] for x in data]
            print(f"Available IDs: {available_ids}")

            record = next((x for x in data if x['id'] == record_id), None)
            if not record:
                raise Exception(f"Record dengan ID {record_id} tidak ditemukan dalam database")

            self.editing_id = record_id
            self.current_record = record
            print(f"Record yang dipilih: {record}")

            # Set form input values
            self.ui2.lineEditTicketnum.setText(str(record.get('ticket_number', '')))
            self.ui2.lineEditNopol.setText(str(record.get('vehicle_no', '')))
            self.ui2.lineEditDriver.setText(str(record.get('driver_name', '')))

            # Set transaction date
            date_str = record.get('transaction_date', '')
            date = QDate.fromString(date_str, "yyyy-MM-dd") if date_str else QDate.currentDate()
            if date.isValid():
                self.ui2.dateEdit.setDate(date)
            else:
                print(f"Tanggal tidak valid: {date_str}, menggunakan tanggal hari ini")
                self.ui2.dateEdit.setDate(QDate.currentDate())

            try:
                weight_in = float(record.get('weight_in', 0))
                print(f"Berat Masuk dari database: {weight_in}")
            except (ValueError, TypeError) as e:
                weight_in = 0
                print(f"Error saat konversi berat masuk: {str(e)}")

                self.ui2.lcdIN.display(weight_in)

            # Stop timers to keep values stable
            if hasattr(self.ui2, 'timerIN') and self.ui2.timerIN:
                self.ui2.timerIN.stop()
            if hasattr(self.ui2, 'timerOUT') and self.ui2.timerOUT:
                self.ui2.timerOUT.stop()

            # Reset status running
            self.ui2.in_running = False
            self.ui2.out_running = False

            # Ambil berat keluar
            try:
                weight_out = float(record.get('weight_out', 0))
                print(f"Berat Keluar: {weight_out}")
            except (ValueError, TypeError) as e:
                weight_out = 0
                print(f"Error saat konversi berat keluar: {str(e)}")

            if weight_out > 0:
                self.ui2.lcdOUT.display(weight_out)
                net_weight = float(record.get('net_weight', abs(weight_in - weight_out)))

                self.ui2.textNet.setPlainText(str(net_weight))
                print(f"Berat Bersih: {net_weight}")

                # Simpan nilai berat
                self.ui2.saved_weights = {'in': weight_in, 'out': weight_out, 'net': net_weight}

                # Nonaktifkan tombol jika transaksi sudah selesai
                self.ui2.btnIN.setEnabled(False)
                self.ui2.btnOUT.setEnabled(False)
                self.ui2.lcdIN.setEnabled(False)
                self.ui2.lcdOUT.setEnabled(False)

                if hasattr(self.ui2, 'comboBoxIN'):
                    self.ui2.comboBoxIN.setEnabled(False)
                if hasattr(self.ui2, 'comboBoxOUT'):
                    self.ui2.comboBoxOUT.setEnabled(False)

                # Perbarui status transaksi
                if hasattr(self.ui2, 'update_status_display') and callable(self.ui2.update_status_display):
                    self.ui2.update_status_display("COMPLETED")
                else:
                    self.ui2.transaction_status = "COMPLETED"
            else:
                # Jika belum ada berat keluar
                self.ui2.btnIN.setEnabled(False)
                self.ui2.lcdIN.setEnabled(False)
                if hasattr(self.ui2, 'comboBoxIN'):
                    self.ui2.comboBoxIN.setEnabled(False)

                self.ui2.lcdOUT.setEnabled(True)
                if hasattr(self.ui2, 'comboBoxOUT'):
                    self.ui2.comboBoxOUT.setEnabled(True)
                self.ui2.btnOUT.setEnabled(True)

                self.ui2.lcdOUT.display(0)

                # Simpan status sementara
                self.ui2.saved_weights = {'in': weight_in, 'out': 0, 'net': 0}

                if hasattr(self.ui2, 'update_status_display') and callable(self.ui2.update_status_display):
                    self.ui2.update_status_display("OUT")
                else:
                    self.ui2.transaction_status = "OUT"

                # Mulai proses pengukuran berat keluar jika tersedia
                if hasattr(self.ui2, 'start_out_measurement') and callable(self.ui2.start_out_measurement):
                    self.ui2.start_out_measurement()

            # Tampilkan jendela transaksi dengan judul sesuai nomor tiket
            ticket_number = str(record.get('ticket_number', ''))
            self.page2.setWindowTitle(f"New Ticket: {ticket_number}")
            self.page2.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat memuat record: {str(e)}")
            print(f"Exception dalam onTableDoubleClick: {str(e)}")

    def saveData(self):
        try:
            # Validasi field wajib
            if not all([
                self.ui2.lineEditTicketnum.text().strip(),
                self.ui2.lineEditNopol.text().strip(),
                self.ui2.lineEditDriver.text().strip()
            ]):
                if hasattr(self.ui2, 'statusbar'):
                    self.ui2.statusbar.showMessage("Error: Please fill all required fields!", 5000)
                return

            config_data = self.db_handler.get_settings()
            comcode = config_data.get("comcode") or "N/A"
            bacode = config_data.get("bacode") or "N/A"
            username = self.get_logged_in_username()

            transaction_dateIN = self.ui2.dateTimeIN.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            transaction_dateOUT = None
            lcdIN_val = int(self.ui2.lcdIN.value())
            lcdOUT_val = int(self.ui2.lcdOUT.value())

            current_data = self.db_handler.load_data()

            username_in = username if lcdIN_val > 0 else "Unknown User"
            username_out = username if lcdOUT_val > 0 else "Unknown User"

            if self.editing_id is not None:
                existing_record = next((x for x in current_data if x['id'] == self.editing_id), None)
                if existing_record:
                    comcode = existing_record.get("comcode", comcode)
                    bacode = existing_record.get("bacode", bacode)
                    username_in = existing_record.get("username_in", username_in)
                    username_out = existing_record.get("username_out", username_out)
                    transaction_dateIN = existing_record.get("TransactionDateIN", transaction_dateIN)
                    transaction_dateOUT = existing_record.get("TransactionDateOUT")

            # === VALIDASI TOKEN DAN DURASI 24 JAM ===
            if lcdOUT_val > 0 and (transaction_dateOUT is None or transaction_dateOUT == ''):
                # Transaksi sebelumnya hanya berat IN, sekarang user isi berat OUT
                in_time = datetime.strptime(transaction_dateIN, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                if now > in_time + timedelta(hours=24):
                    QMessageBox.warning(self, "Session Expired",
                                        "You must login again to complete this transaction. Session expired.")
                    self.logout_user()
                    self.page2.hide()
                    self.show_login_page()  # Panggil halaman login
                    return  # Jangan lanjut simpan

                transaction_dateOUT = self.ui2.dateTimeEditOUT.dateTime().toString("yyyy-MM-dd HH:mm:ss")
                username_out = username

            # ====== FORM DATA DAN API CALL (TIDAK BERUBAH) ======
            form_data = {
                'id': self.editing_id if self.editing_id is not None else self.db_handler.get_next_id(),
                'ticket_number': self.ui2.lineEditTicketnum.text(),
                'vehicle_no': self.ui2.lineEditNopol.text(),
                'driver_name': self.ui2.lineEditDriver.text(),
                'weight_in': str(lcdIN_val),
                'weight_out': str(lcdOUT_val),
                'net_weight': str(int(float(self.ui2.textNet.toPlainText()))),
                'TransactionDateIN': transaction_dateIN,
                'TransactionDateOUT': transaction_dateOUT,
                'comcode': comcode,
                'bacode': bacode,
                'username_in': username_in,
                'username_out': username_out
            }

            # === Kirim ke API ===
            if self.editing_id is None:
                api_response = self.create_ticket(form_data)
                if api_response.status_code == 201:
                    current_data.append(form_data)
                    status_message = "Data saved to server!"
                elif api_response.status_code == 409:
                    api_response = self.update_ticket(form_data["id"], form_data)
                    if api_response.status_code == 200:
                        current_data = [form_data if x['id'] == form_data["id"] else x for x in current_data]
                        status_message = "Ticket already exists, updated instead!"
                    else:
                        raise Exception(
                            f"API Error (update after 409): {api_response.status_code} - {api_response.text}")
                else:
                    raise Exception(f"API Error: {api_response.status_code} - {api_response.text}")
            else:
                check_response = self.get_ticket(self.editing_id)
                if check_response.status_code == 404:
                    raise Exception("Ticket not found on server and cannot be created (auto-create is disabled).")
                else:
                    api_response = self.update_ticket(self.editing_id, form_data)
                    if api_response.status_code == 200:
                        current_data = [form_data if x['id'] == self.editing_id else x for x in current_data]
                        status_message = "Data updated on server!"
                    else:
                        raise Exception(f"API Error: {api_response.status_code} - {api_response.text}")

            # === Simpan local JSON sebagai backup ===
            if self.db_handler.save_data(current_data):
                if hasattr(self.ui2, 'statusbar'):
                    self.ui2.statusbar.showMessage(status_message, 5000)
                self.load_data_to_table()
                if hasattr(self.page2, 'isVisible') and self.page2.isVisible():
                    self.page2.hide()
            else:
                raise Exception("Failed to save local backup")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving data: {str(e)}")

    def logout_user(self):
        self.token = None
        self.editing_id = None
        #self.set_logged_in_user(None)
        if hasattr(self.ui2, 'statusbar'):
            self.ui2.statusbar.showMessage("Logged out. Please login again.", 5000)

    def show_login_page(self):
        self.page2.hide()
        self.show()

    def set_logged_in_user(self, username):
        self.logged_in_user = username

    def get_headers(self):
        try:
            config_path = os.path.join(os.path.dirname(sys.argv[0]), "config.json")
            with open(config_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                token = data.get("token", "")
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        except Exception as e:
            print(f"Error loading token: {e}")
            return {
                "Content-Type": "application/json"
            }

    def get_ticket(self, id):
        if id is None or str(id).strip() == "":
            raise ValueError("Invalid ID: ID cannot be None or empty")

        url = f"{self.base_url}/{id}"
        response = requests.get(url, headers=self.headers)
        return response

    def delete_ticket(self, id):
        url = f"{self.base_url}/{id}"
        response = requests.delete(url, headers=self.headers)
        return response

    def update_ticket(self, id, data):
        url = f"{self.base_url}/{id}"
        response = requests.put(url, headers=self.headers, json=data)
        return response

    def create_ticket(self, data):
        url = self.base_url
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def get_logged_in_username(self):
        try:
            with open("config.json", "r", encoding="utf-8") as config_file:
                token_data = json.load(config_file)
                token = token_data.get("token", "")

            if not token:
                return "Unknown User"

            decoded_token = jwt.decode(token, options={"verify_signature": False})
            return decoded_token.get("username") or decoded_token.get("name") or decoded_token.get(
                "sub") or "Unknown User"

        except Exception as e:
            print(f"Error reading token: {e}")
            return "Unknown User"

    def closeHalaman2(self):
        self.page2.hide()

        # Reset edit mode
        self.editing_id = None
        self.current_record = None
        if hasattr(self.ui2, 'disable_edit_mode'):
            self.ui2.disable_edit_mode()

    def closeEvent(self, event):
        from database_handler import DatabaseHandler
        db_handler = DatabaseHandler()
        db_handler.record_logout_time()
        event.accept()

if __name__ == "__main__":
    from login import LoginWindow

    try:
        app = QApplication(sys.argv)
        app.setFont(app.font())

        login_window = LoginWindow()
        login_window.show()

        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Fatal Error", f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
