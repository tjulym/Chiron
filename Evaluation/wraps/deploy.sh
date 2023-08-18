funcs=("sn-wrap" "mr-wrap" "finra-wrap" "slapp-wrap" "slapp-v-wrap")
for ((i=0;i<5;i++))
do
    faas-cli deploy -f ${funcs[$i]}.yml
done
