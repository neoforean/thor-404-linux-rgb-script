## Thor 404 TKL controller for Linux
Supports custom per-key configuration, different lighting modes, and user-defined colours.

> <img width="643" height="442" alt="image" src="https://github.com/user-attachments/assets/a2aa4736-8163-4083-8f8a-1185aa3984d2" />

Custom mode:
> <img width="1249" height="489" alt="image" src="https://github.com/user-attachments/assets/66305902-1c92-4a38-81a7-20f138edd5fc" />

---

### dependencies
1. get pyusb and pyqt6<br>
installed it with sudo because pyusb wouldn't shut up about permissions:
```
sudo python3 -m pip install pyqt6 pyusb
```

### usage
1. download `thor_keymap.json` and `thorgui.py`

2. put them in the same folder

3. use the gui
```
sudo python3 thorgui.py
```

---

it also accepts arguments (press apply in gui to apply)
```
sudo python3 thorgui.py --effect static --rgb 0000ff
```


```
sudo python3 thorgui.py --effect rainbow --multicolor --direction down
```

---

list available presets
```
sudo python3 thorgui.py --list
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

### notes

> [!note]
> ### AI disclaimer
> the python script was made in a big part with AI. however, i did use virtualbox with USB passthrough and went into wireshark, captured, and examined the packets being sent. tshark was used to filter the .pcapng files in the [Resources](https://github.com/neoforean/thor-404-linux-rgb-script/tree/resources)' `*_txt` folders. only the essential packets are being sent, and the script is confirmed to be working on my hardware.

> [!tip]
> ### Resources
> previous research (offsets, notes, etc.) can be found in the [Resources](https://github.com/neoforean/thor-404-linux-rgb-script/tree/resources) branch 
