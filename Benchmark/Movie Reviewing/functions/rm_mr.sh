funcs=("compose-review" "upload-user-id" "upload-movie-id" "mr-upload-text" "mr-upload-unique-id" "mr-compose-and-upload" "store-review" "upload-user-review" "upload-movie-review")
for ((i=0;i<9;i++))
do
    faas-cli remove -f ${funcs[$i]}.yml
done
