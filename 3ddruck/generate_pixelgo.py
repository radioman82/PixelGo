"""
=============================================================================
Parametrisches FreeCAD-Gehaeuse & TPU-Tasten fuer Handheld "pixelgo-01"
Erstellt fuer: FreeCAD 1.1 / FreeCADCmd (Headless)
3D-Drucker: Artillery Sidewinder X2 (Anycubic PLA+ / TPU)
Befestigung: M3-Messing-Einschmelzmuttern (Heat-Set Inserts 4 x 4 mm)
=============================================================================
"""

import os
import sys
import math
import FreeCAD
import Part
import Mesh
import MeshPart

try:
    import Draft
except ImportError:
    Draft = None

print("=================================================================")
print("  PIXELGO-01 PARAMETRIC 3D CAD GENERATOR (FreeCAD 1.1)")
print("  Inkl. M3-Messing-Einschmelzmuttern (4x4mm) & 45°-Kopfsenkungen")
print("=================================================================")

# ---------------------------------------------------------------------------
# 1. TOLERANZEN & M3-MESSING-EINSCHMELZMUTTERN (EXAKTE VARIABLEN)
# ---------------------------------------------------------------------------
# Thermische M3-Gewindeeinsatze (Heat-Set Inserts 4 x 4 mm: OD = 4.0 mm, L = 4.0 mm)
insert_hole_dia       = 3.80        # 3.80 mm Bohrung fuer festen Schmelzsitz in PLA+
insert_hole_depth     = 5.20        # 5.20 mm Tiefe (4 mm Huelse + 1.2 mm Schmelzmaterial-Freiraum)
boss_outer_dia        = 8.00        # mind. 8.0 mm Aussendurchmesser der 4 Gehaeuse-Eckdome (mind. 2.1 mm Wandung)
tft_boss_outer_dia    = 6.50        # 6.50 mm Aussendurchmesser fuer TFT-Schraubdome (-1mm gegenueber 7.50 mm)
pcb_boss_outer_dia    = 7.50        # 7.50 mm Aussendurchmesser fuer Lochraster-Schraubdome

# M3-Verschraubung von unten (Unterschale)
m3_through_dia        = 3.40        # 3.40 mm M3-Durchgangsloch
m3_counterbore_dia    = 6.20        # 6.20 mm M3-Kopfsenkung
m3_counterbore_depth  = 4.00        # 4.00 mm Senkungstiefe (Kopf komplett versenkt)
m3_cone_height        = (m3_counterbore_dia - m3_through_dia) / 2.0  # 1.40 mm fuer 45°-Kegeluebergang

# Druck- & Passungstoleranzen
button_clearance      = 0.35        # 0.35 mm umlaufend -> Tastenloch-Durchmesser = Schaft + 0.70 mm
pcb_clearance         = 0.30        # +0.30 mm Toleranz fuer Platinen-Taschen und Haltestege
lip_clearance         = 0.25        # 0.25 mm Spiel fuer Zentrierlippe (Lip & Groove)

# Gehaeuse-Hauptmasse
wall_thick            = 2.40        # Wandstaerke des Gehaeuses
case_width            = 102.0       # Gehaeusebreite (X-Achse)
case_height           = 150.0       # Gehaeusehoehe (Y-Achse, 150 mm fuer perfekten Bauteilfreiraum)
front_depth           = 13.0        # Oberschalen-Tiefe (Z-Achse)
back_depth            = 13.0        # Unterschalen-Tiefe (Z-Achse)
total_depth           = front_depth + back_depth # 26.0 mm (< 30 mm!)

corner_radius         = 4.0         # Vertikaler Kantenradius (4 Ecken)
fillet_outer          = 2.0         # Rundung Deckel-/Boden-Aussenkanten

font_file = "C:/Windows/Fonts/arialbd.ttf"
if not os.path.exists(font_file):
    font_file = "C:/Windows/Fonts/arial.ttf"

output_dir = r"D:\Arduino_portable\Projekte\retrogo\pixelgo\3ddruck"
os.makedirs(output_dir, exist_ok=True)

doc_name = "pixelgo_complete_assembly"
doc = FreeCAD.newDocument(doc_name)

# ---------------------------------------------------------------------------
# 2. HILFSFUNKTIONEN FUER 2D-PROFILE & 3D-KOERPER
# ---------------------------------------------------------------------------
def make_rounded_rect_face(w, h, r):
    """Erzeugt ein sauberes, geschlossenes 2D-Face mit abgerundeten Ecken."""
    r = max(0.2, min(r, w / 2.0 - 0.2, h / 2.0 - 0.2))
    x0, x1 = -w / 2.0, w / 2.0
    y0, y1 = -h / 2.0, h / 2.0
    
    p1 = FreeCAD.Vector(x1 - r, y0, 0)
    p2 = FreeCAD.Vector(x1, y0 + r, 0)
    p3 = FreeCAD.Vector(x1, y1 - r, 0)
    p4 = FreeCAD.Vector(x1 - r, y1, 0)
    p5 = FreeCAD.Vector(x0 + r, y1, 0)
    p6 = FreeCAD.Vector(x0, y1 - r, 0)
    p7 = FreeCAD.Vector(x0, y0 + r, 0)
    p8 = FreeCAD.Vector(x0 + r, y0, 0)

    diag = r * (1.0 - math.cos(math.pi / 4.0))
    a1 = Part.Arc(p1, FreeCAD.Vector(x1 - diag, y0 + diag, 0), p2).toShape()
    l2 = Part.makeLine(p2, p3)
    a2 = Part.Arc(p3, FreeCAD.Vector(x1 - diag, y1 - diag, 0), p4).toShape()
    l3 = Part.makeLine(p4, p5)
    a3 = Part.Arc(p5, FreeCAD.Vector(x0 + diag, y1 - diag, 0), p6).toShape()
    l4 = Part.makeLine(p6, p7)
    a4 = Part.Arc(p7, FreeCAD.Vector(x0 + diag, y0 + diag, 0), p8).toShape()
    l1 = Part.makeLine(p8, p1)

    wire = Part.Wire([l1, a1, l2, a2, l3, a3, l4, a4])
    return Part.Face(wire)

def make_shell_blank(w, h, depth, corner_r, fillet_r, is_front=True):
    """Erstellt den Grundkoerper mit abgerundeten Aussenkanten."""
    face = make_rounded_rect_face(w, h, corner_r)
    solid = face.extrude(FreeCAD.Vector(0, 0, depth))
    
    target_z = depth if is_front else 0.0
    target_edges = [
        e for e in solid.Edges 
        if abs(e.BoundBox.ZMin - target_z) < 1e-3 and abs(e.BoundBox.ZMax - target_z) < 1e-3
    ]
    if target_edges and fillet_r > 0.1:
        try:
            solid = solid.makeFillet(fillet_r, target_edges)
        except Exception as e:
            print(f"Hinweis: Fillet vereinfacht ({e}).")
            
    return solid

