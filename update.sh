ips="192.168.1.12 192.168.1.13 192.168.1.10 192.168.1.11"

for ip in $ips
do
    rsync -azv --progress info.json itg@$ip:/home/itg/Desktop/inflatingegos
    rsync -azvr --progress client itg@$ip:/home/itg/Desktop/inflatingegos
    ssh itg@$ip 'DISPLAY=:0 xdotool key F5'
    echo "restarted browser for $ip"
done


bennett
wood
sturgeon
miliband
clegg
cameron
farage
