#!/bin/bash

#devices=$(lsusb | grep "National Instruments Corp")
#num_devices=$(echo $devices | wc -l)
#bus_num=$(echo $devices | cut -d " " -f2)
#dev_num=$(echo $devices | cut -d " " -f4 | sed 's/://')
if [[ -f "usrps.txt" ]]; then
    rm usrps.txt
fi

a=$(lsusb |  grep "National Instruments Corp" | awk '{print $2" "$4}' | sed 's/://')

num_devs=$((`echo $a | wc -w` / 2))

for i in $(seq 0 $(($num_devs-1))); do
    bus_n=`echo $a | cut -d " " -f$(( $(($i * $num_devs)) + 1 ))`
    dev_n=`echo $a | cut -d " " -f$(( $(($i * $num_devs)) + 2 ))`

    echo "<hostdev mode='subsystem' type='usb' managed='no'>
    <source>
        <vendor id='0x3923'/>
        <product id='0x7814'/>
        <address bus='$bus_n' device='$dev_n'/>
    </source>
    <address type='usb' bus='0' port='1'/>
</hostdev>,">> ./usrps.txt
done;

#echo $a
#echo $num_devs