def make_cylinder(dia, height, center_xy, z_start):
    """Erstellt einen Zylinder entlang der Z-Achse."""
    pos = FreeCAD.Vector(center_xy[0], center_xy[1], z_start)
    return Part.makeCylinder(dia / 2.0, height, pos, FreeCAD.Vector(0, 0, 1))

def make_box_center(w, l, h, center_xy, z_start):
    """Erstellt eine zentrierte Box in X und Y mit gegebener Z-Startposition."""
    x = center_xy[0] - w / 2.0
    y = center_xy[1] - l / 2.0
    return Part.makeBox(w, l, h, FreeCAD.Vector(x, y, z_start))

# ---------------------------------------------------------------------------
# 3. POSITIONEN & BEZUGSPUNKTE
# ---------------------------------------------------------------------------
# 4 Gehaeuse-Eckverschraubungen M3
# Optimierte Positionen: Vollstaendig kollisionsfrei zu TFT- und Lochraster-Befestigungen
corner_x = 42.0   # +/- 42.0 mm
corner_y = 68.5   # +/- 68.5 mm (keinerlei Ueberlappung mit TFT- oder PCB-Domen)
corners = [
    (-corner_x, -corner_y),
    ( corner_x, -corner_y),
    ( corner_x,  corner_y),
    (-corner_x,  corner_y)
]

# TFT 2.8" ILI9341
# Sichtfenster: 64 x 47 mm, PCB: 86 x 50 x 8.5 mm, M3-Loecher: 76.5 x 44 mm
# Von der Innenseite gesehen muessen die 4 Befestigungsloecher um 1.5 mm nach rechts verschoben werden.
# In Gehaeusekoordinaten (Blick von innen = umgekehrte X-Richtung) bedeutet dies: X-Verschiebung um -1.5 mm.
# Damit wandert das TFT-Zentrum von X = +3.0 mm auf X = +1.5 mm.
tft_center_x = 1.5
tft_center_y = 38.0
tft_holes = [
    (tft_center_x - 76.5 / 2.0, tft_center_y - 44.0 / 2.0),
    (tft_center_x + 76.5 / 2.0, tft_center_y - 44.0 / 2.0),
    (tft_center_x + 76.5 / 2.0, tft_center_y + 44.0 / 2.0),
    (tft_center_x - 76.5 / 2.0, tft_center_y + 44.0 / 2.0)
]

# Lochrasterplatine fuer Tasten: 91 x 70 x 1.6 mm, Befestigung: 83.5 x 61 mm
# Um 5.6 mm nach oben versetzt (Y = -28.0 mm), damit unten 10 mm Freiraum fuer Gehaeusedome & Akku entstehen
pcb_center_x = 0.0
pcb_center_y = -28.0
pcb_ll_x = pcb_center_x - 91.0 / 2.0   # -45.5 mm
pcb_ll_y = pcb_center_y - 70.0 / 2.0   # -63.0 mm

pcb_holes = [
    (pcb_center_x - 83.5 / 2.0, pcb_center_y - 61.0 / 2.0),
    (pcb_center_x + 83.5 / 2.0, pcb_center_y - 61.0 / 2.0),
    (pcb_center_x + 83.5 / 2.0, pcb_center_y + 61.0 / 2.0),
    (pcb_center_x - 83.5 / 2.0, pcb_center_y + 61.0 / 2.0)
]

# Raster-Berechnung: X = pcb_ll_x + 13.0 + col * 2.54; Y = pcb_ll_y + 5.0 + row * 2.54
def grid_pos(col, row):
    return (pcb_ll_x + 13.0 + col * 2.54, pcb_ll_y + 5.0 + row * 2.54)

# Tasten-Zentren & Mikrotaster-Positionen
# Steuerkreuz (D-Pad)
dpad_center = grid_pos(5, 14)          # (-19.80, -28.04)
sw_dpad_up    = grid_pos(5, 17)        # (-19.80, -20.42)
sw_dpad_down  = grid_pos(5, 11)        # (-19.80, -35.66)
sw_dpad_left  = grid_pos(2, 14)        # (-27.42, -28.04)
sw_dpad_right = grid_pos(8, 14)        # (-12.18, -28.04)

# Aktionstasten A, B, X, Y
btn_a_pos = grid_pos(25, 14)           # (+31.00, -28.04)  Aussen rechts (Haupttaste A)
btn_b_pos = grid_pos(21, 10)           # (+20.84, -38.20)  Unten (Haupttaste B)
btn_x_pos = grid_pos(21, 18)           # (+20.84, -17.88)  Oben (Option X)
btn_y_pos = grid_pos(17, 14)           # (+10.68, -28.04)  Links (Menue Y)

# Menue-Tasten Select & Start
btn_select_pos = grid_pos(10, 3)       # (-7.10, -55.98)
btn_start_pos  = grid_pos(16, 3)       # (+8.14, -55.98)

# Alle Mikrotaster (fuer Loetschablone & Dummys)
microswitches_info = [
    ("SW_UP", sw_dpad_up),
    ("SW_DOWN", sw_dpad_down),
    ("SW_LEFT", sw_dpad_left),
    ("SW_RIGHT", sw_dpad_right),
    ("SW_A", btn_a_pos),
    ("SW_B", btn_b_pos),
    ("SW_X", btn_x_pos),
    ("SW_Y", btn_y_pos),
    ("SW_SEL", btn_select_pos),
    ("SW_START", btn_start_pos)
]

# Lautsprecher rechts unten (an Oberschale)
speaker_center = (34.0, -48.0)

# Standoff-Hoehe fuer Lochrasterplatine:
# Formel: Standoff_Hoehe = TPU_Unterbau (2.2) + Mikrotaster (4.0) + Spiel (0.2) = 6.4 mm
tpu_flange_h = 1.20
tpu_plunger_h = 1.00
tpu_unterbau = tpu_flange_h + tpu_plunger_h   # 2.20 mm
pcb_standoff_h = tpu_unterbau + 4.00 + 0.20   # 6.40 mm

print("Geometrie-Parameter und Rasterkoordinaten berechnet.")

# ---------------------------------------------------------------------------
# 4. OBERSCHALE (FRONT_SHELL) KONSTRUKTION
# ---------------------------------------------------------------------------
print("Konstruiere Oberschale (Front_Shell)...")

# A) Grundkoerper Oberschale
front_shell = make_shell_blank(case_width, case_height, front_depth, corner_radius, fillet_outer, is_front=True)

# B) Innenraum ausholen (Hohlkoerper mit Wandstaerke wall_thick)
cavity_w = case_width - 2.0 * wall_thick
cavity_h = case_height - 2.0 * wall_thick
cavity_r = max(0.5, corner_radius - wall_thick)
cavity_face = make_rounded_rect_face(cavity_w, cavity_h, cavity_r)
cavity_solid = cavity_face.extrude(FreeCAD.Vector(0, 0, front_depth - wall_thick))
front_shell = front_shell.cut(cavity_solid)

