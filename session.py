class Session:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.campaign_id = None
        self.character_id = None
        self.character_name = None
        self.player_id = None
        self.player_name = None
        self.campaign_name = None
        self.race_id = None
        self.race_name = None
        self.skills_purchased = {}
        self.all_skills = {}
        self.regular_skills = {}    
        self.special_abilities = {} 
        self.child_to_parent = {} 
        self.normal_skills = {}
        self.magic_skills = {}
        self.talisman_skills = {}
        self.faith_skills = {}  
        self.psyonic_skills = {} 
        self.skill_percent = {}   
        self.normal_skills_moded = {}
        self.magic_skills_moded = {}
        self.talisman_skills_moded = {}
        self.faith_skills_moded = {}
        self.psyonic_skills_moded = {}      
        self.all_moded_skills = {}
        self.master_skill_info = {}

    def login(self, user_id, username):
        self.user_id = user_id
        self.username = username

    def select_campaign(self, campaign_id, campaign_name):
        self.campaign_id = campaign_id
        self.campaign_name = campaign_name

    def select_character(self, character_id, character_name):
        self.character_id = character_id
        self.character_name = character_name

    def select_player(self, player_id, player_name):
        self.player_id = player_id
        self.player_name = player_name

    def select_race(self, race_id, race_name):
        self.race_name = race_name
        self.race_id = race_id
