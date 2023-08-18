funcs=("marketdata" "lastpx" "side" "trddate" "volume")
for ((i=0;i<5;i++))
do
    faas-cli deploy -f ${funcs[$i]}-100.yml
done

faas-cli deploy -f yfinance-50.yml