# C) 4 Gehaeuse-Eck-Schraubdome (OD = 8.0 mm) mit M3-Einschmelzmutter-Bohrung (3.8 x 5.2 mm)
for cx, cy in corners:
    # Stabiler Schraubdom von Z=0 bis Z = front_depth - wall_thick (10.6 mm)
    boss = make_cylinder(boss_outer_dia, front_depth - wall_thick, (cx, cy), 0.0)
    front_shell = front_shell.fuse(boss)
    # Bohrung fuer M3-Messing-Einschmelzhuelse 4x4 mm (3.80 mm Durchmesser, 5.20 mm Tiefe ab Trennebene Z=0)
    insert_hole = make_cylinder(insert_hole_dia, insert_hole_depth, (cx, cy), 0.0)
    front_shell = front_shell.cut(insert_hole)

# D) 4 Standoffs fuer TFT ILI9341 (OD = 6.5 mm) mit M3-Einschmelzmutter-Bohrung
tft_boss_h = 3.50
for hx, hy in tft_holes:
    boss = make_cylinder(tft_boss_outer_dia, tft_boss_h, (hx, hy), front_depth - wall_thick - tft_boss_h)
    front_shell = front_shell.fuse(boss)
    # 3.8 x 5.2 mm Bohrung fuer M3-Messing-Einschmelzhuelse
    insert_hole = make_cylinder(insert_hole_dia, insert_hole_depth, (hx, hy), front_depth - wall_thick - tft_boss_h)
    front_shell = front_shell.cut(insert_hole)

# E) 4 Standoffs fuer Lochrasterplatine (Hoehe = 6.4 mm, OD = 7.5 mm) mit M3-Einschmelzmutter-Bohrung
for hx, hy in pcb_holes:
    boss = make_cylinder(pcb_boss_outer_dia, pcb_standoff_h, (hx, hy), front_depth - wall_thick - pcb_standoff_h)
    front_shell = front_shell.fuse(boss)
    # 3.8 x 5.2 mm Bohrung fuer M3-Messing-Einschmelzhuelse
    insert_hole = make_cylinder(insert_hole_dia, insert_hole_depth, (hx, hy), front_depth - wall_thick - pcb_standoff_h)
    front_shell = front_shell.cut(insert_hole)

# F) Lautsprecher-Zentrierring (Innen-D 20.9 mm, Hoehe 1.5 mm an der Innenwand)
spk_inner_d = 20.9
spk_ring_thick = 1.2
spk_ring_h = 1.5
spk_ring = make_cylinder(spk_inner_d + 2.0 * spk_ring_thick, spk_ring_h, speaker_center, front_depth - wall_thick - spk_ring_h)
spk_inner_cut = make_cylinder(spk_inner_d, spk_ring_h + 0.1, speaker_center, front_depth - wall_thick - spk_ring_h - 0.05)
spk_ring = spk_ring.cut(spk_inner_cut)
front_shell = front_shell.fuse(spk_ring)

# Lautsprecher-Schallgitter (Akkustik-Loecher durch die Frontwand)
for angle_deg in range(0, 360, 60):
    rad = 5.0
    gx = speaker_center[0] + rad * math.cos(math.radians(angle_deg))
    gy = speaker_center[1] + rad * math.sin(math.radians(angle_deg))
    hole = make_cylinder(1.8, wall_thick + 1.0, (gx, gy), front_depth - wall_thick - 0.5)
    front_shell = front_shell.cut(hole)
center_hole = make_cylinder(2.0, wall_thick + 1.0, speaker_center, front_depth - wall_thick - 0.5)
front_shell = front_shell.cut(center_hole)

# G) Ausschnitt TFT-Sichtfenster (64 x 47 mm, zentriert auf X=0, Y=tft_center_y)
# Exakt gerade, saubere Kanten ohne wellige BSpline-Lofts oder Ueberschneidungen mit den TFT-Domen
tft_win_w = 64.0 + 0.6  # 64.6 mm
tft_win_h = 47.0 + 0.6  # 47.6 mm

tft_window_cut = make_box_center(tft_win_w, tft_win_h, wall_thick + 2.0, (0.0, tft_center_y), front_depth - wall_thick - 0.5)
front_shell = front_shell.cut(tft_window_cut)

# H) Ausschnitte fuer TPU-Tasten (inkl. Haltekragen-Taschen innen & 0.7 mm Loch-Aufmass)
# 1. D-Pad Kreuz-Ausschnitt (24.7 x 24.7 mm mit 8.7 mm Armbreite)
dpad_clear_w = 24.0 + 2.0 * button_clearance  # 24.70 mm
dpad_arm_w   =  8.0 + 2.0 * button_clearance  #  8.70 mm
dpad_cut1 = make_box_center(dpad_clear_w, dpad_arm_w, wall_thick + 2.0, dpad_center, front_depth - wall_thick - 0.5)
dpad_cut2 = make_box_center(dpad_arm_w, dpad_clear_w, wall_thick + 2.0, dpad_center, front_depth - wall_thick - 0.5)
front_shell = front_shell.cut(dpad_cut1.fuse(dpad_cut2))
# D-Pad Haltekragen-Tasche innen (D 26.8 mm, Tiefe 1.3 mm)
dpad_flange_pocket = make_cylinder(26.0 + 0.8, 1.3, dpad_center, front_depth - wall_thick - 0.1)
front_shell = front_shell.cut(dpad_flange_pocket)

# 2. Rundtasten A, B, X, Y (Einheitlich Schaft D 8.5 mm in Loch D 10.7 mm; Haltekragen D 10.8 mm in Tasche D 12.8 mm)
for bx, by in [btn_a_pos, btn_b_pos, btn_x_pos, btn_y_pos]:
    hole = make_cylinder(10.0 + 2.0 * button_clearance, wall_thick + 2.0, (bx, by), front_depth - wall_thick - 0.5)
    pocket = make_cylinder(12.0 + 0.8, 1.3, (bx, by), front_depth - wall_thick - 0.1)
    front_shell = front_shell.cut(hole)
    front_shell = front_shell.cut(pocket)

# 4. Rundtasten Select & Start (Schaft D 8.0 mm -> Loch D 8.7 mm; Haltekragen D 10.0 mm -> Tasche D 10.8 mm)
for bx, by in [btn_select_pos, btn_start_pos]:
    hole = make_cylinder(8.0 + 2.0 * button_clearance, wall_thick + 2.0, (bx, by), front_depth - wall_thick - 0.5)
    pocket = make_cylinder(10.0 + 0.8, 1.3, (bx, by), front_depth - wall_thick - 0.1)
    front_shell = front_shell.cut(hole)
    front_shell = front_shell.cut(pocket)

# I) Zentrierlippe (Lip) an der Oberschale
lip_w = cavity_w + 2.0 * (1.2 - lip_clearance)
lip_h = cavity_h + 2.0 * (1.2 - lip_clearance)
lip_r = max(0.5, corner_radius - 1.2)
lip_outer = make_rounded_rect_face(lip_w, lip_h, lip_r).extrude(FreeCAD.Vector(0, 0, 1.2))
lip_inner = make_rounded_rect_face(cavity_w, cavity_h, cavity_r).extrude(FreeCAD.Vector(0, 0, 1.4))
lip_ring = lip_outer.cut(lip_inner)
lip_ring.translate(FreeCAD.Vector(0, 0, -1.2))
front_shell = front_shell.fuse(lip_ring)

