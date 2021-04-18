import yaml, os
import pandas as pd, numpy as np
import logging, random
from operator import itemgetter



logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    handlers=[logging.StreamHandler()])

THIS_FILEPATH = os.path.dirname(__file__)

with open(os.path.join(THIS_FILEPATH,'data.yml'),'r') as f:
    yaml_data = yaml.safe_load(f)

df_chests = pd.read_csv(os.path.join(THIS_FILEPATH,'chest_id.csv'))
# df_chests = df_chests.iloc[:,:11]

df_items = pd.read_csv(os.path.join(THIS_FILEPATH,'item_id.csv'), dtype='str')


class Area():
    def __init__(self, area_name, area_data):
        self.name = area_name
        for k, v in area_data.items():
            setattr(self, k, v)
        
        self.checks = []
        
        for i, r in df_chests[df_chests['area']==self.name].iterrows():
            self.checks.append(Check(r))
            
            
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
    def __init__(self,check_data):
        for i in check_data.index:
            if check_data[i] != check_data[i]:
                val = None
            else:
                val = check_data[i]
                
            if i == 'req' and val is not None:
                val = list(val.split(","))
                val = [i.strip() for i in val]
            setattr(self, i, val)
            
        self.full_name = "%s %s %s (%s)" % ("{:<4}".format("%s:" % self.id),"{:<30}".format("%s:" % self.area),self.location,self.og_name)
        self.placed = False
        self.placed_collectible = None
        
    def place_collectible(self, collectible):
        self.placed_collectible = collectible
        self.placed = True
        
        
        
        
        
class Collectible():
    def __init__(self, collectible_data):
        self.name = collectible_data['name']
        for i in collectible_data.index:
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
            collectible_data = df_items[df_items['key_item_name']==name].iloc[0]
            for i in collectible_data.index:
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
        for i, r in df_items.iterrows():
            self.collectibles.append(Collectible(r))                
      
        
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
                return np.average(list(self.history.values()))
            except:
                logging.info("Error on history_average, returning 0")
                return 0
                pass

    def choose_collectible(self, check):
        
        choices = [i for i in self.collectibles if i.valid == 'valid' and i.type != 'key_item' and self.history[i.name] < self.history_average]

        if not choices:
            # if no matches, then choose whole list
            # logging.info("Filling choice list to max")
            choices = [i for i in self.collectibles if i.valid == 'valid' and i.type != 'key_item']
            
        chosen_collectible = self.re.choice(choices)
        check.place_collectible(chosen_collectible)
        self.history[chosen_collectible.name] = self.history[chosen_collectible.name] + 1
        

    
class World():
    def __init__(self, random, seed_config):
        self.areas = []
        self.keys = []
        self.latest_checks = []
        self.valid_seed = True
        self.am = AreaManager()
        self.cm = CollectibleManager(random)
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

    def report_placed_keys(self):

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

            logging.info("\nKEY ITEM CHECKS:\n")
            for i in final:
                logging.info(i)
                
                
    def report_placed_items(self):

        if self.valid_seed:
            
            
            items = [(i.full_name, i.placed_collectible.name.upper().replace("_"," "), i.id) for i in self.checks if i.placed and type(i.placed_collectible) != KeyItem]
            items = sorted(items, key=itemgetter(2))
            


            logging.info("\nNON KEY ITEM CHECKS:\n")
            for a, b, c in items:
                logging.info("%s%s" % ("{:90}".format(a),b))
                
            # final = ["%s%s" % (k, v) for (k, v) in d.items()]          


            # for i in final:
                
                
                
                
                
        
    def place_items(self):
        for c in [i for i in self.checks if not i.placed]:
            self.cm.choose_collectible(c)
            
            pass
        
    def assign_starting_areas(self):
        for a in self.seed_config['starting_areas']:
            self.add_area(self.am.get_area_by_name(a))

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
            
            # reporting
            
            self.report_placed_items()
            self.report_placed_keys()     
    def reset_seed(self):
        self.areas = []
        self.keys = []
        self.latest_checks = []
        self.valid_seed = True
        self.am = AreaManager()
        self.attempted_generation = False
        


    
        

        
# SEED_NUM = 733016
SEED_NUM = random.randint(1,1000000)
logging.info("Seed number: %s" % SEED_NUM)
random.seed(SEED_NUM)


