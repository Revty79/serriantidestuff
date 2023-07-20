from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton, QLineEdit, QComboBox, QFormLayout
from session import Session

class PlayerLogin(QDialog):
    attempt_login = pyqtSignal(str, str, str)  # Emits username, password, account_type
    attempt_create_account = pyqtSignal(str, str, str)  # Emits username, password, account_type

    def __init__(self, *args, **kwargs):
        super(PlayerLogin, self).__init__(*args, **kwargs)
        self.setWindowTitle("Serrian Tide Login")
                        # Create the session
        session = Session()
        
        self.username_entry = QLineEdit()
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.account_type = QComboBox()
        self.account_type.addItems(['Player', 'God'])

        login_button = QPushButton('Login')
        login_button.clicked.connect(self.login)

        create_account_button = QPushButton('Create Account')
        create_account_button.clicked.connect(self.create_account)

        form_layout = QFormLayout()
        form_layout.addRow('Username:', self.username_entry)
        form_layout.addRow('Password:', self.password_entry)
        form_layout.addRow('Account Type:', self.account_type)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(create_account_button)
        layout.addWidget(login_button)

        container = QWidget()
        container.setLayout(layout)

        self.setLayout(layout)

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        account_type = self.account_type.currentText()

        self.attempt_login.emit(username, password, account_type)


    def create_account(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        account_type = self.account_type.currentText()

        self.attempt_create_account.emit(username, password, account_type)
