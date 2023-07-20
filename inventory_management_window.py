from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QCheckBox, QTableWidget, QTableWidgetItem, QWidget
import sqlite3

class InventoryManagementWindow(QMainWindow):
    def __init__(self, conn, *args, **kwargs):
        super(InventoryManagementWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Inventory Management")
        self.setMinimumSize(800, 600)
        self.db_path = conn

        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.genres = ["fantasy", "modern", "horror", "sci_fi", "western"]
        self.genre_checkboxes = {genre: QCheckBox(genre.title()) for genre in self.genres}

        for checkbox in self.genre_checkboxes.values():
            self.main_layout.addWidget(checkbox)
            checkbox.stateChanged.connect(self.submit_genres)

        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(['Item', 'Type', 'Credits', 'Mithril', 'Platinum', 'Gold', 'Silver', 'Copper', 'Bronze', 'Special Properties'])
        self.main_layout.addWidget(self.table)

        self.add_button = QPushButton("Add New Item")
        self.add_button.clicked.connect(self.add_item)
        self.main_layout.addWidget(self.add_button)

        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.clicked.connect(self.save_changes)
        self.main_layout.addWidget(self.save_changes_button)

        self.setCentralWidget(self.main_widget)

    def submit_genres(self):
        genres_selected = [genre for genre, checkbox in self.genre_checkboxes.items() if checkbox.isChecked()]

        if genres_selected:
            self.load_data(genres_selected)

    def load_data(self, genres_selected):
        with self.db_path as conn:
            cursor = conn.cursor()
            query = f"SELECT item, type, credits, mitheril, platenum, gold, silver, copper, bronze, special_properties FROM equipment WHERE genre_id IN ({', '.join('?' for _ in genres_selected)})"
            cursor.execute(query, genres_selected)

            self.table.setRowCount(0)
            for row_data in cursor:
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    if data is not None:
                        self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def add_item(self):
        self.table.insertRow(self.table.rowCount())

    def save_changes(self):
        with self.db_path as conn:
            cursor = conn.cursor()
            for row in range(self.table.rowCount()):
                data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is not None:
                        data.append(item.text())
                    else:
                        data.append(None)

                genre_id = self.get_genre_id()
                query = f'''INSERT OR REPLACE INTO equipment(genre_id, item, type, credits, mitheril, platenum, gold, silver, copper, bronze, special_properties)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                cursor.execute(query, (genre_id, *data))
            conn.commit()
            self.load_data([genre_id])

    def get_genre_id(self):
        for genre, checkbox in self.genre_checkboxes.items():
            if checkbox.isChecked():
                return genre  # assuming genre is the same as genre_id
        return None
