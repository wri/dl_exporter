#### DL EXPORTER

CLI for exporting data from DescartesLabs to GCS. _TODO: add import to GEE functionality_

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

The CLI requires a GeoJSON file, and a config file. The GeoJSON file should contain the geometry you want to export. I _think_ it needs to be a simple geometry (containing a single feature).

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

### RUN

Running `$ dl_exporter run ...` will export files from DescartesLabs to GCS.  Additionally it can create two local files (config dependent)L

* `output_file`: a pickled list of gcs files
* `csv_file`: a csv containing tile_key, gcs_path, error_msg, etc...

##### CLI HELP

```bash
Usage: dl_exporter [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config  generate config file: pass kwargs (ie $`dl_exporter config...
  echo    print config: `$dl_exporter echo <geojson-file> (<config-file>)`
  run     run export: `$dl_exporter run <geojson-file> (<config-file>)
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

_NOTE: file extensions ('geojson','yaml') are optional_

```bash
# check config
 dl_exporter echo kerala_dev.geojson

 # dev run (fetch tiles, but skip export)
dl_exporter run india --dev true 

 # trial run (limit the number of exports)
dl_exporter run india --dev false --limit 4

 # full run
dl_exporter run india --dev false

 # 2016 full run
dl_exporter run india dl_exporter.2016.config.yaml --dev false
```



