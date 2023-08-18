funcs=("sn-wrap" "mr-wrap" "finra-wrap" "slapp-wrap" "slapp-v-wrap" "sn-wrap-mpk-build" "mr-wrap-mpk-build" "finra-wrap-mpk-build" "slapp-wrap-mpk-build" "slapp-v-wrap-mpk-build")
for ((i=0;i<10;i++))
do
    faas-cli build -f ${funcs[$i]}.yml
done
