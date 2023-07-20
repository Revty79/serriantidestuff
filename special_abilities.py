from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QTabWidget, QWidget, QLabel, QTextEdit, QScrollArea, QGridLayout
from PyQt5.QtCore import Qt
import sqlite3

class SpecialAbilitiesWindow(QMainWindow):
    def __init__(self, session, db_path, max_skill, next_tier, max_tier, skill_points, allowed_skills, spend_skill_points_window):
        super().__init__()

        self.session = session
        self.db_path = db_path
        self.skill_points = skill_points
        self.spend_skill_points_window = spend_skill_points_window
        self.max_skill = max_skill
        self.next_tier = next_tier
        self.max_tier = max_tier
        self.allowed_skills = allowed_skills

        self.setWindowTitle("Special Abilities Skills")
        self.setMinimumSize(800, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()

        self.skill_points_label = QLabel(f"Skill Points: {self.skill_points}")

        self.skill_tabs = QTabWidget()

        self.skill_buttons = {}  # This will store a reference to each button
        self.skill_id_by_name = {}  # This will store the mapping from skill name to skill ID

        self.populate_skill_tabs()

        self.back_to_spend_skill_points_button = QPushButton("Back to Spend Skill Points")
        self.back_to_spend_skill_points_button.clicked.connect(self.back_to_spend_skill_points)

        self.your_skills_tab = QWidget()
        self.your_skills_display = QTextEdit()
        self.your_skills_display.setReadOnly(True)
        self.reset_skills_button = QPushButton("Reset Skills")
        self.reset_skills_button.clicked.connect(self.reset_skills)

        your_skills_layout = QVBoxLayout()
        your_skills_layout.addWidget(self.your_skills_display)
        your_skills_layout.addWidget(self.reset_skills_button)

        self.your_skills_tab.setLayout(your_skills_layout)
        self.skill_tabs.addTab(self.your_skills_tab, "Your Skills")

        self.layout.addWidget(self.skill_points_label)
        self.layout.addWidget(self.skill_tabs)
        self.layout.addWidget(self.back_to_spend_skill_points_button)

        self.main_widget.setLayout(self.layout)

    def populate_skill_tabs(self):
        special_abilities_tab = QWidget()
        special_abilities_layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(special_abilities_tab)
        
        special_abilities = self.get_special_abilities()
        for i, ability in enumerate(special_abilities):
            ability_button = QPushButton(ability[2])
            ability_button.clicked.connect(lambda checked, a=ability: self.buy_skill(a))
            special_abilities_layout.addWidget(ability_button)

        special_abilities_tab.setLayout(special_abilities_layout)
        self.skill_tabs.addTab(scroll, "Special Abilities")

    def get_special_abilities(self):
        with self.db_path as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM master_skills WHERE type = 'special ability'")
            return cur.fetchall()

    def buy_skill(self, ability):
        current_ability_points = self.session.skills_purchased.get(ability[0], 0)
        max_points_allowed = min(self.max_skill, 100)  # Cap total skill points for special abilities at 100

        if self.skill_points > 0 and current_ability_points < max_points_allowed:
            self.session.skills_purchased[ability[0]] = current_ability_points + 1
            self.skill_points -= 1
            self.skill_points_label.setText(f"Skill Points: {self.skill_points}")
            self.update_your_skills_display()

    def update_your_skills_display(self):
        self.your_skills_display.clear()
        for ability_id, points in self.session.skills_purchased.items():
            ability = self.get_skill_by_id(ability_id)
            if ability:
                self.your_skills_display.append(f"{ability[2]}: {points} point(s)")

    def reset_skills(self):
        self.skill_points += sum(self.session.skills_purchased.values())
        self.session.skills_purchased.clear()
        self.update_your_skills_display()
        self.skill_points_label.setText(f"Skill Points: {self.skill_points}")
        self.skill_tabs.clear()
        self.populate_skill_tabs()

    def back_to_spend_skill_points(self):
        self.spend_skill_points_window.update_your_skills_display(self.session.skills_purchased)
        self.spend_skill_points_window.update_skill_points(self.skill_points)
        self.close()
        self.spend_skill_points_window.show()

    def get_skill_by_id(self, skill_id):
        with self.db_path as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM master_skills WHERE id = ?", (skill_id,))
            return cur.fetchone()
