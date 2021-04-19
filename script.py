import yaml, os, json, subprocess, logging, random, shutil
from operator import itemgetter



from PyQt5.QtWidgets import QLabel, QFrame, QLineEdit, QPushButton, QCheckBox, QApplication, QMainWindow, \
                            QFileDialog, QDialog, QScrollArea, QMessageBox, QWidget, QTextEdit
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPixmap, QIntValidator, QPalette, QColor
from PyQt5.QtCore import QThread, pyqtSignal, QTimer





logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    handlers=[logging.StreamHandler()])

THIS_FILEPATH = os.path.dirname(__file__)
TEMP_DIR = os.path.join(THIS_FILEPATH,'tmp')

with open(os.path.join(THIS_FILEPATH,'data','data.yml'),'r') as f:
    yaml_data = yaml.safe_load(f)

with open(os.path.join('data','checks.json'),'r') as f:
    check_dict = json.load(f)
with open(os.path.join('data','items.json'),'r') as f:
    items_dict = json.load(f)
with open(os.path.join('data','shops.json'),'r') as f:
    shops_dict = json.load(f)



def b2i(byte):
    return int(byte,base=16)
def i2b(integer):
    return hex(integer).replace("0x","").upper()
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


if not os.path.exists(os.path.join(THIS_FILEPATH,"output")):
    os.mkdir(os.path.join(THIS_FILEPATH,"output"))
    







































class Area():
    def __init__(self, area_name, area_data):
        self.name = area_name
        for k, v in area_data.items():
            setattr(self, k, v)
        
        self.checks = []
        
        for idx in [i for i in check_dict if check_dict[i]['area']==self.name]:
            self.checks.append(Check(idx))
            
            
class AreaManager():
    def __init__(self):
        self.areas = []
        for k, v in yaml_data ['areas'].items():
            self.areas.append(Area(k, v))
    
    def get_area_by_name(self,name):
        if name in [i.name for i in self.areas]:
            return [i for i in self.areas if i.name == name][0]
        else:
            # logging.info("Area %s not found in AreaManager" % name)
            return None
        

                
class Check():
    def __init__(self,idx):
        check_data = check_dict[idx]
        
        for i in check_data.keys():
            if check_data[i] != check_data[i]:
                val = None
            else:
                val = check_data[i]
                
            if i == 'req' and val is not None:
                val = list(val.split(","))
                val = [i.strip() for i in val]
            setattr(self, i, val)
            
        # old with vanilla name
        # self.full_name = "%s %s %s (%s)" % ("{:<4}".format("%s:" % self.id),"{:<30}".format("%s:" % self.area),self.location,self.og_name)
        self.full_name = "%s %s %s" % ("{:<4}".format("%s:" % self.id),"{:<32}".format("%s:" % self.area),self.location)
        self.placed = False
        self.placed_collectible = None
        
    def place_collectible(self, collectible):
        self.placed_collectible = collectible
        self.placed = True
        
        
        
        
        
class Collectible():
    def __init__(self, collectible_data):
        self.name = collectible_data['name']
        for i in collectible_data.keys():
            if collectible_data[i] != collectible_data[i]:
                val = None
            else:
                val = collectible_data[i]
                
            if i == 'req' and val is not None:
                val = list(val.split(","))
                val = [i.strip() for i in val]
            setattr(self, i, val)

            

class KeyItem():
    def __init__(self, name, ignore_data = False):
        self.name = name
        
        if not ignore_data:
            collectible_data = items_dict[[i for i in items_dict if items_dict[i]['key_item_name']=='final_key'][0]]
            for i in collectible_data.keys():
                if collectible_data[i] != collectible_data[i]:
                    val = None
                else:
                    val = collectible_data[i]
                    
                if i == 'name':
                    i = 'proper_name'
                    
                if i == 'req' and val is not None:
                    val = list(val.split(","))
                    val = [i.strip() for i in val]
                setattr(self, i, val)
            
        

               
