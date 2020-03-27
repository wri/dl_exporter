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

import dl_exporter.config as c
import dl_exporter.utils as utils
import dl_exporter.printer as printer


#
# DEFAULTS
#
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
LIMIT=c.get('limit')
CHECK_EXT=c.get('check_ext')
EXPORT_CONFIG=c.get('export_config')
REMOVE_DOWNLOADS=c.get('remove_downloads')
CSV_COLS=['tile_key','tile_empty','path','error','error_msg']
TMP_DIR='tmp'
MAX_PROCESSES=16
#
# MAIN
#
def run(geometry,config=None,dev=IS_DEV,noisy=NOISY,limit=LIMIT,check_ext=CHECK_EXT):
    # setup/config
    timer=utils.Timer()
    timer.start()
    if not dev:
        utils.ensure_dir(directory=TMP_DIR)
    geometry_filename=geometry
    printer.section(
        noisy,
        'export start',
        first=True,
        geometry=geometry_filename,
        config=config or 'default')
    config=_load_config(config,check_ext=check_ext)
    csv=_csv_filename(geometry_filename,config)
    if csv: printer.csv_header(csv,*CSV_COLS)
    printer.section(
            noisy,
            'config',
            export_config=config)
    # dl-tiles
    geometry, tiles=_load_geometry_and_tiles(geometry_filename,config['tiling'],check_ext=check_ext)
    tile_keys=geometry.get('tile_keys')
    if tile_keys:
        printer.section(
                noisy,
                'tile_keys',
                filename=geometry_filename,
                nb_keys=len(tile_keys))
    else:
        printer.section(
                noisy,
                'geometry',
                geometry=geometry_filename,
                nb_features=len(geometry.get('features')),
                properties=geometry.get('properties'),
                feat_properties=geometry['features'][0].get('properties'))
    printer.section(
        noisy,
        'tiles',
        nb_tiles=len(tiles),
        first_tile=tiles[0],
        limit=limit)
    if limit:
        tiles=tiles[:limit]
    # export
    def _export(tile):
        try:
            dest, empty=_export_tile(tile,config['search'],config['output'],dev,noisy)
            error=False
            error_msg=None
        except Exception as e:
            _,_,_,dest=_export_args(tile.key,config['output'])
            dest=f'error://{dest}'
            error=True
            error_msg=str(e)
            empty=None
        if csv: printer.csv_row(csv,tile.key,empty,dest,error,error_msg)
        return dest
    out=mproc.map_with_threadpool(
        _export,
        tiles,
        max_processes=config.get('max_processes',8))
    out=[o for o in out if o]
    if dev:
        nb_transfered=f'(dev) {len(out)}'
    else:
        nb_transfered=len(out)
    printer.section(
        noisy,        
        'export complete',
        nb_transfered=nb_transfered)
    # close
    if out:
        output_file=_output_filename(geometry_filename,config)
        if output_file:
            utils.save_pickle(out,output_file)
    else:
        output_file=False
    timer.stop()
    printer.section(
        noisy,
        'complete',
        duration=timer.duration(),
        csv_log=csv,
        file_list=output_file)



def echo(geometry,config=None,check_ext=True):
    geometry_filename=geometry
    config=_load_config(config,check_ext=check_ext)
    geometry, tiles=_load_geometry_and_tiles(geometry_filename,False,check_ext=check_ext)
    printer.section(
            True,
            'config',
            export_config=config)
    printer.section(
            True,
            'geometry',
            geometry=geometry_filename,
            nb_features=len(geometry['features']),
            properties=geometry.get('properties'),
            feat_properties=geometry['features'][0].get('properties'))




#
# INTERNAL
#
def _load_geometry_and_tiles(geometry,tiling_config,check_ext):
    if re.search('.p$',geometry):
        tile_keys=utils.read_pickle(geometry)
        tiles=[DLTile.from_key(k) for k in tile_keys]
        geometry={'tile_keys': tile_keys}
    else:
        geometry=_load_geojson(geometry,check_ext)
        if tiling_config:
            tiles=DLTile.from_shape(geometry,**tiling_config)
        else:
            tiles=False
    return geometry, tiles


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
    filename, bucket, folder, dest=_export_args(tile.key,output_params)
    if scs:
        if not dev:
            im=scs.mosaic(output_params['bands'],tile)       
            tmp_name=f'{TMP_DIR}/{dest}'
            utils.ensure_dir(tmp_name)
            dest=gcs_utils.image_to_gcs(
                im,
                dest=filename,
                profile=utils.image_profile(im,tile),
                tmp_name=tmp_name,
                bucket=bucket,
                folder=folder,
                return_path=True)
            if REMOVE_DOWNLOADS:
                os.remove(tmp_name)
        return dest, False
    else:
        return None, True


def _export_args(tile_key,config):
    prefix=config.get('prefix')
    suffix=config.get('suffix')
    bucket=config.get('bucket')
    folder=config.get('folder')
    filename=tile_key
    if prefix: filename=f'{prefix}_{filename}'
    if suffix: filename=f'{filename}_{suffix}'
    filename=f'{filename}.tif'
    dest='/'.join([bucket, folder, filename])
    return filename, bucket, folder, dest


def _filename(fname,geometry_filename,search_config,ext):
    if fname and (not isinstance(fname,str)):
        geometry_filename=re.sub('.geojson$','',geometry_filename)
        fname="--".join(search_config['products'])
        start=search_config.get('start_datetime')
        end=search_config.get('end_datetime')
        if start: fname=f'{fname}_{start}'
        if end: fname=f'{fname}--{end}'
        fname=f'{fname}.{geometry_filename}.{ext}'
    return fname


def _csv_filename(geometry_filename,config):
    fname=config.get('csv_file')
    fname=_filename(fname,geometry_filename,config['search'],'csv')
    if fname:
        output_dir=config.get('csv_dir')
        if output_dir:
            fname=f'{output_dir}/{fname}'
    return fname


def _output_filename(geometry_filename,config):
    fname=config.get('output_file')
    fname=_filename(fname,geometry_filename,config['search'],'p')
    if fname:
        output_dir=config.get('output_dir')
        if output_dir:
            fname=f'{output_dir}/{fname}'
    return fname



