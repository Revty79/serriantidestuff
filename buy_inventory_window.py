from PyQt5.QtWidgets import QMainWindow

class BuyInventoryWindow(QMainWindow):
    def __init__(self, session, db_path, *args, **kwargs):
        super(BuyInventoryWindow, self).__init__(*args, **kwargs)
        
        self.session = session  
        self.db_path = db_path
        # TODO: Implement details later
