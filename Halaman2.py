import sys
import random
import re
import json
import jwt
import requests
import os
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, QTimer)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QDateEdit, QDateTimeEdit,
    QFrame, QGroupBox, QLCDNumber, QLabel, QMessageBox,
    QLineEdit, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTextEdit, QWidget, QInputDialog)


class TicketValidator:
    def __init__(self):
        self.ticket_pattern = r'^[a-zA-Z0-9]{1,50}$'
        self.vehicle_pattern = r'^[a-zA-Z0-9\s]{1,15}$'
        self.driver_pattern = r'^[a-zA-Z0-9\s\-]{1,100}$'
        self.transaction_number_pattern = r'^\d{10}$'
        self.number_pattern = r'^\d+$'
        self.date_pattern = r'^\d{8}$'

    def validate_ticket(self, ticket_number):
        return bool(re.fullmatch(self.ticket_pattern, ticket_number))

    def validate_vehicle(self, vehicle_number):
        return bool(re.fullmatch(self.vehicle_pattern, vehicle_number))

    def validate_driver(self, driver_name):
        return bool(re.fullmatch(self.driver_pattern, driver_name))

    def validate_transaction_number(self, transaction_number):
        return bool(re.fullmatch(self.transaction_number_pattern, transaction_number))

    def validate_number(self, number):
        return bool(re.fullmatch(self.number_pattern, number))

    def validate_date(self, date):
        return bool(re.fullmatch(self.date_pattern, date))

