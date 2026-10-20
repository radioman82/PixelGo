import uuid
import json

root_uuid = "103be8ea-3298-48d4-9175-9d8bc739cda4"
proj_name = "pixelgo_gamepad"

def gen_uuid():
    return str(uuid.uuid4())

# 1. Update kicad_pro
pro_data = {
  "board": {
    "design_settings": {
      "defaults": {},
      "diff_pair_dimensions": [],
      "drc_exclusions": [],
      "rules": {},
      "track_widths": [],
      "via_dimensions": []
    }
  },
  "boards": [],
  "libraries": {
    "pinned_footprint_libs": [],
    "pinned_symbol_libs": []
  },
  "meta": {
    "filename": "pixelgo_gamepad.kicad_pro",
    "version": 1
  },
  "net_settings": {
    "classes": [],
    "meta": {
      "version": 0
    }
  },
  "pcbnew": {
    "page_layout_descr_file": ""
  },
  "sheets": [
    [
      root_uuid,
      "Root"
    ]
  ],
  "text_variables": {}
}

with open(r"d:\Arduino_portable\Projekte\retrogo\pixelgo\kicad\pixelgo_gamepad\pixelgo_gamepad.kicad_pro", "w", encoding="utf-8") as f:
    json.dump(pro_data, f, indent=2)

# 2. Build kicad_sch
sch_text = f"""(kicad_sch
\t(version 20250901)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{root_uuid}")
\t(paper "A4")
\t(title_block
\t\t(title "PixelGo-01 Handheld Gamepad")
\t\t(date "2026-10-20")
\t\t(rev "v1.0")
\t\t(company "PixelGo Handheld DIY")
\t\t(comment 1 "10 Tactile Switches + ESP32-S3 Interface Header")
\t\t(comment 2 "Abmessungen: 91 x 70 mm (Passend zum 3D-Druckgehaeuse)")
\t)
\t(lib_symbols
\t\t(symbol "Connector_Generic:Conn_01x12"
\t\t\t(pin_names (offset 1.016))
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(property "Reference" "J" (at 0 15.24 0) (effects (font (size 1.27 1.27))))
\t\t\t(property "Value" "Conn_01x12" (at 0 -17.78 0) (effects (font (size 1.27 1.27))))
\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t\t(symbol "Conn_01x12_1_1"
\t\t\t\t(rectangle (start -1.27 15.24) (end 1.27 -15.24) (stroke (width 0.254)) (fill (type background)))
\t\t\t\t(pin passive line (at -5.08 13.97 0) (length 3.81) (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 11.43 0) (length 3.81) (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 8.89 0) (length 3.81) (name "Pin_3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 6.35 0) (length 3.81) (name "Pin_4" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 3.81 0) (length 3.81) (name "Pin_5" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 1.27 0) (length 3.81) (name "Pin_6" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 -1.27 0) (length 3.81) (name "Pin_7" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 -3.81 0) (length 3.81) (name "Pin_8" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 -6.35 0) (length 3.81) (name "Pin_9" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 -8.89 0) (length 3.81) (name "Pin_10" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 -11.43 0) (length 3.81) (name "Pin_11" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at -5.08 -13.97 0) (length 3.81) (name "Pin_12" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
\t\t\t)
\t\t)
\t\t(symbol "Switch:SW_Push"
\t\t\t(pin_numbers (offset 1.016) (hide yes))
\t\t\t(pin_names (offset 0) (hide yes))
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(property "Reference" "SW" (at 1.27 2.54 0) (effects (font (size 1.27 1.27))))
\t\t\t(property "Value" "SW_Push" (at 1.27 -2.54 0) (effects (font (size 1.27 1.27))))
\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t\t(symbol "SW_Push_0_1"
\t\t\t\t(circle (center -2.032 0) (radius 0.508) (stroke (width 0)) (fill (type none)))
\t\t\t\t(circle (center 2.032 0) (radius 0.508) (stroke (width 0)) (fill (type none)))
\t\t\t\t(polyline (pts (xy -1.524 1.27) (xy 1.524 1.27)) (stroke (width 0.254)))
\t\t\t\t(polyline (pts (xy 0 1.27) (xy 0 3.048)) (stroke (width 0.254)))
\t\t\t)
\t\t\t(symbol "SW_Push_1_1"
\t\t\t\t(pin passive line (at -5.08 0 0) (length 2.54) (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at 5.08 0 180) (length 2.54) (name "2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
\t\t\t)
\t\t)
\t\t(symbol "power:GND"
\t\t\t(pin_names (offset 0) (hide yes))
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t\t(property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t\t(symbol "GND_0_1"
\t\t\t\t(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0)) (fill (type outline)))
\t\t\t)
\t\t\t(symbol "GND_1_1"
\t\t\t\t(pin power_in line (at 0 0 270) (length 0) (hide yes) (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
\t\t\t)
\t\t)
\t)
"""

j1_uuid = gen_uuid()
sch_text += f"""\t(symbol
\t\t(lib_id "Connector_Generic:Conn_01x12")
\t\t(at 50.8 100.0 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{j1_uuid}")
\t\t(property "Reference" "J1" (at 50.8 81.28 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "Conn_01x12_ESP32" (at 50.8 119.38 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical" (at 50.8 100.0 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(pin "3" (uuid "{gen_uuid()}"))
\t\t(pin "4" (uuid "{gen_uuid()}"))
\t\t(pin "5" (uuid "{gen_uuid()}"))
\t\t(pin "6" (uuid "{gen_uuid()}"))
\t\t(pin "7" (uuid "{gen_uuid()}"))
\t\t(pin "8" (uuid "{gen_uuid()}"))
\t\t(pin "9" (uuid "{gen_uuid()}"))
\t\t(pin "10" (uuid "{gen_uuid()}"))
\t\t(pin "11" (uuid "{gen_uuid()}"))
\t\t(pin "12" (uuid "{gen_uuid()}"))
\t\t(instances
\t\t\t(project "{proj_name}"
\t\t\t\t(path "/{root_uuid}"
\t\t\t\t\t(reference "J1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
"""

