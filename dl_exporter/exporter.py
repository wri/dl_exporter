from __future__ import print_function
import re
import geojson
import yaml
from pprint import pprint
from copy import deepcopy
import dl_exporter.config as c

#
# DEFAULTS
#
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
LIMIT=c.get('limit')
TILE_CONFIG=c.get('tile_config')


#
# MAIN
#
def run(geometry,config=None,dev=IS_DEV,noisy=NOISY,limit=LIMIT,check_ext=True):
    print(1,geometry)
    print(2,config,type(config))
    geometry, config=_load_setup(geometry,config,check_ext,noisy)


def echo(geometry,config=None,check_ext=True):
    _load_setup(geometry,config,check_ext,True)





#
# INTERNAL
#
def _load_setup(geometry,config,check_ext,noisy):
    if noisy:
        print()
        print(f'GEOMETRY ({geometry}):')
        print()
        geometry=_load_geojson(geometry,check_ext=check_ext)
        pprint(geometry)
        print('\n'*4)
        print(f'TILE_CONFIG ({config or "default"}):')
        print()
        config=_load_config(config,check_ext=check_ext)
        pprint(config)
    return geometry, config




def _load_geojson(geometry,check_ext):
    if check_ext and (not re.search('.geojson$',geometry)):
        geometry=f'{geometry}.geojson'
    with open(geometry) as file:
        geometry=geojson.load(file)
    return geometry


def _load_config(config,check_ext):
    if config:
        if check_ext and (not re.search('.yaml$',config)):
            config=f'{config}.yaml'
        config=yaml.safe_load(open(config))
    else:
        config=deepcopy(TILE_CONFIG)
    return config