class CollectibleManager():
    def __init__(self, re):
        self.collectibles = []
        
        #index system
        for v in items_dict.values():
            self.collectibles.append(Collectible(v))                

        self.re = re
        self.history = {}
        
        for c in self.collectibles:
            if c.type != 'key_item':
                self.history[c.name] = 0
        
        
        
    @property
    def history_average(self):
        if not self.history:
            return 0
        else:
            try:
                return mean(list(self.history.values()))
            except:
                logging.info("Error on history_average, returning 0")
                return 0
                pass

    def choose_collectible(self, check, medal_flag=False):


        if medal_flag:
            chosen_collectible = [i for i in self.collectibles if i.bag_id == 'D0'][0]
        else:
            choices = [i for i in self.collectibles if i.valid == 'valid' and i.type != 'key_item' and self.history[i.name] < self.history_average]
    
            if not choices:
                # if no matches, then choose whole list
                # logging.info("Filling choice list to max")
                choices = [i for i in self.collectibles if i.valid == 'valid' and i.type != 'key_item']
                
            chosen_collectible = self.re.choice(choices)
        
        
        check.place_collectible(chosen_collectible)
        self.history[chosen_collectible.name] = self.history[chosen_collectible.name] + 1
        
    def choose_shop_collectibles(self, tier, k):
        choices = [i for i in self.collectibles if i.valid == 'valid' and  i.shop_ignore != 'ignore' and i.type != 'key_item' and i.type != 'misc' and tier-1 < int(i.tier) < tier+1]
        
        if len(choices) < k:
            # re roll once more tiers
            choices = [i for i in self.collectibles if i.valid == 'valid' and i.type != 'key_item' and i.type != 'misc' and tier-2 < int(i.tier) < tier+2]
            if len(choices) < k:
                k = len(choices)
                choices = [i for i in self.collectibles if i.valid == 'valid' and i.type != 'key_item' and i.type != 'misc' and tier-2 < int(i.tier) < tier+2]
        return self.re.sample(choices,k)
        
        
    def generate_price_changes(self):
        
        output_str = '\n;Price Changes\n'
        for c in self.collectibles:
            if c.cost_new:
                cost_hex = i2b(int(c.cost_new))
                output_str += 'org $%s\ndb $%s, $%s\n'  % (c.cost_addr, cost_hex[2:4], cost_hex[0:2])
        return output_str
        

        
class Shop():
    def __init__(self, shop_data):
        self.name = shop_data['name']
        for i in shop_data.keys():
            if shop_data[i] != shop_data[i]:
                val = None
            else:
                val = shop_data[i]
                
            if i == 'req' and val is not None:
                val = list(val.split(","))
                val = [i.strip() for i in val]
            setattr(self, i, val)

class ShopManager():
    def __init__(self, re, cm):
        self.shops = []
        self.cm = cm
        
        #index system
        for v in shops_dict.values():
            self.shops.append(Shop(v))
        self.re = re

    def generate_shops(self):
        
        shop_data = {}
        for shop in self.shops:
            if shop.valid == 'valid':
                temp_shop = {'items': {}}
                # logging.info("Processing shop %s" % shop.name)
                temp_shop_data = shop.data[2:]
                shop_items = [i for i in [temp_shop_data[i:i+2] for i in range(0, len(temp_shop_data), 2)] if i != '00']
                choices = self.cm.choose_shop_collectibles(int(shop.tier),len(shop_items))
                for c in choices:
                    temp_shop['items'][c.name] = c.bag_id
                
                if shop.name == 'Kol Item 2':
                    temp_shop['items']['King Sword'] = 'E9'
                if shop.name == 'Sioux Item':
                    # delete last item, replace
                    new_dict = {}
                    for k in list(temp_shop['items'].keys())[:-2]:
                        new_dict[k] = temp_shop['items'][k]
                    temp_shop['items'] = new_dict
                    temp_shop['items']['Invisible Herb'] = 'A9'
                    temp_shop['items']['Moth Powder'] = 'C6'
                if shop.name == 'Lancel Item':
                    temp_shop['items']['Invisible Herb'] = 'A9'

                    
                temp_shop['addr'] = i2b(b2i(shop.addr) + 1)
                shop_data[shop.name] = temp_shop
        
        output_str = '; SHOP DATA'
        shop_log = "\n========== Shops:==========\n"
        
        for shop, data in shop_data.items():
            output_str += ';%s\norg $%s\ndb $%s\n' % (shop, data['addr'], ', $'.join(data['items'].values()))
            
            shop_log += '%s:\n' % shop.upper()
            for item in data['items'].keys():
                shop_log += '%s\n' % item
            shop_log += '\n'
        
        

        
        self.shop_asm = output_str
        self.shop_log = shop_log
                  

                    


