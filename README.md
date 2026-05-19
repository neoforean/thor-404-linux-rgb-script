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

### technical
the main packet's offsets:
| Offset | Meaning           |
| ------ | ----------------- |
| 0x00   | effect ID         |
| 0x01   | red               |
| 0x02   | green             |
| 0x03   | blue              |
| 0x08   | multicolor toggle |
| 0x09   | brightness        |
| 0x0A   | speed             |
| 0x0B   | direction         |
| 0x0E   | 0xAA              |
| 0x0F   | 0x55              |

> **example `120000ff00000000011002010000aa55`**
> | Field      | Value            |
> | ---------- | ---------------- |
> | effect     | `0x12` = wave    |
> | RGB        | `0000ff` = blue  |
> | multicolor | `0x01` = enabled |
> | brightness | `0x10` = 16      |
> | speed      | `0x02` = 2       |
> | direction  | `0x01` = right   |

there is a `Custom` preset which allows for per-key lighting, but for now i'm happy with this controller


### notes

> [!note]
> ### AI disclaimer
> the python script was made in a big part with AI. however, i did use virtualbox with USB passthrough and went into wireshark, captured, and examined the packets being sent. tshark was used to filter the .pcapng files in the `effects` folder. i do know how the main packet is structured. i did confirm which exact packets were essential, and i did confirm that the script works on my keyboard.

> [!tip]
> ### Resources
> previous research (offsets, notes, etc.) can be found in the [Resources](https://github.com/neoforean/thor-404-linux-rgb-script/tree/resources) branch 
