import sqlite3

# Connect to the database
conn = sqlite3.connect('master_skills.db')
cursor = conn.cursor()

# Special abilities dictionary
special_abilities = {
    "breserker_rage": {"name": "Breserker Rage"},
    "shift_forms": {"name": "Shift Forms"},
    "harbinger_rage": {"name": "Harbinger Rage"},
    "magic_imunity": {"name": "Magic Imunity"},
    "dragon_fire": {"name": "Dragon Fire"},
    "dragon_acid": {"name": "Dragon Acid"},
    "dragon_spark": {"name": "Dragon Spark"},
    "dragon_frost": {"name": "Dragon Frost"},
    "dragon_sleep": {"name": "Dragon Sleep"},
    "direct_casting": {"name": "Direct Casting"},
    "purification_corruption": {"name": "Purification/Corruption"},
    "vampiric_forms": {"name": "Vampiric Forms"},
    "blood_legacy": {"name": "Blood Legacy"},
    "charm": {"name": "Charm"},
    "wild_tallent": {"name": "Wild Tallent"},
    "elemental_breath": {"name": "Elemental Breath"},
    "leadership": {"name": "Leadership"},
    "flight": {"name": "Flight"},
    "narutal_camoflage": {"name": "Natural Camoflage"},
    "attribute_booster": {"name": "Attribute Booster"},
    "shape_shifting": {"name": "Shape Shifting"},
    "super_powers": {"name": "Super Powers"},
    "telepathic_bond": {"name": "Telepathic Bond"},
    "shadow_manipulation": {"name": "Shadow Manipulation"},
    "energy_channeling": {"name": "Energy Channeling"},
    "ecolocation": {"name": "Ecolocation"},
    "gravity_manipulation": {"name": "Gravity Manipulation"},
}

# Iterate over the special abilities and insert into the table
for ability_key, ability_data in special_abilities.items():
    name = ability_data['name']
    attribute = "N/A"
    tier = "N/A"
    parent_skill = None
    grandparent_skill = None
    skill_type = "special ability"

    # Execute the SQL query to insert the ability into the table
    query = "INSERT INTO master_skills (attribute, name, tier, parent_skill, grandparent_skill, type) VALUES (?, ?, ?, ?, ?, ?)"
    cursor.execute(query, (attribute, name, tier, parent_skill, grandparent_skill, skill_type))

# Commit the changes and close the connection
conn.commit()
conn.close()
