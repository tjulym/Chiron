for file in `ls imgs`
do
  docker load -i imgs/$file
done
