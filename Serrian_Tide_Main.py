from PyQt5.QtWidgets import QApplication
from player_login import PlayerLogin
from god_creation_portal import GodCreationPortal
from player_control_portal import PlayerControlPortal
from database_converter import DataCopier
from session import Session
import math
import sqlite3

class SerrianTideMain:
    def __init__(self):
        
        self.init_db()
        self.initialize_database()
        copier = DataCopier(self.conn)
        src_dbs = ["races.db", "master_skills.db", "shop_inventory.db", "genres.db"]
        copier.perform_copy(src_dbs)
        self.create_attribute_db()
        self.create_hp_db()
        self.create_initiative_db()
        self.populate_weapons_and_armor()
        self.session = Session()
        self.player_login = PlayerLogin()
        self.player_login.attempt_login.connect(self.handle_login_attempt)
        self.player_login.attempt_create_account.connect(self.handle_create_account_attempt)        


    def handle_login_attempt(self, username, password, account_type):
        self.cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        result = self.cursor.fetchone()

        if result:
            # Assuming that result[0] is user_id and result[1] is username.
            self.session.login(result[0], result[1])
            if account_type == 'Player' and result[3] == 1:
                print('Logged in as Player')
                self.player_control_portal = PlayerControlPortal(self.session, self.conn)
                self.player_control_portal.show()
            elif account_type == 'God' and result[4] == 1:
                print('Logged in as God')
                self.god_creation_portal = GodCreationPortal(self.session, self.conn)
                self.god_creation_portal.show()
            else:
                print('Invalid account type for this user')
        else:
            print('Invalid username or password')
        
    def handle_create_account_attempt(self, username, password, account_type):
        if account_type == 'Player':
            is_player, is_god = 1, 0
        elif account_type == 'God':
            is_player, is_god = 0, 1
        else:
            print('Please select an account type')
            return

        try:
            self.cursor.execute('INSERT INTO users (username, password, is_player, is_god) VALUES (?, ?, ?, ?)', 
                                (username, password, is_player, is_god))
            self.conn.commit()
            print('Account created')
        except sqlite3.IntegrityError:
            self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            result = self.cursor.fetchone()
            if result:
                if account_type == 'Player' and result[3] == 0:
                    self.cursor.execute('UPDATE users SET is_player = 1 WHERE username = ?', (username,))
                    self.conn.commit()
                    print('Player account added')
                elif account_type == 'God' and result[4] == 0:
                    self.cursor.execute('UPDATE users SET is_god = 1 WHERE username = ?', (username,))
                    self.conn.commit()
                    print('God account added')
                else:
                    print('Account already exists')
            else:
                print('Error creating account')


    def init_db(self):
        self.conn = sqlite3.connect('serrian_tide.db')
        self.cursor = self.conn.cursor()

    def initialize_database(self):
        self.conn = sqlite3.connect('serrian_tide.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL,
                                is_player INTEGER NOT NULL,
                                is_god INTEGER NOT NULL)''')
    
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS races (
                                id INTEGER PRIMARY KEY,
                                race_name TEXT UNIQUE,
                                max_strength INTEGER,
                                max_dexterity INTEGER,
                                max_constitution INTEGER,
                                max_intelligence INTEGER,
                                max_wisdom INTEGER,
                                max_charisma INTEGER,
                                base_magic INTEGER,
                                base_movement INTEGER)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS race_bonus_skills (
                                id INTEGER PRIMARY KEY,
                                race_id INTEGER,
                                skill_id INTEGER,
                                skill_name TEXT,
                                point_value INTEGER,
                                FOREIGN KEY (race_id) REFERENCES races (id),
                                FOREIGN KEY (skill_id) REFERENCES skills (id))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS race_special_abilities (
                                id INTEGER PRIMARY KEY,
                                race_id INTEGER,
                                ability_id INTEGER,
                                skill_name TEXT,
                                point_value INTEGER,
                                FOREIGN KEY (race_id) REFERENCES races (id),
                                FOREIGN KEY (ability_id) REFERENCES special_abilities (id))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS master_skills (
                                id INTEGER PRIMARY KEY,
                                attribute TEXT NOT NULL,
                                name TEXT NOT NULL,
                                tier INTEGER NOT NULL,
                                parent_skill_id TEXT,
                                grandparent_skill TEXT,
                                type TEXT,
                                FOREIGN KEY(parent_skill_id) REFERENCES skills(id))''')


        self.cursor.execute('''CREATE TABLE IF NOT EXISTS campaigns (
                                id INTEGER PRIMARY KEY,
                                god_id  INTEGER,
                                genre TEXT,
                                starting_credits INTEGER,
                                use_coins INTEGER,
                                use_credits INTEGER,
                                campaign_name TEXT UNIQUE NOT NULL,
                                attribute_points INTEGER,
                                skill_points INTEGER,
                                max_skill INTEGER,
                                next_tier INTEGER,
                                max_tier INTEGER,
                                allowed_skills TEXT,
                                allowed_races TEXT,
                                FOREIGN KEY (genre) REFERENCES genres (genre_name),
                                FOREIGN KEY (god_id) REFERENCES users (id))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS campaign_players_characters (
                                id INTEGER PRIMARY KEY,
                                campaign_id INTEGER,
                                god_id INTEGER,
                                player_id INTEGER,
                                character_name TEXT,
                                FOREIGN KEY (god_id) REFERENCES users (id),
                                FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
                                FOREIGN KEY (player_id) REFERENCES users (id))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS character_record_sheet (
                                id INTEGER PRIMARY KEY,
                                player_id INTEGER,
                                character_id INTEGER,
                                campaign_id INTEGER,
                                character_name TEXT,
                                race_id INTEGER,
                                age TEXT,
                                sex TEXT,
                                height TEXT,
                                weight TEXT,
                                skin_color TEXT,
                                hair_color TEXT,
                                eye_color TEXT,
                                deity TEXT,
                                fame INTEGER,
                                experience_points INTEGER,
                                total_experience_points INTEGER,
                                quintessence INTEGER, 
                                total_quintessence INTEGER,
                                fate INTEGER,
                                dmcq TEXT,
                                attribute_strength INTEGER,
                                mod_strength INTEGER,
                                percent_strength INTEGER,
                                attribute_dexterity INTEGER,
                                mod_dexterity INTEGER,
                                percent_dexterity INTEGER,
                                attribute_constitution INTEGER,
                                mod_constitution INTEGER,
                                percent_constitution INTEGER,
                                attribute_intelligence INTEGER,
                                mod_intelligence INTEGER,
                                percent_intelligence INTEGER,
                                attribute_wisdom INTEGER,
                                mod_wisdom INTEGER,
                                percent_wisdom INTEGER,
                                attribute_charisma INTEGER,
                                mod_charisma INTEGER,
                                percent_charisma INTEGER,
                                base_hp INTEGER,
                                total_hp INTEGER,
                                head_hp INTEGER,
                                chest_hp INTEGER,
                                r_arm_hp INTEGER,
                                l_arm_hp INTEGER,
                                r_leg_hp INTEGER,
                                l_leg_hp INTEGER,
                                manna INTEGER,
                                base_movement INTEGER,
                                base_magic INTEGER,
                                base_initiative INTEGER,
                                total_initiative INTEGER,
                                credits INTEGER,
                                mitheril INTEGER,
                                platenum INTEGER,
                                gold INTEGER,
                                silver INTEGER,
                                copper INTEGER,
                                bronze INTEGER,
                                FOREIGN KEY (campaign_id) REFERENCES campaigns (id),                        
                                FOREIGN KEY (race_id) REFERENCES races (id))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS character_skills (
                                id INTEGER PRIMARY KEY,
                                character_id INTEGER,
                                skill_id INTEGER,
                                skill_name TEXT,
                                number INTEGER,
                                rank INTEGER,
                                percent INTEGER,
                                FOREIGN KEY (character_id) REFERENCES campaign_players_characters (id),
                                FOREIGN KEY (skill_id) REFERENCES skills (id),
                                UNIQUE(character_id, skill_id))''')


        self.cursor.execute('''CREATE TABLE IF NOT EXISTS genres  (
                                id INTEGER PRIMARY KEY,
                                genre_name TEXT,
                                inventory_name TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS attribute_mods_percents (
                                attribute INTEGER PRIMARY KEY,
                                mod INTEGER,
                                percent INTEGER)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS hp_data (
                                attribute INTEGER PRIMARY KEY,
                                base_hp INTEGER,
                                total_hp INTEGER,
                                head_hp INTEGER,
                                chest_hp INTEGER,
                                right_arm_hp INTEGER,
                                left_arm_hp INTEGER,
                                right_leg_hp INTEGER,
                                left_leg_hp INTEGER)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS initiative_data (
                                dexterity INTEGER PRIMARY KEY,
                                base_initiative INTEGER)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS equipment(
                                id INTEGER PRIMARY KEY,
                                genre_id INTEGER,
                                item TEXT,
                                type TEXT,
                                credits INTEGER,
                                mitheril INTEGER,
                                platenum INTEGER,
                                gold INTEGER,
                                silver INTEGER,
                                copper INTEGER,
                                bronze INTEGER,
                                special_properties TEXT,
                                FOREIGN KEY(genre_id) REFERENCES genres(id)
                                UNIQUE(item, type))''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS player_equipment(
                                id INTEGER PRIMARY KEY,
                                item_id INTEGER,
                                item_name TEXT,
                                character_id INTEGER,
                                FOREIGN KEY(item_id) REFERENCES equipment(id),
                                FOREIGN KEY(character_id) REFERENCES character_record_sheet(id)
                                UNIQUE(item_id, character_id))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS inventory_lists (
                                id INTEGER PRIMARY KEY,
                                inventory_name TEXT,
                                item_id INTEGER,
                                genre_id INTEGER,
                                FOREIGN KEY(item_id) REFERENCES equipment(id),
                                FOREIGN KEY(genre_id) REFERENCES genres(id))''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Weapons (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                damage_type TEXT,
                                range INTEGER,
                                durability INTEGER,
                                damage INTEGER)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Armor (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                area_covered TEXT,
                                special_properties TEXT,
                                durability INTEGER,
                                soaks INTEGER)''') 
        
    
        
        self.conn.commit()
        
    def populate_weapons_and_armor(self):
        # Populate Weapons table from Equipment table
        self.cursor.execute('''INSERT OR IGNORE INTO Weapons (id, name)
                                SELECT id, item
                                FROM equipment
                                WHERE type = 'weapon';''')

        # Populate Armor table from Equipment table
        self.cursor.execute('''INSERT  OR IGNORE INTO Armor (id, name)
                                SELECT id, item
                                FROM equipment
                                WHERE type = 'armor';''')

        # Commit the changes
        self.conn.commit()
        
    def create_attribute_db(self):
        self.cursor = self.conn.cursor()

        attribute_data = self.generate_attribute_data()

        for data in attribute_data:
            self.cursor.execute('''INSERT OR IGNORE INTO attribute_mods_percents (attribute, mod, percent) VALUES (?, ?, ?)''', data)

        self.conn.commit()
      
    def create_hp_db(self):
        self.cursor = self.conn.cursor()

        
        hp_data = self.generate_hp_data()

        for data in hp_data:
            self.cursor.execute('''INSERT OR IGNORE INTO hp_data (attribute, base_hp, total_hp, head_hp, chest_hp, right_arm_hp, left_arm_hp, right_leg_hp, left_leg_hp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

        self.conn.commit()

    @staticmethod
    def calculate_mod(attribute):
        if attribute == 1:
            return -5
        elif 2 <= attribute <= 5:
            return -4
        elif 6 <= attribute <= 10:
            return -3
        elif 11 <= attribute <= 15:
            return -2
        elif 16 <= attribute <= 20:
            return -1
        elif 21 <= attribute <= 25:
            return 0
        else:
            return (attribute - 25) // 5

    def generate_attribute_data(self):
        attribute_data = []

        for attribute in range(1, 101):
            mod = self.calculate_mod(attribute)
            percent = 100 - attribute
            attribute_data.append((attribute, mod, percent))

        return attribute_data

    def generate_hp_data(self):
        self.cursor = self.conn.cursor()

        self.cursor.execute('''SELECT attribute, mod FROM attribute_mods_percents''')
        attribute_mod_data = self.cursor.fetchall()

        hp_data = []

        for attribute, mod in attribute_mod_data:
            base_hp, total_hp, hit_areas = self.calculate_hit_points(attribute, mod)
            hp_data.append((attribute, base_hp, total_hp, *hit_areas.values()))

        return hp_data
    @staticmethod
    
    def calculate_hit_points(attribute, mod):
        base_hp = attribute * 2
        total_hp = base_hp + mod

        if total_hp < 1:
            total_hp = 1

        hit_areas = {
            'head': math.ceil(base_hp * 0.1),
            'chest': math.ceil(base_hp * 0.3),
            'right_arm': math.ceil(base_hp * 0.15),
            'left_arm': math.ceil(base_hp * 0.15),
            'right_leg': math.ceil(base_hp * 0.15),
            'left_leg': math.ceil(base_hp * 0.15)
        }

        return base_hp, total_hp, hit_areas
    
    def create_initiative_db(self):
        self.cursor = self.conn.cursor()
        
        initiative_data = self.generate_initiative_data()

        for data in initiative_data:
            self.cursor.execute('''INSERT OR IGNORE INTO initiative_data (dexterity, base_initiative) VALUES (?, ?)''', data)

        self.conn.commit()

    def generate_initiative_data(self):
        initiative_data = []

        for dex in range(1, 101):
            if dex == 1:
                base_initiative = 1
            else:
                base_initiative = (dex - 1) // 5 + 2

            initiative_data.append((dex, base_initiative))

        return initiative_data# Include here any methods that handle interactions between your windows.

def main():
    app = QApplication([])

    main_module = SerrianTideMain()
    main_module.player_login.show() # Starts with player login window.

    app.exec_()

if __name__ == "__main__":
    main()
