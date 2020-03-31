import re
import yaml
from pprint import pprint
from datetime import datetime
import dl_exporter.utils as utils
import dl_exporter.printer as printer

ASSET_PREFIX='projects/earthengine-legacy/assets'


def generate_manifest(config,uris,dest,pretty=False,noisy=True,limit=None):
    printer.section(
        noisy,        
        'generate manifest',
        config=config,
        uris=uris,
        output_file=dest,
        pretty=pretty,
        limit=limit)   
    config=utils.read_yaml(config)
    if re.search('.p$',uris):
        uris=utils.read_pickle(uris)
    else:
        uris=utils.read_lines(uris)
    uris=uris[:limit]
    printer.section(
        noisy,        
        'data',
        nb_uris=len(uris),
        first_uri=uris[0],
        config=config)
    uris=[_uri_obj(u) for u in uris]
    config['name']=_prefixed_name(config['name'])
    config['tilesets'][0]['sources']=[u for u in uris if u]
    config['start_time']=_timestamp_obj(config.get('start_time'))
    config['end_time']=_timestamp_obj(config.get('end_time'))
    if pretty:
        indent=4
    else:
        indent=None
    utils.save_json(config,dest,indent=indent)


def _prefixed_name(name):
    if not re.search(ASSET_PREFIX,name):
        name=f'{ASSET_PREFIX}/{name}'
    return name
    

def _uri_obj(uri):
    uri=re.sub(r'[\n\r ]$','',uri)
    if uri:
        return { "uris": [uri] }
    return False


def _timestamp_obj(timestamp):
    if isinstance(timestamp,int):
        timestamp={ "seconds": timestamp }
    elif isinstance(timestamp,str):
        timestamp={ "seconds": _to_timestamp(timestamp) }
    return timestamp


def _to_int(dstr):
    return int(re.sub('^0','',str(dstr)))


def _to_datetime(date):
    y,m,d=[_to_int(p) for p in date.split('-')]
    return datetime(y,m,d)


def _to_timestamp(date):
    date=_to_datetime(date)
    return int((date - datetime.utcfromtimestamp(0)).total_seconds())


