
# """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#
# IMPORTANT NOTE:
#
# Please don't use this script!
#
# This bash-script was written to upload files to GEE. However its much faster to generate 
# a manifest ( using `dl_exporter manifest ...` ) and then use 
#
# ```earthengine upload image --manifest ...```
#
#
# """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


#
# CONFIG
#
CREATE=true                             # if "true" create ee-ic, otherwise assume it already exists
DRY_RUN=false                           # if "true" print out commands but do not execute
TEST=true                              # if "true" only execute on head (first 10 images)
USER=projects/wri-datalab               # gee root
IC=TEST-UrbanIndia2                       # name of image_collection
NO_DATA=6                               # if int set gee no-data value
BANDS="lulc,counts,observations"        # comma-sep list of band names
GS_FOLDER=dl-exports/urban_india-2019   # gs-folder with assets
TIME_START="2019-11-01"
TIME_END="2020-01-15"


#
# CONSTANTS
#
GS_HEAD="gs://"
IC_FOLDER="$USER/$IC"
GS_FOLDER="$GS_HEAD$GS_FOLDER"
CREATE_IC_ROOT="earthengine create collection "
LS_ROOT="gsutil ls "
UPLOAD_IM_ROOT="earthengine upload image --asset_id="
TIF_EXT='.tif'
DOT='.'
COLON=':'


#
# CREATE IC
#
if [ "$CREATE" = "true" ]; then
    cmd="$CREATE_IC_ROOT$IC_FOLDER"
    echo $cmd
    if [ "$DRY_RUN" = "false" ]; then
        $cmd
    fi
fi


#
# UPLOAD IMs
#
ls_cmd=$LS_ROOT$GS_FOLDER
if [ "$TEST" = "true" ];then
    ls_cmd="$ls_cmd | head"
fi
echo "$ls_cmd"
eval $ls_cmd | while read -r filepath ; do
    filename=${filepath/$GS_FOLDER/""}
    filename=${filename/$TIF_EXT/""}
    filename=${filename//$DOT/"d"}    
    filename=${filename//$COLON/"_"}
    cmd="$UPLOAD_IM_ROOT$USER/$IC$filename"
    if [[ "$NO_DATA" =~ ^[0-9]+$ ]];then
        cmd="$cmd --nodata_value=$NO_DATA"
    fi
    cmd="$cmd --bands=$BANDS --time_start=$TIME_START --time_end=$TIME_END $filepath"
    echo $cmd
    if [ "$DRY_RUN" = "false" ]; then
        $cmd
    fi
done



