from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QComboBox, QPushButton, QWidget
from create_character_window import CreateCharacterWindow
import sqlite3

class PlayerControlPortal(QMainWindow):
    def __init__(self, session, conn, *args, **kwargs):
        super(PlayerControlPortal, self).__init__(*args, **kwargs)
        
        # Main window properties
        self.setWindowTitle("Player Creation Portal")
        self.setMinimumSize(400, 400)
        self.session = session
        self.db_path = conn
        self.player_id = self.session.user_id

        # Main layout
        main_layout = QVBoxLayout()

        # Welcome Label
        main_layout.addWidget(QLabel(f"Welcome {self.session.username}"))
        
        # Section 1: Campaign Selection
        main_layout.addWidget(QLabel("Select Campaign:"))
        self.campaign_combobox = QComboBox()
        main_layout.addWidget(self.campaign_combobox)

        # Section 2: Character Selection
        main_layout.addWidget(QLabel("Which character shall we see:"))
        self.character_combobox = QComboBox()
        main_layout.addWidget(self.character_combobox)

        # Section 3: Updatable Buttons
        self.updatable_button1 = QPushButton("Updatable Button 1")
        main_layout.addWidget(self.updatable_button1)

        self.updatable_button2 = QPushButton("Updatable Button 2")
        main_layout.addWidget(self.updatable_button2)

        # Section 4: View Character
        view_character_button = QPushButton("View Character")
        main_layout.addWidget(view_character_button)

        # Section 5: Leave Realms Button
        leave_realms_button = QPushButton("Leave the Realms")
        leave_realms_button.clicked.connect(self.close)
        main_layout.addWidget(leave_realms_button)

        # Set the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect combobox signal
        self.campaign_combobox.currentIndexChanged.connect(self.load_characters)
        self.character_combobox.currentIndexChanged.connect(self.update_buttons)

        # Load campaigns
        self.load_campaigns()

    def load_campaigns(self):
        # Clear combobox
        self.campaign_combobox.clear()

        # Query the database
        c = self.db_path.cursor()
        c.execute("SELECT campaign_id FROM campaign_players_characters WHERE player_id = ?", (self.player_id,))

        # Fetch campaign IDs and store them
        self.campaign_ids = [row[0] for row in c.fetchall()]

        # Query the database to fetch campaign names
        for campaign_id in self.campaign_ids:
            c.execute("SELECT campaign_name FROM campaigns WHERE id = ?", (campaign_id,))
            campaign_name = c.fetchone()[0]  # Fetch the first column of the first (and only) row
            self.campaign_combobox.addItem(campaign_name)

        # Load characters for the first campaign
        self.load_characters()

    def load_characters(self):
        # Clear the combobox
        self.character_combobox.clear()

        # Get selected campaign ID
        selected_campaign_id = self.campaign_ids[self.campaign_combobox.currentIndex()]

        c = self.db_path.cursor()
        c.execute("SELECT character_name FROM character_record_sheet WHERE player_id = ? AND campaign_id = ?", (self.player_id, selected_campaign_id))

        # Fetch character names and populate the combobox
        for row in c.fetchall():
            self.character_combobox.addItem(row[0])

        # Update the buttons according to the first character
        self.update_buttons()

    def update_buttons(self):
        # Disconnecting all connected slots
        try:
            self.updatable_button1.clicked.disconnect()
            self.updatable_button2.clicked.disconnect()
        except TypeError:  # If nothing was connected, disconnect() raises a TypeError.
            pass  # Ignore it.
            
        if self.character_combobox.currentText() == "New Character":
            self.updatable_button1.setText("Create Character")
            self.updatable_button1.clicked.connect(self.show_create_character_window)
            self.updatable_button2.setText("Random Character")
            # self.updatable_button2.clicked.connect(self.random_character)   # Placeholder for actual function
        else:
            self.updatable_button1.setText("Spend Experience")
            # self.updatable_button1.clicked.connect(self.spend_experience)  # Placeholder for actual function
            self.updatable_button2.setText("Spend Quintessence")
            # self.updatable_button2.clicked.connect(self.spend_quintessence)  # Placeholder for actual function

    def show_create_character_window(self):
        self.session.campaign_name = self.campaign_combobox.currentText()
        self.session.campaign_id = self.campaign_ids[self.campaign_combobox.currentIndex()]

        # Query the database for character_id of 'New Character'
        c = self.db_path.cursor()
        c.execute("SELECT id FROM character_record_sheet WHERE player_id = ? AND campaign_id = ? AND character_name = 'New Character'",
                (self.session.user_id, self.session.campaign_id))

        character_id = c.fetchone()[0]
        self.session.character_id = character_id  # Storing the character_id in the session object

        self.create_character_window = CreateCharacterWindow(self.session, self.db_path)
        self.create_character_window.show()



    # Placeholder functions. You can implement these later
    def random_character(self):
        pass 

    def spend_experience(self):
        pass 

    def spend_quintessence(self):
        pass
