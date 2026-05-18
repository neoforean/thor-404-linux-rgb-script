im using nobara linux but this should be straightforward for any linux distro

### dependencies
1. get pyusb<br>
installed it with sudo because pyusb wouldn't shut up about permissions:
```
sudo python3 -m pip install pyusb
```

### usage
format: `sudo python3 thor.py --rgb RRGGBB` (no hashtag)<br>
example:
```
voi@pc:~/Documents/replay$ sudo python3 thor.py --rgb 7700e0
```
> it will hopefully output `[21/21]`