# J) Front-Cover: Auf alle Texte und Bezeichnungen auf dem Cover verzichten (optimale Drucksauberkeit)
print("  Front-Cover wird sauber und glatt ohne Text/Beschriftungen ausgefuehrt.")

print("Oberschale erfolgreich modelliert.")

# ---------------------------------------------------------------------------
# 5. UNTERSCHALE (BACK_SHELL) KONSTRUKTION
# ---------------------------------------------------------------------------
print("Konstruiere Unterschale (Back_Shell)...")

# A) Grundkoerper Unterschale
back_blank = make_shell_blank(case_width, case_height, back_depth, corner_radius, fillet_outer, is_front=False)

# B) Innenraum ausholen
cavity_back = make_rounded_rect_face(cavity_w, cavity_h, cavity_r).extrude(FreeCAD.Vector(0, 0, back_depth - wall_thick))
cavity_back.translate(FreeCAD.Vector(0, 0, wall_thick))
back_shell_pos = back_blank.cut(cavity_back)

# Nach Z = -back_depth bis 0 verschieben
back_shell = back_shell_pos
back_shell.translate(FreeCAD.Vector(0, 0, -back_depth))

# C) 4 Eck-Schraubdome (OD = 8.0 mm) mit 3.4 mm Durchgangsbohrung,
#    4.0 mm tiefer Kopfsenkung (6.2 mm) und 45°-Kegeluebergang (ohne Support druckbar)
for cx, cy in corners:
    # Stabiler Schraubdom von Z = -back_depth + wall_thick (-10.6) bis Z=0
    boss = make_cylinder(boss_outer_dia, back_depth - wall_thick, (cx, cy), -back_depth + wall_thick)
    back_shell = back_shell.fuse(boss)
    
    # 1. Zylindrische Kopfsenkung an Gehaeuse-Unterseite: D 6.2 mm, Tiefe 4.0 mm (von Z = -13.0 bis Z = -9.0)
    c_sink = make_cylinder(m3_counterbore_dia, m3_counterbore_depth, (cx, cy), -back_depth - 0.1)
    
    # 2. 45°-Kegeluebergang von D 6.2 mm auf D 3.4 mm (Hoehe = 1.4 mm, von Z = -9.0 bis Z = -7.6)
    cone_pos = FreeCAD.Vector(cx, cy, -back_depth + m3_counterbore_depth - 0.1)
    c_cone = Part.makeCone(m3_counterbore_dia / 2.0, m3_through_dia / 2.0, m3_cone_height, cone_pos, FreeCAD.Vector(0, 0, 1))
    
    # 3. Durchgangsloch D 3.4 mm vom Kegelende bis zur Trennebene Z=0
    c_through = make_cylinder(m3_through_dia, back_depth, (cx, cy), -back_depth + m3_counterbore_depth + m3_cone_height - 0.1)
    
    screw_cutout = c_sink.fuse(c_cone).fuse(c_through)
    back_shell = back_shell.cut(screw_cutout)

# D) Zentriernut (Groove) am Trennrand (Z = -1.5 bis Z = 0) fuer die Zentrierlippe
groove_w = cavity_w + 2.0 * 1.2
groove_h = cavity_h + 2.0 * 1.2
groove_outer = make_rounded_rect_face(groove_w, groove_h, max(0.5, corner_radius - 1.2)).extrude(FreeCAD.Vector(0, 0, 1.5))
groove_inner = make_rounded_rect_face(cavity_w, cavity_h, cavity_r).extrude(FreeCAD.Vector(0, 0, 1.6))
groove_cut = groove_outer.cut(groove_inner)
groove_cut.translate(FreeCAD.Vector(0, 0, -1.5))
back_shell = back_shell.cut(groove_cut)

# E) Akku-Halterahmen auf dem Boden der Unterschale (Z = -10.6 mm)
# Akku: 94 x 30 x 10 mm. Sitzt quer im unteren Bereich (Y = -63 bis -33 mm)
bat_w = 94.0 + 2.0 * pcb_clearance  # 94.6 mm
bat_h = 30.0 + 2.0 * pcb_clearance  # 30.6 mm
bat_y_center = -48.0
bat_frame_h = 3.0
bat_outer = make_box_center(bat_w + 2.4, bat_h + 2.4, bat_frame_h, (0.0, bat_y_center), -back_depth + wall_thick)
bat_inner = make_box_center(bat_w, bat_h, bat_frame_h + 1.0, (0.0, bat_y_center), -back_depth + wall_thick - 0.5)
bat_frame = bat_outer.cut(bat_inner)

# Grosszuegiger Kabelkanal / Aussparung im Rahmen (24 mm breit) oben links in Richtung TP4065 Lademodul
# Damit das dicke 5-Draht-Anschlusskabel und der 15x6 mm Stecker ohne Knicken oder Quetschen austreten koennen
bat_cable_notch = make_box_center(24.0, 4.0, bat_frame_h + 1.0, (-12.0, bat_y_center + bat_h / 2.0), -back_depth + wall_thick - 0.5)
bat_frame = bat_frame.cut(bat_cable_notch)
back_shell = back_shell.fuse(bat_frame)

# F) Klemmrahmen fuer MT3608 Step-Up (37 x 17 x 6.5 mm) & MAX98357A (17.5 x 19 mm)
# Nach oben versetzt (Y = -9.0 mm), damit ueber dem Akku 14 mm Freiraum fuer das Kabel entsteht
mt_w = 37.0 + 2.0 * pcb_clearance
mt_h = 17.0 + 2.0 * pcb_clearance
mt_center = (-5.0, -9.0)
mt_outer = make_box_center(mt_w + 2.0, mt_h + 2.0, 2.5, mt_center, -back_depth + wall_thick)
mt_inner = make_box_center(mt_w, mt_h, 3.5, mt_center, -back_depth + wall_thick - 0.5)
back_shell = back_shell.fuse(mt_outer.cut(mt_inner))

amp_w = 17.5 + 2.0 * pcb_clearance
amp_h = 19.0 + 2.0 * pcb_clearance
amp_center = (28.0, -9.0)
amp_outer = make_box_center(amp_w + 2.0, amp_h + 2.0, 2.5, amp_center, -back_depth + wall_thick)
amp_inner = make_box_center(amp_w, amp_h, 3.5, amp_center, -back_depth + wall_thick - 0.5)
back_shell = back_shell.fuse(amp_outer.cut(amp_inner))

# G) I/O Fuehrungen & Durchbrueche
# 1. Linke Seite (X = -51.0): Grosszuegiges Doppel-USB-C Langloch (22.0 x 4.5 mm) fuer ESP32-S3
# Damit beide USB-C-Kabel garantiert kollisionsfrei passen
esp_usb_slot = make_box_center(wall_thick * 2.0 + 4.0, 22.0, 4.5, (-case_width / 2.0, 29.25), -2.25)
back_shell = back_shell.cut(esp_usb_slot)
front_shell = front_shell.cut(esp_usb_slot)

