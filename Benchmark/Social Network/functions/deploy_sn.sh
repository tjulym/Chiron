funcs=("compose-post" "upload-media" "upload-creator" "upload-text" "upload-user-mentions" "upload-unique-id" "compose-and-upload" "post-storage" "upload-user-timeline" "upload-home-timeline")
for ((i=0;i<10;i++))
do
    faas-cli build -f ${funcs[$i]}.yml
    faas-cli deploy -f ${funcs[$i]}.yml
done
