import yaml, os, json, subprocess, logging, random, shutil, sys
from operator import itemgetter
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QFrame, QLineEdit, QPushButton, QCheckBox, QApplication, QMainWindow, \
                            QFileDialog, QDialog, QScrollArea, QMessageBox, QWidget, QTextEdit
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPixmap, QIntValidator, QPalette, QColor
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

try:
    from PyQt5 import sip
except ImportError:
    import sip

from randomizer import World


logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    handlers=[logging.StreamHandler()])

THIS_FILEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
TEMP_DIR = os.path.join(THIS_FILEPATH,'tmp')



DEV_OVERRIDE = False
try:
    with open(os.path.join(THIS_FILEPATH,'dev','path.txt'),'r') as f:
        DEV_ROM_PATH = f.read()
except:
    DEV_ROM_PATH = ''



with open(os.path.join(THIS_FILEPATH,'data','data.yml'),'r') as f:
    yaml_data = yaml.safe_load(f)


if not os.path.exists(os.path.join(THIS_FILEPATH,"output")):
    os.mkdir(os.path.join(THIS_FILEPATH,"output"))
if not os.path.exists(os.path.join(THIS_FILEPATH,"tmp")):
    os.mkdir(os.path.join(THIS_FILEPATH,"tmp"))
    