class World():
    def __init__(self, random, seed_config):
        self.areas = []
        self.seed_num = seed_config['seed_num']
        self.keys = []
        self.latest_checks = []
        self.valid_seed = True
        self.am = AreaManager()
        self.cm = CollectibleManager(random)
        self.sm = ShopManager(random, self.cm)
        self.re = random
        self.seed_config = seed_config
        self.attempted_generation = False
        
    @property
    def key_names(self):
        return [i.name for i in self.keys]
    @property
    def area_names(self):
        return [i.name for i in self.areas]
    @property
    def check_names(self):
        return "\n".join([i.full_name for i in self.latest_checks])
    @property
    def checks_by_area(self):
        d = {}
        for a in self.areas:
            d[a.name] = len(a.checks)
        return d


    def get_check_by_id(self, idx):
        idx = int(idx)
        for check in self.checks:
            if check.id == idx:
                return check


    def add_area(self,area):
        if area.name not in self.area_names:
            self.areas.append(area)
        else:
            # logging.info("Area already present, ignoring addition to World's areas")
            pass


    def gather_checks(self):
        checks = []
        for i in self.areas:
            for i2 in i.checks:
                checks.append(i2)
        
        self.checks = checks

    
    def assess_areas_for_checks(self):
        areas_to_check = self.area_names
        checked_area_names = []


        def add_area_to_check(area_name):
            area = self.am.get_area_by_name(area_name)
            try:
                temp = area.name + ""
            except:
                logging.info("Area %s is not present as an area, check config" % area_name)
            # add to self.areas
            if area_name not in self.area_names:
                # logging.info("Area %s added to self.areas" % area_name)
                self.add_area(area)
                self.parse_areas_for_rewards()
                
            else:
                # logging.info("Area %s already in self.areas, ignoring" % area_name)
                pass
            
            # add to checked list
            if area_name not in checked_area_names:
                # logging.info("Area %s added to check" % area_name)
                areas_to_check.append(area_name)

                checked_area_names.append(area_name)
            else:
                # logging.info("Area %s already in checked_area_names, ignoring" % area_name)
                pass

        iter_num = 1000
        while areas_to_check:
            
            iter_num -= 1
            if iter_num < 0:
                # logging.info("Exceeded 1000 checks, breaking loop")
                break

            area = self.am.get_area_by_name(areas_to_check.pop())
            
            
            if area:
                # logging.info("\nChecking area %s, remaining size of areas_to_check %s" % (area.name,len(areas_to_check)))
                
                connections = area.connections
                for connection, configs in connections.items():
                    # try:


                    if connection != "None":
                        # if area.name == 'Sea' and "Olivia" in connection:
                        #     breakpoint()                            
                        if not configs:
                            # logging.info("Area %s has no reqs, attempting add" % connection)
                            add_area_to_check(connection)                
                        elif 'reqs' not in configs.keys():
                            # logging.info("Area %s has no reqs, attempting add" % connection)
                            add_area_to_check(connection)
                        else:
                            reqs = [i.strip() for i in configs['reqs'].split(",")]
                            req_pass_flag = all([i in self.key_names for i in reqs])
                            if req_pass_flag:
                                # logging.info("Requirements %s were met with current keys %s" % (reqs, self.key_names))
                                add_area_to_check(connection)
                            else:
                                # logging.info("Requirements %s were NOT met with current keys %s" % (reqs, self.key_names))
                                pass
                    # except Exception as e:
                    #     if 'None' in connections.keys():
                    #         pass
                    #     else:
                    #         logging.info("Error: %s" % e)
                    #         logging.info("\n\n\nCHECK CONFIG FILE FOR CONNECTIONS AND COLONS: %s\n\n\n" % connections)
                    #         pass
        
        
        # now, check each area for available checks
        # logging.info("Assessing checks for placement")
        available_checks = []
        for area in self.areas:
            for check in area.checks:
                if not check.placed:
                    if not check.reqs:
                        # logging.info("Adding check %s, no requirements" % (check.og_name))
                        available_checks.append(check)
                    else:
                        reqs = [i.strip() for i in check.reqs.split(",")]
                        req_pass_flag = all([i in self.key_names for i in reqs])
                        if req_pass_flag:
                            # logging.info("Adding check %s, reqs met" % (check.og_name))
                            available_checks.append(check)
                        else:
                            # logging.info("NOT adding check %s, reqs %s not met by %s" % (check.og_name, reqs, self.key_names))
                            pass
                            
        # logging.info("Len %s" % len(available_checks))
        self.latest_checks = available_checks
        self.gather_checks()
        
        
    def parse_areas_for_rewards(self):
        # this is primarily used to add "key items" for rewards like kandar_1 and kandar_2
        for area in self.areas:
            if 'reward' in area.__dict__:
                if area.reward not in self.key_names:
                    # logging.info("Adding reward %s for area %s" % (area.reward, area.name))
                    self.keys.append(KeyItem(area.reward, ignore_data = True))
                    
        # this checks if the player has stones_of_sunlight and rain_staff, give them rainbow_drop
        
        if 'stones_of_sunlight' in self.key_names and 'rain_staff' in self.key_names and 'rainbow_drop' not in self.key_names:
            # logging.info("Adding rainbow_drop to key_items, stones and rain staff identified")
            self.keys.append(KeyItem('rainbow_drop'))
            
        # this checks if the player has can access black pepper via vanilla methods
        
        if 'Portoga' in self.area_names\
        and 'Baharata' in self.area_names\
        and 'Kazave' in self.area_names\
        and ('magic_key' in self.key_names or 'final_key' in self.key_names)\
        and 'black_pepper' not in self.key_names:
            # logging.info("Adding black_pepper to key_items, areas & keys identified")
            self.keys.append(KeyItem('black_pepper'))


    def gather_latest_reqs(self, passed_keys):
        
        passed_keys = [i.name for i in passed_keys]
        latest_reqs = []
        for a in self.areas:
            
            # breakpoint()
            # first gather reqs for area's connections
            for c in a.connections:
                if a.connections[c]:
                    if 'reqs' in a.connections[c].keys():
                        reqs = a.connections[c]['reqs']
                        for i in reqs.split(","):
                            latest_reqs.append(i.strip())
                            
            # then gather reqs for area's checks
            for c in a.checks:
                reqs = c.reqs
                if reqs:
                    for i in reqs.split(","):
                        latest_reqs.append(i.strip())
            
        
        all_keys = list(set(latest_reqs))
        all_keys = [i for i in all_keys if i not in ['kandar_1','kandar_2','baramos','zoma']]
        
        
        new_keys = [i for i in all_keys if i not in passed_keys]
        # breakpoint()
        return [KeyItem(i) for i in new_keys]
        
    def place_key_items(self, passed_key_items):
        
        # key items first
        if self.seed_config['shuffle_key_item_placement']:
            self.re.shuffle(passed_key_items)
            
            
        #####################
        # DYNAMIC (PLACEMENT PRIORITIZES KEY ITEMS THAT ARE REQUIRED TO OPEN THE WORLD)
        #####################
        if self.seed_config['key_item_placement_method'] == 'dynamic':

            
            # this gets init with the key items we don't want to place
            placed_key_items = [KeyItem('black_pepper'),KeyItem('rainbow_drop')]
            
            latest_key_item_reqs_start = self.gather_latest_reqs(placed_key_items)
            
            # logging.info("First: %s" % len(latest_key_item_reqs_start))
            # breakpoint()
            
            def assign_keys(latest_key_item_reqs, bypass_gather=False):
                while latest_key_item_reqs:
                    # logging.info([i.name for i in latest_key_item_reqs])
                    key = latest_key_item_reqs.pop()
                    # logging.info("Checking key %s" % key.name)
                    # logging.info("Placing key item %s, len of latest_checks %s" % (key.name, len(self.latest_checks)))
                    if self.seed_config['place_keys_in_chests_only']:
                        # logging.info("Placing in chests only")
                        available_checks = [i for i in self.latest_checks if not i.placed and i.type == 'chest' and i.valid == 'valid']
        
                    else:
                        available_checks = [i for i in self.latest_checks if not i.placed and i.valid == 'valid']
                        
                        
                    if available_checks:
                        chosen_check = self.re.choice(available_checks)
                        # logging.info("Chose %s" % chosen.full_name)
                        chosen_check.place_collectible(key)
                        self.keys.append(key)
                        self.assess_areas_for_checks()
                        
                        # dynamic keys update
                        if not bypass_gather:
                            placed_key_items.append(key)
                            latest_key_item_reqs = self.gather_latest_reqs(placed_key_items)
                        # logging.info("Remaining keys: %s" % len(latest_key_item_reqs))
    
                    else:
                        logging.error("!!! No available checks, seed deemed impossible...")
                        self.valid_seed = False
                        break

            assign_keys(latest_key_item_reqs_start)

            # breakpoint()
            # this is saying, place all the key items that hadnt yet been placed
            latest_key_item_reqs_final = [i.name for i in passed_key_items if i.name not in [i.name for i in placed_key_items]]
            # logging.info("Placing missing keys %s" % latest_key_item_reqs_final)

            latest_key_item_reqs_final = [KeyItem(i) for i in latest_key_item_reqs_final]
            
            # breakpoint()
            assign_keys(latest_key_item_reqs_final, bypass_gather=True)
            



        #####################
        # BASIC (SHUFFLED OR NOT)
        #####################


        elif self.seed_config['key_item_placement_method'] == 'basic':
                
                
                
            for key in passed_key_items:
                # logging.info("Placing key item %s, len of latest_checks %s" % (key.name, len(self.latest_checks)))
                if self.seed_config['place_keys_in_chests_only']:
                    # logging.info("Placing in chests only")
                    available_checks = [i for i in self.latest_checks if not i.placed and i.type == 'chest' and i.valid == 'valid']
    
                else:
                    available_checks = [i for i in self.latest_checks if not i.placed and i.valid == 'valid']
                    
                    
                if available_checks:
                    chosen_check = self.re.choice(available_checks)
                    # logging.info("Chose %s" % chosen.full_name)
                    chosen_check.place_collectible(key)
                    self.keys.append(key)
                    
                    self.assess_areas_for_checks()
                else:
                    logging.error("!!! No available checks, seed deemed impossible...")
                    self.valid_seed = False
                    break
            
        if self.valid_seed:
            # one more             
            self.assess_areas_for_checks()
        
        
        
    def place_medal_rewards(self):
        output_str = ''
        medal_keys = 0
        medal_keys_limit = 3
        chosen_collectibles = []
        
        def validate_medal_item(collectibles, choice):
            
            if (choice.type == 'key_item' and medal_keys >= medal_keys_limit) or (choice in chosen_collectibles):
                pass_flag = False
                choice = self.re.choice(collectibles)
            else:
                pass_flag = True
        
            return choice, pass_flag        
            
        
        
        medal_data = {}
        medal_lookup = {1:'3',
                  2:'3',
                  3:'3',
                  4:'4',
                  5:'4',
                  6:'4',
                  7:'5',
                  8:'5',
                  9:'5',
                  10:'6',
                  11:'6',
                  12:'6',}
        item_list = [i for i in range(1,13)]
        self.re.shuffle(item_list)
        for medal_num in item_list:
            
            tier = medal_lookup[medal_num]
            collectibles = [i for i in self.cm.collectibles if i.tier == str(tier)]
            choice = self.re.choice(collectibles)    
            pass_flag = False
            iter_num = 0
            while not pass_flag and iter_num < 100:
                choice, pass_flag = validate_medal_item(collectibles, choice)
                iter_num += 1
            if iter_num >= 100:
                logging.info("Exceed 100 tries for Small Medal item, assigning random without tier")
                try:
                    choice = self.re.choice([i for i in collectibles if i not in chosen_collectibles and i.type != 'key_item' and i.valid == 'valid'])
                except:
                    logging.info("Failed previous, assigning pure random")
                    choice = self.re.choice([i for i in collectibles if i.valid == 'valid'])
                
            
        
            # final chosen 
            if choice.type == 'key_item':
                medal_keys = medal_keys + 1
        
            chosen_collectibles.append(choice)
            medal_data[medal_num] = choice
        
        
        output_str += '\n\n\n;SMALL MEDALS\norg $C31350\n'
        medal_log = '\n==========Small Medal Rewards:==========\n'
        
        medal_keys = sorted(list(medal_data.keys()))
        for medal_cost in medal_keys:
            choice = medal_data[medal_cost]
            cost_byte = "0%s" % i2b(medal_cost)            
            output_str += "db $%s, $%s\n" % (cost_byte, choice.bag_id)
            medal_log  += "%s%s\n" % ("{:<5}".format("%s:" % medal_cost), choice.name)
            output_str += "\n"
            
        
        self.medal_log = medal_log
        self.medal_asm = output_str


    def report_placed_keys(self):

        items_str = ''
        if self.valid_seed:
            items = [(i.full_name, i.placed_collectible.name.upper().replace("_"," ")) for i in self.checks if i.placed and type(i.placed_collectible) == KeyItem]
            d = dict(zip(["{:<20}".format(i[1]) for i in items],[i[0] for i in items]))
    
            order = [   'THIEF KEY           ',
                        'MAGIC BALL          ',
                        'MAGIC KEY           ',
                        'KING LETTER         ',
                        'DREAM RUBY          ',
                        'WAKE UP POWDER      ',
                        'THIRSTY PITCHER     ',
                        'FINAL KEY           ',
                        'SAILOR BONE         ',
                        'LOVELY MEMORIES     ',
                        'RA MIRROR           ',
                        'GAIA SWORD          ',
                        'RED ORB             ',
                        'GREEN ORB           ',
                        'PURPLE ORB          ',
                        'YELLOW ORB          ',
                        'BLUE ORB            ',
                        'SILVER ORB          ',
                        'FAIRY FLUTE         ',
                        'RAIN STAFF          ',
                        'SACRED TALISMAN     ',
                        'STONES OF SUNLIGHT  ',
                        'LIGHT ORB           ']
            
            final = ["%s%s" % (i, d[i]) for i in order]          

            items_str +=  "\n==========Key Item Checks:==========\n"
            for i in final:
                items_str +=  "%s\n" % i
        return items_str
                
    def report_placed_items(self):
        items_str = ''
        if self.valid_seed:
            
                
            items = [(i.full_name, i.placed_collectible.name.upper().replace("_"," "), i.id) for i in self.checks if i.placed]
            items = sorted(items, key=itemgetter(2))
            


            items_str += "\n==========All Checks:==========\n"
            for a, b, c in items:
                items_str +=  "%s%s\n" % ("{:80}".format(a),b)
                
        return items_str
                

    def report_placed_medal_items(self):
        medal_str = self.medal_log  
        placed_names = [i.full_name for i in self.checks if i.placed_collectible.bag_id == 'D0']
        medal_str += "\n==========Small Medal Locations:==========\n"
        for i in placed_names:
            medal_str += '%s\n' % i
        return medal_str
              

    def generate_spoiler(self):
        spoiler_str = 'SPOILER LOG:\nSeed: %s\n' % self.seed_num
        
        spoiler_str += '\n==========Configurations:==========\n'
        for k, v in self.seed_config.items():
            spoiler_str += "%s%s\n" % ("{:<30}".format(k), v)
        
        spoiler_str += '\n'
        
        spoiler_str += self.report_placed_items()
        spoiler_str += self.report_placed_medal_items()     
        spoiler_str += self.sm.shop_log
        spoiler_str += self.report_placed_keys()     
        
        self.spoiler_log = spoiler_str
        with open(os.path.join(THIS_FILEPATH,'output','dq3_%s.log' % self.seed_num),'w') as f:
            f.write(spoiler_str)
        with open(os.path.join(THIS_FILEPATH,'asar','spoiler.log'),'w') as f:
            f.write(spoiler_str)
        
    def place_items(self):

        # first place small medals
        chosen_checks = self.re.sample([i for i in self.checks if not i.placed and i.valid == 'valid'], self.seed_config['small_medal_count'])
        for c in chosen_checks:
            self.cm.choose_collectible(c,medal_flag=True)
            
        for c in [i for i in self.checks if not i.placed]:
            self.cm.choose_collectible(c)
            
            pass
        
    def assign_starting_areas(self):
        for a in self.seed_config['starting_areas']:
            self.add_area(self.am.get_area_by_name(a))


    def generate_patch(self):
        output_str = 'hirom\n\n'
        
        ######## PICKUPS
        for check in [i for i in self.checks if i.check_type == 'pickup']:
            
            addr = i2b(b2i(check.address) + 3)
            
            new_data = check.placed_collectible.data_1_l + check.item_data[1:2] + check.placed_collectible.data_2
            
            new_data = "$%s, $%s" % (new_data[0:2],new_data[2:4])
            
            output_str += ';%s\n;%s\norg $%s\ndb %s\n\n' % (check.full_name, check.placed_collectible.name,addr, new_data)
            pass
        
        
        ######## EVENTS
        for check in [i for i in self.checks if i.check_type == 'event']:
            
                
            addresses = check.address.split(",")
            
            for addr in addresses:
                addr = addr.strip()
                new_data = "$%s" % (check.placed_collectible.bag_id)
                output_str += ';%s\n;%s\norg $%s\ndb %s\n\n' % (check.full_name, check.placed_collectible.name,addr, new_data)
            pass
        
        output_str += self.medal_asm
        output_str += self.sm.shop_asm
        output_str += self.cm.generate_price_changes()

        with open(os.path.join(THIS_FILEPATH,'asar','patch_r.asm'),'w') as f:
            f.write(output_str)
        with open(os.path.join(self.temp_,'asar','patch_r.asm'),'w') as f:
            f.write(output_str)
            
        
        
    def generate_seed(self):
        key_items = [KeyItem(i) for i in ['thief_key','magic_key','magic_ball','final_key','king_letter','lovely_memories','gaia_sword','sailor_bone','thirsty_pitcher','sacred_talisman','blue_orb','green_orb','red_orb','silver_orb','yellow_orb','purple_orb','light_orb','stones_of_sunlight','rain_staff','ra_mirror','fairy_flute','dream_ruby','wake_up_powder']]
        
        if not self.valid_seed or not self.attempted_generation:
            self.attempted_generation = True
            logging.info("Seed generation attempt 1")
            
            self.reset_seed()
            self.assign_starting_areas()
            self.assess_areas_for_checks()
            self.place_key_items(key_items)

            attempts = 2
            while not self.valid_seed and attempts < self.seed_config['seed_generation_attempt_count']:
                logging.info("Seed generation attempt %s" % attempts)
                self.reset_seed()
                self.assign_starting_areas()
                self.assess_areas_for_checks()
                self.place_key_items(key_items)
                attempts += 1                
                
            if not self.valid_seed:
                logging.error("!!! Seed could not generate after %s attempts, aborting" % attempts)

        if self.valid_seed:
            
        
            # begin item placement
            self.place_items()
            self.place_medal_rewards()
            self.sm.generate_shops()
            
            
            # reporting            
            self.generate_patch()
            self.generate_spoiler()
            
            
    def reset_seed(self):
        self.areas = []
        self.keys = []
        self.latest_checks = []
        self.valid_seed = True
        self.am = AreaManager()
        self.attempted_generation = False
        


    
        

