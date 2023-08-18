funcs=("disk-io" "factorial" "fibonacci" "pbkdf2" "pi" "network-io")
for ((i=0;i<6;i++))
do
    faas-cli remove -f ${funcs[$i]}.yml
done