class MainWindow(object):
    SCREEN_HEIGHT = 600
    SCREEN_WIDTH = 600
    def __init__(self):
        self.app = QApplication([])
        self.window = QMainWindow()
        self.window.setFixedSize(self.SCREEN_WIDTH,self.SCREEN_HEIGHT)
        self.window.setWindowTitle('Dragon Quest III: Heavenly Flight')
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(os.path.join(THIS_FILEPATH,"ico.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.window.setWindowIcon(self.icon)


        self.title_container = QLabel(self.window)
        self.title_container.setGeometry(QtCore.QRect(0, 0, self.SCREEN_WIDTH, 30))
        self.title_container.setStyleSheet("background-color:black;")
        
        self.title_label = QLabel("Dragon Quest III: Heavenly Flight",self.window)
        self.title_label.setGeometry(QtCore.QRect(0, 0, self.SCREEN_WIDTH, 30))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.title_label_border = QFrame(self.window)
        self.title_label_border.setGeometry(QtCore.QRect(-10, -10, self.SCREEN_WIDTH + 20, 40))
        self.title_label_border.setStyleSheet("border:2px solid rgb(0, 0, 0); ")




        self.rom_label = QLabel("Input ROM path:",self.window)
        self.rom_label.setGeometry(QtCore.QRect(10, 40, 120, 30))
        self.rom_label.setToolTip('Choose ROM path:')
        
        self.rom_label_input = QLineEdit("",self.window)
        self.rom_label_input.setGeometry(QtCore.QRect(140, 40, 360, 30))
        self.rom_label_input.setToolTip('Choose ROM path:')
        self.rom_label_input.setText("")

        self.rom_button = QPushButton("Browse",self.window)
        self.rom_button.setGeometry(QtCore.QRect(510, 40, 80, 30))
        self.rom_button.clicked.connect(self.rom_input_click)



        self.seed_label = QLabel("Seed:",self.window)
        self.seed_label.setGeometry(QtCore.QRect(10, 80, 120, 30))
        self.seed_label.setToolTip('Choose a seed number. Blank will generate a new random one.')
        
        self.seed_label_input = QLineEdit("",self.window)
        self.seed_label_input.setGeometry(QtCore.QRect(140, 80, 360, 30))
        self.seed_label_input.setToolTip('Choose a seed number. Blank will generate a new random one.')
        self.seed_label_input.setText("")
        self.onlyInt = QIntValidator()
        self.seed_label_input.setValidator(self.onlyInt)        
        


        self.key_item_chests_checkbox = QCheckBox("Place Key Items in chests only",self.window)
        self.key_item_chests_checkbox.setGeometry(QtCore.QRect(10, 120, 350, 30))
        self.key_item_chests_checkbox.setToolTip('Checked: Key Items will only be placed in chests. Searchable locations (visible and invisible) and NPC events will not have keys.\nUnchecked: Key Items can be placed anywhere.\nBoth options adhere to having all checks with logical requirements.\nTiering has no impact on Key Item placement.')
        self.key_item_chests_checkbox.setChecked(True)

        self.reward_tiering_checkbox = QCheckBox("Reward tiering",self.window)
        self.reward_tiering_checkbox.setGeometry(QtCore.QRect(10, 150, 350, 30))
        self.reward_tiering_checkbox.setToolTip('Checked: Rewards are placed with collectibles of increasing value throughout the game, with a small chance of higher tier goods randomly appearing anywhere.\nUnchecked: All rewards have completely random value goods.\nBoth options adhere to a placement average system, controlling how often items appear throughout the seed.\nRewards can be placed with higher or lower tiers than the check tier by design, but are usually +/- 1 with tiering.')
        self.reward_tiering_checkbox.setChecked(True)

        self.shop_tiering_checkbox = QCheckBox("Shop tiering",self.window)
        self.shop_tiering_checkbox.setGeometry(QtCore.QRect(10, 180, 350, 30))
        self.shop_tiering_checkbox.setToolTip('Checked: Shops are placed with wares of increasing value throughout the game.\nUnchecked: All shops have randomly assigned wares of any value.\nBoth options do not adhere to a placement average system, where different shops may have similar items.\nWares can be placed with higher or lower tiers than the shop tier by design, but are usually +/- 1 with tiering.')
        self.shop_tiering_checkbox.setChecked(True)



        self.small_medal_count_label = QLabel("Small Medal count:",self.window)
        self.small_medal_count_label.setGeometry(QtCore.QRect(380, 120, 200, 30))
        self.small_medal_count_label.setToolTip('Number of Small Medals to place in the world. Only 12 Small Medals are required for all rewards.\nMinimum amount is 0, and maximum amount is 50.')  

        self.small_medal_count_input = QLineEdit("15",self.window)
        self.small_medal_count_input.setGeometry(QtCore.QRect(540, 120, 40, 30))
        self.small_medal_count_input.setValidator(self.onlyInt)        

        
        self.generate_button = QPushButton("Generate",self.window)
        self.generate_button.setGeometry(QtCore.QRect(10, 240, 580, 30))
        self.generate_button.clicked.connect(self.generate)

    






        self.log_header_label = QLabel("Console log:",self.window)
        self.log_header_label.setGeometry(QtCore.QRect(10, 280, 90, 30))

        self.log_output = QTextEdit(self.window)
        self.log_output.setGeometry(QtCore.QRect(10, 320, 580, 200))
        # self.log_output = self.set_white(self.log_output)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().minimum())
        
        self.log_output_thread = LogThread(self.window)
        self.log_output_thread.log.connect(self.update_log_text)
        # self.log_output_thread.started.connect(lambda: self.update_log('start'))
        
        
        self.log_clear_button = QPushButton("Clear Log",self.window)
        self.log_clear_button.setGeometry(QtCore.QRect(10, 540, 100, 30))
        self.log_clear_button.clicked.connect(self.clear_log)  
        
        
        
        self.open_dir_button = QPushButton("Open Output Folder",self.window)
        self.open_dir_button.setGeometry(QtCore.QRect(410, 540, 180, 30))
        self.open_dir_button.clicked.connect(self.open_output_folder)  












        # Final settings
        self.app.setStyle('Fusion')
        self.app.setFont(QtGui.QFont("Segoe UI", 12))
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(120, 120, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.app.setPalette(palette)


    def update_log(self, text):
        self.log_output_thread.setText(text)
        self.log_output_thread.start()
        
    def update_log_text(self, val):
        self.log_output.append(str(val))
        
    def clear_log(self, message):
        self.log_output.setText("")
        
    def open_output_folder(self):
        os.startfile(os.path.join(THIS_FILEPATH,'output'))


    def rom_input_click(self):
        dialog = QFileDialog()
        new_file = dialog.getOpenFileName(None,"Select video","",filter="sfc (*.sfc);;smc (*.smc)")
        if not new_file[0]:
            self.update_log_text("No file chosen. Generation will not occur until a file is chosen.")            
        else:
            self.rom_label_input.setText(new_file[0])

    def generate(self):
        # parse configs into dict

        if self.rom_label_input.text() != '' or DEV_OVERRIDE:
            if DEV_OVERRIDE:
                self.rom_label_input.setText(DEV_ROM_PATH)
            
            try:
                try:        
                    medal_parse = int(self.small_medal_count_input.text())
                    if medal_parse < 0:
                        medal_parse = 0
                    if medal_parse > 50:
                        medal_parse = 50
                except:
                    medal_parse = 12
                
        
                if self.seed_label_input.text():
                    SEED_NUM = int(self.seed_label_input.text())
                else:
                    SEED_NUM = random.randint(1,1000000)
        
        
                seed_config = {'starting_areas' : ['Aliahan'], 
                                'place_keys_in_chests_only' : self.key_item_chests_checkbox.isChecked(),
                                'small_medal_count' : medal_parse,
                                'reward_tiering' : self.reward_tiering_checkbox.isChecked(),
                                'shop_tiering' : self.shop_tiering_checkbox.isChecked(),
                                'seed_num' : SEED_NUM}
        
                self.update_log_text("Beginning seed generation...")        
                self.update_log_text("Seed number %s..." % SEED_NUM)
                
                logging.info("Seed number: %s" % SEED_NUM)
                random.seed(SEED_NUM)
                self.world = World(random, seed_config)
                
                try:
                    self.world.generate_seed()
                    logging.info("\n\n\n")
#                    logging.info(self.world.spoiler_log)
                
                    self.update_log_text("Finished seed creation, patching ROM...")
                    
                    self.patch_rom()                    
                    
                
                except Exception as e:
                    logging.info("Seed resulted in error. Seed was not generated: %s" % e)
                    self.update_log("Seed resulted in error. Seed was not generated: %s" % e)
    
            except Exception as e:
                logging.info("Program error %s" % e)
                self.update_log("Program error %s" % e)
    
        else:
            self.update_log_text("No file chosen. Generation will not occur until a file is chosen.")            
                
    def patch_rom(self):
        
        
        try:
            
            new_rom_path = os.path.join(THIS_FILEPATH,'tmp', "dq3_%s.sfc" % self.world.seed_num)
#            logging.info(new_rom_path)
#            logging.info(self.rom_label_input.text())
            shutil.copy(self.rom_label_input.text(), new_rom_path)
            
            sh_calls = ["%s" % os.path.join(THIS_FILEPATH,'asar','asar.exe'), "--fix-checksum=off", os.path.join("tmp","patch_r.asm"), new_rom_path]

            subprocess.call(sh_calls)
            new_new_rom_path = os.path.join(THIS_FILEPATH, 'output',os.path.basename(new_rom_path))
#            logging.info(new_rom_path)
            shutil.move(new_rom_path, new_new_rom_path)
            try:
                os.remove(os.path.join(THIS_FILEPATH,'tmp','patch_r.asm'))
            except Exception as e:
                logging.info("Could not remove files from tmp dir: %s" % e)
            
            logging.info("File %s successfully patched & created! " % (new_rom_path))
            self.update_log_text("File %s successfully patched & created! " % (new_rom_path))
        except Exception as e:
            logging.info("File %s was NOT successfully patched & created: %s " % (new_rom_path, e))
            self.update_log_text("File %s was NOT successfully patched & created: %s " % (new_rom_path, e))
        
        
        
class LogThread(QThread):
    log = pyqtSignal(str)

    def __init__(self, parent=None):
        super(LogThread, self).__init__(parent)
        self._text = ''

    def setText(self, text):
            self._text = text

    def run(self):
        self.log.emit(str(self._text))

        
        
        



if __name__ == '__main__':
    main_window = MainWindow()
    main_window.window.show()
    main_window.app.exec_()



if False:    
    temp_dir = os.path.join(THIS_FILEPATH,'tmp')
    
        

        
        
        
        
        
