from __future__ import print_function
import os.path
import warnings
import yaml
import dl_exporter.constants as c
from copy import deepcopy


warnings.filterwarnings("ignore", category=DeprecationWarning)
#
# DEFALUTS 
#
_DEFAULTS={
    'is_dev': c.IS_DEV,
    'noisy': c.NOISY,
    'limit': c.LIMIT,
    'check_ext': c.CHECK_EXT,
    'export_config': c.EXPORT_CONFIG
}
_RASIE='__RAISE'

#
# LOAD CONFIG
#
CONFIG=deepcopy(_DEFAULTS)
print(c.DL_EXPORTER_CONFIG_PATH)
if os.path.exists(c.DL_EXPORTER_CONFIG_PATH):
    CONFIG.update(yaml.safe_load(open(c.DL_EXPORTER_CONFIG_PATH)))


def get(key,default=_RASIE):
    """ get value
    """
    if default==_RASIE:
        return CONFIG[key]
    else:
        return CONFIG.get(key,default)


def generate(
        is_dev=c.IS_DEV,
        noisy=c.NOISY,
        limit=c.LIMIT,
        check_ext=c.CHECK_EXT,
        export_config=c.EXPORT_CONFIG,
        force=False):
    """ generate config file
    """
    config={
        'is_dev': _truthy(is_dev),
        'noisy': _truthy(noisy),
        'limit': limit,
        'check_ext': _truthy(check_ext),
        'export_config': export_config,
    }
    if not force and os.path.exists(c.DL_EXPORTER_CONFIG_PATH):
        _log(c.DL_EXPORTER_CONFIG_EXISTS,True,level="ERROR")
    else:
        with open(c.DL_EXPORTER_CONFIG_PATH,'w+') as file:
            file.write("# {}\n".format(c.DL_EXPORTER_CONFIG_COMMENT))
            file.write(yaml.safe_dump(config, default_flow_style=False))
        _log(c.DL_EXPORTER_CONFIG_CREATED,noisy)


#
# INTERNAL
#
_FALSEY=['false','none','no','null','f','n','0']
def _truthy(value):
    """ duplicate of dl_jobs.helpers.truthy
    """
    if isinstance(value,bool) or isinstance(value,int) or (value is None):
        return value
    elif is_str(value):
        value=value.lower()
        return value not in FALSEY
    else:
        raise ValueError('truthy: value must be str,int,bool')


def _to_arr(value):
    if isinstance(value,str):
        return value.split(',')
    else:
        return value


def _log(msg,noisy,level='INFO'):
    if noisy:
        print("[{}] DL_EXPORTER: {}".format(level,msg))



