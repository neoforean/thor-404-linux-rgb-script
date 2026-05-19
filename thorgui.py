#!/usr/bin/env python3

import argparse
import json
import sys
import time
from pathlib import Path

import usb.core
import usb.util

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


VENDOR_ID = 0x331A
PRODUCT_ID = 0x501C
REPORT_TYPE_FEATURE = 0x0300

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_KEYMAP_PATH = SCRIPT_DIR / "thor_keymap.json"

# Packets that are always sent in normal mode.
HANDSHAKE_PACKETS = [
    "04020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "04190000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "04130000000000001200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
]

COMMON_PREFIX_PACKETS = [
    "01ff00000000000000100c000000aa55020000ff0000000001100c000000aa55030000ff0000000001100c000000aa55040000ff0000000001100c000000aa55",
    "050000ff0000000001100c000000aa55060000ff0000000000100c000000aa55075affff0000000000100c000000aa55080000ff0000000000100c000000aa55",
    "090000ff0000000001100c030000aa550a0000ff0000000001100c030000aa550b0000ff0000000001100c000000aa550c0000ff0000000001100c000000aa55",
    "0d0000ff0000000001100c000000aa550e0000ff0000000001100c000000aa550f0000ff0000000001100c000000aa55100000ff0000000001100c000000aa55",
    "110000ff0000000001100c000000aa55120000ff0000000001100c000000aa55130000ff0000000001100c000000aa558000000000000000001000000000aa55",
    "00" * 64,
    "00" * 64,
    "00" * 64,
]

# Normal preset framebuffer area.
COMMON_FRAME_PACKETS = [
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
]

FINALIZE_PACKETS = [
    "04020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "04f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
]


EFFECTS = {
    "static":       0x01,
    "single_on":    0x02,
    "single_off":   0x03,
    "stars":        0x04,
    "raindrops":    0x05,
    "colourful":    0x06,
    "breathing":    0x07,
    "neon":         0x08,
    "spectrum":     0x09,
    "rainbow":      0x0A,
    "prismo":       0x0B,
    "circle":       0x0C,
    "escape_beam":  0x0D,
    "shockwave":    0x0E,
    "explosion":    0x0F,
    "escape":       0x10,
    "sine_wave":    0x11,
    "wave":         0x12,
    "shuttle":      0x13,
    "custom":       0x14,
}

DIRECTIONS = {
    "none":  0x00,
    "left":  0x00,
    "right": 0x01,
    "up":    0x02,
    "down":  0x03,
}

DISPLAY_LABELS = {
    "escape": "ESC",
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
    "backtick": "`",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "0": "0",
    "-": "-",
    "=": "=",
    "backspace": "Backspace",
    "tab": "Tab",
    "q": "Q",
    "w": "W",
    "e": "E",
    "r": "R",
    "t": "T",
    "y": "Y",
    "u": "U",
    "i": "I",
    "o": "O",
    "p": "P",
    "[": "[",
    "]": "]",
    "reverse slash": "\\",
    "caps lock": "CapsLk",
    "a": "A",
    "s": "S",
    "d": "D",
    "f": "F",
    "g": "G",
    "h": "H",
    "j": "J",
    "k": "K",
    "l": "L",
    ";": ";",
    "'": "'",
    "enter": "Enter",
    "left shift": "Shift",
    "z": "Z",
    "x": "X",
    "c": "C",
    "v": "V",
    "b": "B",
    "n": "N",
    "m": "M",
    ",": ",",
    "period": ".",
    "slash": "/",
    "right shift": "Shift",
    "up arrow": "↑",
    "left ctrl": "Ctrl",
    "windows": "Win",
    "left alt": "Alt",
    "space": "Space",
    "right alt": "Alt",
    "function": "Fn",
    "menu": "Menu",
    "right ctrl": "Ctrl",
    "left arrow": "←",
    "down arrow": "↓",
    "right arrow": "→",
    "prtsc": "PrtSc",
    "scrllk": "ScrLk",
    "pause": "Pause",
    "insert": "Ins",
    "home": "Home",
    "page up": "PgUp",
    "del": "Del",
    "end": "End",
    "page down": "PgDn",
}


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def validate_rgb(rgb: str) -> str:
    rgb = rgb.lower().strip().replace("#", "")
    if len(rgb) != 6:
        raise ValueError("RGB must be 6 hex chars")
    int(rgb, 16)
    return rgb


