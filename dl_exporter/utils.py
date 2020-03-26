from __future__ import print_function
import os
from pathlib import Path, PurePath
import re
import pickle
from datetime import datetime
import functools
import operator
import minigeo
import dl_exporter.config as c
#
# FILES
#
def ensure_dir(path):
    Path(PurePath(path).parent).mkdir(
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





