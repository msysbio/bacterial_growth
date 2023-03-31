YML_FILE_TMP=$1
YML_FILE=$2

sed 's/description:/## description:/' $YML_FILE_TMP | \
    sed 's/STUDY:/\n\nSTUDY:/' | \
    sed 's/EXPERIMENT:/\n\nEXPERIMENT:/' | \
    sed 's/PERTURBATION:/\n\PERTURBATION:/' | \
    sed 's/FILES:/\n\nFILES:/' > $YML_FILE

rm $YML_FILE_TMP