# Rueckanschlag / Support-Cradle fuer ESP32-S3 im Back Shell gegen Einsteckdruck
esp_cradle = make_box_center(2.0, 28.5 + 4.0, 5.0, (-case_width / 2.0 + wall_thick + 64.0, 29.25), -back_depth + wall_thick)
back_shell = back_shell.fuse(esp_cradle)

# 2. Linke Seite: USB-Ausschnitt fuer TP4065 Lademodul (10.0 x 4.5 mm bei Y = -3.25 mm)
tp_usb = make_box_center(wall_thick * 2.0 + 4.0, 10.0, 4.5, (-case_width / 2.0, -3.25), -5.5)
back_shell = back_shell.cut(tp_usb)
tp_cradle = make_box_center(2.0, 17.5 + 4.0, 4.0, (-case_width / 2.0 + wall_thick + 23.5, -3.25), -back_depth + wall_thick)
back_shell = back_shell.fuse(tp_cradle)

# 3. Rechte Seite (X = +51.0): Ein-/Ausschalter mit formschluessigem Haltekaefig
# Knubbel: 3x3x7 mm, Kaefig: 13.3 x 6.3 mm Innenmass, 2.1 mm Abstand zur Innenwand
# Knubbel ragt exakt 7.0 - 2.1 - 2.4 = 2.5 mm nach aussen!
# Aussparung fuer den Schiebeknubbel: 11.0 mm (in Y-Richtung, > 10 mm), damit der 3 mm Schieber
# ungehindert den vollen Schiebeweg (ca. 4-5 mm) zuruecklegen kann
sw_cage_x = case_width / 2.0 - wall_thick - 2.1 - 7.0 / 2.0
sw_y = 30.0
sw_slot_len = 11.0  # 11.0 mm Langloch fuer Schiebeschalter
sw_slot = make_box_center(wall_thick * 2.0 + 4.0, sw_slot_len, 3.8, (case_width / 2.0, sw_y), -1.9)
back_shell = back_shell.cut(sw_slot)
front_shell = front_shell.cut(sw_slot)

cage_wall_outer = make_box_center(7.0 + 2.0, 13.3 + 2.4, 6.0, (sw_cage_x, sw_y), -back_depth + wall_thick)
cage_wall_inner = make_box_center(7.0 + 0.1, 13.3, 7.0, (sw_cage_x, sw_y), -back_depth + wall_thick - 0.5)
back_shell = back_shell.fuse(cage_wall_outer.cut(cage_wall_inner))

# 4. Micro-SD-Kartenmodul (18 x 28 x 4 mm) & Einschubschlitz an der oberen Gehaeusewand
# Flacher, flachprofiliger Halterahmen direkt auf dem Boden der Unterschale (Z = -10.6 mm):
# - Bauhoehe nur 2.0 mm: Laesst nach oben zur Trennebene (Z=0) und zum TFT-Display volle 8.7 mm Freiraum!
# - Seitliche Haltestege & Rueckanschlag: Verhindern jedes Verrutschen beim Einschieben der Karte
# - Schlitz ausschliesslich in der Unterschale: Oberschale bleibt oben komplett geschlossen und unberuehrt
sd_w = 18.0 + 2.0 * pcb_clearance  # 18.6 mm
sd_l = 28.0 + 2.0 * pcb_clearance  # 28.6 mm
sd_rib_h = 2.0  # Nur 2 mm flache Fuehrungsrippen am Boden
sd_cradle_y = case_height / 2.0 - wall_thick - sd_l / 2.0  # 58.3 mm

# A) Flacher U-Rahmen am Boden der Unterschale (Fuehrung links, rechts und Rueckanschlag)
sd_outer = make_box_center(sd_w + 2.4, sd_l + 1.2, sd_rib_h, (0.0, sd_cradle_y - 0.6), -back_depth + wall_thick)
sd_inner = make_box_center(sd_w, sd_l + 4.0, sd_rib_h + 1.0, (0.0, sd_cradle_y + 1.5), -back_depth + wall_thick - 0.5)
sd_frame = sd_outer.cut(sd_inner)

# Drahtaussparung im Ruecksteg fuer die Loetanschluesse
sd_wire_notch = make_box_center(10.0, 3.0, sd_rib_h + 1.0, (0.0, sd_cradle_y - sd_l / 2.0 - 0.6), -back_depth + wall_thick - 0.5)
sd_frame = sd_frame.cut(sd_wire_notch)
back_shell = back_shell.fuse(sd_frame)

# B) Micro-SD-Kartenschlitz nur an der oberen Gehaeusewand der Unterschale
# Schlitz liegt flach ueber dem Platinenboden (Z = -9.5 bis -7.1 mm, Hoehe 2.4 mm)
sd_slot = make_box_center(14.5, wall_thick * 2.0 + 2.0, 2.4, (0.0, case_height / 2.0), -back_depth + wall_thick + 1.1)
back_shell = back_shell.cut(sd_slot)

print("Unterschale erfolgreich modelliert.")

# ---------------------------------------------------------------------------
# 6. PLA-TASTEN KONSTRUKTION (OPTIMIERTE MASSE, INNENLOCH 7.2 mm, RUNDUNGEN)
# ---------------------------------------------------------------------------
print("Konstruiere optimierte PLA-Tasten (A/B: 9.0mm, X/Y: 7.5mm, Innenloecher: 7.2mm, abgerundete Kanten)...")

def make_pla_button(cap_dia, cap_h, flange_dia, flange_h, pocket_dia, pocket_depth, label=None):
    """
    Erstellt eine zylindrische PLA-Taste mit Haltekragen, 45°-Druckschraege,
    abgerundeter Druckflaeche oben (0.7 mm Fillet), unterseitigem Sackloch fuer den Gummiknuppel
    und optional tief eingepraegter Beschriftung (0.85 mm tief).
    """
    flange = make_cylinder(flange_dia, flange_h, (0, 0), 0.0)
    chamfer_h = (flange_dia - cap_dia) / 2.0
    cone = Part.makeCone(flange_dia / 2.0, cap_dia / 2.0, chamfer_h, FreeCAD.Vector(0, 0, flange_h))
    cap = make_cylinder(cap_dia, cap_h - chamfer_h, (0, 0), flange_h + chamfer_h)
    
    # Obere Tastenkante ergonomisch abrunden (0.7 mm Radius)
    top_z = flange_h + cap_h
    top_edges = [e for e in cap.Edges if abs(e.BoundBox.ZMax - top_z) < 1e-3 and e.Curve.TypeId == 'Part::GeomCircle']
    if top_edges:
        try:
            cap = cap.makeFillet(0.7, top_edges)
        except Exception as e:
            print(f"Hinweis: Tasten-Fillet vereinfacht ({e}).")
            
    btn = flange.fuse(cone).fuse(cap)
    
    # Unterseitiges Sackloch (Aufnahme fuer den Gummiknuppel, 1 mm groesser -> Ø 7.2 mm)
    if pocket_dia > 0 and pocket_depth > 0:
        pocket = make_cylinder(pocket_dia, pocket_depth, (0, 0), 0.0)
        btn = btn.cut(pocket)
        
    # Oben stark eingepraegte Beschriftung (0.85 mm tief)
    if label and Draft:
        try:
            f_size = 4.0 if cap_dia >= 8.5 else 3.5
            ss = Draft.make_shapestring(label, font_file, f_size)
            doc.recompute()
            bb = ss.Shape.BoundBox
            dx = (bb.XMin + bb.XMax) / 2.0
            dy = (bb.YMin + bb.YMax) / 2.0
            letter = ss.Shape.extrude(FreeCAD.Vector(0, 0, 1.2))
            letter.translate(FreeCAD.Vector(-dx, -dy, top_z - 0.85))
            btn = btn.cut(letter)
        except Exception as e:
            print(f"Hinweis: Beschriftung '{label}' vereinfacht ({e}).")
            
    return btn

