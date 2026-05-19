this is a repo in which i experiment with changing my genesis thor 404 tkl keyboard's led lighting through python

> [!NOTE]
> `custom` per-key rgb mode is not coming. though, everything else should work.

---

im using nobara linux but this should be straightforward for any linux distro

### dependencies
1. get pyusb<br>
installed it with sudo because pyusb wouldn't shut up about permissions:
```
sudo python3 -m pip install pyusb
```

### usage
use the interactive terminal interface
```
sudo python3 thorctl.py --tui
```

---

it also accepts arguments
```
sudo python3 thorctl.py --effect static --rgb 0000ff
```


```
sudo python3 thorctl.py --effect rainbow --multicolor --direction down
```

---

list available presets
```
sudo python3 thorctl.py --list
```

### notes

> [!note]
> ### AI disclaimer
> the python script was made in a big part with AI. however, i did use virtualbox with USB passthrough and went into wireshark, captured, and examined the packets being sent. tshark was used to filter the .pcapng files in the `effects` folder. i do know how the main packet is structured. i did confirm which exact packets were essential, and i did confirm that the script works on my keyboard.
