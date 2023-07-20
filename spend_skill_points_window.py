import sqlite3

from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QGridLayout, QTextEdit
from strength_skills import StrengthSkillWindow
from dexterity_skills import DexteritySkillWindow
from constitution_skills import ConstitutionSkillWindow
from intelligence_skills import IntelligenceSkillWindow
from wisdom_skills import WisdomSkillWindow 
from charisma_skills import CharismaSkillWindow
from magic_skills import MagicSkillWindow  
from talismanism_skills import TalismanismSkillWindow 
from faith_skills import FaithSkillWindow
from psyonics_skills import PsyonicsSkillWindow 
from special_abilities import SpecialAbilitiesWindow
from skill_calculator import SkillCalculator

class SpendSkillPointsWindow(QMainWindow):
    def __init__(self, session, db_path):
        super().__init__()

        self.session = session
        self.db_path = db_path

        rules = self.fetch_rules()
        self.skill_points = rules['skill_points']
        self.max_skill = rules['max_skill']
        self.next_tier = rules['next_tier']
        self.max_tier = rules['max_tier']
        self.allowed_skills = rules['allowed_skills'].split(', ')
        
        self.setWindowTitle("Skill Points")
        self.setMinimumSize(400, 400)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.skill_layout = QGridLayout()
        
        self.skill_buttons = {}
        skills = ["Strength", "Dexterity", "Constitution", "Intelligence", "Magic", 
                  "Talismanism", "Wisdom", "Faith", "Psyonics", "Charisma", "Special Abilities"]

        lockable_skills = ["Magic", "Talismanism", "Faith", "Psyonics", "Special Abilities"]
        allowed_skills = rules["allowed_skills"].split(', ')
        
        for i, skill in enumerate(skills):
            self.skill_buttons[skill] = QPushButton(skill)
            if skill in lockable_skills and skill not in allowed_skills:
                self.skill_buttons[skill].setEnabled(False)
            if skill == "Strength":
                self.skill_buttons[skill].clicked.connect(self.open_strength_skills)
            elif skill == "Dexterity":
                self.skill_buttons[skill].clicked.connect(self.open_dexterity_skills)
            elif skill == "Constitution":
                self.skill_buttons[skill].clicked.connect(self.open_constitution_skills)
            elif skill == "Intelligence":
                self.skill_buttons[skill].clicked.connect(self.open_intelligence_skills)
            elif skill == "Wisdom":
                self.skill_buttons[skill].clicked.connect(self.open_wisdom_skills)
            elif skill == "Charisma":
                self.skill_buttons[skill].clicked.connect(self.open_charisma_skills)
            elif skill == "Magic":
                self.skill_buttons[skill].clicked.connect(self.open_magic_skills)
            elif skill == "Talismanism":
                self.skill_buttons[skill].clicked.connect(self.open_talismanism_skills)
            elif skill == "Faith":
                self.skill_buttons[skill].clicked.connect(self.open_faith_skills)
            elif skill == "Psyonics":
                self.skill_buttons[skill].clicked.connect(self.open_psyonics_skills)
            elif skill == "Special Abilities":
                self.skill_buttons[skill].clicked.connect(self.open_special_abilities)
            self.skill_layout.addWidget(self.skill_buttons[skill], i // 3, i % 3)
        
        self.skill_points_label = QLabel(f"Skill Points: {self.skill_points}")
        
        self.your_skills_display = QTextEdit()
        self.your_skills_display.setReadOnly(True)
        
        self.save_and_continue_button = QPushButton("Save and Close")
        self.save_and_continue_button.clicked.connect(self.save_and_continue)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.skill_points_label)
        self.main_layout.addLayout(self.skill_layout)
        self.main_layout.addWidget(self.your_skills_display)
        self.main_layout.addWidget(self.save_and_continue_button)

        self.main_widget.setLayout(self.main_layout)

    def execute_db_query(self, query, params):
        conn = self.db_path
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result

    def fetch_rules(self):
        query = "SELECT skill_points, max_skill, next_tier, max_tier, allowed_skills FROM campaigns WHERE id = ?"
        params = (self.session.campaign_id,)  # use dot notation here
        result = self.execute_db_query(query, params)
        return {
            "skill_points": result[0],
            "max_skill": result[1],
            "next_tier": result[2],
            "max_tier": result[3],
            "allowed_skills": result[4]
        }

    def update_your_skills_display(self, skills_purchased):
        self.your_skills_display.clear()
        for skill_id, points in skills_purchased.items():
            skill_name = self.get_skill_name(skill_id)
            self.your_skills_display.append(f"{skill_name}: {points} point(s)")

    def get_skill_name(self, skill_id):
        query = "SELECT name FROM master_skills WHERE id = ?"
        params = (skill_id,)
        result = self.execute_db_query(query, params)
        return result[0] if result else "Unknown Skill"


    def spend_skill_points(self, points_to_spend):
        if self.skill_points >= points_to_spend:
            self.skill_points -= points_to_spend
            self.skill_points_label.setText(f"Skill Points: {self.skill_points}")
        else:
            # Not enough skill points to spend, show an error message or do something else
            pass

    def open_strength_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.strength_skill_window = StrengthSkillWindow(self.session, self.db_path, self.max_skill, self.next_tier, self.max_tier, self.skill_points, self.allowed_skills, self)
        self.strength_skill_window.show()
        
    def open_dexterity_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.dexterity_skill_window = DexteritySkillWindow(self.session, self.db_path, self.max_skill, self.next_tier, self.max_tier, self.skill_points, self.allowed_skills, self)
        self.dexterity_skill_window.show()

    def open_constitution_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.constitution_skill_window = ConstitutionSkillWindow(self.session, self.db_path, self.max_skill, self.next_tier, self.max_tier, self.skill_points, self.allowed_skills, self)
        self.constitution_skill_window.show()

    def open_intelligence_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.intelligence_skill_window = IntelligenceSkillWindow(self.session, self.db_path, self.max_skill, self.next_tier, self.max_tier, self.skill_points, self.allowed_skills, self)
        self.intelligence_skill_window.show()

    def open_wisdom_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.wisdom_skill_window = WisdomSkillWindow(self.session, self.db_path, self.max_skill, self.next_tier, self.max_tier, self.skill_points, self.allowed_skills, self)
        self.wisdom_skill_window.show()

    def open_charisma_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.charisma_skill_window = CharismaSkillWindow(self.session, self.db_path, self.max_skill, self.next_tier, self.max_tier, self.skill_points, self.allowed_skills, self)
        self.charisma_skill_window.show()

    def open_magic_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.magic_skill_window = MagicSkillWindow(self.session, self.db_path, self.max_skill, self.max_tier, self.skill_points, self)
        self.magic_skill_window.show()
        
    def open_talismanism_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.talismanism_skill_window = TalismanismSkillWindow(self.session, self.db_path, self.max_skill, self.max_tier, self.skill_points, self)
        self.talismanism_skill_window.show()
        
    def open_faith_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.faith_skill_window = FaithSkillWindow(self.session, self.db_path, self.max_skill, self.max_tier, self.skill_points, self)
        self.faith_skill_window.show()
        
    def open_psyonics_skills(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.psyonics_skill_window = PsyonicsSkillWindow(self.session, self.db_path, self.max_skill, self.max_tier, self.skill_points, self)
        self.psyonics_skill_window.show()
        
    def open_special_abilities(self):
        self.hide()  # Hide the SpendSkillPointsWindow
        self.special_abilities_window = SpecialAbilitiesWindow(self.session, self.db_path, self.max_skill, self.next_tier, self.max_tier, self.skill_points, self.allowed_skills, self)
        self.special_abilities_window.show()
        
    def update_skill_points(self, skill_points):
        self.skill_points = skill_points
        self.skill_points_label.setText(f"Skill Points: {self.skill_points}")

    def save_and_continue(self):
        # First, make sure you have the connection to your database
        conn = self.db_path
        cursor = conn.cursor()

        # Insert skills into the character_skills table
        for skill_id, number in self.session.skills_purchased.items():
            cursor.execute("SELECT name FROM master_skills WHERE id = ?", (skill_id,))
            skill_name = cursor.fetchone()[0]
            cursor.execute("INSERT INTO character_skills (character_id, skill_id, skill_name, number) VALUES (?, ?, ?, ?)", (self.session.character_id, skill_id, skill_name, number))
                
        # Commit the changes
        conn.commit()

        # Close the current window
        self.close()

        # Initiate SkillCalculator pass-through
        self.skill_calculator = SkillCalculator(self.session, self.db_path)
