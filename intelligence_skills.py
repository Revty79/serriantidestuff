from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QTabWidget, QWidget, QLabel, QTextEdit, QScrollArea, QGridLayout, QHBoxLayout
from PyQt5.QtCore import Qt
import sqlite3

class IntelligenceSkillWindow(QMainWindow):
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

        self.setWindowTitle("Intelligence Skills")
        self.setMinimumSize(800, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()

        self.skill_points_label = QLabel(f"Skill Points: {self.skill_points}")

        self.skill_tabs = QTabWidget()

        self.skill_buttons = {}  
        self.skill_id_by_name = {}

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
        tiers = [1, 2, 3]
        for tier in tiers:
            if 'Tier '+str(tier) in self.allowed_skills: 
                skill_tab = QWidget()
                skill_layout = QVBoxLayout()
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(skill_tab)
                
                skills = self.get_skills_by_tier(tier)
                for i, skill in enumerate(skills):
                    skill_widget = QWidget()
                    skill_widget_layout = QHBoxLayout()

                    skill_name_label = QLabel(skill[2])
                    points_label = QLabel('0')  # Initialize with 0 points
                    add_button = QPushButton('+')
                    subtract_button = QPushButton('-')

                    add_button.clicked.connect(lambda checked, s=skill: self.add_skill_point(s, points_label))
                    subtract_button.clicked.connect(lambda checked, s=skill: self.subtract_skill_point(s, points_label))

                    skill_widget_layout.addWidget(skill_name_label)
                    skill_widget_layout.addWidget(points_label)
                    skill_widget_layout.addWidget(add_button)
                    skill_widget_layout.addWidget(subtract_button)

                    skill_widget.setLayout(skill_widget_layout)
                    skill_layout.addWidget(skill_widget)

                    self.skill_buttons[skill[0]] = (points_label, add_button, subtract_button)
                    self.skill_id_by_name[skill[2]] = skill[0]
                
                skill_tab.setLayout(skill_layout)
                self.skill_tabs.addTab(scroll, f"Tier {tier}")

    def get_skill_by_id(self, skill_id):
        with self.db_path as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM master_skills WHERE id = ?", (skill_id,))
            return cur.fetchone()

    def get_skills_by_tier(self, tier):
        with self.db_path as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM master_skills WHERE tier = ? AND attribute = 'Intelligence' AND type = 'normal'", (tier,))
            return cur.fetchall()

    def add_skill_point(self, skill, points_label):
        current_skill_points = self.session.skills_purchased.get(skill[0], 0)
        max_points_allowed = min(self.max_skill, self.max_tier)

        if self.skill_points > 0 and current_skill_points < max_points_allowed:
            self.session.skills_purchased[skill[0]] = current_skill_points + 1
            self.skill_points -= 1
            self.skill_points_label.setText(f"Skill Points: {self.skill_points}")
            points_label.setText(str(current_skill_points + 1))  # Update points label
            self.update_your_skills_display()
            self.update_skill_buttons()

    def subtract_skill_point(self, skill, points_label):
        current_skill_points = self.session.skills_purchased.get(skill[0], 0)
        if current_skill_points > 0:
            self.session.skills_purchased[skill[0]] = current_skill_points - 1
            self.skill_points += 1
            self.skill_points_label.setText(f"Skill Points: {self.skill_points}")
            points_label.setText(str(current_skill_points - 1))  # Update points label

            self.update_your_skills_display()
            self.update_skill_buttons()

    def update_skill_buttons(self):
        for skill_id, (points_label, add_button, subtract_button) in self.skill_buttons.items():
            skill = self.get_skill_by_id(skill_id)
            current_skill_points = self.session.skills_purchased.get(skill_id, 0)
            points_label.setText(str(current_skill_points))  # Update points label
            
            if skill:
                parent_skill_id = self.skill_id_by_name.get(skill[4])
                current_skill_points = self.session.skills_purchased.get(skill_id, 0)
                max_points_allowed = min(self.max_skill, self.max_tier)

                add_button.setDisabled(
                    self.skill_points <= 0
                    or current_skill_points >= max_points_allowed
                    or (parent_skill_id is not None and self.session.skills_purchased.get(parent_skill_id, 0) < self.next_tier)
                )

                subtract_button.setDisabled(current_skill_points <= 0)

    def update_your_skills_display(self):
        self.your_skills_display.clear()
        for skill_id, points in self.session.skills_purchased.items():
            skill = self.get_skill_by_id(skill_id)
            if skill:
                self.your_skills_display.append(f"{skill[2]}: {points} point(s)")

    def reset_skills(self):
        self.skill_points += sum(self.session.skills_purchased.values())
        self.session.skills_purchased.clear()
        self.update_your_skills_display()
        self.skill_points_label.setText(f"Skill Points: {self.skill_points}")
        self.skill_tabs.clear()
        self.skill_buttons.clear()
        self.skill_id_by_name.clear()
        self.populate_skill_tabs()

    def back_to_spend_skill_points(self):
        self.spend_skill_points_window.update_your_skills_display(self.session.skills_purchased)
        self.spend_skill_points_window.update_skill_points(self.skill_points)
        self.close()
        self.spend_skill_points_window.show()