seed_config = {'starting_areas' : ['Aliahan'], 
               'place_keys_in_chests_only' : True,
               'shuffle_key_item_placement' : True,
               'seed_generation_attempt_count' : 25,
               'key_item_placement_method': 'dynamic'}
w = World(random, seed_config)

w.generate_seed()

logging.info("\n\n\n")


def b2i(byte):
    return int(byte,base=16)
def i2b(integer):
    return hex(integer).replace("0x","").upper()
    
output_str = 'hirom\n\n'

######## PICKUPS
for check in [i for i in w.checks if i.check_type == 'pickup']:
    
    addr = i2b(b2i(check.address) + 3)
    
    new_data = check.placed_collectible.data_1_l + check.item_data[1:2] + check.placed_collectible.data_2
    
    new_data = "$%s, $%s" % (new_data[0:2],new_data[2:4])
    
    output_str += ';%s\n;%s\norg $%s\ndb %s\n\n' % (check.full_name, check.placed_collectible.name,addr, new_data)
    pass


######## EVENTS
for check in [i for i in w.checks if i.check_type == 'event']:
    
        
    addresses = check.address.split(",")
    
    for addr in addresses:
        addr = addr.strip()
        new_data = "$%s" % (check.placed_collectible.bag_id)
        output_str += ';%s\n;%s\norg $%s\ndb %s\n\n' % (check.full_name, check.placed_collectible.name,addr, new_data)
    pass



######## SMALL MEDALS

output_str += '\n\n\n;SMALL MEDALS\norg $C31350\n'
medal_cost = 1
for tier in range(1,7):
    collectibles = [i for i in w.cm.collectibles if i.tier == str(tier)]
    choices = random.sample(collectibles, 2)
    for choice in choices:
        cost_byte = "0%s" % i2b(medal_cost)            
        output_str += "db $%s, $%s\n" % (cost_byte, choice.bag_id)
        medal_cost += 1
output_str += "\n"
    






with open('asar/patch_r.asm','w') as f:
    f.write(output_str)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
if False:

    ## use this to make sure all areas in data.yml match those in chest_id.csv
    # this looks both ways
    # the first loop should never return entries (makes sure all chests are placed to a matching area)
    # its ok if the second loop returns some entries (some areas dont have chests)
    

    #l1 comes from all unique entries in chest_id for areas 
    l1 = ['Reeve','Portoga','Merchant Town','Noaniels','Ashalam','Baharata','Lancel','Mercado','Rimuldar','Domdora','Isis Town','Luzami','Kazave','Elf Village','Tedanki','Muor','Zipangu','Pirate Hideout','Sioux','Sailor Bone Hut','Kol','Aliahan','Romaly','Edinbear','Isis Castle','Baramos Castle','Dragon Queen Castle','Dharma','Samanosa','Ludatorm','Zoma Castle','Najimi Tower','Bahn Tunnel Ashalam Side','Necrogond Cave','Cave of Temptation Romaly Side','Underworld Lake','Kandar Cave','Zipangu Cave','Gaia Navel','Ra Mirror Cave','Loto Cave','Marsh Cave','Mountain Cave','Bonus Dungeon','Shrine of Temptation','Shrine Prison','Desert Shrine','Necrogond Shrine','East Dharma Shrine','West Edinbear Shrine','Garin Shrine','Dark World Harbor','Rubiss Shrine','Rain Staff Shrine','Portoga Shrine Portoga Side','Final Key Shrine','Hobbit Shrine','Cape Olivia Shrine','Ramia Shrine','Garuna Tower','Arb Tower','Shampane Tower','Rubiss Tower','Pyramid','Ghost Ship','Pachisi Track Romaly','Pachisi Track Ashalam','Pachisi Track Cape','Pachisi Track Kol','Pachisi Track Zipangu',]
    l2 = w.area_names
    
    for l in l1:
        if l not in l2:
            print(l)
    print("\n\n\n")        
    for l in l2:
        if l not in l1:
            print(l)
    print("\n\n\n")        
    
    
    
    
    
    d1 = w.checks_by_area

    d2 = {}
    for i in w.latest_checks:
        if i.area in d2.keys():
            d2[i.area] = d2[i.area] + 1
        else:
            d2[i.area] = 1
        
    for k, v in d1.items():
        if k in d2.keys():
            v2 = d2[k]
            match = ""
            if v2 != v:
                match = "MISMATCH"
            print(k, v, v2, match)
        
        
        