class Ui_MainWindow(QObject):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 600)
        self.pending_transaction = None


        # Inisialisasi TicketValidator
        self.validator = TicketValidator()

         # random number
        self.target_in_value = random.randint(5000, 100000)
        self.target_out_value = random.randint(5000, 100000)
        self.step_multiplier = 0.1
        self.out_step_multiplier = 0.1 
        self.in_running = True
        self.current_in_value = 0

        # central widget
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        # Add status indicator label
        self.labelStatus = QLabel("Status:", self.centralwidget)
        self.labelStatus.setGeometry(QRect(520, 350, 60, 30))
        self.labelStatus.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.statusValue = QLabel("NEW", self.centralwidget)
        self.statusValue.setGeometry(QRect(590, 350, 200, 30))
        self.statusValue.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold;
            padding: 5px 15px;
            background-color: #FFF9C4;
            border-radius: 5px;
        """)

        # Initialize additional states
        self.transaction_status = "NEW"
        self.saved_weights = {'in': None, 'out': None, 'net': None}
        self.in_running = True  
        self.out_running = False
        
        # Setup Timers with automatic start for IN
        self.timerIN = QTimer(self)
        self.timerIN.timeout.connect(self.update_lcd_in)
        self.timerIN.start(500)
        
        self.timerOUT = QTimer(self)
        self.timerOUT.timeout.connect(self.update_lcd_out)

        # Initialize status as NEW
        self.update_status_display("NEW")
        
        # Main Frame
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName("frame")
        self.frame.setGeometry(QRect(0, 30, 501, 481))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        
        # Create groupBox_IN first
        self.groupBox_IN = QGroupBox("Weight IN", self.centralwidget)
        self.groupBox_IN.setGeometry(QRect(520, 30, 301, 91))
        
        # Create groupBox_OUT first
        self.groupBox_OUT = QGroupBox("Weight OUT", self.centralwidget)
        self.groupBox_OUT.setGeometry(QRect(520, 120, 301, 91))
        
        # Now create buttons that reference the groupboxes
        self.btnIN = QPushButton("IN", self.groupBox_IN)
        self.btnIN.setGeometry(QRect(10, 20, 61, 41))
        self.btnIN.clicked.connect(self.handle_in_button)
        
        
        self.btnOUT = QPushButton("OUT", self.groupBox_OUT)
        self.btnOUT.setGeometry(QRect(10, 20, 61, 41))
        self.btnOUT.clicked.connect(self.handle_out_button)
        self.btnOUT.setEnabled(False)

         # Initialize states
        self.transaction_status = "NEW"
        self.saved_weights = {'in': None, 'out': None, 'net': None}
        self.in_running = True
        self.out_running = False

        # Now we can safely disable OUT button and LCD
        self.btnOUT.setEnabled(False)
        
        # Transaction Date
        self.labelDatr = QLabel("Transaction Date", self.frame)
        self.labelDatr.setGeometry(QRect(10, 30, 101, 16))
        self.dateEdit = QDateEdit(self.frame)
        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit.setGeometry(120, 30, 311, 23)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDateTime(QDateTime.currentDateTime())
        
        # UI components
        self.labelScan = QLabel("Scan QR", self.frame)
        self.labelScan.setGeometry(QRect(10, 70, 51, 16))
        self.lineScan = QLineEdit(self.frame)
        self.lineScan.setGeometry(QRect(120, 70, 241, 21))
        
        self.labelDriver = QLabel("Driver Name", self.frame)
        self.labelDriver.setGeometry(QRect(10, 110, 71, 16))
        self.lineEditDriver = QLineEdit(self.frame)
        self.lineEditDriver.setGeometry(QRect(120, 110, 301, 21))
        
        self.labelNopol = QLabel("Vehicle No.", self.frame)
        self.labelNopol.setGeometry(QRect(10, 150, 71, 16))
        self.lineEditNopol = QLineEdit(self.frame)
        self.lineEditNopol.setGeometry(QRect(120, 150, 301, 21))
        
        self.label = QLabel("Ticket Number", self.frame)
        self.label.setGeometry(QRect(10, 190, 81, 16))
        self.lineEditTicketnum = QLineEdit(self.frame)
        self.lineEditTicketnum.setGeometry(QRect(120, 190, 301, 21))
        
        # Action Buttons
        self.btnSave = QPushButton("Save", self.centralwidget)
        self.btnSave.setGeometry(QRect(730, 510, 81, 31))
        self.btnSave.clicked.connect(self.handle_save_button)
        self.btnCancel = QPushButton("Cancel Transaction", self.centralwidget)
        self.btnCancel.setGeometry(QRect(590, 510, 131, 31))
        self.btnVerify = QPushButton("Verify", self.frame)
        self.btnVerify.setGeometry(QRect(370, 70, 81, 31))

        #Button  Verify
        self.btnVerify.clicked.connect(self.verify_scan)
        
        # Weight IN Components
        self.lcdIN = QLCDNumber(self.groupBox_IN)
        self.lcdIN.setGeometry(QRect(80, 20, 91, 23))
        self.label_5 = QLabel("Kg", self.groupBox_IN)
        self.label_5.setGeometry(QRect(180, 20, 21, 16))
        self.comboBoxIN = QComboBox(self.groupBox_IN)
        self.comboBoxIN.setGeometry(QRect(200, 20, 80, 24))
        self.comboBoxIN.addItem("DUM 1")
        self.comboBoxIN.addItem("DUM 2")
        self.dateTimeIN = QDateTimeEdit(self.groupBox_IN)
        self.dateTimeIN.setGeometry(QRect(80, 50, 201, 23))

        # Add Edit Weight IN Button
        self.btnEditIN = QPushButton("Edit", self.groupBox_IN)
        self.btnEditIN.setGeometry(QRect(200, 50, 80, 24))
        self.btnEditIN.clicked.connect(self.edit_weight_in)
        self.btnEditIN.hide()

        # Weight OUT Components
        self.lcdOUT = QLCDNumber(self.groupBox_OUT)
        self.lcdOUT.setEnabled(False)
        self.lcdOUT.setGeometry(QRect(80, 20, 91, 23))
        self.label_6 = QLabel("Kg", self.groupBox_OUT)
        self.label_6.setGeometry(QRect(180, 20, 21, 16))
        self.comboBoxOUT = QComboBox(self.groupBox_OUT)
        self.comboBoxOUT.setEnabled(False)
        self.comboBoxOUT.setGeometry(QRect(200, 20, 80, 24))
        self.comboBoxOUT.addItem("DUM 1")
        self.comboBoxOUT.addItem("DUM 2")
        self.dateTimeEditOUT = QDateTimeEdit(self.groupBox_OUT)
        self.dateTimeEditOUT.setGeometry(QRect(80, 50, 194, 23))

        # Add Edit Weight OUT Button
        self.btnEditOUT = QPushButton("Edit", self.groupBox_OUT)
        self.btnEditOUT.setGeometry(QRect(200, 50, 80, 24))
        self.btnEditOUT.clicked.connect(self.edit_weight_out)
        self.btnEditOUT.hide()

        # NET Components - Adjusted position since status is removed
        self.labelNET = QLabel("NET", self.centralwidget)
        self.labelNET.setGeometry(QRect(520, 220, 50, 30))
        self.labelNET.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.textNet = QTextEdit(self.centralwidget)
        self.textNet.setGeometry(QRect(550, 260, 260, 80))  
        self.textNet.setStyleSheet("font-size: 28px; font-weight: bold; color: #ff0000; background-color: #f0f0f0;")
        self.textNet.setReadOnly(True)

        # Initialize LCD displays and text
        self.lcdIN.display(0)
        self.lcdOUT.display(0)
        self.textNet.setPlainText("0")
        
        self.labelkg = QLabel("Kg", self.centralwidget)
        self.labelkg.setGeometry(QRect(800, 220, 60, 30))  
        self.labelkg.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # Setup Timers with automatic start for IN
        self.timerIN = QTimer(self)
        self.timerIN.timeout.connect(self.update_lcd_in)
        self.timerIN.start(500)
        
        self.timerOUT = QTimer(self)
        self.timerOUT.timeout.connect(self.update_lcd_out)
        
        
        # Connect net weight updates to timers
        self.timerIN.timeout.connect(self.update_net_weight)
        self.timerOUT.timeout.connect(self.update_net_weight)
        
        # Menu and Status Bars
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 835, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

        self.edit_mode = False

    def update_status_display(self, status):
        self.transaction_status = status
        self.statusValue.setText(status)

        # color coding
        colors = {
            "NEW": "#FFF9C4",      
            "IN": "#FFEB3B",       
            "OUT": "#90CAF9",      
            "COMPLETED": "#A5D6A7"  
        }

        self.statusValue.setStyleSheet(f"""
            font-size: 16px; 
            font-weight: bold;
            padding: 5px 15px;
            background-color: {colors.get(status, "#FFFFFF")};
            border-radius: 5px;
        """)

        # Update UI on status
        if status == "IN":
            self.btnIN.setEnabled(True)
            self.btnOUT.setEnabled(False)
            self.lcdOUT.setEnabled(False)
            self.comboBoxOUT.setEnabled(False)
            self._set_form_enabled(True)
            self.textNet.setPlainText("0.00")
    
        if status == "OUT":
            # Disable IN components
            self.btnIN.setEnabled(False)
            self.lcdIN.setEnabled(False)
            self.comboBoxIN.setEnabled(False)
        
            # OUT components will be enabled when ticket is reloaded
            self.btnOUT.setEnabled(False)
            self.lcdOUT.setEnabled(False)
            self.comboBoxOUT.setEnabled(False)
    
        elif status == "COMPLETED":
            self.btnIN.setEnabled(False)
            self.btnOUT.setEnabled(False)
            self._set_form_enabled(False)
            # Final NET weight calculation happens here
            self.update_net_weight()

    def update_lcd_in(self):
        if self.in_running:
            current_value = self.current_in_value
            distance = abs(self.target_in_value - current_value)

            # Reduce the step multiplier for slower changes
            self.step_multiplier = 0.01  # Reduced from 0.03

            # Calculate step size with smoother transitions
            step_size = max(distance * self.step_multiplier, 0.1)  # Smaller minimum step

            # Add small random variation for natural movement
            variation = random.uniform(0.98, 1.02)
            step_size *= variation

            # Stabilization near target value
            if distance < 20:  # Increased stabilization zone
                step_size *= random.uniform(0.3, 0.6)  # Slower movements near target
                if random.random() < 0.2:  # Less chance of oscillation
                    step_size *= -1

            # Generate new target if very close to current target
            if distance < 1:
                min_target = max(5000, current_value - 3000)
                max_target = min(100000, current_value + 3000)
                self.target_in_value = random.randint(int(min_target), int(max_target))
            else:
                # Move towards target with smoother interpolation
                if current_value < self.target_in_value:
                    self.current_in_value = min(current_value + step_size, self.target_in_value)
                else:
                    self.current_in_value = max(current_value - step_size, self.target_in_value)

            # Update display with rounded value
            self.lcdIN.display(round(self.current_in_value))

    def update_lcd_out(self):
        if self.out_running:
            current_value = float(self.lcdOUT.value())

            # Calculate distance to target
            distance = abs(self.target_out_value - current_value)

            # Reduced step multiplier for slower changes
            self.out_step_multiplier = 0.01  # Reduced from 0.05

            # Dynamic step size calculation with smaller minimum step
            step_size = max(distance * self.out_step_multiplier, 0.1)

            # Add small random variation for natural movement
            variation = random.uniform(0.97, 1.03)
            step_size *= variation

            # Stabilization near target value
            if distance < 20:  # Increased stabilization zone
                step_size *= random.uniform(0.3, 0.6)  # Slower movements near target
                if random.random() < 0.2:  # Less chance of oscillation
                    step_size *= -1

            # Generate new target if very close to current target
            if distance < 1:
                min_target = max(5000, current_value - 3000)
                max_target = min(100000, current_value + 3000)
                self.target_out_value = random.randint(int(min_target), int(max_target))
            else:
                # Move towards target with smoother interpolation
                if current_value < self.target_out_value:
                    new_value = min(current_value + step_size, self.target_out_value)
                else:
                    new_value = max(current_value - step_size, self.target_out_value)

                # Update display with rounded value
                self.lcdOUT.display(round(new_value))
    def _set_form_enabled(self, enabled):
        form_elements = [
            self.lineEditTicketnum,
            self.lineEditNopol,
            self.lineEditDriver,
            self.dateEdit,
            self.lineScan
        ]
    
        for element in form_elements:
            element.setEnabled(enabled)
            if not enabled:
                element.setStyleSheet("background-color: #F0F0F0;")  
            else:
                element.setStyleSheet("")

    def edit_weight_in(self):
        try:
            current_weight = self.lcdIN.value()
            new_weight, ok = QInputDialog.getDouble(
                self.groupBox_IN,
                "Edit Weight IN",
                "Enter new weight (kg):",
                current_weight,
                0, 999999, 2
            )
            if ok:
                self.lcdIN.display(new_weight)
                self.saved_weights['in'] = new_weight
                self.update_net_weight()
        except Exception as e:
            QMessageBox.warning(self.groupBox_IN, "Error", f"Failed to update weight: {str(e)}")

    def edit_weight_out(self):
        try:
            current_weight = self.lcdOUT.value()
            new_weight, ok = QInputDialog.getDouble(
                self.groupBox_OUT,
                "Edit Weight OUT",
                "Enter new weight (kg):",
                current_weight,
                0, 999999, 2
            )
            if ok:
                self.lcdOUT.display(new_weight)
                self.saved_weights['out'] = new_weight
                self.update_net_weight()
        except Exception as e:
            QMessageBox.warning(self.groupBox_OUT, "Error", f"Failed to update weight: {str(e)}")

    def handle_out_button(self):
        if self.out_running:
            self.timerOUT.stop()
            self.out_running = False
            self.btnOUT.setText("OUT")

            self.saved_weights['out'] = float(self.lcdOUT.value())
            self.dateTimeEditOUT.setDateTime(QDateTime.currentDateTime())  # Simpan waktu OUT

            net_weight = self.calculate_net_weight()
            self.textNet.setPlainText(f"{net_weight:.2f}")

            self.update_status_display("COMPLETED")
            self.statusbar.showMessage(
                f"Weight OUT: {self.saved_weights['out']:.2f} kg | Net Weight: {net_weight:.2f} kg",
                5000
            )

    def redirect_to_login(self):
        QMessageBox.information(self.centralwidget, "Logout", "Anda akan diarahkan ke halaman login.")

        # Tutup jendela utama (Halaman2.py)
        main_window = self.centralwidget.window()
        main_window.close()

        # Import dan tampilkan halaman login
        from login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()

    def handle_in_button(self):
        if self.in_running:
            self.stop_in_measurement()
            self.saved_weights['in'] = self.current_in_value
            self.dateTimeIN.setDateTime(QDateTime.currentDateTime())

            self.update_status_display("IN")
            self.statusbar.showMessage(f"Weight IN recorded: {self.saved_weights['in']:,.2f} kg", 5000)
            self.btnSave.setEnabled(True)

    def enable_edit_mode(self):
        self.edit_mode = True
        self.btnEditIN.show()
        self.btnEditOUT.show()

        # Reset status timer
        self.timerIN.stop()
        self.timerOUT.stop()
        self.in_running = False
        self.out_running = False

        # Tampilkan nilai yang tersimpan
        if self.saved_weights['in'] is not None:
            self.lcdIN.display(self.saved_weights['in'])
        if self.saved_weights['out'] is not None:
            self.lcdOUT.display(self.saved_weights['out'])

        # Update text tombol
        self.btnIN.setText("Start IN")
        self.btnOUT.setText("Start OUT")

        # Set status transaksi
        self.transaction_status = "EDIT"

    def disable_edit_mode(self):
        self.edit_mode = False
        self.btnEditIN.hide()
        self.btnEditOUT.hide()

    def _handle_edit_mode_in(self):
        if not self.in_running:
            self.timerIN.start(500)
            self.in_running = True
            self.btnIN.setText("Stop IN")
            self.editing_weights['in'] = True
        else:
            self.timerIN.stop()
            self.in_running = False
            self.saved_weights['in'] = self.lcdIN.value()
            self.btnIN.setText("Start IN")
            self.editing_weights['in'] = False

    def _handle_edit_mode_out(self):
        if not self.out_running:
            self.timerOUT.start(500)
            self.out_running = True
            self.btnOUT.setText("Stop OUT")
            self.editing_weights['out'] = True
        else:
            self.timerOUT.stop()
            self.out_running = False
            self.saved_weights['out'] = self.lcdOUT.value()
            self.btnOUT.setText("Start OUT")
            self.editing_weights['out'] = False

    def update_net_weight(self):
        try:
            if self.transaction_status in ["OUT", "COMPLETED"]:
                net_weight = self.calculate_net_weight()
                formatted_weight = f"{net_weight:.2f}" 
                self.textNet.setPlainText(formatted_weight)

                if net_weight > 0:
                    self.textNet.setStyleSheet("""
                    font-size: 28px;
                    font-weight: bold;
                    color: #2E7D32;  /* Dark green for positive */
                    background-color: #E8F5E9;  /* Light green background */
                    border: 2px solid #2E7D32;
                    border-radius: 5px;
                    padding: 5px;
                """)
                else:
                    self.textNet.setStyleSheet("""
                        font-size: 28px;
                        font-weight: bold;
                        color: #757575;  /* Gray for zero/initial state */
                        background-color: #F5F5F5;  /* Light gray background */
                        border: 2px solid #757575;
                        border-radius: 5px;
                        padding: 5px;
                    """)
        except ValueError:
            self.textNet.setPlainText("0.00")

    
    def calculate_net_weight(self):
        try:
            weight_in = self.saved_weights['in'] if self.saved_weights['in'] is not None else self.lcdIN.value()
            weight_out = self.saved_weights['out'] if self.saved_weights['out'] is not None else self.lcdOUT.value()
        
            # Convert to float, removing any commas first if they exist
            if isinstance(weight_in, str):
                weight_in = float(weight_in.replace(',', ''))
            else:
                weight_in = float(weight_in)
            
            if isinstance(weight_out, str):
                weight_out = float(weight_out.replace(',', ''))
            else:
                weight_out = float(weight_out)
        
            # Handle different transaction states
            if self.transaction_status == "NEW" or weight_in == 0:
                return 0.0
        
            if self.transaction_status == "IN" and weight_out == 0:
                return weight_in

            if weight_in > 0 and weight_out > 0:
                return abs(weight_in - weight_out)
            
            # Default case
            return 0.0
        except (ValueError, TypeError):
            return 0.0

    def reset_transaction(self):
        # Reset weights
        self.saved_weights = {'in': None, 'out': None, 'net': None}
        self.lcdIN.display(0)
        self.lcdOUT.display(0)
        self.textNet.setPlainText("0")
    
        # Reset status
        self.transaction_status = "NEW"
        self.update_status_display("NEW")
    
        # Reset buttons
        self.btnIN.setEnabled(True)
        self.btnIN.setText("STOP")  
        self.btnOUT.setEnabled(False)
        self.btnOUT.setText("OUT")
    
        # Reset flags and start IN measurement
        self.in_running = True
        self.out_running = False
        self.start_auto_in_measurement()
    
        # Reset edit mode
        self.edit_mode = False
        self.btnEditIN.hide()
        self.btnEditOUT.hide()

    def start_auto_in_measurement(self):
        self.lcdIN.display(0)
        self.target_in_value = random.randint(5000, 100000)
        self.timerIN.start(500)
        self.in_running = True
        self.btnIN.setText("STOP")  

    def stop_in_measurement(self):
        if self.in_running:
            self.timerIN.stop()
            self.in_running = False
            self.btnIN.setText("IN")  

    def start_auto_in_measurement(self):
        self.current_in_value = 0
        self.target_in_value = random.randint(5000, 100000)
        self.timerIN.start(500)
        self.in_running = True
        self.btnIN.setText("STOP")

    def stop_out_measurement(self):
        if self.out_running:
            self.timerOUT.stop()
            self.out_running = True
            # Simpan berat OUT terakhir yang ditampilkan di LCD
            self.saved_weights['out'] = int(self.lcdOUT.value())
            # Hitung NET Weight
            self.saved_weights['net'] = self.saved_weights['out'] - self.saved_weights['in']
            self.textNet.setText(str(self.saved_weights['net']))


    def start_out_measurement(self):
        self.lcdOUT.setEnabled(True)
        self.btnOUT.setEnabled(True)
        self.target_out_value = random.randint(5000, 100000)
        self.out_running = True
        self.out_step_multiplier = 0.1
        self.timerOUT.start(500)
        self.btnOUT.setText("STOP")

    def on_btnOUT_clicked(self):
        self.stop_out_measurement()

    def handle_save_button(self):

        # Ambil tanggal transaksi IN dan OUT
        transaction_date_in = self.dateTimeIN.dateTime().toString("yyyy-MM-dd")
        transaction_date_out = self.dateTimeEditOUT.dateTime().toString("yyyy-MM-dd")

        # Validasi input yang diperlukan
        if not all([
            self.lineEditTicketnum.text().strip(),
            self.lineEditNopol.text().strip(),
            self.lineEditDriver.text().strip()
        ]):
            QMessageBox.warning(
                self.centralwidget,
                "Validation Error",
                "Harap isi semua data yang diperlukan sebelum menyimpan transaksi."
            )
            return

        # Ambil username dari sesi login
        username = self.get_logged_in_username()

        if self.transaction_status == "IN" and self.saved_weights['in'] is not None:
            # Ubah status ke OUT dan simpan transaksi IN
            self.transaction_status = "OUT"
            self.update_status_display("OUT")
            # Nonaktifkan komponen IN
            self.btnIN.setEnabled(False)
            self.lcdIN.setEnabled(False)
            self.comboBoxIN.setEnabled(False)

            transaction_data = {
                'ticket_number': self.lineEditTicketnum.text().strip(),
                'driver_name': self.lineEditDriver.text().strip(),
                'vehicle_no': self.lineEditNopol.text().strip(),
                'weight_in': self.saved_weights['in'],
                'weight_out': 0,
                'net_weight': 0,
                'status': 'OUT',
                'date_in': self.dateTimeIN.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
                'date_out': None,
                'username_in': username
            }
            self.statusbar.showMessage("Weight IN berhasil disimpan. Siap untuk transaksi OUT.", 5000)
            self.start_out_measurement()
            return
        elif self.transaction_status == "OUT" and self.saved_weights['out'] is not None:
            net_weight = self.calculate_net_weight()
            transaction_data = {
                'ticket_number': self.lineEditTicketnum.text().strip(),
                'weight_out': self.saved_weights['out'],
                'net_weight': net_weight,
                'status': 'COMPLETED',
                'date_out': self.dateTimeEditOUT.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
                'username_out': username
            }

    def get_auth_headers(self):
        try:
            # Read token from config.json
            with open("config.json", "r", encoding="utf-8") as config_file:
                token_data = json.load(config_file)
                token = token_data.get("token", "")

            # Return headers with authorization
            return {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}"
            }
        except Exception as e:
            print(f"Error reading token: {e}")
            return {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

    def get_logged_in_username(self):
        try:
            # Baca token dari file config.json
            with open("config.json", "r", encoding="utf-8") as config_file:
                token_data = json.load(config_file)
                token = token_data.get("token", "")

            if not token:
                return "Unknown User"

            # Decode JWT token tanpa verifikasi tanda tangan
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            username = decoded_token.get("username", "Unknown User")

            return username

        except Exception as e:
            print(f"Error reading token: {e}")
            return "Unknown User"

    def verify_scan(self):
        scan_value = self.lineScan.text().strip()

        if not scan_value:
            self.labelStatus.setText("Silakan scan QR terlebih dahulu.")
            return

        # Split data QR berdasarkan semicolon
        parts = scan_value.split(';')

        # Pastikan ada minimal 3 bagian
        if len(parts) < 3:
            self.labelStatus.setText("Data QR tidak lengkap atau format salah.")
            return

        # Ambil 3 bagian pertama
        ticket_number, vehicle_number, driver_info = parts[:3]

        # Bersihkan spasi berlebih
        ticket_number = ticket_number.strip()
        vehicle_number = vehicle_number.strip()
        driver_info = driver_info.strip()

        # Validasi dengan regex
        is_ticket_valid = self.validator.validate_ticket(ticket_number)
        is_vehicle_valid = self.validator.validate_vehicle(vehicle_number)
        is_driver_valid = self.validator.validate_driver(driver_info)

        if is_ticket_valid and is_vehicle_valid and is_driver_valid:
            # Isi form dengan data yang valid
            self.lineEditTicketnum.setText(ticket_number)
            self.lineEditNopol.setText(vehicle_number)
            self.lineEditDriver.setText(driver_info)
            self.lineScan.setEnabled(False)

        else:
            error_message = "QR tidak valid: "
            if not is_ticket_valid:
                error_message += "Ticket salah. "
            if not is_vehicle_valid:
                error_message += "Nopol salah. "
            if not is_driver_valid:
                error_message += "Driver salah."

            self.labelStatus.setText(error_message)

            # Opsional: Hapus field yang salah
            self.lineEditTicketnum.clear()
            self.lineEditNopol.clear()
            self.lineEditDriver.clear()

    def load_existing_ticket(self, ticket_data):
        try:
            # Update form fields with ticket data
            self.lineEditTicketnum.setText(ticket_data.get('ticket_number', ''))
            self.lineEditDriver.setText(ticket_data.get('driver_name', ''))
            self.lineEditNopol.setText(ticket_data.get('vehicle_no', ''))

            # Get the status and weights
            status = ticket_data.get('status', 'NEW')
            weight_in = ticket_data.get('weight_in', 0)

            # Stop any running timers
            self.timerIN.stop()
            self.timerOUT.stop()
            self.in_running = False
            self.out_running = False

            # Update saved weights
            self.saved_weights = {
                'in': weight_in,
                'out': 0,
                'net': 0
            }

            if status == 'OUT':
                # Disable IN components
                self.btnIN.setEnabled(False)
                self.lcdIN.setEnabled(False)
                self.comboBoxIN.setEnabled(False)
    
                # Display saved IN weight
                self.lcdIN.display(weight_in)
    
                # Enable OUT components
                self.lcdOUT.setEnabled(True)
                self.comboBoxOUT.setEnabled(True)
                self.btnOUT.setEnabled(True)
    
                # Update status display
                self.update_status_display("OUT")
            
                # Start automatic OUT measurement
                self.start_out_measurement()

            # Update date/time if available
            if ticket_data.get('date_in'):
                self.dateTimeIN.setDateTime(
                    QDateTime.fromString(ticket_data['date_in'], 'yyyy-MM-dd HH:mm:ss')
                )

        except Exception as e:
            QMessageBox.warning(
                self.centralwidget,
                "Error",
                f"Failed to load ticket data: {str(e)}"
            )

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Vehicle Transaction System"))
        self.labelDatr.setText(_translate("MainWindow", "Transaction Date"))
        self.labelScan.setText(_translate("MainWindow", "Scan QR"))
        self.labelDriver.setText(_translate("MainWindow", "Driver Name"))
        self.labelNopol.setText(_translate("MainWindow", "Vehicle No."))
        self.label.setText(_translate("MainWindow", "Ticket Number"))
        self.btnSave.setText(_translate("MainWindow", "Save"))
        self.btnCancel.setText(_translate("MainWindow", "Cancel Transaction"))
        self.groupBox_IN.setTitle(_translate("MainWindow", "Weight IN"))
        self.btnIN.setText(_translate("MainWindow", "IN"))
        self.label_5.setText(_translate("MainWindow", "Kg"))
        self.groupBox_OUT.setTitle(_translate("MainWindow", "Weight OUT"))
        self.btnOUT.setText(_translate("MainWindow", "OUT"))
        self.label_6.setText(_translate("MainWindow", "Kg"))
        self.labelNET.setText(_translate("MainWindow", "NET"))
        self.labelkg.setText(_translate("MainWindow", "Kg"))