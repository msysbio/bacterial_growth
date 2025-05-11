PROJECT_PATH=$1
MEDIA_PATH=$2
MEDIA_FILE_NAME=$3

## 1) CREATE THE DIRECTORY
## ==========================================================================================================================================================================
cd $PROJECT_PATH
mkdir -p IntermediateFiles/

mkdir -p Data/
mkdir -p Data/media/
rm -f $PROJECT_PATH'IntermediateFiles/listOfMedia.list'

path_origin=$MEDIA_PATH
path_destination=$PROJECT_PATH'Data/media/'
final_file=$path_destination$MEDIA_FILE_NAME

echo $final_file >> $PROJECT_PATH'IntermediateFiles/listOfMedia.list'

cp $path_origin $path_destination
