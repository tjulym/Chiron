funcs=("disk-io" "factorial" "fibonacci" "pbkdf2" "pi" "pi2" "network-io")
for ((i=0;i<7;i++))
do
    faas-cli remove -f ${funcs[$i]}.yml
done
