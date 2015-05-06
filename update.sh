
# bennett
# wood
# sturgeon
# miliband
# clegg
# cameron
# farage



ips="$nuc2 $nuc3 $nuc4"

for ip in `echo $ips`
do
    rsync -azv --progress info.json itg@$ip:/home/itg/Desktop/inflatingegos
    rsync -azvr --progress client itg@$ip:/home/itg/Desktop/inflatingegos
    ssh itg@$ip 'export DISPLAY=:0; xdotool key F5; xdotool keydown alt key Tab; sleep 1; xdotool keyup alt; xdotool key F5'
    echo "restarted browser for $ip"

    # scp scripts/load.sh itg@$ip:
done

