funcs=("network-io-java" "factorial-java" "disk-io-java" "fibonacci-java" "pi-java" "pbkdf2-java" "slapp-java" "marketdata-java" "lastpx-java" "side-java" "trddate-java" "volume-java" "margin-balance-java" "finra5-java")
for ((i=0;i<14;i++))
do
    faas-cli build -f ${funcs[$i]}.yml
    faas-cli deploy -f ${funcs[$i]}.yml
done