def load_keymap(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "keys" not in data or "layout_rows" not in data:
        raise ValueError(f"invalid keymap file: {path}")

    return data


def build_effect_packet(effect_id, rgb, multicolor, brightness, speed, direction):
    brightness = clamp(brightness, 1, 16)
    speed = clamp(speed, 1, 16)

    r = int(rgb[0:2], 16)
    g = int(rgb[2:4], 16)
    b = int(rgb[4:6], 16)

    packet = bytearray(64)
    packet[0] = effect_id
    packet[1] = r
    packet[2] = g
    packet[3] = b
    packet[8] = 0x01 if multicolor else 0x00
    packet[9] = brightness
    packet[10] = speed
    packet[11] = direction
    packet[14] = 0xAA
    packet[15] = 0x55
    return packet.hex()


def build_custom_frame_packets(keymap, key_colors, fallback_rgb):
    """
    Build the custom framebuffer from the per-key map.

    The keyboard captures show 9 row packets in the framebuffer area:
    8 visible rows plus one trailing block. The trailing block remains
    unchanged; the first 8 rows receive per-key RGB data.
    """
    fallback_rgb = validate_rgb(fallback_rgb)
    rows = [bytearray.fromhex("80000000" * 16) for _ in range(9)]

    def pack_for(key_name):
        rgb = validate_rgb(key_colors.get(key_name, fallback_rgb))
        return bytes.fromhex("80" + rgb)

    for key_name, info in keymap["keys"].items():
        primary = info.get("capture")
        blocks = []
        if primary:
            blocks.append(primary)
        blocks.extend(info.get("extra_dwords", []))

        for block in blocks:
            line = block.get("line")
            dword = block.get("dword")
            if line is None or dword is None:
                continue

            row_index = line - 12
            if 0 <= row_index < 8 and 0 <= dword < 16:
                rows[row_index][dword * 4 : (dword + 1) * 4] = pack_for(key_name)

    return [row.hex() for row in rows]


def find_keyboard_interface(dev):
    cfg = dev.get_active_configuration()
    for intf in cfg:
        if (
            intf.bInterfaceClass == 0x03
            and intf.bInterfaceSubClass == 0x01
            and intf.bInterfaceProtocol == 0x01
        ):
            return intf.bInterfaceNumber
    raise RuntimeError("keyboard HID interface not found")


def send_packet(dev, intf, payload_hex):
    payload = bytes.fromhex(payload_hex)
    dev.ctrl_transfer(
        0x21,
        0x09,
        REPORT_TYPE_FEATURE,
        intf,
        payload,
        timeout=1000,
    )
    try:
        dev.ctrl_transfer(
            0xA1,
            0x01,
            REPORT_TYPE_FEATURE,
            intf,
            64,
            timeout=1000,
        )
    except Exception:
        pass


def apply_effect(
    effect,
    rgb,
    multicolor,
    brightness,
    speed,
    direction,
    keymap=None,
    key_colors=None,
):
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise RuntimeError("device not found")

    intf = find_keyboard_interface(dev)

    detached = False
    try:
        if dev.is_kernel_driver_active(intf):
            dev.detach_kernel_driver(intf)
            detached = True
    except Exception:
        pass

    usb.util.claim_interface(dev, intf)

    try:
        packets = []
        packets.extend(HANDSHAKE_PACKETS)
        packets.extend(COMMON_PREFIX_PACKETS)

        if effect == "custom":
            if keymap is None:
                raise RuntimeError("custom preset requires a keymap")
            packets.extend(
                build_custom_frame_packets(
                    keymap=keymap,
                    key_colors=key_colors or {},
                    fallback_rgb=rgb,
                )
            )
        else:
            packets.extend(COMMON_FRAME_PACKETS)

        packets.append(
            build_effect_packet(
                effect_id=EFFECTS[effect],
                rgb=rgb,
                multicolor=multicolor,
                brightness=brightness,
                speed=speed,
                direction=DIRECTIONS[direction],
            )
        )
        packets.extend(FINALIZE_PACKETS)

        for pkt in packets:
            send_packet(dev, intf, pkt)
            time.sleep(0.01)

    finally:
        usb.util.release_interface(dev, intf)
        if detached:
            try:
                dev.attach_kernel_driver(intf)
            except Exception:
                pass


class CustomEditorDialog(QDialog):
    def __init__(self, keymap, colors, fallback_rgb, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Per-Key Lighting")
        self.resize(1228, 430)
        self.setFixedSize(1228, 430)

        self.keymap = keymap
        self.colors = dict(colors)
        self.fallback_rgb = validate_rgb(fallback_rgb)

        self.buttons = {}
        self.selected_keys = set()
        self.selected_rgb = self.fallback_rgb

        root = QVBoxLayout(self)

        info = QLabel(
            "Select keys, choose a color, then apply it to the selection."
        )
        info.setWordWrap(True)
        root.addWidget(info)

        toolbar = QHBoxLayout()

        self.preview = QLabel()
        self.preview.setFixedSize(48, 24)
        self.update_preview(self.selected_rgb)

        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.pick_batch_color)

        self.apply_selection_btn = QPushButton("Apply To Selection")
        self.apply_selection_btn.clicked.connect(self.apply_to_selection)

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)

        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.clicked.connect(self.clear_selection)

        self.fill_btn = QPushButton("Fill All")
        self.fill_btn.clicked.connect(self.fill_all)

        self.clear_btn = QPushButton("Blackout")
        self.clear_btn.clicked.connect(self.clear_all)

        toolbar.addWidget(self.preview)
        toolbar.addWidget(self.color_btn)
        toolbar.addWidget(self.apply_selection_btn)
        toolbar.addSpacing(16)
        toolbar.addWidget(self.select_all_btn)
        toolbar.addWidget(self.clear_selection_btn)
        toolbar.addSpacing(16)
        toolbar.addWidget(self.fill_btn)
        toolbar.addWidget(self.clear_btn)
        toolbar.addStretch(1)

        root.addLayout(toolbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedSize(1206, 296)
        root.addWidget(scroll)

        host = QWidget()
        scroll.setWidget(host)

        outer = QHBoxLayout(host)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(24)

        left_stack = QVBoxLayout()
        left_stack.setSpacing(14)
        outer.addLayout(left_stack, 1)

        right_stack = QVBoxLayout()
        right_stack.setSpacing(10)
        right_stack.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight
        )
        outer.addLayout(right_stack, 0)

        self._build_group_1(left_stack)
        self._build_group_2(left_stack)
        self._build_group_3(right_stack)

        actions = QDialogButtonBox()

        self.save_btn = actions.addButton(
            "Save",
            QDialogButtonBox.ButtonRole.AcceptRole,
        )

        self.cancel_btn = actions.addButton(
            "Cancel",
            QDialogButtonBox.ButtonRole.RejectRole,
        )

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        root.addWidget(actions)

    def _make_button(self, key_name, width, height=40):
        label = DISPLAY_LABELS.get(key_name, key_name)

        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setFixedSize(width, height)
        btn.setFont(QFont("Sans Serif", 8))

        btn.clicked.connect(
            lambda checked=False, k=key_name: self.toggle_key(k)
        )

        self.buttons[key_name] = btn
        self.update_button(key_name)

        return btn

    def _build_group_1(self, parent_layout):
        box = QWidget()
        box.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        row.addWidget(self._make_button("escape", 58))
        row.addSpacing(14)

        for key in ["f1", "f2", "f3", "f4"]:
            row.addWidget(self._make_button(key, 58))

        row.addSpacing(18)

        for key in ["f5", "f6", "f7", "f8"]:
            row.addWidget(self._make_button(key, 58))

        row.addSpacing(18)

        for key in ["f9", "f10", "f11", "f12"]:
            row.addWidget(self._make_button(key, 58))

        parent_layout.addWidget(
            box,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter,
        )

    def _build_group_2(self, parent_layout):
        rows = [
            [("backtick", 64), ("1", 58), ("2", 58), ("3", 58), ("4", 58), ("5", 58), ("6", 58), ("7", 58), ("8", 58), ("9", 58), ("0", 58), ("-", 58), ("=", 58), ("backspace", 122)],
            [("tab", 78), ("q", 58), ("w", 58), ("e", 58), ("r", 58), ("t", 58), ("y", 58), ("u", 58), ("i", 58), ("o", 58), ("p", 58), ("[", 58), ("]", 58), ("reverse slash", 78)],
            [("caps lock", 92), ("a", 58), ("s", 58), ("d", 58), ("f", 58), ("g", 58), ("h", 58), ("j", 58), ("k", 58), ("l", 58), (";", 58), ("'", 58), ("enter", 132)],
            [("left shift", 132), ("z", 58), ("x", 58), ("c", 58), ("v", 58), ("b", 58), ("n", 58), ("m", 58), (",", 58), ("period", 58), ("slash", 58), ("right shift", 122)],
            [("left ctrl", 72), ("windows", 72), ("left alt", 72), ("space", 330), ("right alt", 72), ("function", 72), ("menu", 72), ("right ctrl", 72)],
        ]

        box = QWidget()

        box.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        for row_spec in rows:
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)

            for key_name, width in row_spec:
                row_layout.addWidget(
                    self._make_button(key_name, width)
                )

            row_layout.addStretch(1)
            layout.addLayout(row_layout)

        parent_layout.addWidget(
            box,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter,
        )

    def _build_group_3(self, parent_layout):
        box = QWidget()

        box.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignCenter
        )

        def row(keys):
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)

            for key_name in keys:
                if key_name is None:
                    spacer = QWidget()
                    spacer.setFixedSize(74, 40)

                    spacer.setSizePolicy(
                        QSizePolicy.Policy.Fixed,
                        QSizePolicy.Policy.Fixed,
                    )

                    row_layout.addWidget(spacer)

                else:
                    row_layout.addWidget(
                        self._make_button(key_name, 74)
                    )

            row_layout.addStretch(1)
            return row_layout

        layout.addLayout(row(["prtsc", "scrllk", "pause"]))
        layout.addLayout(row(["insert", "home", "page up"]))
        layout.addLayout(row(["del", "end", "page down"]))
        layout.addLayout(row([None, None, None]))
        layout.addLayout(row([None, "up arrow", None]))
        layout.addLayout(row(["left arrow", "down arrow", "right arrow"]))

        parent_layout.addWidget(
            box,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter,
        )

    def toggle_key(self, key_name):
        btn = self.buttons[key_name]

        if btn.isChecked():
            self.selected_keys.add(key_name)
        else:
            self.selected_keys.discard(key_name)

        self.update_button(key_name)

    def update_preview(self, rgb):
        self.preview.setStyleSheet(
            f"""
            background-color: #{rgb};
            border: 1px solid #555;
            """
        )

    def pick_batch_color(self):
        color = QColorDialog.getColor(
            QColor("#" + self.selected_rgb),
            self,
            "Select Color",
        )

        if not color.isValid():
            return

        self.selected_rgb = color.name()[1:]
        self.update_preview(self.selected_rgb)

    def apply_to_selection(self):
        for key_name in self.selected_keys:
            self.colors[key_name] = self.selected_rgb
            self.update_button(key_name)

    def update_button(self, key_name):
        btn = self.buttons.get(key_name)

        if btn is None:
            return

        rgb = validate_rgb(
            self.colors.get(key_name, self.fallback_rgb)
        )

        r = int(rgb[0:2], 16)
        g = int(rgb[2:4], 16)
        b = int(rgb[4:6], 16)

        luminance = (r * 299 + g * 587 + b * 114) // 1000
        fg = "#000" if luminance > 155 else "#fff"

        selected = key_name in self.selected_keys

        border = "#ffffff" if selected else "#444444"
        border_width = 3 if selected else 1

        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #{rgb};
                color: {fg};
                border: {border_width}px solid {border};
                border-radius: 4px;
                padding: 2px;
            }}

            QPushButton:hover {{
                border-color: #dddddd;
            }}
            """
        )

    def select_all(self):
        for key_name, btn in self.buttons.items():
            btn.setChecked(True)
            self.selected_keys.add(key_name)
            self.update_button(key_name)

    def clear_selection(self):
        for key_name, btn in self.buttons.items():
            btn.setChecked(False)
            self.selected_keys.discard(key_name)
            self.update_button(key_name)

    def fill_all(self):
        for key_name in self.buttons:
            self.colors[key_name] = self.selected_rgb
            self.update_button(key_name)

    def clear_all(self):
        for key_name in self.buttons:
            self.colors[key_name] = "000000"
            self.update_button(key_name)

    def accept(self):
        for key_name in self.buttons:
            self.colors.setdefault(
                key_name,
                self.fallback_rgb,
            )

        super().accept()


class MainWindow(QMainWindow):
    def __init__(self, keymap):
        super().__init__()
        self.keymap = keymap
        self.current_rgb = "ff0000"
        self.custom_colors = {k: self.current_rgb for k in self.keymap["keys"]}
        self.custom_editor = None

        self.setWindowTitle("Thor RGB Controller")
        self.resize(620, 380)

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)

        box = QGroupBox("Lighting")
        outer.addWidget(box)
        form = QFormLayout(box)

        self.effect_combo = QComboBox()
        self.effect_combo.addItems(EFFECTS.keys())
        self.effect_combo.currentTextChanged.connect(self.update_ui_state)
        form.addRow("Effect", self.effect_combo)

        color_row = QHBoxLayout()
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(48, 24)
        self.update_color_preview()

        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.pick_color)

        color_row.addWidget(self.color_preview)
        color_row.addWidget(self.color_btn)
        color_row.addStretch(1)
        form.addRow("Base Color", color_row)

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(1, 16)
        self.brightness_slider.setValue(16)
        self.brightness_label = QLabel("16")
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_label.setText(str(v))
        )
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_label)
        form.addRow("Brightness", brightness_layout)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 16)
        self.speed_slider.setValue(12)
        self.speed_label = QLabel("12")
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(str(v))
        )
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        form.addRow("Speed", speed_layout)

        self.direction_combo = QComboBox()
        self.direction_combo.addItems(DIRECTIONS.keys())
        form.addRow("Direction", self.direction_combo)

        self.multicolor_checkbox = QCheckBox("Enable multicolor mode")
        form.addRow(self.multicolor_checkbox)

        self.custom_btn = QPushButton("Customize per-key lighting")
        self.custom_btn.clicked.connect(self.open_custom_editor)
        form.addRow("Custom", self.custom_btn)

        buttons = QGridLayout()

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply)

        self.static_red_btn = QPushButton("Static Red")
        self.static_red_btn.clicked.connect(lambda: self.quick_apply("ff0000"))

        self.static_green_btn = QPushButton("Static Green")
        self.static_green_btn.clicked.connect(lambda: self.quick_apply("00ff00"))

        self.static_blue_btn = QPushButton("Static Blue")
        self.static_blue_btn.clicked.connect(lambda: self.quick_apply("0000ff"))

        buttons.addWidget(self.apply_btn, 0, 0)
        buttons.addWidget(self.static_red_btn, 0, 1)
        buttons.addWidget(self.static_green_btn, 1, 0)
        buttons.addWidget(self.static_blue_btn, 1, 1)
        outer.addLayout(buttons)

        outer.addStretch(1)
        self.update_ui_state(self.effect_combo.currentText())

    def update_ui_state(self, effect_name):
        is_custom = effect_name == "custom"
        self.custom_btn.setEnabled(is_custom)

    def update_color_preview(self):
        self.color_preview.setStyleSheet(
            f"background-color: #{self.current_rgb}; border: 1px solid #555;"
        )

    def pick_color(self):
        color = QColorDialog.getColor(QColor("#" + self.current_rgb), self)
        if not color.isValid():
            return
        self.current_rgb = color.name()[1:]
        self.update_color_preview()

    def quick_apply(self, rgb):
        self.current_rgb = rgb
        self.update_color_preview()
        self.effect_combo.setCurrentText("static")
        self.multicolor_checkbox.setChecked(False)
        self.apply()

    def open_custom_editor(self):
        if self.effect_combo.currentText() != "custom":
            return

        dlg = CustomEditorDialog(
            keymap=self.keymap,
            colors=self.custom_colors,
            fallback_rgb=self.current_rgb,
            parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.custom_colors = dict(dlg.colors)

    def apply(self):
        effect = self.effect_combo.currentText()

        try:
            apply_effect(
                effect=effect,
                rgb=validate_rgb(self.current_rgb),
                multicolor=self.multicolor_checkbox.isChecked(),
                brightness=self.brightness_slider.value(),
                speed=self.speed_slider.value(),
                direction=self.direction_combo.currentText(),
                keymap=self.keymap if effect == "custom" else None,
                key_colors=self.custom_colors if effect == "custom" else None,
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        QMessageBox.information(self, "Done", "Lighting updated.")


def main():
    parser = argparse.ArgumentParser(description="Thor keyboard RGB controller")
    parser.add_argument(
        "--keymap",
        default=str(DEFAULT_KEYMAP_PATH),
        help="path to thor_keymap.json",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="print available presets and exit",
    )
    parser.add_argument(
        "--effect",
        default=None,
        choices=sorted(EFFECTS.keys()),
        help="initial preset shown in the GUI",
    )
    parser.add_argument("--rgb", default="ff0000", help="RRGGBB")
    parser.add_argument("--brightness", type=int, default=16)
    parser.add_argument("--speed", type=int, default=12)
    parser.add_argument("--multicolor", action="store_true")
    parser.add_argument(
        "--direction",
        default="none",
        choices=["none", "left", "right", "up", "down"],
    )
    args = parser.parse_args()

    keymap = load_keymap(Path(args.keymap))

    if args.list:
        for name in EFFECTS:
            print(name)
        return

    app = QApplication(sys.argv)
    win = MainWindow(keymap)

    if args.effect:
        win.effect_combo.setCurrentText(args.effect)

    win.current_rgb = validate_rgb(args.rgb)
    win.update_color_preview()
    win.brightness_slider.setValue(args.brightness)
    win.speed_slider.setValue(args.speed)
    win.multicolor_checkbox.setChecked(args.multicolor)
    win.direction_combo.setCurrentText(args.direction)

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
