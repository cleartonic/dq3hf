import yaml, os, json
import pandas as pd, numpy as np
import logging, random
from operator import itemgetter




logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    handlers=[logging.StreamHandler()])

THIS_FILEPATH = os.path.dirname(__file__)




df_checks = pd.read_csv(os.path.join(THIS_FILEPATH,'data','source','check_id.csv'))
check_dict = df_checks.T.to_dict()
with open(os.path.join('data','checks.json'),'w') as f:
    json.dump(check_dict, f)
    
df_items = pd.read_csv(os.path.join(THIS_FILEPATH,'data','source','item_id.csv'), dtype='str')
items_dict = df_items.T.to_dict()
with open(os.path.join('data','items.json'),'w') as f:
    json.dump(items_dict, f)
    
    
df_shops = pd.read_csv(os.path.join(THIS_FILEPATH,'data','source','shop_id.csv'), dtype='str')
shops_dict = df_shops.T.to_dict()
with open(os.path.join('data','shops.json'),'w') as f:
    json.dump(shops_dict, f)


df_warps = pd.read_csv(os.path.join(THIS_FILEPATH,'data','source','warp_id.csv'), dtype='str')
warps_dict = df_warps.T.to_dict()
with open(os.path.join('data','warps.json'),'w') as f:
    json.dump(warps_dict, f)


