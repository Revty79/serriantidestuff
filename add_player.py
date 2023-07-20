from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class AddPlayerDialog(QDialog):
    def __init__(self, session, conn, *args, **kwargs):
        super(AddPlayerDialog, self).__init__(*args, **kwargs)
        self.session = session
        self.conn = conn
        self.setWindowTitle("Add Character")
        self.setLayout(QVBoxLayout())
        
        self.layout().addWidget(QLabel("Select Player:"))
        
        self.player_combobox = QComboBox()
        self.update_players_dropdown()
        self.layout().addWidget(self.player_combobox)
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.add_player_to_campaign)  
        self.layout().addWidget(self.submit_button)
        
    def update_players_dropdown(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username FROM users WHERE is_player = 1')
        player_names = [row[0] for row in cursor.fetchall()]
        self.player_combobox.clear()
        self.player_combobox.addItems(player_names)
        
    def add_player_to_campaign(self):
        selected_player = self.player_combobox.currentText()
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (selected_player,))
        result = cursor.fetchone()
        if result:
            player_id = result[0]
            cursor.execute('''
                SELECT * 
                FROM campaign_players_characters
                WHERE player_id = ? AND campaign_id = ?
            ''', (player_id, self.session.campaign_id))
            result = cursor.fetchone()
            if result:
                self.error_label.setText('Player already exists in this campaign.')
            else:
                cursor.execute('''
                    INSERT INTO campaign_players_characters (god_id, player_id, campaign_id)
                    VALUES (?, ?, ?)
                ''', (self.session.user_id, player_id, self.session.campaign_id))
                self.conn.commit()
                self.accept()

