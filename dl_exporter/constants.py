""" CONSTANTS
"""
IS_DEV=True
NOISY=True
LIMIT=None
CHECK_EXT=True


#
# DEFAULT TILE CONFIG
#
TILE_CONFIG={
    'max_processes': 5,
    'tiling': {
        'tilesize': 2**10,
        'resolution': 10,
        'pad': 0
    },
    'search': {
        'products': [],
        'start_datetime': None,
        'end_datetime': None
    }
}
#
# DL_JOBS CONFIG:
#
DL_EXPORTER_CONFIG_PATH='dl_exporter.config.yaml'
DL_EXPORTER_CONFIG_COMMENT="dl_exporter: config"
DL_EXPORTER_CONFIG_EXISTS="dl_exporter.config.yaml exists.  use force=True to overwrite."
DL_EXPORTER_CONFIG_CREATED="dl_exporter.config.yaml created. edit file to change configuration"

