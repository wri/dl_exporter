from __future__ import print_function
import re
import geojson
import yaml
from pprint import pprint
from copy import deepcopy
import descarteslabs as dl
from descarteslabs.scenes import DLTile
import mproc
import dl_exporter.config as c



import tfr2human.utils as gcs_utils
import minigeo
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.blob import Blob
from google.cloud import storage
from affine import Affine



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
    geometry, config=_load_setup(geometry,config,check_ext,noisy)
    tiles=DLTile.from_shape(geometry,**config['tiling'])
    if noisy:
        print()
        print('-'*50)
        print('NB TILES:',len(tiles))
        print('FIRST TILE:')
        pprint(tiles[0])
    if limit:
        tiles=tiles[:limit]
        if noisy:
            print("LIMIT:",len(tiles))
    def _export(tile):
        return _export_tile(tile,config['search'])
    out=mproc.map_with_threadpool(
        _export,
        tiles,
        max_processes=config.get('max_processes',8))



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


def _export_tile(tile,search_params):
    scs,_=dl.scenes.search(tile,**search_params)
    if scs:
        print(scs)
    else:
        print('--')




def _affine(gdal_trans):
    c, a, b, f, d, e=gdal_trans
    return Affine(a, b, c, d, e, f)


def _save_to_gcs(im,profile,filename,bucket,folder):
    tmp_name=f'{secrets.token_urlsafe(16)}.tif'
    dest=gcs_utils.image_to_gcs(
        im,
        dest=filename,
        profile=profile,
        tmp_name=tmp_name,
        folder=folder,
        bucket=bucket)
    os.remove(tmp_name)
    return dest


def _get_profile(im,aoi):
    return minigeo.build_profile(
        crs=aoi.crs, 
        transform=_affine(aoi.geotrans), 
        size=aoi.tilesize, 
        count=im.shape[0], 
        nodata=None, 
        dtype='uint8', 
        compress='lzw')