if False:        
    # SEED_NUM = 966503
    SEED_NUM = random.randint(1,1000000)
    logging.info("Seed number: %s" % SEED_NUM)
    random.seed(SEED_NUM)
    
    
    seed_config = {'starting_areas' : ['Aliahan','Samanosa'], 
                   'place_keys_in_chests_only' : True,
                   'shuffle_key_item_placement' : True,
                   'seed_generation_attempt_count' : 25,
                   'key_item_placement_method': 'dynamic',
                   'small_medal_count' : 15,
                   'seed_num' : SEED_NUM}
    y = World(random, seed_config)
    
    try:
        y.generate_seed()
        logging.info("\n\n\n")
        logging.info(y.spoiler_log)
    
    except Exception as e:
        logging.info("Seed resulted in error. Seed was not generated: %s" % e)
    
    
    
    
    
    
    
    
    
    






class MainWindow(object):
    SCREEN_HEIGHT = 600
    SCREEN_WIDTH = 600
    def __init__(self):
        self.app = QApplication([])
        self.window = QMainWindow()
        self.window.setFixedSize(self.SCREEN_WIDTH,self.SCREEN_HEIGHT)
        self.window.setWindowTitle('DQ3R')
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("ico.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.window.setWindowIcon(self.icon)


        self.title_container = QLabel(self.window)
        self.title_container.setGeometry(QtCore.QRect(0, 0, self.SCREEN_WIDTH, 30))
        # self.title_container = self.set_white(self.title_container)
        
        self.title_label = QLabel("DQ3R",self.window)
        self.title_label.setGeometry(QtCore.QRect(0, 0, self.SCREEN_WIDTH, 30))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.title_label_border = QFrame(self.window)
        self.title_label_border.setGeometry(QtCore.QRect(0, 0, self.SCREEN_WIDTH, 30))
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
        self.key_item_chests_checkbox.setToolTip('Checked: Key Items will only be placed in chests. Searchable locations (visible and invisible) and NPC events will not have keys.\nUnchecked: Key Items can be placed anywhere. All checks have logical requirements.')
        self.key_item_chests_checkbox.setChecked(True)


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


    def rom_input_click(self):
        dialog = QFileDialog()
        new_file = dialog.getOpenFileName(None,"Select video","",filter="sfc (*.sfc);;smc (*.smc)")
        self.rom_label_input.setText(new_file[0])

    def generate(self):
        # parse configs into dict

    
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        
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
                            'shuffle_key_item_placement' : True,
                            'seed_generation_attempt_count' : 25,
                            'key_item_placement_method': 'dynamic',
                            'small_medal_count' : medal_parse,
                            'seed_num' : SEED_NUM}
    
            self.update_log_text("Beginning seed generation...")        
            self.update_log_text("Seed number %s..." % SEED_NUM)
            
            logging.info("Seed number: %s" % SEED_NUM)
            random.seed(SEED_NUM)
            y = World(random, seed_config)
            
            try:
                y.generate_seed()
                logging.info("\n\n\n")
                logging.info(y.spoiler_log)
            
                self.update_log_text("Finished generation!")
            
            except Exception as e:
                logging.info("Seed resulted in error. Seed was not generated: %s" % e)
                self.update_log("Seed resulted in error. Seed was not generated: %s" % e)

        except Exception as e:
            logging.info("Program error %s" % e)
            self.update_log("Program error %s" % e)

        if not os.path.exists(TEMP_DIR):
            os.rm(TEMP_DIR)        
                
                
        

        
class LogThread(QThread):
    log = pyqtSignal(str)

    def __init__(self, parent=None):
        super(LogThread, self).__init__(parent)
        self._text = ''

    def setText(self, text):
            self._text = text

    def run(self):
        self.log.emit(str(self._text))

        
        
        



# if __name__ == '__main__':
#     main_window = MainWindow()
#     main_window.window.show()
#     # main_window.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())
#     main_window.app.exec_()
#     # del main_window



    
temp_dir = os.path.join(THIS_FILEPATH,'tmp')

    
TEMP_SEED = random.randint(1,1000000)
ROM_PATH = "E:\pmac_junk_rev_1\emulators\DQIII\ROM\dq3_en_patch.sfc"
NEW_ROM_PATH = os.path.join(THIS_FILEPATH,'temp', "dq3_%s.sfc" % TEMP_SEED)
shutil.copy(ROM_PATH, NEW_ROM_PATH)

sh_calls = ["%s" % os.path.join(THIS_FILEPATH,'asar','asar.exe'), "--fix-checksum=off", "asar/patch.asm", "%s" % NEW_ROM_PATH]
    
subprocess.call(sh_calls)
    
    
    
    
    
