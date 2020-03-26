from datetime import datetime
from pprint import pprint
#
# CONSTANTS
#
TS_FMT="%b %d %Y %H:%M:%S"
INLINE_TYPES=(str,float,int,list)
LINE_LENGTH=75


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
    print(columns)
    pass


def csv_row(filename,*values):
    print(values)
    pass


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




