import sqlite3
from buy_inventory_window import BuyInventoryWindow

class SkillCalculator:
    def __init__(self, session, db_path):
        self.session = session
        self.db_path = db_path
        self.merge_bonus_and_purchased_skills()
        self.separate_skills_and_abilities()
        self.map_parent_child_relationship()
        self.update_special_abilities_in_db()
        self.calculate_normal_skills_rank()
        self.calculate_magic_skills_rank()
        self.calculate_talisman_skills_rank()
        self.calculate_faith_skills_rank()
        self.calculate_psyonic_skills_rank() 
        self.merge_moded_skills()
        self.build_master_skill_info()
        self.calculate_skill_percent_all()  
        self.update_skills_in_db()
        self.open_buy_inventory()
        
        
    def merge_bonus_and_purchased_skills(self):
        conn = self.db_path
        cursor = conn.cursor()

        cursor.execute("SELECT skill_id, skill_name, point_value FROM race_bonus_skills WHERE race_id = ?", (self.session.race_id,))
        race_bonus_skills = {row[0]: row[2] for row in cursor.fetchall()}

        cursor.execute("SELECT ability_id, skill_name, point_value FROM race_special_abilities WHERE race_id = ?", (self.session.race_id,))
        race_special_abilities = {f'ability_{row[0]}': row[2] for row in cursor.fetchall()}

        all_skills = self.session.skills_purchased.copy()

        for skill_id, points in race_bonus_skills.items():
            if skill_id in all_skills:
                all_skills[skill_id] += points
            else:
                all_skills[skill_id] = points

        for ability_id, points in race_special_abilities.items():
            if ability_id in all_skills:
                all_skills[ability_id] += points
            else:
                all_skills[ability_id] = points

        self.session.all_skills = all_skills

    def separate_skills_and_abilities(self):
        conn = self.db_path
        cursor = conn.cursor()

        cursor.execute("SELECT id, type FROM master_skills")
        master_skills_types = {row[0]: row[1] for row in cursor.fetchall()}

        self.session.regular_skills = {}
        self.session.special_abilities = {}
        self.session.normal_skills = {}
        self.session.magic_skills = {}
        self.session.talisman_skills = {}
        self.session.faith_skills = {}
        self.session.psyonic_skills = {}

        for skill_id, points in self.session.all_skills.items():
            if 'ability' in str(skill_id):
                self.session.special_abilities[skill_id] = points
            else:
                skill_type = master_skills_types.get(skill_id)
                if skill_type == 'special ability':
                    self.session.special_abilities[skill_id] = points
                else:
                    self.session.regular_skills[skill_id] = points
                    if skill_type == 'normal':
                        self.session.normal_skills[skill_id] = points
                    elif skill_type == 'magic':
                        self.session.magic_skills[skill_id] = points
                    elif skill_type == 'talisman':
                        self.session.talisman_skills[skill_id] = points
                    elif skill_type == 'faith':
                        self.session.faith_skills[skill_id] = points
                    elif skill_type == 'psyonics':
                        self.session.psyonic_skills[skill_id] = points
                    
    def map_parent_child_relationship(self):
        conn = self.db_path
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, type, parent_skill_id FROM master_skills")
        master_skills = cursor.fetchall()

        name_type_to_id = {(row[1], row[2]): row[0] for row in master_skills}

        child_to_parent = {}
        for row in master_skills:
            skill_id, skill_name, type, parent_skill_name = row
            if parent_skill_name:
                key = (skill_id, type)
                parent_skill_id = name_type_to_id[(parent_skill_name, type)]
                child_to_parent[key] = parent_skill_id

        self.session.child_to_parent = child_to_parent


    def update_special_abilities_in_db(self):
        conn = self.db_path
        cursor = conn.cursor()

        for ability_id, points in self.session.special_abilities.items():
            rank = 'N/A'
            percent = 100 - points

            # Fetch the skill name from the master skills database
            cursor.execute("SELECT name FROM master_skills WHERE id = ?", (ability_id,))
            skill_name = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT OR REPLACE INTO character_skills (character_id, skill_id, skill_name, number, rank, percent)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.session.character_id, ability_id, skill_name, points, rank, percent)
            )

        conn.commit()


    def calculate_normal_skills_rank(self):
        # Connect to the database
        conn = self.db_path
        cursor = conn.cursor()

        # Fetch mod values from character_record_sheet
        cursor.execute("SELECT mod_strength, mod_dexterity, mod_constitution, mod_intelligence, mod_wisdom, mod_charisma FROM character_record_sheet WHERE character_id = ?", (self.session.character_id,))
        mods = cursor.fetchone()  # Returns a tuple of mod values in the same order as selected

        # Fetch tier, attribute, and parent skill id from master_skills
        cursor.execute("SELECT id, tier, attribute, type FROM master_skills")
        master_skill_info = {row[0]: (row[1], row[2].lower(), row[3]) for row in cursor.fetchall()}  # Lowercase the attribute names

        # Initialize an empty dictionary for moded normal skills
        self.session.normal_skills_moded = {}

        # Map attribute names to mod values
        attribute_to_mod = {
            'strength': mods[0],
            'dexterity': mods[1],
            'constitution': mods[2],
            'intelligence': mods[3],
            'wisdom': mods[4],
            'charisma': mods[5]
        }

        # First loop: calculate rank for tier 1 skills
        for skill_id, points in self.session.normal_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 1:
                mod = attribute_to_mod[attribute]
                rank = points + mod
                self.session.normal_skills_moded[skill_id] = (points, rank)

        # Second loop: calculate rank for tier 2 skills
        for skill_id, points in self.session.normal_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 2:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'normal')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.normal_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.normal_skills_moded[skill_id] = (points, rank)

        # Third loop: calculate rank for tier 3 skills
        for skill_id, points in self.session.normal_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 3:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'normal')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.normal_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.normal_skills_moded[skill_id] = (points, rank)

        
    def calculate_magic_skills_rank(self):
        # Connect to the database
        conn = self.db_path
        cursor = conn.cursor()

        # Fetch mod values from character_record_sheet
        cursor.execute("SELECT mod_strength, mod_dexterity, mod_constitution, mod_intelligence, mod_wisdom, mod_charisma FROM character_record_sheet WHERE character_id = ?", (self.session.character_id,))
        mods = cursor.fetchone()  # Returns a tuple of mod values in the same order as selected

        # Fetch tier, attribute, and parent skill id from master_skills
        cursor.execute("SELECT id, tier, attribute, type FROM master_skills")
        master_skill_info = {row[0]: (row[1], row[2].lower(), row[3]) for row in cursor.fetchall()}  # Lowercase the attribute names

        # Initialize an empty dictionary for moded magic skills
        self.session.magic_skills_moded = {}

        # Map attribute names to mod values
        attribute_to_mod = {
            'strength': mods[0],
            'dexterity': mods[1],
            'constitution': mods[2],
            'intelligence': mods[3],
            'wisdom': mods[4],
            'charisma': mods[5]
        }

        # First loop: calculate rank for tier 1 skills
        for skill_id, points in self.session.magic_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 1:
                mod = attribute_to_mod[attribute]
                rank = points + mod
                self.session.magic_skills_moded[skill_id] = (points, rank)

        # Second loop: calculate rank for tier 2 skills
        for skill_id, points in self.session.magic_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 2:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'magic')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.magic_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.magic_skills_moded[skill_id] = (points, rank)

        # Third loop: calculate rank for tier 3 skills
        for skill_id, points in self.session.magic_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 3:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'magic')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.magic_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.magic_skills_moded[skill_id] = (points, rank)

        
        
    def calculate_talisman_skills_rank(self):
        # Connect to the database
        conn = self.db_path
        cursor = conn.cursor()

        # Fetch mod values from character_record_sheet
        cursor.execute("SELECT mod_strength, mod_dexterity, mod_constitution, mod_intelligence, mod_wisdom, mod_charisma FROM character_record_sheet WHERE character_id = ?", (self.session.character_id,))
        mods = cursor.fetchone()  # Returns a tuple of mod values in the same order as selected

        # Fetch tier, attribute, and parent skill id from master_skills
        cursor.execute("SELECT id, tier, attribute, type FROM master_skills")
        master_skill_info = {row[0]: (row[1], row[2].lower(), row[3]) for row in cursor.fetchall()}  # Lowercase the attribute names

        # Initialize an empty dictionary for moded talisman skills
        self.session.talisman_skills_moded = {}

        # Map attribute names to mod values
        attribute_to_mod = {
            'strength': mods[0],
            'dexterity': mods[1],
            'constitution': mods[2],
            'intelligence': mods[3],
            'wisdom': mods[4],
            'charisma': mods[5]
        }

        # First loop: calculate rank for tier 1 skills
        for skill_id, points in self.session.talisman_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 1:
                mod = attribute_to_mod[attribute]
                rank = points + mod
                self.session.talisman_skills_moded[skill_id] = (points, rank)

        # Second loop: calculate rank for tier 2 skills
        for skill_id, points in self.session.talisman_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 2:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'talisman')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.talisman_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.talisman_skills_moded[skill_id] = (points, rank)

        # Third loop: calculate rank for tier 3 skills
        for skill_id, points in self.session.talisman_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 3:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'talisman')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.talisman_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.talisman_skills_moded[skill_id] = (points, rank)

        
    def calculate_faith_skills_rank(self):
        # Connect to the database
        conn = self.db_path
        cursor = conn.cursor()

        # Fetch mod values from character_record_sheet
        cursor.execute("SELECT mod_strength, mod_dexterity, mod_constitution, mod_intelligence, mod_wisdom, mod_charisma FROM character_record_sheet WHERE character_id = ?", (self.session.character_id,))
        mods = cursor.fetchone()  # Returns a tuple of mod values in the same order as selected

        # Fetch tier, attribute, and parent skill id from master_skills
        cursor.execute("SELECT id, tier, attribute, type FROM master_skills")
        master_skill_info = {row[0]: (row[1], row[2].lower(), row[3]) for row in cursor.fetchall()}  # Lowercase the attribute names

        # Initialize an empty dictionary for moded faith skills
        self.session.faith_skills_moded = {}

        # Map attribute names to mod values
        attribute_to_mod = {
            'strength': mods[0],
            'dexterity': mods[1],
            'constitution': mods[2],
            'intelligence': mods[3],
            'wisdom': mods[4],
            'charisma': mods[5]
        }

        # First loop: calculate rank for tier 1 skills
        for skill_id, points in self.session.faith_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 1:
                mod = attribute_to_mod[attribute]
                rank = points + mod
                self.session.faith_skills_moded[skill_id] = (points, rank)

        # Second loop: calculate rank for tier 2 skills
        for skill_id, points in self.session.faith_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 2:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'faith')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.faith_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.faith_skills_moded[skill_id] = (points, rank)

        # Third loop: calculate rank for tier 3 skills
        for skill_id, points in self.session.faith_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 3:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'faith')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.faith_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.faith_skills_moded[skill_id] = (points, rank)

        
    def calculate_psyonic_skills_rank(self):
        # Connect to the database
        conn = self.db_path
        cursor = conn.cursor()

        # Fetch mod values from character_record_sheet
        cursor.execute("SELECT mod_strength, mod_dexterity, mod_constitution, mod_intelligence, mod_wisdom, mod_charisma FROM character_record_sheet WHERE character_id = ?", (self.session.character_id,))
        mods = cursor.fetchone()  # Returns a tuple of mod values in the same order as selected

        # Fetch tier, attribute, and parent skill id from master_skills
        cursor.execute("SELECT id, tier, attribute, type FROM master_skills")
        master_skill_info = {row[0]: (row[1], row[2].lower(), row[3]) for row in cursor.fetchall()}  # Lowercase the attribute names

        # Initialize an empty dictionary for moded psyonics skills
        self.session.psyonic_skills_moded = {}

        # Map attribute names to mod values
        attribute_to_mod = {
            'strength': mods[0],
            'dexterity': mods[1],
            'constitution': mods[2],
            'intelligence': mods[3],
            'wisdom': mods[4],
            'charisma': mods[5]
        }

        # First loop: calculate rank for tier 1 skills
        for skill_id, points in self.session.psyonic_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 1:
                mod = attribute_to_mod[attribute]
                rank = points + mod
                self.session.psyonic_skills_moded[skill_id] = (points, rank)

        # Second loop: calculate rank for tier 2 skills
        for skill_id, points in self.session.psyonic_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 2:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'psyonics')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.psyonic_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.psyonic_skills_moded[skill_id] = (points, rank)

        # Third loop: calculate rank for tier 3 skills
        for skill_id, points in self.session.psyonic_skills.items():
            tier, attribute, type = master_skill_info[skill_id]
            if tier == 3:
                parent_skill_id = self.session.child_to_parent[(skill_id, 'psyonics')]  # Assume parent skill exists
                parent_skill_points, parent_skill_rank = self.session.psyonic_skills_moded[parent_skill_id]
                rank = points + parent_skill_rank
                self.session.psyonic_skills_moded[skill_id] = (points, rank)
                
    def build_master_skill_info(self):
        conn = self.db_path
        cursor = conn.cursor()

        cursor.execute("SELECT id, attribute FROM master_skills")
        master_skills = cursor.fetchall()

        # Store master skill information in the session
        self.session.master_skill_info = {row[0]: row[1] for row in master_skills}


                
    def merge_moded_skills(self):
        self.session.all_moded_skills = {}

        skill_types = [
            self.session.normal_skills_moded, 
            self.session.magic_skills_moded, 
            self.session.talisman_skills_moded, 
            self.session.faith_skills_moded, 
            self.session.psyonic_skills_moded
        ]

        for skill_type in skill_types:
            self.session.all_moded_skills.update(skill_type)
            

                
    def calculate_skill_percent_all(self):
        # Connect to the database
        conn = self.db_path
        cursor = conn.cursor()

        # Fetch attributes from character_record_sheet
        cursor.execute("SELECT attribute_strength, attribute_dexterity, attribute_constitution, attribute_intelligence, attribute_wisdom, attribute_charisma FROM character_record_sheet WHERE character_id = ?", (self.session.character_id,))
        attributes = cursor.fetchone()

        # Map attribute names to attribute values
        attribute_to_value = {
            'strength': attributes[0],
            'dexterity': attributes[1],
            'constitution': attributes[2],
            'intelligence': attributes[3],
            'wisdom': attributes[4],
            'charisma': attributes[5]
        }

        self.session.attribute_to_value = attribute_to_value

        for skill_id, values in self.session.all_moded_skills.items():
            points, rank = values

            attribute = self.session.master_skill_info[skill_id].lower()  # Fetch the attribute for this skill and convert it to lowercase
            attribute_value = attribute_to_value[attribute]  # Get the value of the corresponding attribute

            # Calculate percent
            percent = 100 - (rank + attribute_value)

            # Save percent into the dictionary
            self.session.all_moded_skills[skill_id] = (points, rank, percent)

    def update_skills_in_db(self):
        # Connect to the database
        conn = self.db_path
        cursor = conn.cursor()

        for skill_id, values in self.session.all_moded_skills.items():
            points, rank, percent = values
            
            # Fetch the skill name from the master skills database
            cursor.execute("SELECT name FROM master_skills WHERE id = ?", (skill_id,))
            skill_name = cursor.fetchone()[0]

            # Update or insert skill in character_skills for this character
            cursor.execute(
                """
                INSERT OR REPLACE INTO character_skills (character_id, skill_id, skill_name, number, rank, percent)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.session.character_id, skill_id, skill_name, points, rank, percent)
            )

        # Commit the changes and close the connection
        conn.commit()
        
    def open_buy_inventory(self):
        self.buy_inventory_window = BuyInventoryWindow(self.session, self.db_path)
        self.buy_inventory_window.show()

