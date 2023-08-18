funcs=("disk-io" "factorial" "fibonacci" "pbkdf2" "pi" "network-io")
for ((i=0;i<6;i++))
do
    faas-cli build -f ${funcs[$i]}.yml
    faas-cli deploy -f ${funcs[$i]}.yml
done
faas-cli deploy -f pi2.yml
