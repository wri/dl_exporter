from __future__ import print_function
import re
import yaml
import dl_exporter.config as c
from pprint import pprint
#
# DEFAULTS
#
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
LIMIT=c.get('limit')



#
# MAIN
#
def run(job,dev=IS_DEV,noisy=NOISY,limit=LIMIT,check_ext=True):
    pass


def echo(job,check_ext=True):
    job=_load_job(job,check_ext=True)
    pprint(job)




#
# INTERNAL
#
def _load_job(job,check_ext):
    if check_ext and (not re.search('.yaml$',job)):
        job=f'{job}.yaml'
    return yaml.safe_load(open(job))