j1_signals = [
    (1,  "GND",        13.97, True),
    (2,  "BTN_LEFT",   11.43, False),
    (3,  "BTN_UP",      8.89, False),
    (4,  "BTN_DOWN",    6.35, False),
    (5,  "BTN_RIGHT",   3.81, False),
    (6,  "BTN_SELECT",  1.27, False),
    (7,  "BTN_START",  -1.27, False),
    (8,  "BTN_Y",      -3.81, False),
    (9,  "BTN_B",      -6.35, False),
    (10, "BTN_X",      -8.89, False),
    (11, "BTN_A",     -11.43, False),
    (12, "GND",       -13.97, True)
]

for pin_num, net_name, y_off, is_gnd in j1_signals:
    py = round(100.0 - y_off, 2)
    sch_text += f"\t(wire (pts (xy 45.72 {py}) (xy 40.64 {py})) (stroke (width 0)) (uuid \"{gen_uuid()}\"))\n"
    if is_gnd:
        pwr_uuid = gen_uuid()
        sch_text += f"""\t(symbol
\t\t(lib_id "power:GND")
\t\t(at 40.64 {py} 0)
\t\t(unit 1)
\t\t(uuid "{pwr_uuid}")
\t\t(property "Reference" "#PWR" (at 40.64 {py-2} 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Value" "GND" (at 40.64 {py+2} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at 40.64 {py} 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(instances
\t\t\t(project "{proj_name}"
\t\t\t\t(path "/{root_uuid}"
\t\t\t\t\t(reference "#PWR")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
"""
    else:
        sch_text += f"\t(label \"{net_name}\" (at 40.64 {py} 180) (fields_autoplaced yes) (effects (font (size 1.27 1.27))) (uuid \"{gen_uuid()}\"))\n"

switches = [
    ("SW3",  "BTN_LEFT",   "LEFT (GPIO 45)",  120.0,  50.0),
    ("SW1",  "BTN_UP",     "UP (GPIO 6)",     120.0,  65.0),
    ("SW2",  "BTN_DOWN",   "DOWN (GPIO 0)",   120.0,  80.0),
    ("SW4",  "BTN_RIGHT",  "RIGHT (GPIO 7)",  120.0,  95.0),
    ("SW9",  "BTN_SELECT", "SELECT (GPIO 16)",120.0, 110.0),
    ("SW10", "BTN_START",  "START (GPIO 17)", 120.0, 125.0),
    ("SW8",  "BTN_Y",      "Y (GPIO 18)",     120.0, 140.0),
    ("SW6",  "BTN_B",      "B (GPIO 5)",      120.0, 155.0),
    ("SW7",  "BTN_X",      "X (GPIO 8)",      120.0, 170.0),
    ("SW5",  "BTN_A",      "A (GPIO 15)",     120.0, 185.0),
]

for ref, net_name, val_label, sx, sy in switches:
    sw_u = gen_uuid()
    pwr_u = gen_uuid()
    sch_text += f"""\t(symbol
\t\t(lib_id "Switch:SW_Push")
\t\t(at {sx} {sy} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{sw_u}")
\t\t(property "Reference" "{ref}" (at {sx} {sy-3.81} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "{val_label}" (at {sx} {sy+3.81} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Button_Switch_THT:SW_PUSH_6mm" (at {sx} {sy} 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances
\t\t\t(project "{proj_name}"
\t\t\t\t(path "/{root_uuid}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
\t(wire (pts (xy {sx-5.08} {sy}) (xy {sx-10.16} {sy})) (stroke (width 0)) (uuid \"{gen_uuid()}\"))
\t(label \"{net_name}\" (at {sx-10.16} {sy} 180) (fields_autoplaced yes) (effects (font (size 1.27 1.27))) (uuid \"{gen_uuid()}\"))
\t(wire (pts (xy {sx+5.08} {sy}) (xy {sx+10.16} {sy})) (stroke (width 0)) (uuid \"{gen_uuid()}\"))
\t(symbol
\t\t(lib_id "power:GND")
\t\t(at {sx+10.16} {sy} 270)
\t\t(unit 1)
\t\t(uuid "{pwr_u}")
\t\t(property "Reference" "#PWR" (at {sx+10.16} {sy-2} 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(property "Value" "GND" (at {sx+12} {sy} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at {sx+10.16} {sy} 0) (effects (font (size 1.27 1.27)) (hide yes)))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(instances
\t\t\t(project "{proj_name}"
\t\t\t\t(path "/{root_uuid}"
\t\t\t\t\t(reference "#PWR")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
"""

sch_text += f"""\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
"""

with open(r"d:\Arduino_portable\Projekte\retrogo\pixelgo\kicad\pixelgo_gamepad\pixelgo_gamepad.kicad_sch", "w", encoding="utf-8") as f:
    f.write(sch_text)

print("Synchronisierte Dateien pixelgo_gamepad.kicad_sch und pixelgo_gamepad.kicad_pro erfolgreich generiert!")
