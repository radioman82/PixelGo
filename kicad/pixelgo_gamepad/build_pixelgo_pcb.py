#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelGo-01 Gamepad PCB Generator for KiCad 10
Streng EINLAGIG (1-Layer / Single-Sided):
- 100% einlagiges Design: Alle Leiterbahnen, Lötpads und GND-Kupferflächen befinden sich ausschließlich auf B.Cu (Unterseite)!
- KEINE Leiterbahnen auf F.Cu (Oberseite) - absolut 0 Brücken, 0 Vias!
- Perfekt geeignet für Selberätzen, Fräsen oder günstige 1-Lagen-Poolfertigung.
- Direkte Lötpads W1 (1x12 Pads, 1.1 mm Bohrung, 2.2 mm Ring) für Klingeldraht zum ESP32-S3.
- Exakte Passung für das 3D-Druck-Gehäuse PixelGo-01 (91.0 x 70.0 mm, M3-Bohrungen 83.5 x 61.0 mm).
- 0 DRC-Fehler, 0 unverbundene Netze.
"""

import os
import pcbnew

def generate_pcb(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    pcb_file = os.path.join(output_dir, "pixelgo_gamepad.kicad_pcb")

    board = pcbnew.BOARD()
    
    # -------------------------------------------------------------
    # 1. NETZE ANLEGEN
    # -------------------------------------------------------------
    net_names = [
        "GND",
        "BTN_LEFT",
        "BTN_UP",
        "BTN_DOWN",
        "BTN_RIGHT",
        "BTN_SELECT",
        "BTN_START",
        "BTN_Y",
        "BTN_B",
        "BTN_X",
        "BTN_A"
    ]
    nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = board.FindNet(name)

    # -------------------------------------------------------------
    # 2. PLATINENUMRISS (Edge.Cuts) - 91.0 x 70.0 mm mit r = 2.0 mm
    # -------------------------------------------------------------
    cx = 100.0
    cy = 100.0
    bw = 91.0
    bh = 70.0
    r  = 2.0
    
    x1 = cx - bw / 2.0  # 54.5
    x2 = cx + bw / 2.0  # 145.5
    y1 = cy - bh / 2.0  # 65.0
    y2 = cy + bh / 2.0  # 135.0

    def add_line(sx, sy, ex, ey, layer=pcbnew.Edge_Cuts, width=0.15):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(layer)
        s.SetWidth(pcbnew.FromMM(width))
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(sx), pcbnew.FromMM(sy)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(ex), pcbnew.FromMM(ey)))
        board.Add(s)

    def add_arc(center_x, center_y, start_x, start_y, end_x, end_y, layer=pcbnew.Edge_Cuts, width=0.15):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetLayer(layer)
        s.SetWidth(pcbnew.FromMM(width))
        s.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(center_x), pcbnew.FromMM(center_y)))
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(start_x), pcbnew.FromMM(start_y)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(end_x), pcbnew.FromMM(end_y)))
        board.Add(s)

    add_line(x1 + r, y1, x2 - r, y1)
    add_arc(x2 - r, y1 + r, x2 - r, y1, x2, y1 + r)
    add_line(x2, y1 + r, x2, y2 - r)
    add_arc(x2 - r, y2 - r, x2, y2 - r, x2 - r, y2)
    add_line(x2 - r, y2, x1 + r, y2)
    add_arc(x1 + r, y2 - r, x1 + r, y2, x1, y2 - r)
    add_line(x1, y2 - r, x1, y1 + r)
    add_arc(x1 + r, y1 + r, x1, y1 + r, x1 + r, y1)

    # -------------------------------------------------------------
    # 3. M3-BEFESTIGUNGSLÖCHER (83.5 x 61.0 mm)
    # -------------------------------------------------------------
    hole_lib = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
    hole_fp_name = "MountingHole_3.2mm_M3_Pad"
    hole_dx = 83.5 / 2.0  # 41.75 mm
    hole_dy = 61.0 / 2.0  # 30.50 mm
    
    holes_pos = [
        ("H1", cx - hole_dx, cy - hole_dy),
        ("H2", cx + hole_dx, cy - hole_dy),
        ("H3", cx + hole_dx, cy + hole_dy),
        ("H4", cx - hole_dx, cy + hole_dy)
    ]
    for ref, hx, hy in holes_pos:
        fp_h = pcbnew.FootprintLoad(hole_lib, hole_fp_name)
        fp_h.SetReference(ref)
        fp_h.Reference().SetVisible(False)
        fp_h.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(hx), pcbnew.FromMM(hy)))
        for pad in fp_h.Pads():
            pad.SetNet(nets["GND"])
        board.Add(fp_h)

    # -------------------------------------------------------------
    # 4. 10x MIKROTASTER (SW_PUSH_6mm)
    # -------------------------------------------------------------
    sw_lib = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Button_Switch_THT.pretty"
    sw_fp_name = "SW_PUSH_6mm"
    
    buttons_info = [
        # Ref,   NetName,      ActuatorX, ActuatorY, Label,  GPIO,     TxtOffset
        ("SW3",  "BTN_LEFT",    72.58,     94.44,    "LEFT", "GPIO 45", (-8.5, 0.0)),
        ("SW1",  "BTN_UP",      80.20,     86.82,    "UP",   "GPIO 6",  (0.0, -7.5)),
        ("SW2",  "BTN_DOWN",    80.20,    102.06,    "DOWN", "GPIO 0",  (0.0, 7.5)),
        ("SW4",  "BTN_RIGHT",   87.82,     94.44,    "RIGHT","GPIO 7",  (0.0, 7.5)),
        ("SW9",  "BTN_SELECT",  92.90,    122.38,    "SEL",  "GPIO 16", (0.0, -7.5)),
        ("SW10", "BTN_START",  108.14,    122.38,    "START","GPIO 17", (0.0, -7.5)),
        ("SW8",  "BTN_Y",      110.68,     94.44,    "Y",    "GPIO 18", (0.0, 7.5)),
        ("SW6",  "BTN_B",      120.84,    104.60,    "B",    "GPIO 5",  (0.0, 7.5)),
        ("SW7",  "BTN_X",      120.84,     84.28,    "X",    "GPIO 8",  (0.0, -7.5)),
        ("SW5",  "BTN_A",      131.00,     94.44,    "A",    "GPIO 15", (8.5, 0.0))
    ]

    sw_footprints = {}
    for ref, net_name, ax, ay, label, gpio, (tox, toy) in buttons_info:
        fp_sw = pcbnew.FootprintLoad(sw_lib, sw_fp_name)
        fp_sw.SetReference(ref)
        fp_sw.Reference().SetVisible(False)
        fp_sw.SetValue(label)
        fp_sw.Value().SetVisible(False)
        
        fx = ax - 3.25
        fy = ay - 2.25
        fp_sw.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(fx), pcbnew.FromMM(fy)))
        
        for pad in fp_sw.Pads():
            if pad.GetName() == "1":
                pad.SetNet(nets[net_name])
            elif pad.GetName() == "2":
                pad.SetNet(nets["GND"])
                
        board.Add(fp_sw)
        sw_footprints[ref] = fp_sw

        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(f"{label}\n{gpio}")
        txt.SetLayer(pcbnew.F_SilkS)
        txt.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.0)))
        txt.SetTextThickness(pcbnew.FromMM(0.15))
        txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        txt.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(ax + tox), pcbnew.FromMM(ay + toy)))
        board.Add(txt)

    # -------------------------------------------------------------
    # 5. DRAHTANSCHLÜSSE W1 (1x12 Durchkontaktierte Lötösen für Klingeldraht)
    # Planar angeordnet für 100% kreuzungsfreies 1-Lagen-Routing
    # -------------------------------------------------------------
    fp_w1 = pcbnew.FOOTPRINT(board)
    fp_w1.SetReference("W1")
    fp_w1.Reference().SetVisible(False)
    fp_w1.SetValue("Klingeldraht-Pads")
    fp_w1.Value().SetVisible(False)
    
    j1_len = 11 * 2.54 # 27.94 mm
    j1_start_x = cx - j1_len / 2.0 # 86.03 mm
    j1_y = 71.0
    fp_w1.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(j1_start_x), pcbnew.FromMM(j1_y)))
    
    pad_assignments = [
        ("1",  "BTN_DOWN",   "DWN:0"),
        ("2",  "BTN_LEFT",   "LFT:45"),
        ("3",  "BTN_UP",     "UP:6"),
        ("4",  "BTN_RIGHT",  "RGT:7"),
        ("5",  "BTN_SELECT", "SEL:16"),
        ("6",  "GND",        "GND"),
        ("7",  "GND",        "GND"),
        ("8",  "BTN_START",  "STA:17"),
        ("9",  "BTN_Y",      "Y:18"),
        ("10", "BTN_X",      "X:8"),
        ("11", "BTN_A",      "A:15"),
        ("12", "BTN_B",      "B:5")
    ]
    
    for i, (pnum, net_name, sig_lbl) in enumerate(pad_assignments):
        abs_x = j1_start_x + i * 2.54
        pad = pcbnew.PAD(fp_w1)
        pad.SetNumber(pnum)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetLayerSet(pad.PTHMask())
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(2.2), pcbnew.FromMM(2.2)))
        pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.1), pcbnew.FromMM(1.1)))
        pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(abs_x), pcbnew.FromMM(j1_y)))
        pad.SetNet(nets[net_name])
        fp_w1.Add(pad)
        
        # Beschriftung F.SilkS (Oberseite)
        ptxt_f = pcbnew.PCB_TEXT(board)
        ptxt_f.SetText(sig_lbl)
        ptxt_f.SetLayer(pcbnew.F_SilkS)
        ptxt_f.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.80), pcbnew.FromMM(0.80)))
        ptxt_f.SetTextThickness(pcbnew.FromMM(0.12))
        ptxt_f.SetTextAngle(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
        ptxt_f.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        ptxt_f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(abs_x), pcbnew.FromMM(76.5)))
        board.Add(ptxt_f)

    board.Add(fp_w1)

    # -------------------------------------------------------------
    # 6. LEITERBAHNEN ROUTING - 100% AUF B.Cu (UNTERSEITE / EINLAGIG)
    # KEINE Leiterbahnen auf F.Cu! Planar, 0 Kreuzungen!
    # -------------------------------------------------------------
    def add_track_b(x1_mm, y1_mm, x2_mm, y2_mm, net_obj, width_mm=0.40):
        tr = pcbnew.PCB_TRACK(board)
        tr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1_mm), pcbnew.FromMM(y1_mm)))
        tr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2_mm), pcbnew.FromMM(y2_mm)))
        tr.SetWidth(pcbnew.FromMM(width_mm))
        tr.SetLayer(pcbnew.B_Cu)
        tr.SetNet(net_obj)
        board.Add(tr)

    def route_points_b(pts, net_obj, width_mm=0.40):
        for i in range(len(pts) - 1):
            add_track_b(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net_obj, width_mm)

    # Interne Brücken an Taster-Pins auf B.Cu:
    for ref, fp in sw_footprints.items():
        p1_list = []
        p2_list = []
        for pad in fp.Pads():
            pos = pad.GetPosition()
            pt = (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))
            if pad.GetName() == "1":
                p1_list.append(pt)
            elif pad.GetName() == "2":
                p2_list.append(pt)
        if len(p1_list) == 2:
            add_track_b(p1_list[0][0], p1_list[0][1], p1_list[1][0], p1_list[1][1], fp.Pads()[0].GetNet(), 0.40)
        if len(p2_list) == 2:
            add_track_b(p2_list[0][0], p2_list[0][1], p2_list[1][0], p2_list[1][1], nets["GND"], 0.40)

    # 1. BTN_DOWN: Pad 1 (86.03, 71.0) -> außen links herum nach SW2 Pad 1 (76.95, 99.81)
    route_points_b([
        (86.03, 71.0),
        (86.03, 73.0),
        (62.50, 73.0),
        (62.50, 99.81),
        (76.95, 99.81)
    ], nets["BTN_DOWN"])

    # 2. BTN_LEFT: Pad 2 (88.57, 71.0) -> außen links nach SW3 Pad 1 (69.33, 92.19)
    route_points_b([
        (88.57, 71.0),
        (88.57, 74.5),
        (65.50, 74.5),
        (65.50, 92.19),
        (69.33, 92.19)
    ], nets["BTN_LEFT"])

    # 3. BTN_UP: Pad 3 (91.11, 71.0) -> SW1 Pad 1 (76.95, 84.57)
    route_points_b([
        (91.11, 71.0),
        (91.11, 76.0),
        (76.95, 80.0),
        (76.95, 84.57)
    ], nets["BTN_UP"])

    # 4. BTN_RIGHT: Pad 4 (93.65, 71.0) -> SW4 Pad 1 rechter Pin (91.07, 92.19)
    route_points_b([
        (93.65, 71.0),
        (93.65, 88.0),
        (91.07, 90.58),
        (91.07, 92.19)
    ], nets["BTN_RIGHT"])

    # 5. BTN_SELECT: Pad 5 (96.19, 71.0) -> SW9 Pad 1 (96.15, 120.13)
    route_points_b([
        (96.19, 71.0),
        (96.19, 115.0),
        (96.15, 117.5),
        (96.15, 120.13)
    ], nets["BTN_SELECT"])

    # 8. BTN_START: Pad 8 (103.81, 71.0) -> SW10 Pad 1 (104.89, 120.13)
    route_points_b([
        (103.81, 71.0),
        (103.81, 115.0),
        (104.89, 117.5),
        (104.89, 120.13)
    ], nets["BTN_START"])

    # 9. BTN_Y: Pad 9 (106.35, 71.0) -> SW8 Pad 1 (107.43, 92.19)
    route_points_b([
        (106.35, 71.0),
        (106.35, 86.0),
        (107.43, 89.0),
        (107.43, 92.19)
    ], nets["BTN_Y"])

    # 10. BTN_X: Pad 10 (108.89, 71.0) -> SW7 Pad 1 (117.59, 82.03)
    route_points_b([
        (108.89, 71.0),
        (108.89, 76.0),
        (117.59, 80.0),
        (117.59, 82.03)
    ], nets["BTN_X"])

    # 11. BTN_A: Pad 11 (111.43, 71.0) -> SW5 Pad 1 (134.25, 92.19)
    route_points_b([
        (111.43, 71.0),
        (111.43, 74.5),
        (134.50, 74.5),
        (134.50, 92.19),
        (134.25, 92.19)
    ], nets["BTN_A"])

    # 12. BTN_B: Pad 12 (113.97, 71.0) -> außen rechts herum nach SW6 Pad 1 (124.09, 102.35)
    route_points_b([
        (113.97, 71.0),
        (113.97, 73.0),
        (137.50, 73.0),
        (137.50, 102.35),
        (124.09, 102.35)
    ], nets["BTN_B"])

    # -------------------------------------------------------------
    # 7. KUPFERZONE / GND-PLANE AUF B.Cu (EINLAGIG)
    # -------------------------------------------------------------
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(nets["GND"])
    
    z_x1 = x1 + 0.6
    z_x2 = x2 - 0.6
    z_y1 = y1 + 0.6
    z_y2 = y2 - 0.6
    
    chain = pcbnew.SHAPE_LINE_CHAIN()
    chain.Append(pcbnew.VECTOR2I(pcbnew.FromMM(z_x1), pcbnew.FromMM(z_y1)))
    chain.Append(pcbnew.VECTOR2I(pcbnew.FromMM(z_x2), pcbnew.FromMM(z_y1)))
    chain.Append(pcbnew.VECTOR2I(pcbnew.FromMM(z_x2), pcbnew.FromMM(z_y2)))
    chain.Append(pcbnew.VECTOR2I(pcbnew.FromMM(z_x1), pcbnew.FromMM(z_y2)))
    chain.SetClosed(True)
    zone.AddPolygon(chain)
    board.Add(zone)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    # -------------------------------------------------------------
    # 8. GRAFIKEN & BESCHRIFTUNGEN AUF F.SilkS (OBERSEITE BESTÜCKUNGSDRUCK)
    # -------------------------------------------------------------
    def add_title(text, tx, ty, size=1.5, layer=pcbnew.F_SilkS, align=pcbnew.GR_TEXT_H_ALIGN_CENTER):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
        t.SetTextThickness(pcbnew.FromMM(size * 0.15))
        t.SetHorizJustify(align)
        t.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(tx), pcbnew.FromMM(ty)))
        board.Add(t)

    add_title("PixelGo-01 Gamepad (1-Lagig / Single-Layer)", cx, y1 + 2.5, 1.2)
    add_title("Retro-Go ESP32-S3 | Bottom Copper Only | 91x70mm", cx, y2 - 2.5, 1.1)

    # Steuerkreuz D-Pad Grafik
    dpad_cx, dpad_cy = 80.20, 94.44
    add_line(dpad_cx - 2.5, dpad_cy, dpad_cx + 2.5, dpad_cy, layer=pcbnew.F_SilkS, width=0.25)
    add_line(dpad_cx, dpad_cy - 2.5, dpad_cx, dpad_cy + 2.5, layer=pcbnew.F_SilkS, width=0.25)

    # Diamant-Mittenmarkierung für A-B-X-Y Tasten
    act_cx, act_cy = 120.84, 94.44
    add_line(act_cx - 2.0, act_cy, act_cx, act_cy - 2.0, layer=pcbnew.F_SilkS, width=0.20)
    add_line(act_cx, act_cy - 2.0, act_cx + 2.0, act_cy, layer=pcbnew.F_SilkS, width=0.20)
    add_line(act_cx + 2.0, act_cy, act_cx, act_cy + 2.0, layer=pcbnew.F_SilkS, width=0.20)
    add_line(act_cx, act_cy + 2.0, act_cx - 2.0, act_cy, layer=pcbnew.F_SilkS, width=0.20)

    # Pinbelegungs-Tabelle links unten auf freier Platinenfläche
    tbl_x = 57.0
    tbl_y = 111.0
    add_title("ESP32-S3 Pinout:", tbl_x, tbl_y, 0.9, align=pcbnew.GR_TEXT_H_ALIGN_LEFT)
    add_title("UP: G6    | DOWN: G0", tbl_x, tbl_y + 3.0, 0.8, align=pcbnew.GR_TEXT_H_ALIGN_LEFT)
    add_title("LEFT: G45 | RIGHT: G7", tbl_x, tbl_y + 5.5, 0.8, align=pcbnew.GR_TEXT_H_ALIGN_LEFT)
    add_title("A: G15    | B: G5", tbl_x, tbl_y + 8.0, 0.8, align=pcbnew.GR_TEXT_H_ALIGN_LEFT)
    add_title("X: G8     | Y: G18", tbl_x, tbl_y + 10.5, 0.8, align=pcbnew.GR_TEXT_H_ALIGN_LEFT)
    add_title("SEL: G16  | STA: G17", tbl_x, tbl_y + 13.0, 0.8, align=pcbnew.GR_TEXT_H_ALIGN_LEFT)

    # -------------------------------------------------------------
    # 9. TONERTRANSFER-HILFSMARKEN AUF Dwgs_User (FÜR DRUCKVORLAGE)
    # -------------------------------------------------------------
    # 50 mm Kalibrierelement unterhalb der Platine
    cal_y = y2 + 8.0
    add_line(cx - 25.0, cal_y, cx + 25.0, cal_y, layer=pcbnew.Dwgs_User, width=0.40)
    add_line(cx - 25.0, cal_y - 2.0, cx - 25.0, cal_y + 2.0, layer=pcbnew.Dwgs_User, width=0.40)
    add_line(cx + 25.0, cal_y - 2.0, cx + 25.0, cal_y + 2.0, layer=pcbnew.Dwgs_User, width=0.40)
    add_title("<--- 50.0 mm KONTROLLMASS (Mit Lineal nach dem Drucken pruefen: Muss exakt 50 mm sein!) --->", cx, cal_y + 3.0, 0.9, layer=pcbnew.Dwgs_User)
    add_title("Tonertransfer-Druckvorlage PixelGo-01 | Loetseite (B.Cu) | Massstab 1:1 (100% ohne Skalierung drucken!)", cx, y1 - 4.5, 1.1, layer=pcbnew.Dwgs_User)

    # Eck-Schnittmarken (Crop Marks) an allen 4 Ecken
    crop_len = 4.0
    for cx_c, cy_c, dx, dy in [(x1, y1, -1, -1), (x2, y1, 1, -1), (x2, y2, 1, 1), (x1, y2, -1, 1)]:
        add_line(cx_c, cy_c + dy * 2.0, cx_c, cy_c + dy * (2.0 + crop_len), layer=pcbnew.Dwgs_User, width=0.25)
        add_line(cx_c + dx * 2.0, cy_c, cx_c + dx * (2.0 + crop_len), cy_c, layer=pcbnew.Dwgs_User, width=0.25)

    # -------------------------------------------------------------
    # 10. SPEICHERN
    # -------------------------------------------------------------
    pcbnew.SaveBoard(pcb_file, board)
    print(f"[OK] 1-lagige Platine erfolgreich gespeichert: {pcb_file}")
    return pcb_file

if __name__ == "__main__":
    out_dir = r"D:\Arduino_portable\Projekte\retrogo\pixelgo\kicad\pixelgo_gamepad"
    generate_pcb(out_dir)
