from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QButtonGroup, QRadioButton, QCheckBox, QScrollArea, QVBoxLayout, QGridLayout, QPushButton, QComboBox, QWidget, QGroupBox
from PyQt5.QtCore import Qt, pyqtSignal
import sqlite3

class CreateCampaign(QDialog):
    campaign_created = pyqtSignal()

    def __init__(self, session, conn):
        super().__init__()

        self.session = session
        self.conn = conn

        self.setWindowTitle("Create Campaign")
        self.setGeometry(0, 0, 850, 650)
        self.create_widgets()

    def get_genre_names(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT genre_name FROM genres')
        return [row[0] for row in cursor.fetchall()]

    def get_race_names(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT race_name FROM races ORDER BY id')
        return [row[0] for row in cursor.fetchall()]

    def create_widgets(self):
        self.grid_layout = QGridLayout()

        self.grid_layout.addWidget(QLabel("Choose Genre:"), 0, 0)
        self.choose_genre_combobox = QComboBox()
        genre_names = self.get_genre_names()
        for genre_name in genre_names:
            self.choose_genre_combobox.addItem(genre_name)
        self.grid_layout.addWidget(self.choose_genre_combobox, 0, 1, 1, 2)

        self.field_labels = ["Campaign Name", "Attribute Points", "Skill Points", "Max Skill", "Next Tier", "Max Tier", "Starting Credits"]
        self.entries = []
        for i, label in enumerate(self.field_labels):
            self.grid_layout.addWidget(QLabel(label), (i//3)+1, (i%3)*2)
            entry = QLineEdit()
            self.grid_layout.addWidget(entry, (i//3)+1, (i%3)*2+1)
            self.entries.append(entry)

        self.currency_var = QButtonGroup(self)
        self.currency_label = QLabel("Currency Type:")
        self.grid_layout.addWidget(self.currency_label, 4, 0)
        self.use_coins = QRadioButton('Coins')
        self.use_credits = QRadioButton('Credits')
        self.currency_var.addButton(self.use_coins, 1)
        self.currency_var.addButton(self.use_credits, 2)
        self.grid_layout.addWidget(self.use_coins, 4, 1)
        self.grid_layout.addWidget(self.use_credits, 4, 2)

        self.tiers_frame = QGroupBox("Allowed Tiers")
        self.tiers_layout = QGridLayout()
        self.tiers = ["Tier 1", "Tier 2", "Tier 3", "Magic", "Talismanism", "Faith", "Psyonics", "Special Abilities"]
        self.tier_vars = {}
        for i, tier in enumerate(self.tiers):
            self.tier_vars[tier] = QCheckBox(tier)
            self.tiers_layout.addWidget(self.tier_vars[tier], i//4, i%4)
        self.tiers_frame.setLayout(self.tiers_layout)
        self.grid_layout.addWidget(self.tiers_frame, 5, 0, 1, 6)

        self.races_frame = QGroupBox("Allowed Races")
        self.races_layout = QVBoxLayout()
        self.scrollable_races_frame = QScrollArea()
        self.scrollable_races_frame.setWidgetResizable(True)
        self.scrollable_races_frame.setWidget(self.races_frame)
        race_names = self.get_race_names()
        self.race_vars = {}
        for race_name in race_names:
            self.race_vars[race_name] = QCheckBox(race_name)
            self.races_layout.addWidget(self.race_vars[race_name])
        self.races_frame.setLayout(self.races_layout)
        self.grid_layout.addWidget(self.scrollable_races_frame, 6, 0, 1, 6)

        self.submit_button = QPushButton("Submit Campaign")
        self.close_button = QPushButton("Close")
        self.grid_layout.addWidget(self.submit_button, 7, 4)
        self.submit_button.clicked.connect(self.submit_campaign)
        self.grid_layout.addWidget(self.close_button, 7, 5)
        self.close_button.clicked.connect(self.close)
        self.close_button.clicked.connect(self.close)

        self.setLayout(self.grid_layout)

    def gather_inputs(self):
        campaign_data = {
            "god_id": self.session.user_id,
            "genre": self.choose_genre_combobox.currentText(),
            "campaign_name": self.entries[0].text(),
            "attribute_points": int(self.entries[1].text()),
            "skill_points": int(self.entries[2].text()),
            "max_skill": int(self.entries[3].text()),
            "next_tier": int(self.entries[4].text()),
            "max_tier": int(self.entries[5].text()),
            "starting_credits": int(self.entries[6].text()),
            "use_coins": int(self.use_coins.isChecked()),
            "use_credits": int(self.use_credits.isChecked()),
            "allowed_skills": ", ".join(tier for tier, checkbox in self.tier_vars.items() if checkbox.isChecked()),
            "allowed_races": ", ".join(race for race, checkbox in self.race_vars.items() if checkbox.isChecked()),
        }
        return campaign_data

    def submit_campaign(self):
        campaign_data = self.gather_inputs()
        cursor = self.conn.cursor()

        cursor.execute(
            '''INSERT INTO campaigns(
                    god_id, genre, starting_credits, use_coins, use_credits,
                    campaign_name, attribute_points, skill_points, max_skill, next_tier,
                    max_tier, allowed_skills, allowed_races) 
            VALUES(:god_id, :genre, :starting_credits, :use_coins, :use_credits,
                    :campaign_name, :attribute_points, :skill_points, :max_skill, :next_tier,
                    :max_tier, :allowed_skills, :allowed_races)''',
            campaign_data
        )
        self.conn.commit()
        self.campaign_created.emit()
