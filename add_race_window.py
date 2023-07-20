from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QFormLayout, QWidget, QGridLayout, QComboBox, QPushButton
import sqlite3

class AddRaceWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(AddRaceWindow, self).__init__(*args, **kwargs)

        # Setup widgets
        self.race_name = QLineEdit(self)
        self.create_tables()

        self.max_strength = QLineEdit(self)
        self.max_dexterity = QLineEdit(self)
        self.max_constitution = QLineEdit(self)
        self.max_intelligence = QLineEdit(self)
        self.max_wisdom = QLineEdit(self)
        self.max_charisma = QLineEdit(self)
        self.base_magic = QLineEdit(self)
        self.base_movement = QLineEdit(self)

        self.skill_dropdowns = [QComboBox(self) for _ in range(10)]
        self.skill_entries = [QLineEdit(self) for _ in range(10)]

        self.ability_dropdowns = [QComboBox(self) for _ in range(10)]
        self.ability_entries = [QLineEdit(self) for _ in range(10)]

        # Setup buttons
        self.save_button = QPushButton('Save Race', self)
        self.close_button = QPushButton('Close Window', self)

        # Setup layout
        self.grid_layout = QGridLayout()

        race_form_layout = QFormLayout()
        race_form_layout.addRow(QLabel("Race Name:"), self.race_name)
        race_form_layout.addRow(QLabel("Max Strength:"), self.max_strength)
        race_form_layout.addRow(QLabel("Max Dexterity:"), self.max_dexterity)
        race_form_layout.addRow(QLabel("Max Constitution:"), self.max_constitution)
        race_form_layout.addRow(QLabel("Max Intelligence:"), self.max_intelligence)
        race_form_layout.addRow(QLabel("Max Wisdom:"), self.max_wisdom)
        race_form_layout.addRow(QLabel("Max Charisma:"), self.max_charisma)
        race_form_layout.addRow(QLabel("Base Magic:"), self.base_magic)
        race_form_layout.addRow(QLabel("Base Movement:"), self.base_movement)
        race_form_layout.addRow(self.save_button)
        race_form_layout.addRow(self.close_button)
        self.grid_layout.addLayout(race_form_layout, 0, 0)

        skill_form_layout = QFormLayout()
        for i in range(10):
            skill_form_layout.addRow(QLabel(f"Skill {i+1}:"), self.skill_dropdowns[i])
            skill_form_layout.addRow(QLabel(f"Skill {i+1} Points:"), self.skill_entries[i])
        self.grid_layout.addLayout(skill_form_layout, 0, 1)

        ability_form_layout = QFormLayout()
        for i in range(10):
            ability_form_layout.addRow(QLabel(f"Ability {i+1}:"), self.ability_dropdowns[i])
            ability_form_layout.addRow(QLabel(f"Ability {i+1} Points:"), self.ability_entries[i])
        self.grid_layout.addLayout(ability_form_layout, 0, 2)

        # Connect buttons to their respective slots
        self.save_button.clicked.connect(self.save_race)
        self.close_button.clicked.connect(self.close_window)

        # Set widget to hold the layout
        widget = QWidget()
        widget.setLayout(self.grid_layout)
        self.setCentralWidget(widget)

        # Load the skills and abilities into the dropdowns
        self.load_skills_and_abilities()
        
    def create_tables(self):
        # Create a connection to the races database
        conn = sqlite3.connect('races.db')
        cursor = conn.cursor()

        # Create the races table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS races (
                id INTEGER PRIMARY KEY,
                race_name TEXT NOT NULL,
                max_strength INTEGER NOT NULL,
                max_dexterity INTEGER NOT NULL,
                max_constitution INTEGER NOT NULL,
                max_intelligence INTEGER NOT NULL,
                max_wisdom INTEGER NOT NULL,
                max_charisma INTEGER NOT NULL,
                base_magic INTEGER NOT NULL,
                base_movement INTEGER NOT NULL
            )
        ''')

        # Create the race_bonus_skills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS race_bonus_skills (
                id INTEGER PRIMARY KEY,
                race_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                skill_points INTEGER NOT NULL,
                FOREIGN KEY(race_id) REFERENCES races(id)
            )
        ''')

        # Create the race_special_abilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS race_special_abilities (
                id INTEGER PRIMARY KEY,
                race_id INTEGER NOT NULL,
                ability_id INTEGER NOT NULL,
                ability_name TEXT NOT NULL,
                ability_points INTEGER NOT NULL,
                FOREIGN KEY(race_id) REFERENCES races(id)
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()


    def load_skills_and_abilities(self):
        # Create a connection to the master database
        conn = sqlite3.connect('serrian_tide.db')
        cursor = conn.cursor()

        # Fetch skills and abilities from the master_skills table
        cursor.execute("SELECT id, name FROM master_skills WHERE type != 'special ability'")
        skills = cursor.fetchall()
        skills.append(('None', 'None'))  # append a None option
        for dropdown in self.skill_dropdowns:
            dropdown.addItem('None', 'None')
            for skill in skills:
                dropdown.addItem(skill[1], skill[0])

        cursor.execute("SELECT id, name FROM master_skills WHERE type = 'special ability'")
        abilities = cursor.fetchall()
        abilities.append(('None', 'None'))  # append a None option
        for dropdown in self.ability_dropdowns:
            dropdown.addItem('None', 'None')
            for ability in abilities:
                dropdown.addItem(ability[1], ability[0])

        # Close the connection to the master database
        conn.close()
        
    def save_race(self):
        # Create a connection to the races database
        conn = sqlite3.connect('races.db')
        cursor = conn.cursor()

        # Fetch the input values
        race_name = self.race_name.text()
        max_strength = self.max_strength.text()
        max_dexterity = self.max_dexterity.text()
        max_constitution = self.max_constitution.text()
        max_intelligence = self.max_intelligence.text()
        max_wisdom = self.max_wisdom.text()
        max_charisma = self.max_charisma.text()
        base_magic = self.base_magic.text()
        base_movement = self.base_movement.text()

        # Insert the race data into the races table
        cursor.execute('INSERT INTO races (race_name, max_strength, max_dexterity, max_constitution, max_intelligence, max_wisdom, max_charisma, base_magic, base_movement) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (race_name, max_strength, max_dexterity, max_constitution, max_intelligence, max_wisdom, max_charisma, base_magic, base_movement))

        # Get the ID of the race that was just inserted
        race_id = cursor.lastrowid

        # Insert the skills and abilities data into their respective tables
        for i in range(10):
            skill_id = self.skill_dropdowns[i].currentData()
            skill_name = self.skill_dropdowns[i].currentText()
            if skill_id and skill_name != 'None':
                skill_points = self.skill_entries[i].text()
                cursor.execute('INSERT INTO race_bonus_skills (race_id, skill_id, skill_name, skill_points) VALUES (?, ?, ?, ?)', (race_id, skill_id, skill_name, skill_points))

            ability_id = self.ability_dropdowns[i].currentData()
            ability_name = self.ability_dropdowns[i].currentText()
            if ability_id and ability_name != 'None':
                ability_points = self.ability_entries[i].text()
                cursor.execute('INSERT INTO race_special_abilities (race_id, ability_id, ability_name, ability_points) VALUES (?, ?, ?, ?)', (race_id, ability_id, ability_name, ability_points))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def close_window(self):
        self.close()