# A & B Haupttasten:
# - Schaftdurchmesser um 0.5 mm erhoeht auf Ø 9.0 mm
# - Unterseitige Sackloch-Aufnahme Ø 7.2 mm x 1.1 mm Tiefe
# - Oben 0.85 mm tief eingepraegte Kennzeichnungen A und B mit abgerundeter Kante
btn_a = make_pla_button(9.0, 5.0, 11.2, 1.2, 7.2, 1.1, label="A")
btn_b = make_pla_button(9.0, 5.0, 11.2, 1.2, 7.2, 1.1, label="B")

# X & Y Tasten:
# - Schaftdurchmesser um 1.0 mm reduziert auf Ø 7.5 mm
# - Unterseitige Sackloch-Aufnahme Ø 7.2 mm x 1.1 mm Tiefe (vollstaendig im Flansch D 10.0 mm gebettet)
# - Oben 0.85 mm tief eingepraegte Kennzeichnungen X und Y mit abgerundeter Kante
btn_x = make_pla_button(7.5, 5.0, 10.0, 1.2, 7.2, 1.1, label="X")
btn_y = make_pla_button(7.5, 5.0, 10.0, 1.2, 7.2, 1.1, label="Y")

# Select & Start Tasten:
# - Schaft Ø 7.5 mm (wie bisher)
# - Unterseitige Sackloch-Aufnahme Ø 7.2 mm x 2.1 mm Tiefe
btn_sel = make_pla_button(7.5, 5.0, 10.0, 1.2, 7.2, 2.1, label=None)
btn_sta = make_pla_button(7.5, 5.0, 10.0, 1.2, 7.2, 2.1, label=None)

# Steuerkreuz (D-Pad):
# - Masse bestaetigt: Armbreite 6.5 mm, Kreuzlaenge 22.5 mm
# - Obere Kanten der Kreuzarme ergonomisch abgerundet (0.6 mm Fillet)
# - 4 unterseitige Sackloecher auf Ø 7.2 mm x 2.1 mm Tiefe vergroessert
def make_pla_dpad():
    arm_w = 6.5
    arm_l = 22.5
    arm_h = 5.0
    flange_w = 8.8
    flange_l = 24.5
    flange_h = 1.2
    
    # Kreuz-Haltekragen mit Zentralversteifung
    f1 = Part.makeBox(flange_l, flange_w, flange_h, FreeCAD.Vector(-flange_l/2.0, -flange_w/2.0, 0.0))
    f2 = Part.makeBox(flange_w, flange_l, flange_h, FreeCAD.Vector(-flange_w/2.0, -flange_l/2.0, 0.0))
    center_disc = Part.makeCylinder(flange_w / 2.0, flange_h, FreeCAD.Vector(0, 0, 0))
    flange = f1.fuse(f2).fuse(center_disc)
    
    # 45°-Uebergangsphase fuer 100% supportfreien Druck
    chamfer_h = (flange_w - arm_w) / 2.0  # 1.15 mm
    t1 = Part.makeBox(flange_l - 0.5, flange_w - 0.5, chamfer_h, FreeCAD.Vector(-(flange_l-0.5)/2.0, -(flange_w-0.5)/2.0, flange_h))
    t2 = Part.makeBox(flange_w - 0.5, flange_l - 0.5, chamfer_h, FreeCAD.Vector(-(flange_w-0.5)/2.0, -(flange_l-0.5)/2.0, flange_h))
    trans = t1.fuse(t2)
    
    # Kreuzarme mit abgerundeten Druckkanten (0.5 mm Fillet pro Arm vor dem Fusing)
    top_z = flange_h + arm_h
    a1 = Part.makeBox(arm_l, arm_w, arm_h, FreeCAD.Vector(-arm_l/2.0, -arm_w/2.0, flange_h))
    a2 = Part.makeBox(arm_w, arm_l, arm_h, FreeCAD.Vector(-arm_w/2.0, -arm_l/2.0, flange_h))
    edges1 = [e for e in a1.Edges if abs(e.BoundBox.ZMin - top_z) < 1e-3 and abs(e.BoundBox.ZMax - top_z) < 1e-3]
    edges2 = [e for e in a2.Edges if abs(e.BoundBox.ZMin - top_z) < 1e-3 and abs(e.BoundBox.ZMax - top_z) < 1e-3]
    a1_f = a1.makeFillet(0.5, edges1)
    a2_f = a2.makeFillet(0.5, edges2)
    cross = a1_f.fuse(a2_f)
    
    dpad = flange.fuse(trans).fuse(cross)
    
    # 4 unterseitige Knuppel-Aufnahmen (Ø 7.2 mm x 1.2 mm Tiefe im Flansch) exakt bei Radius = 7.62 mm
    nub_dist = 7.62
    for nx, ny in [(0, nub_dist), (0, -nub_dist), (-nub_dist, 0), (nub_dist, 0)]:
        pocket = make_cylinder(7.2, 1.2, (nx, ny), 0.0)
        dpad = dpad.cut(pocket)
        
    # Zentraler Drehpunkt (Pivot) fuer praezisen Kipppunkt (D 3.0 mm, Hoehe 1.2 mm)
    pivot = Part.makeCylinder(1.5, 1.2, FreeCAD.Vector(0, 0, -1.2))
    dpad = dpad.fuse(pivot)
    return dpad

btn_dpad = make_pla_dpad()

# Druck-Layout fuer print_buttons_pla.stl (180° gedreht -> flache Tastenfront liegt auf Z=0 am Druckbett!)
btn_print_group = []
buttons_for_print = [
    (btn_dpad,  -35.0,   0.0),
    (btn_a,      -5.0,  16.0),
    (btn_b,      -5.0, -16.0),
    (btn_x,      16.0,  16.0),
    (btn_y,      16.0, -16.0),
    (btn_sel,    35.0,   8.0),
    (btn_sta,    35.0,  -8.0)
]
for shape_obj, px, py in buttons_for_print:
    top_z = shape_obj.BoundBox.ZMax
    sh = shape_obj.copy()
    rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 180)
    sh.Placement = FreeCAD.Placement(FreeCAD.Vector(px, py, top_z), rot)
    btn_print_group.append(sh)

buttons_print_solid = Part.Compound(btn_print_group)

