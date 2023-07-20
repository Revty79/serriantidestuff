from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QSpinBox, QFormLayout, QWidget
from spend_skill_points_window import SpendSkillPointsWindow  

import sqlite3

class AssignAttributesWindow(QMainWindow):
    def __init__(self, session, db_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Create Character")
        self.setMinimumSize(500, 250)
        self.session = session
        self.db_path = db_path

        self.fetch_max_race_attributes()
        self.fetch_campaign_attribute_points()

        self.attribute_counter = QLabel(f'Attribute Points: {self.attribute_points-60}')
        self.attributes = {
            'Strength': QSpinBox(),
            'Dexterity': QSpinBox(),
            'Constitution': QSpinBox(),
            'Intelligence': QSpinBox(),
            'Wisdom': QSpinBox(),
            'Charisma': QSpinBox(),
        }

        for attribute, spin_box in self.attributes.items():
            spin_box.setRange(1, self.max_attributes[attribute])
            spin_box.setValue(10)
            spin_box.valueChanged.connect(self.update_attribute_points)

        layout = QFormLayout()
        layout.addRow(self.attribute_counter)

        for attribute, spin_box in self.attributes.items():
            layout.addRow(QLabel(f'{attribute}:'), spin_box)


        self.save_and_continue_button = QPushButton('Save and Continue')
        self.save_and_continue_button.clicked.connect(self.save_and_continue_button_clicked)

        layout.addRow(self.save_and_continue_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def fetch_campaign_attribute_points(self):
        conn = self.db_path
        cur = conn.cursor()
        cur.execute("SELECT attribute_points FROM campaigns WHERE id=?", (self.session.campaign_id,))
        self.attribute_points = cur.fetchone()[0]

    def fetch_max_race_attributes(self):
        conn = self.db_path
        cur = conn.cursor()
        cur.execute("""SELECT max_strength, max_dexterity, max_constitution, max_intelligence, max_wisdom, max_charisma
                    FROM races WHERE id=?""", (self.session.race_id,))
        self.max_attributes = dict(zip(['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma'], cur.fetchone()))

        
    def update_attribute_points(self):
        total_points_assigned = sum(spin_box.value() for spin_box in self.attributes.values())
        points_left = self.attribute_points - total_points_assigned
        self.attribute_counter.setText(f'Attribute Points: {points_left}')

    def save_and_continue_button_clicked(self):
        conn = self.db_path
        cur = conn.cursor()

        # 1. Collect attribute scores
        attribute_values = {k: v.value() for k, v in self.attributes.items()}

        # 2. Fetch mods and percentages for each attribute
        for attribute, value in attribute_values.items():
            cur.execute("SELECT mod, percent FROM attribute_mods_percents WHERE attribute=?", (value,))
            mod, percent = cur.fetchone()
            attribute_values[attribute] = (value, mod, percent)

        # 3. Calculate HP
        cur.execute("SELECT * FROM hp_data WHERE attribute=?", (attribute_values['Constitution'][0],))
        hp_data = cur.fetchone()

        # 4. Fetch base initiative
        cur.execute("SELECT base_initiative FROM initiative_data WHERE dexterity=?", (attribute_values['Dexterity'][0],))
        base_initiative = cur.fetchone()[0]

        # 5. Fetch base movement
        cur.execute("SELECT base_movement FROM races WHERE id=?", (self.session.race_id,))
        base_movement = cur.fetchone()[0]

        # 6. Calculate total initiative
        total_initiative = base_initiative * base_movement

        # 7. Update the character_record_sheet table
        cur.execute("""
            UPDATE character_record_sheet 
            SET
                attribute_strength=?, mod_strength=?, percent_strength=?,
                attribute_dexterity=?, mod_dexterity=?, percent_dexterity=?,
                attribute_constitution=?, mod_constitution=?, percent_constitution=?,
                attribute_intelligence=?, mod_intelligence=?, percent_intelligence=?,
                attribute_wisdom=?, mod_wisdom=?, percent_wisdom=?,
                attribute_charisma=?, mod_charisma=?, percent_charisma=?,
                base_hp=?, total_hp=?, head_hp=?, chest_hp=?, r_arm_hp=?, l_arm_hp=?, r_leg_hp=?, l_leg_hp=?,
                base_movement=?, base_initiative=?, total_initiative=?
            WHERE player_id=? AND campaign_id=? AND character_id = ? AND character_name=?
            """, (
                *attribute_values['Strength'], 
                *attribute_values['Dexterity'],
                *attribute_values['Constitution'],
                *attribute_values['Intelligence'],
                *attribute_values['Wisdom'],
                *attribute_values['Charisma'],
                *hp_data[1:],  # skip attribute column in hp_data
                base_movement, base_initiative, total_initiative,
                self.session.user_id,  # assumed player_id is stored in the session
                self.session.campaign_id,  # assumed campaign_id is stored in the session
                self.session.character_id,  # assumed character_id is stored in the session
                self.session.character_name  # assumed character_name is stored in the session
            )
        )


        conn.commit()
        
            # Open the SpendSkillPointsWindow
        self.spend_skill_points_window = SpendSkillPointsWindow(self.session, self.db_path)
        self.spend_skill_points_window.show()
        self.close()
