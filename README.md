#### DL EXPORTER

CLI for exporting data from DescartesLabs to GCS. Additionally `dl_exporter manifest ...` will generate a GEE Manifest to ingest your exports into Google Earth Engine.

1. [Install](#install)
2. [Project Setup](#setup)
3. [Export Tiles](#run)
4. [Google Earth Engine Imports](#gee)

---

<a name="install"/>

### INSTALL

```bash
git clone https://github.com/wri/dl_exporter.git
pushd dl_exporter
pip install -e .
popd
```

---

<a name="setup"/>

### PROJECT SETUP

The CLI requires a _GeoJSON_ file or _pickled-tile-keys_, and a config file. 

The GeoJSON file should contain the geometry you want to export. I _think_ it needs to be a simple geometry (containing a single feature). The _pickled-tile-keys_ file must have the ext '.p', this is how the CLI knows to treat it as a tile list rather than a geometry.

There are two types of config files:

1. project config file: this contains both the cli-config and the default export-config
2. (optional) additional export config files.

##### PROJECT CONFIG

Create the project config ( `dl_exporter.config.yaml` ) by running
```bash
dl_exporter config
```

This file must be updated to contain relevant project information.  Here is an example config:

```yaml
# dl_exporter: config
check_ext: true
export_config:
  output_file: true
  output_dir: out
  csv_file: true
  csv_dir: log
  max_processes: 16
  output:
    bands: lulc counts observations
    bucket: dl-exports
    folder: urban_india-2019
    prefix: wri:ulu-india
    suffix: 2019
  search:
    products: ['wri:ulu-india']
    limit: 200
    start_datetime: '2019-11-01'
    end_datetime: '2020-01-15'
  tiling:
    pad: 0
    resolution: 5
    tilesize: 8192
is_dev: true
limit: null
noisy: true
```

##### ADDITIONAL CONFIGS

You may run also include additional export config files. Additional config files only include the `export_config` data.  For example, one might create another config file called `dl_exporter.2016.config.yaml`:

```yaml
output_file: true
output_dir: out
csv_file: true
csv_dir: log
max_processes: 16
output:
  bands: lulc counts observations
  bucket: dl-exports
  folder: urban_india-2016
  prefix: wri:ulu-india
  suffix: 2016
search:
  products: ['wri:ulu-india']
  start_datetime: '2016-11-01'
  end_datetime: '2017-01-15'
tiling:
  pad: 0
  resolution: 5
  tilesize: 8192
```


---

<a name="run"/>

### EXPORT TILES

Running `$ dl_exporter run ...` will export files from DescartesLabs to GCS.  Additionally it (optionally) creates two local files:

* `output_file`: a pickled list of gcs files
* `csv_file`: a csv containing tile_key, gcs_path, error_msg, etc...

##### CLI HELP

```bash
Usage: dl_exporter [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config  generate config file: pass kwargs (ie $`dl_exporter config...
  echo    print config: `$dl_exporter echo <geojson-file/tile-pickle> (<config-file>)`
  run     run export: `$dl_exporter run <geojson-file/tile-pickle> (<config-file>)
```

```bash
Usage: dl_exporter run [OPTIONS] GEOMETRY [CONFIG]

  run export: `$dl_exporter run <geojson-file> (<config-file>)`

Options:
  --dev BOOLEAN        <bool> run without performing export
  --noisy BOOLEAN      <bool> be noisy
  --limit INTEGER      <int> limit number of exports
  --check_ext BOOLEAN  <bool> if true add `.yaml` if not included in config
                       arg
  --help               Show this message and exit.
```

##### EXAMPLES

NOTE: file extensions ('geojson','yaml') are optional. However if you have a _pickled-tile-keys_ file as the first argument you must include the '.p' ext.


```bash
# check config (including the .geojson ext)
 dl_exporter echo kerala_dev.geojson

 # this works too!
 dl_exporter echo kerala_dev

 # dev run (fetch tiles, but skip export)
dl_exporter run india --dev true 

 # trial run (limit the number of exports)
dl_exporter run india --dev false --limit 4

 # full run
dl_exporter run india --dev false

 # full run from tile-list rather than geometry
dl_exporter run india_tile_keys.p --dev false

 # 2016 full run
dl_exporter run india dl_exporter.2016.config.yaml --dev false
```

---

<a name="gee"/>

### GOOGLE EARTH ENGINE IMPORTS

_TODO: UPDATE README TO SHOW HOW TO WORK ACROSS EPSG ZONES_

1. _create image collection_
2. _[generate multi-epsg-tilesets.json](https://github.com/wri/dl_exporter/blob/master/nb_archive/GenerateTilesetsJSON.ipynb) file
3. _use multi-epsg-tilesets.json to generate manifests for each epsg-specific-tileset_
4. _run `earthengine upload` for each manifest file_


The GEE CLI allow you to import a list to tifs into a single mosaic `ee.Image` asset using `earthengine upload image --manifest <manifest-json-file>`.  A detailed description is given [here](https://developers.google.com/earth-engine/image_manifest).

`dl_exporter manifest ...`  makes generating the manifest-json file easy. 

This command requires 2 different setup files:

1. manifest-config-file <yaml>: contains all the config except for the uris
2. uris-file <pickled-list or line-sep-text-file>: list of uris

This example usage should be somewhat self explanatory 

```bash
# generate gee-manifest 
dl_exporter manifiest manifest_config.json gcs_uris.txt output_gee_manifest.json

# upload-to-gee
earthengine upload image --manifiest output_gee_manifest.json
```

Generating the uris-file can be done in many ways. One simple way is:

```bash
gsutil ls gs://bucket/path/to/folder/*.tif > gcs_uris.txt
```

The manifest-config file is simply a yaml version of the file described [here](https://developers.google.com/earth-engine/image_manifest#manifest_field_definitions). Here is an example:

```yaml
# example-config
name: projects/wri-datalab/test_im1112
tilesets:
- data_type: UINT8
bands:
- id: lulc
  tileset_band_index: 0
  pyramidingPolicy: MODE
- id: counts
  tileset_band_index: 1
  pyramidingPolicy: MODE
- id: observations
  tileset_band_index: 2
  pyramidingPolicy: MODE
missing_data:
  values:
  - 6
pyramiding_policy: MODE
start_time: '2019-11-01'
end_time: '2020-01-15'
properties:
  'band_description': >-
    lulc - urban land use category 
    counts: - the number of observations with the predicted lulc category 
    observations:  the total number of observations
  '0': Open Space
  '1': Non-Residential
  '2': Residential Atomistic
  '3': Residential Informal Subdivision
  '4': Residential Formal Subdivision
  '5': Residential Housing Project
  '6': No Data
```


A few notes:

1. `name`:  `dl_exporter manifest` will automatically prepend the name with `projects/earthengine-legacy/assets` if it is not already included.
2. `start/end_time`: you can pass 'yyyy-mm-dd' strings, or seconds-since-1970-ints (rather than the python-dict containing seconds) if you prefer.


#####  MANIFEST CLI HELP

```bash
Usage: dl_exporter manifest [OPTIONS] CONFIG URIS DEST

  generate gee-manifest: `$dl_exporter manifiest <manifiest-config-file>
  <uris-file> <destination>`

Options:
  --pretty BOOLEAN  <bool> if pretty indent json file
  --noisy BOOLEAN   <bool> be noisy
  --limit INTEGER   <int> limit number of uris for dev
  --help            Show this message and exit.
```