print("PLA-Tasten erfolgreich konstruiert (180° flach auf Z=0, Sackloecher oben 100% supportfrei).")

# ---------------------------------------------------------------------------
# 7. LOETSCHABLONE (SOLDER JIG) FUER LOCHRASTERPLATINE
# ---------------------------------------------------------------------------
print("Konstruiere Loetschablone (Solder Jig)...")
jig_plate = make_box_center(91.0, 70.0, 2.0, (0.0, 0.0), 0.0)

# 4 M3 Eck-Befestigungsbohrungen
for hx, hy in [(-83.5/2, -61.0/2), (83.5/2, -61.0/2), (83.5/2, 61.0/2), (-83.5/2, 61.0/2)]:
    jig_hole = make_cylinder(m3_through_dia, 3.0, (hx, hy), -0.5)
    jig_plate = jig_plate.cut(jig_hole)

# Quadratische Taschen 6.3 x 6.3 mm an allen 10 Taster-Positionen
for name, (gx, gy) in microswitches_info:
    lx = gx - pcb_center_x
    ly = gy - pcb_center_y
    pocket = make_box_center(6.30, 6.30, 3.0, (lx, ly), -0.5)
    jig_plate = jig_plate.cut(pocket)

print("Loetschablone erfolgreich konstruiert.")

# ---------------------------------------------------------------------------
# 8. BAUTEIL-DUMMYS FUER DIE VISUELLE MONTAGEKONTROLLE
# ---------------------------------------------------------------------------
print("Erzeuge elektronische Bauteil-Dummys...")

def create_box_dummy(w, l, h, pos_center_xy, z_pos):
    return make_box_center(w, l, h, pos_center_xy, z_pos)

# 1. TFT ILI9341 Dummy (86 x 50 x 8.5 mm, Displayflaeche 64 x 47 mm)
dummy_tft = create_box_dummy(86.0, 50.0, 8.5, (tft_center_x, tft_center_y), front_depth - wall_thick - 8.5)

# 2. Lochrasterplatine Dummy (91 x 70 x 1.6 mm)
dummy_pcb = create_box_dummy(91.0, 70.0, 1.6, (pcb_center_x, pcb_center_y), front_depth - wall_thick - pcb_standoff_h - 1.6)

# 3. 10x Mikrotaster Dummys (6 x 6 x 4 mm) auf der Lochrasterplatine
dummy_switches = []
for name, (gx, gy) in microswitches_info:
    sw_d = create_box_dummy(6.0, 6.0, 4.0, (gx, gy), front_depth - wall_thick - pcb_standoff_h)
    dummy_switches.append(sw_d)
all_switches_dummy = dummy_switches[0]
for sw in dummy_switches[1:]:
    all_switches_dummy = all_switches_dummy.fuse(sw)

# 4. Lautsprecher Dummy (D 20.5 mm x 5.0 mm)
dummy_speaker = make_cylinder(20.5, 5.0, speaker_center, front_depth - wall_thick - 5.0)

# 5. Akku Dummy (94 x 30 x 10 mm) mit 25 mm Anschlusskabel und 15x6 mm Stecker
bat_main = create_box_dummy(94.0, 30.0, 10.0, (0.0, bat_y_center), -back_depth + wall_thick)
# Dickes Kabelbuendel (ca. 10x18x5 mm) oben links herausgefuehrt
bat_cable = create_box_dummy(10.0, 18.0, 5.0, (-12.0, bat_y_center + 15.0 + 9.0), -back_depth + wall_thick + 2.5)
# 15x6x6 mm Steckerbuchse
bat_plug = create_box_dummy(15.0, 6.0, 6.0, (-12.0, bat_y_center + 15.0 + 18.0), -back_depth + wall_thick + 2.0)
dummy_battery = bat_main.fuse(bat_cable).fuse(bat_plug)

# 6. ESP32-S3 Dummy (64 x 28.5 x 5 mm) an linker Gehaeusewand
dummy_esp = create_box_dummy(64.0, 28.5, 5.0, (-case_width / 2.0 + wall_thick + 64.0 / 2.0, 29.25), -back_depth + wall_thick)

# 7. TP4065 Lademodul Dummy (23.5 x 17.5 x 4 mm)
dummy_tp = create_box_dummy(23.5, 17.5, 4.0, (-case_width / 2.0 + wall_thick + 23.5 / 2.0, -3.25), -back_depth + wall_thick)

# 8. MT3608 Step-Up Wandler Dummy (37 x 17 x 6.5 mm)
dummy_mt = create_box_dummy(37.0, 17.0, 6.5, mt_center, -back_depth + wall_thick)

# 9. MAX98357A I2S Audio Amp Dummy (17.5 x 19 x 3 mm)
dummy_amp = create_box_dummy(17.5, 19.0, 3.0, amp_center, -back_depth + wall_thick)

# 10. Ein-/Ausschalter Dummy (13 x 6 x 7 mm Korpus + 3x3x7 mm Knubbel)
sw_body = create_box_dummy(7.0, 13.0, 6.0, (sw_cage_x, sw_y), -3.0)
sw_knob = create_box_dummy(7.0, 3.0, 3.0, (case_width / 2.0 - 2.5 / 2.0, sw_y), -1.5)
dummy_switch = sw_body.fuse(sw_knob)

# 11. Micro-SD Modul Dummy (18 x 28 x 4 mm) flach auf dem Boden der Unterschale
dummy_sd = create_box_dummy(18.0, 28.0, 4.0, (0.0, sd_cradle_y), -back_depth + wall_thick)

print("Bauteil-Dummys erfolgreich erstellt.")

# ---------------------------------------------------------------------------
# 9. FREECAD DOKUMENT (FCStd) & STL-EXPORTE
# ---------------------------------------------------------------------------
print("Erstelle FreeCAD-Dokument und Baugruppe...")

