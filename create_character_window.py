from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QGridLayout, QWidget, QSizePolicy, QTextEdit, QMessageBox
from assign_attribute_window import AssignAttributesWindow
import sqlite3

class CreateCharacterWindow(QMainWindow):
    def __init__(self, session, db_path, *args, **kwargs):
        super(CreateCharacterWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Create Character")
        self.setMinimumSize(800, 600)
        self.session = session
        self.db_path = db_path
        


        # Main layout
        main_layout = QVBoxLayout()

        # Grid layout
        grid_layout = QGridLayout()

        # Player Name
        player_name_label = QLabel("Player Name:")
        player_name_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        grid_layout.addWidget(player_name_label, 0, 0)
        self.player_name_label = QLabel(self.session.username)
        self.player_name_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        grid_layout.addWidget(self.player_name_label, 0, 1)

        # Character Name
        grid_layout.addWidget(QLabel("Character Name:"), 1, 0)
        self.character_name_lineedit = QLineEdit()
        grid_layout.addWidget(self.character_name_lineedit, 1, 1)

        # Campaign
        campaign_label = QLabel("Campaign:")
        campaign_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        grid_layout.addWidget(campaign_label, 0, 2)
        self.campaign_label = QLabel(self.session.campaign_name)
        self.campaign_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        grid_layout.addWidget(self.campaign_label, 0, 3)

        # Race
        grid_layout.addWidget(QLabel("Race:"), 1, 2)
        self.race_combobox = QComboBox()
        self.load_races()       
        grid_layout.addWidget(self.race_combobox, 1, 3)

        # Age
        grid_layout.addWidget(QLabel("Age:"), 2, 0)
        self.age_lineedit = QLineEdit()
        grid_layout.addWidget(self.age_lineedit, 2, 1)

        # Sex
        grid_layout.addWidget(QLabel("Sex:"), 3, 0)
        self.sex_lineedit = QLineEdit()
        grid_layout.addWidget(self.sex_lineedit, 3, 1)

        # Height
        grid_layout.addWidget(QLabel("Height:"), 2, 2)
        self.height_lineedit = QLineEdit()
        grid_layout.addWidget(self.height_lineedit, 2, 3)

        # Weight
        grid_layout.addWidget(QLabel("Weight:"), 3, 2)
        self.weight_lineedit = QLineEdit()
        grid_layout.addWidget(self.weight_lineedit, 3, 3)

        # Skin Color
        grid_layout.addWidget(QLabel("Skin Color:"), 4, 0)
        self.skin_color_lineedit = QLineEdit()
        grid_layout.addWidget(self.skin_color_lineedit, 4, 1)

        # Hair Color
        grid_layout.addWidget(QLabel("Hair Color:"), 5, 0)
        self.hair_color_lineedit = QLineEdit()
        grid_layout.addWidget(self.hair_color_lineedit, 5, 1)

        # Eye Color
        grid_layout.addWidget(QLabel("Eye Color:"), 4, 2)
        self.eye_color_lineedit = QLineEdit()
        grid_layout.addWidget(self.eye_color_lineedit, 4, 3)

        # Deity
        grid_layout.addWidget(QLabel("Deity:"), 5, 2)
        self.deity_lineedit = QLineEdit()
        grid_layout.addWidget(self.deity_lineedit, 5, 3)

        # Fate
        grid_layout.addWidget(QLabel("Fate:"), 6, 0)
        self.fate_lineedit = QLineEdit()
        grid_layout.addWidget(self.fate_lineedit, 6, 1)

        # Defining Marks & Character Quirks
        grid_layout.addWidget(QLabel("Defining Marks & Character Quirks:"), 7, 0, 1, 4)  # This label spans four columns
        self.character_quirks_textedit = QTextEdit()
        grid_layout.addWidget(self.character_quirks_textedit, 8, 0, 3, 4)  # This QTextEdit spans four columns and four rows


        main_layout.addLayout(grid_layout)

        # Save and Continue Button
        save_and_continue_button = QPushButton("Save and Continue")
        save_and_continue_button.clicked.connect(self.save_and_continue)
        main_layout.addWidget(save_and_continue_button)

        # Exit without saving button
        exit_button = QPushButton("Exit Without Saving")
        exit_button.clicked.connect(self.close)
        main_layout.addWidget(exit_button)

        # Set the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def load_races(self):
        # Connect to the database
        c = self.db_path.cursor()

        # Query the database
        c.execute("SELECT allowed_races FROM campaigns WHERE campaign_name = ?", (self.session.campaign_name,))

        # Fetch the comma-separated string of races
        races_string = c.fetchone()[0]  # Fetch the first column of the first (and only) row

        # Split the string by commas
        races_list = races_string.split(',')

        # Add each race to the combobox
        for race in races_list:
            self.race_combobox.addItem(race.strip())  # .strip() removes any leading or trailing whitespace
            
    def save_and_continue(self):
        character_name = self.character_name_lineedit.text()
        race_name = self.race_combobox.currentText()
        age = self.age_lineedit.text()
        sex = self.sex_lineedit.text()
        height = self.height_lineedit.text()
        weight = self.weight_lineedit.text()
        skin_color = self.skin_color_lineedit.text()
        hair_color = self.hair_color_lineedit.text()
        eye_color = self.eye_color_lineedit.text()
        deity = self.deity_lineedit.text()
        fate = self.fate_lineedit.text()
        defining_marks = self.character_quirks_textedit.toPlainText()

        c = self.db_path.cursor()

        # get race_id from race_name
        c.execute("SELECT id FROM races WHERE race_name = ?", (race_name,))
        race_id = c.fetchone()[0]
        self.session.race_id = race_id

        # Update database
        update_sql = """UPDATE character_record_sheet SET
                        character_name = ?,
                        race_id = ?,
                        age = ?,
                        sex = ?,
                        height = ?,
                        weight = ?,
                        skin_color = ?,
                        hair_color = ?,
                        eye_color = ?,
                        deity = ?,
                        fate = ?,
                        dmcq = ?
                    WHERE player_id = ? AND campaign_id = ? AND character_id = ? AND character_name = 'New Character'"""


        update_params = (character_name, self.session.race_id, age, sex, height, weight, skin_color, hair_color, eye_color, deity, fate, defining_marks,
                        self.session.user_id, self.session.campaign_id, self.session.character_id)

        

        c.execute(update_sql, update_params)

        # Commit the transaction
        self.db_path.commit()

        # Check if the update was successful
        if c.rowcount == 0:
            # Show an error message
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Warning)
            error_message.setText("No character with the name 'New Character' was found.")
            error_message.setWindowTitle("Error")
            error_message.exec_()
            return
        else:
            # If the update was successful, update the session attributes and switch to the next window
            self.session.character_name = character_name
            self.session.race_name = race_name
            

            self.assign_attribute_window = AssignAttributesWindow(self.session, self.db_path)
            self.assign_attribute_window.show()
            self.close()


