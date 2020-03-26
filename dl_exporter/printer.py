from datetime import datetime
from pprint import pprint
import dl_exporter.utils as utils
#
# CONSTANTS
#
TS_FMT="%b %d %Y %H:%M:%S"
INLINE_TYPES=(str,float,int,list)
LINE_LENGTH=75
SEP=', '

#
# METHODS
#
def section(noisy,header,**data):
    first=data.pop('first',False)
    if noisy:
        _section_header(header,first)
        print('timestamp:',_timestamp())
        for k,v in data.items():
            _section_data(k,v)


def csv_header(filename,*columns):
    utils.ensure_dir(filename)
    _write_line(filename,_line(columns),overwrite=True)


def csv_row(filename,*values):
    _write_line(filename,_line(values))


def vspace(n=1):
    print("\n"*n)


def line(char='-',length=LINE_LENGTH):
    print(char*length)


#
# INTERNAL
#
def _section_header(name,first=False):
    if first:
        vspace()
    else:
        vspace(3)
    line()
    print(f'{name.upper()}:')
    line()
    vspace()


def _section_data(key,value):
    if value:
        if isinstance(value,INLINE_TYPES):
            print(f'{key}:',value)
        else:
            print(f'{key}:')
            vspace()
            pprint(value)
            vspace()


def _timestamp():
    return datetime.now().strftime(TS_FMT)


def _line(values):
    values=[_safe_value(v) for v in values]
    return SEP.join(values)


def _safe_value(value):
    if value is None:
        value=''
    return str(value)


def _write_line(path,line,overwrite=False,func=None,**kwargs):
    if overwrite:
        mode='w'
    else:
        mode='a'
    with open(path,mode) as file:
        file.write('{}\n'.format(line))