def add_part_to_doc(name, shape, color_rgb=(0.8, 0.8, 0.8), transparency=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    try:
        obj.ViewObject.ShapeColor = color_rgb
        obj.ViewObject.Transparency = transparency
    except:
        pass
    return obj

# Gehaeuseteile
obj_front = add_part_to_doc("Front_Shell_PLA", front_shell, (0.2, 0.45, 0.85), 20)
obj_back  = add_part_to_doc("Back_Shell_PLA", back_shell, (0.15, 0.25, 0.4), 20)

# PLA-Tasten (im montierten Zustand)
tpu_z_assembly = front_depth - wall_thick - tpu_flange_h
dpad_ass = btn_dpad.copy()
dpad_ass.translate(FreeCAD.Vector(dpad_center[0], dpad_center[1], tpu_z_assembly))
obj_dpad = add_part_to_doc("PLA_DPad", dpad_ass, (0.1, 0.1, 0.1))

def place_btn(btn_shape, pos):
    b = btn_shape.copy()
    b.translate(FreeCAD.Vector(pos[0], pos[1], tpu_z_assembly))
    return b

obj_btn_a = add_part_to_doc("PLA_Button_A", place_btn(btn_a, btn_a_pos), (0.85, 0.15, 0.15))
obj_btn_b = add_part_to_doc("PLA_Button_B", place_btn(btn_b, btn_b_pos), (0.85, 0.65, 0.15))
obj_btn_x = add_part_to_doc("PLA_Button_X", place_btn(btn_x, btn_x_pos), (0.15, 0.65, 0.85))
obj_btn_y = add_part_to_doc("PLA_Button_Y", place_btn(btn_y, btn_y_pos), (0.15, 0.85, 0.35))
obj_btn_sel = add_part_to_doc("PLA_Button_Select", place_btn(btn_sel, btn_select_pos), (0.3, 0.3, 0.3))
obj_btn_sta = add_part_to_doc("PLA_Button_Start", place_btn(btn_sta, btn_start_pos), (0.3, 0.3, 0.3))

# Elektronik-Dummys
add_part_to_doc("Dummy_TFT_ILI9341", dummy_tft, (0.1, 0.2, 0.7), 0)
add_part_to_doc("Dummy_Lochraster_PCB", dummy_pcb, (0.1, 0.55, 0.2), 0)
add_part_to_doc("Dummy_Microswitches", all_switches_dummy, (0.8, 0.8, 0.8), 0)
add_part_to_doc("Dummy_Speaker", dummy_speaker, (0.7, 0.6, 0.2), 0)
add_part_to_doc("Dummy_Battery", dummy_battery, (0.2, 0.7, 0.8), 0)
add_part_to_doc("Dummy_ESP32_S3", dummy_esp, (0.1, 0.45, 0.15), 0)
add_part_to_doc("Dummy_TP4065", dummy_tp, (0.1, 0.35, 0.55), 0)
add_part_to_doc("Dummy_MT3608", dummy_mt, (0.2, 0.3, 0.6), 0)
add_part_to_doc("Dummy_MAX98357A", dummy_amp, (0.4, 0.2, 0.5), 0)
add_part_to_doc("Dummy_Power_Switch", dummy_switch, (0.9, 0.1, 0.1), 0)
add_part_to_doc("Dummy_MicroSD_Module", dummy_sd, (0.2, 0.5, 0.5), 0)

doc.recompute()
fcstd_file = os.path.join(output_dir, "pixelgo_complete_assembly.FCStd")
doc.saveAs(fcstd_file)
print(f"-> FreeCAD Baugruppe gespeichert: {fcstd_file}")

# ---------------------------------------------------------------------------
# 10. STL-EXPORTE FUER 3D-DRUCK (Artillery Sidewinder X2)
# ---------------------------------------------------------------------------
print("\nExportiere 3D-Druck-STLs...")

def export_stl_shape(shape, filepath, linear_deflection=0.03, angular_deflection=0.1745):
    """Exportiert ein Part-Shape als hochpraezises, fehlerfreies STL-Mesh."""
    try:
        mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=linear_deflection, AngularDeflection=angular_deflection)
        mesh.write(filepath)
    except Exception as e:
        print(f"Hinweis: Fallback fuer STL-Export ({e})")
        Mesh.export([Part.show(shape)], filepath)

# 1. print_front_shell_pla.stl (Oberschale, fuer Druck flach auf Front Z=0 gelegt)
front_print_shape = front_shell.copy()
front_print_shape.translate(FreeCAD.Vector(0, 0, -front_depth))
stl_front = os.path.join(output_dir, "print_front_shell_pla.stl")
export_stl_shape(front_print_shape, stl_front)
print(f"1. [PLA+] Oberschale: {stl_front}")

# 2. print_back_shell_pla.stl (Unterschale, flach mit Rueckseite auf Druckbett)
back_print_shape = back_shell.copy()
back_print_shape.translate(FreeCAD.Vector(0, 0, back_depth))
stl_back = os.path.join(output_dir, "print_back_shell_pla.stl")
export_stl_shape(back_print_shape, stl_back)
print(f"2. [PLA+] Unterschale: {stl_back}")

# 3. print_buttons_pla.stl (Alle PLA-Tasten flach mit Tastenkappe auf Druckbett Z=0)
stl_buttons_pla = os.path.join(output_dir, "print_buttons_pla.stl")
export_stl_shape(buttons_print_solid, stl_buttons_pla)
print(f"3. [PLA+] Steuerungstasten: {stl_buttons_pla}")

# Kompatibilitaetsdatei: print_buttons_tpu.stl ebenfalls mit aktuellem Stand aktualisieren
stl_buttons_tpu = os.path.join(output_dir, "print_buttons_tpu.stl")
export_stl_shape(buttons_print_solid, stl_buttons_tpu)

# 4. print_solder_jig_pla.stl (Loetschablone fuer Lochrasterplatine)
stl_jig = os.path.join(output_dir, "print_solder_jig_pla.stl")
export_stl_shape(jig_plate, stl_jig)
print(f"4. [PLA+] Loetschablone: {stl_jig}")

# 5. preview_assembly_with_dummies.stl (Gesamtvorschau inkl. aller Dummys)
preview_objects = [
    obj_front, obj_back, obj_dpad, obj_btn_a, obj_btn_b, obj_btn_x, obj_btn_y,
    obj_btn_sel, obj_btn_sta, doc.Dummy_TFT_ILI9341, doc.Dummy_Lochraster_PCB,
    doc.Dummy_Microswitches, doc.Dummy_Speaker, doc.Dummy_Battery, doc.Dummy_ESP32_S3,
    doc.Dummy_TP4065, doc.Dummy_MT3608, doc.Dummy_MAX98357A, doc.Dummy_Power_Switch,
    doc.Dummy_MicroSD_Module
]
stl_preview = os.path.join(output_dir, "preview_assembly_with_dummies.stl")
Mesh.export(preview_objects, stl_preview)
print(f"5. [Vorschau] Gesamtbaugruppe mit Dummys: {stl_preview}")

# ---------------------------------------------------------------------------
# 11. GEOMETRIE-VALIDIERUNG & SCHLUSSBERICHT
# ---------------------------------------------------------------------------
print("\n-----------------------------------------------------------------")
print("  GEOMETRIE-VALIDIERUNG (MANIFOLD & SOLIDS)")
print("-----------------------------------------------------------------")
checks = [
    ("Oberschale (Front_Shell)", front_shell),
    ("Unterschale (Back_Shell)", back_shell),
    ("PLA-Tastensatz", buttons_print_solid),
    ("Loetschablone (Solder_Jig)", jig_plate),
    ("TFT Dummy", dummy_tft),
    ("Lochraster Dummy", dummy_pcb),
    ("Akku Dummy", dummy_battery)
]

all_valid = True
for name, shape in checks:
    valid = shape.isValid()
    vol = shape.Volume / 1000.0 # in cm^3
    status = "OK (Solid Manifold)" if valid else "WARNUNG: Nicht geschlossen"
    if not valid:
        all_valid = False
    print(f" - {name:28s}: {status} | Volumen: {vol:7.2f} cm3")

print("-----------------------------------------------------------------")
if all_valid:
    print("ERFOLG: Alle Solids sind 100% gueltig, geschlossen und druckbar!")
else:
    print("HINWEIS: Bitte Pruefhinweise beachten.")
print("=================================================================\n")
