YML_FILE_TMP=$1
YML_FILE=$2

sed 's/description:/## description:/' $YML_FILE_TMP | \
    sed 's/description_2:/## description_2:/' | \
    sed 's/STUDY:/\n\nSTUDY:/' | \
    sed 's/BIOLOGICAL_REPLICATE:/\n\nBIOLOGICAL_REPLICATE:/' | \
    sed 's/PERTURBATION:/\n\nPERTURBATION:/' > $YML_FILE

rm $YML_FILE_TMP