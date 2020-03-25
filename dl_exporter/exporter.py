from __future__ import print_function
import os
import re
import secrets
import geojson
import yaml
from pprint import pprint
from copy import deepcopy
from affine import Affine
import descarteslabs as dl
from descarteslabs.scenes import DLTile

import mproc
import tfr2human.utils as gcs_utils
import minigeo

import dl_exporter.config as c
import dl_exporter.utils as utils


#
# DEFAULTS
#
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
LIMIT=c.get('limit')
EXPORT_CONFIG=c.get('export_config')


#
# MAIN
#
def run(geometry,config=None,dev=IS_DEV,noisy=NOISY,limit=LIMIT,check_ext=True):
    geometry_filename=geometry
    timer=utils.Timer()
    timer.start()
    if noisy:
        _section_header('EXPORT START',first=True)
        print('geometry:',geometry_filename)
        print('config:',config or 'default')
        print('timestamp:',timer.stop())
    geometry, config=_load_setup(geometry_filename,config,check_ext,noisy)
    tiles=DLTile.from_shape(geometry,**config['tiling'])
    if noisy:
        _section_header('TILES')
        print('nb_tiles:',len(tiles))
        print('first_tile:')
        print('timestamp:',timer.now())
        pprint(tiles[0])
    if limit:
        tiles=tiles[:limit]
        if noisy:
            print("LIMIT:",len(tiles))
    def _export(tile):
        return _export_tile(tile,config['search'],config['output'],dev,noisy)
    out=mproc.map_with_threadpool(
        _export,
        tiles,
        max_processes=config.get('max_processes',8))
    out=[o for o in out if o]
    if noisy:
        _section_header('EXPORT COMPLETE')
        print('nb_transfered:',len(out))
        print('timestamp:',timer.now())
    output_file=_output_filename(geometry_filename,config)
    if output_file:
        utils.save_pickle(out,output_file)
        if noisy:
            _section_header('OUTPUT SAVED')
            print('path:',output_file)
            print('timestamp:',timer.now())    
            print(out)
    timer.stop()
    if noisy:
        _section_header('COMPLETE')
        print('duration:',timer.duration())
        print('timestamp:',timer.stop())
        print('\n'*4)


def echo(geometry,config=None,check_ext=True):
    _load_setup(geometry,config,check_ext,True)





#
# INTERNAL
#
def _load_setup(geometry,config,check_ext,noisy):
    if noisy:
        _section_header(f'GEOMETRY ({geometry})')
        geometry=_load_geojson(geometry,check_ext=check_ext)
        pprint(geometry)
        _section_header(f'EXPORT_CONFIG ({config or "default"})')
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
        config=deepcopy(EXPORT_CONFIG)
    return config


def _export_tile(tile,search_params,output_params,dev,noisy):
    scs,_=dl.scenes.search(tile,**search_params)
    if scs:
        filename, bucket, folder=_export_args(tile.key,output_params)
        print(filename,bucket,folder)
        if not dev:
            im=scs.mosaic(output_params['bands'],tile)
            if noisy:
                print(im.nbytes,im.shape,im.shape[0]*im.shape[1]*im.shape[2])        
            tmp_name=f'{secrets.token_urlsafe(16)}.tif'
            dest=gcs_utils.image_to_gcs(
                im,
                dest=filename,
                profile=_get_profile(im,tile),
                tmp_name=tmp_name,
                bucket=bucket,
                folder=folder,
                return_path=True)
            os.remove(tmp_name)
            return dest
        else:
            if noisy:
                print('dev run')
                pprint(output_params)


def _export_args(tile_key,config):
    prefix=config.get('prefix')
    suffix=config.get('suffix')
    bucket=config.get('bucket')
    folder=config.get('folder')
    filename=tile_key
    if prefix: filename=f'{prefix}_{filename}'
    if suffix: filename=f'{filename}_{suffix}'
    filename=f'{filename}.tif'
    return filename, bucket, folder



def _affine(gdal_trans):
    c, a, b, f, d, e=gdal_trans
    return Affine(a, b, c, d, e, f)


def _get_profile(im,aoi):
    return minigeo.build_profile(
        crs=aoi.crs, 
        transform=_affine(aoi.geotrans), 
        size=aoi.tilesize, 
        count=im.shape[0], 
        nodata=None, 
        dtype='uint8', 
        compress='lzw')


def _output_filename(geometry_filename,config):
    fname=config.get('output_file')
    if fname and (not isinstance(fname,str)):
        geometry_filename=re.sub('.geojson$','',geometry_filename)
        search_config=config['search']
        fname="--".join(search_config['products'])
        start=search_config.get('start_datetime')
        end=search_config.get('end_datetime')
        if start: fname=f'{fname}_{start}'
        if end: fname=f'{fname}--{end}'
        fname=f'{fname}.{geometry_filename}.p'
    if fname:
        output_dir=config.get('output_dir')
        if output_dir:
            fname=f'{output_dir}/{fname}'
    return fname


def _section_header(name,first=False):
    if first:
        print('\n'*1)
    else:
        print('\n'*4)
    print('-'*50)
    print(f'{name.upper()}:')
    print('-'*50)
    print()

