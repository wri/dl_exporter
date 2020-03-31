from __future__ import print_function
import os
from pathlib import Path, PurePath
import re
import pickle
import json
import geojson
import yaml
from datetime import datetime
import functools
import operator
import minigeo
import dl_exporter.config as c
#
# FILES
#
def ensure_dir(path=None,directory=None):
    if path:
        directory=PurePath(path).parent
    Path(directory).mkdir(
            parents=True,
            exist_ok=True)


def save_pickle(obj,path,mkdirs=True):
    """ save object to pickle file
    """ 
    if mkdirs:
        ensure_dir(path)
    with open(path,'wb') as file:
        pickle.dump(obj,file,protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(path):
    """ read pickle file
    """    
    with open(path,'rb') as file:
        obj=pickle.load(file)
    return obj


def read_yaml(path,*key_path):
    """ read yaml file
    path<str>: path to yaml file
    *key_path: keys to go to in object
    """    
    with open(path,'rb') as file:
        obj=yaml.safe_load(file)
    for k in key_path:
        obj=obj[k]
    return obj


def read_json(path,*key_path):
    """ read json file
    path<str>: path to json file
    *key_path: keys to go to in object
    """    
    with open(path,'rb') as file:
        obj=json.load(f)
    for k in key_path:
        obj=obj[k]
    return obj


def save_json(obj,path,indent=4,sort_keys=False,mkdirs=True):
    """ save object to json file
    """ 
    if mkdirs:
        ensure_dir(path)
    with open(path,'w') as file:
        json.dump(obj,file,indent=indent,sort_keys=sort_keys)


def read_geojson(path,*key_path):
    """ read geojson file
    path<str>: path to geojson file
    *key_path: keys to go to in object
    """    
    with open(path,'rb') as file:
        obj=geojson.load(f)
    for k in key_path:
        obj=obj[k]
    return obj


def read_lines(path,*key_path):
    """ read yaml file
    path<str>: path to yaml file
    *key_path: keys to go to in object
    """    
    with open(path,'r') as file:
        obj=[l for l in file]
    return obj

#
# Timer
#
TS_FMT="%b %d %Y %H:%M:%S"
class Timer(object):

    def __init__(self,ts_fmt=TS_FMT):
        self.ts_fmt=TS_FMT
        self._start_time=None
        self._end_time=None


    def start(self):
        if not self._start_time:
            self._start_time=datetime.now()
        return self._start_time.strftime(self.ts_fmt)


    def stop(self):
        if not self._end_time:
            self._end_time=datetime.now()
        return self._end_time.strftime(self.ts_fmt)


    def duration(self):
        delta=self._end_time-self._start_time
        return str(delta).split('.')[0]
        

    def now(self):
        return datetime.now().strftime(self.ts_fmt)



#
# GEO
#
def image_profile(im,aoi):
    return minigeo.build_profile(
        crs=aoi.crs, 
        transform=minigeo.gdaltrans_to_affine(aoi.geotrans), 
        size=aoi.tilesize, 
        count=im.shape[0], 
        nodata=None, 
        dtype='uint8', 
        compress='lzw')





