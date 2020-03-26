from datetime import datetime
from pprint import pprint
#
# CONSTANTS
#
TS_FMT="%b %d %Y %H:%M:%S"
INLINE_TYPES=(str,float,int,list)



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


#
# INTERNAL
#
def _section_header(name,first=False):
    if first:
        print('\n'*1)
    else:
        print('\n'*4)
    print('-'*50)
    print(f'{name.upper()}:')
    print('-'*50)
    print()


def _section_data(key,value):
    if value:
        if isinstance(value,INLINE_TYPES):
            print(f'{key}:',value)
        else:
            print(f'{key}:')
            print()
            pprint(value)
            print()


def _timestamp():
    return datetime.now().strftime(TS_FMT)




