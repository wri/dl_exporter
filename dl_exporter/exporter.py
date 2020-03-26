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
import dl_exporter.printer as printer


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
    # setup
    geometry_filename=geometry
    timer=utils.Timer()
    timer.start()
    printer.section(
        noisy,
        'export start',
        first=True,
        geometry=geometry_filename,
        config=config or 'default')
    # run data
    geometry=_load_geojson(geometry_filename,check_ext=check_ext)
    config=_load_config(config,check_ext=check_ext)
    printer.section(
            noisy,
            'config',
            export_config=config)
    printer.section(
            noisy,
            'geometry',
            geometry=geometry_filename,
            nb_features=len(geometry['features']),
            properties=geometry.get('properties'),
            feat_properties=geometry['features'][0].get('properties'))
    # dl-tiles
    tiles=DLTile.from_shape(geometry,**config['tiling'])
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
        return _export_tile(tile,config['search'],config['output'],dev,noisy)
    out=mproc.map_with_threadpool(
        _export,
        tiles,
        max_processes=config.get('max_processes',8))
    out=[o for o in out if o]
    printer.section(
        noisy,        
        'export complete',
        nb_transfered=len(out))
    # close
    if out:
        output_file=_output_filename(geometry_filename,config)
        if output_file:
            utils.save_pickle(out,output_file)
            printer.section(
                noisy,
                'ouput saved',
                path=output_file,
                output=out)
    timer.stop()
    printer.section(
        noisy,
        'complete',
        duration=timer.duration())



def echo(geometry,config=None,check_ext=True):
    _load_setup(geometry,config,check_ext,True)





#
# INTERNAL
#
def _load_setup(geometry_filename,config,check_ext,noisy):

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
        if dev:
            return '/'.join([bucket, folder, filename])
        else:
            im=scs.mosaic(output_params['bands'],tile)       
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



