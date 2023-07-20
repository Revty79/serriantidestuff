from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox, QGridLayout, QScrollArea, QStatusBar, QWidget
from create_campaign import CreateCampaign
from add_player import AddPlayerDialog
from add_race_window import AddRaceWindow
from inventory_management_window import InventoryManagementWindow

class GodCreationPortal(QMainWindow):
    def __init__(self, session, conn, *args, **kwargs):
        super(GodCreationPortal, self).__init__(*args, **kwargs)
        
        # Main window properties
        self.setWindowTitle("God Creation Portal")
        self.setMinimumSize(800, 600)
        self.session = session
        self.conn = conn

        # Main layout
        main_layout = QVBoxLayout()

        # Section 1: Campaign Selection
        layout_campaign = QHBoxLayout()
        layout_campaign.addWidget(QLabel("Campaign:"))
        self.campaign_combobox = QComboBox()
        self.campaign_combobox.currentIndexChanged.connect(self.handle_campaign_selection)
        layout_campaign.addWidget(self.campaign_combobox)
        self.create_campaign_button = QPushButton("Create Campaign")
        self.create_campaign_button.clicked.connect(self.open_create_campaign)
        layout_campaign.addWidget(self.create_campaign_button)
        main_layout.addLayout(layout_campaign)
        
        # Section 2: Player Selection
        layout_player = QHBoxLayout()
        layout_player.addWidget(QLabel("Player:"))
        self.player_combobox = QComboBox()
        self.player_combobox.currentIndexChanged.connect(self.handle_player_selection)  # add this line here
        layout_player.addWidget(self.player_combobox)
        self.update_players_dropdown()
        self.new_player_button = QPushButton("New Player")
        self.new_player_button.clicked.connect(self.open_add_player)
        layout_player.addWidget(self.new_player_button)
        main_layout.addLayout(layout_player)

        # Section 3: Character Selection
        layout_character = QHBoxLayout()
        layout_character.addWidget(QLabel("Character:"))
        self.character_combobox = QComboBox()  # store this combobox as an instance variable
        layout_character.addWidget(self.character_combobox)
        layout_character.addWidget(QPushButton("New Character", clicked=self.create_character))
        main_layout.addLayout(layout_character)

        # Section 4: Campaign Settings
        groupbox_settings = QGroupBox("Campaign Settings")
        layout_settings = QGridLayout()
        scroll_settings = QScrollArea()
        scroll_settings.setWidgetResizable(True)

        # Create labels
        labels = ["Genre:", "Starting credits:", "Use coins:", "Use credits:", "Campaign name:",
                "Attribute points:", "Skill points:", "Max skill:", "Next tier:", "Max tier:",
                "Allowed skills:", "Allowed races:"]
        self.campaign_info_labels = []

        for index, text in enumerate(labels):
            label = QLabel(text)
            output_label = QLabel()  # will be updated with the actual data
            layout_settings.addWidget(label, index, 0)
            layout_settings.addWidget(output_label, index, 1)
            self.campaign_info_labels.append(output_label)  # store reference to output label for later use

        scroll_settings.setWidget(groupbox_settings)
        groupbox_settings.setLayout(layout_settings)
        main_layout.addWidget(scroll_settings)
        main_layout.setStretchFactor(scroll_settings, 1)

        # Section 5: Additional Controls
        layout_controls = QGridLayout()
        buttons = ["Edit Character", "Add Race", "Edit Race", "Add Skill", "Edit Skill",
                "Add Mystical Skill", "Edit Mystical Skill", "Add Genre",
                "Add Weapon", "Add Armor", "Inventory Management", "Leave The Heavens"]

        self.buttons = []
        for index, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            if button_text == "Add Race":
                button.clicked.connect(self.open_add_race)
            elif button_text == "Inventory Management":
                button.clicked.connect(self.open_inventory_management)  # connect the button to the open_inventory_management function
            elif button_text == "Leave The Heavens":
                button.clicked.connect(self.close)
            layout_controls.addWidget(button, index // 4, index % 4)
            self.buttons.append(button)



        # Connect the "Leave The Heavens" button to the window's close function
        self.buttons[-1].clicked.connect(self.close)

        main_layout.addLayout(layout_controls)

       # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Set the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.update_campaigns_dropdown()
        
    def open_create_campaign(self):
        self.create_campaign_dialog = CreateCampaign(self.session, self.conn)
        self.create_campaign_dialog.finished.connect(self.update_campaigns_dropdown)
        self.create_campaign_dialog.show()

    def update_campaigns_dropdown(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT campaign_name FROM campaigns WHERE god_id = ?', (self.session.user_id,))
        campaign_names = [row[0] for row in cursor.fetchall()]
        self.campaign_combobox.clear()
        self.campaign_combobox.addItems(campaign_names)
        
    def handle_campaign_selection(self, index):
        selected_campaign = self.campaign_combobox.itemText(index)
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, genre, starting_credits, use_coins, use_credits, campaign_name, attribute_points, skill_points, max_skill, next_tier, max_tier, allowed_skills, allowed_races FROM campaigns WHERE campaign_name = ?', (selected_campaign,))
        result = cursor.fetchone()
        if result:
            self.session.select_campaign(result[0], selected_campaign)
            self.update_players_dropdown()  # update the player list after selecting a campaign

            # Update campaign info
            for i, data in enumerate(result[1:]):  # skip id
                self.campaign_info_labels[i].setText(str(data))  # update output labels with campaign info

    def open_add_player(self):
        self.add_player_dialog = AddPlayerDialog(self.session, self.conn)
        self.add_player_dialog.finished.connect(self.update_players_dropdown)  # update the player list after adding a player
        self.add_player_dialog.show()

    def update_players_dropdown(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT users.username
            FROM campaign_players_characters
            INNER JOIN users ON users.id = campaign_players_characters.player_id
            WHERE campaign_players_characters.god_id = ? AND campaign_players_characters.campaign_id = ?
        ''', (self.session.user_id, self.session.campaign_id))
        player_names = [row[0] for row in cursor.fetchall()]
        self.player_combobox.clear()
        self.player_combobox.addItems(player_names)
        
    def create_character(self):
        selected_player = self.player_combobox.currentText()
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (selected_player,))
        result = cursor.fetchone()
        if result:
            player_id = result[0]
            cursor.execute('''
                UPDATE campaign_players_characters
                SET character_name = 'Has Characters'
                WHERE player_id = ? AND campaign_id = ?
            ''', (player_id, self.session.campaign_id))
            self.conn.commit()

            # Add a new character to character_record_sheet
            cursor.execute('''
                INSERT INTO character_record_sheet (player_id, campaign_id, character_name)
                VALUES (?, ?, 'New Character')
            ''', (player_id, self.session.campaign_id))
            self.conn.commit()

            # Retrieve the id of the newly inserted character
            new_character_id = cursor.lastrowid

            # Update the character_id in the character_record_sheet for the new character
            cursor.execute('''
                UPDATE character_record_sheet
                SET character_id = ?
                WHERE id = ?
            ''', (new_character_id, new_character_id))
            self.conn.commit()

        # Update the characters dropdown after creating a new character
        self.update_characters_dropdown()



    def handle_player_selection(self, index):
        selected_player = self.player_combobox.itemText(index)
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (selected_player,))
        result = cursor.fetchone()
        if result:
            self.session.select_player(result[0], selected_player)
            self.update_characters_dropdown()

    def update_characters_dropdown(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT character_name
            FROM character_record_sheet
            WHERE player_id = ? AND campaign_id = ?
        ''', (self.session.player_id, self.session.campaign_id))
        character_names = [row[0] for row in cursor.fetchall()]
        self.character_combobox.clear()
        self.character_combobox.addItems(character_names)

    def open_add_race(self):
        self.add_race_window = AddRaceWindow()
        self.add_race_window.show()
        
    def open_inventory_management(self):
        self.inventory_management_window = InventoryManagementWindow(self.conn)
        self.inventory_management_window.show()
