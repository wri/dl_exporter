import re
import yaml
from pprint import pprint
import dl_exporter.utils as utils
import dl_exporter.printer as printer




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
    config['tilesets'][0]['sources']=[u for u in uris if u]
    if pretty:
        indent=4
    else:
        indent=None
    utils.save_json(config,dest,indent=indent)


def _uri_obj(uri):
    uri=re.sub(r'[\n\r ]$','',uri)
    if uri:
        return { "uris": [uri] }
    return False