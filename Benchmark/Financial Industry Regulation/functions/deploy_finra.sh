funcs=("marketdata" "lastpx" "side" "trddate" "volume" "margin-balance" "yfinance")
for ((i=0;i<7;i++))
do
    faas-cli build -f ${funcs[$i]}.yml
    faas-cli deploy -f ${funcs[$i]}.yml
done
