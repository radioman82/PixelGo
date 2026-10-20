Beschreibung des pixelgo für den 3D Druck

Aufgabe: Es soll ein gameboyähnliches Gehäuse aus pla+ mit einem artillery sidewinder x2 erstellt und gedruckt werden ungefähr mit den Massen 140mmx100mm – als Orientierung. Das Gehäuse soll aussen abgerundete Ecken haben. Das Gehäuse soll professionellen Ansprüchen genügen. Als CAD Programm kommt FreeCad zum Einsatz. Die exe liegt hier: "C:\Program Files\FreeCAD 1.1\bin\freecad.exe" . Alle notwendigen Dateien sind hier gespeichert. D:\Arduino_portable\Projekte\retrogo\pixelgo\3ddruck. Von allen Boards sind fotos im Ordner abgelegt. Die Steuerungstasten werden aus TPU selbst gedruckt, dafür braucht man auch entsprechende Druckdateien. Vorab sollen von den Boards, Tasten usw. Dummys erstellt werden und in den fertigen stl dateien gelegt werden, damit man einen Überblich erhält, wie alles angeordnet ist. Alle Boards haben keine Stiftleiste. Es wird alles mit Klingeldraht verdrahtet. Das TP4065 board hat einen flachen USB Anschluss, das esp32S3 n16R8 hat 2 USB-C Anschlüsse, beide Boards müssen mit den usb Anshlüssen an der Seite nach aussen geführt werden. Verwendet wird ein SD Card Modul für micro SD card. Die sd card muss entweder auch von aussen erreichbar sein oder so im inneren verbaut sein, dass man sie ohne Probleme entnehmen kann. 
Bitte die schrumpungstoleranz bei pla+ von anycubic sowie beim tpu mit einrechnen. Gedruckt wird pla+ mit 200Grad nozzel und 70Grad bed.
Über dem TFT auf der Vorderseite den schriftzug pixelgo-01 aufprägen. Größe muss moderat aber erkennbar sein
Steurungstasten: Steuerkreuz aus tpu ca 24*24*5 (beim gamepad hat das steuerkreuz unten eine runde Fläche, damit das in der ausparung hält
Taster für A,B,X,Y – Größe der TPU Taster 10x6
Wenn notwendig können X,Y auch kleiner gewählt werden sie sind für Option und Menü zuständig
Select und Start – auch rund aber kleiner z.b. 8*6
Gemessen an der größe der TPU Taster und des Kreuzes müssen auf der Lochrasteplatte zielgenau die microtaster plaziert werden. Die TPU Knöpfe müssen so gestaltet werden dass ein eindeutiger druckpunkt auf die microtaster erzielt wird. Dann müssen im Gehäuse die 4 Befestigungspunkte für die Lochrasteplatte so von der höhe gewählt werden das die knöpfe die steuertasten erreichen und gut drückbar sind.
Wenn möglich die Taster alle rund machen bis auf das steuerkreuz und so anordnen wie auf dem klassischen Gameboy. 
Die Tastenknöpfe beim tpu am besten oben beschriften mit A,B,X,Y, Sel, start. Wenn das nicht geht am besten die Beschriftung am gehäuse vornehmen. 

Inhalte die im Board verbau werden in mm
TFT 2,8Zoll ili9341 -86*50*8,5, die sichtbare Displayfläche soll 64*47 betragen. Die displayplatine hat 4 Löcher für m3 schrauben 76,5*44
TP4065 – 23,5x17,5x4
MT3608 37*17*6,5
Max98357a 17,5*19
Lautsprecher rund Durchmesser 20,5*5 – soll innen rechts unten am oberen gehäusedeckel angeklebt werden
Sdcard modul 18*28 (mit sdcard im schacht)*4
ESP32S3 64*28,5*5
Lochrasteplatte für Taster: 91*70. Die Lochrasteplatte hat 4 Löcher für m3 schrauben 83,5*61. Die Lochrastelöcher vom linken rand befinden sich 13mm und von unten 5mm von oben 6,5 von rechts 8,5. Die lochrasteplatte zwischen den anschlüssen hat 2,54mm.
Akku 94*30*10. Der Akku hat oben in der Mitte ein anschlusskabel von25mm länge die an einem 15mm breiten und 6mm dicken stecker mündet. Mit 5 drähten 2schwarz, ein weiss, 2 rot. Der  stecker sitzt in einer buchse mit lötpins an den der tp4065 angeschlossen wird
Microtaster 6*6*4
Einschalter: 13*6. Der einschaltknuppel ist 7mm lang rechteckig mit 3*3mm. Der einschalter muss irgendwie eingebettet werden an der seite, er kann nicht separat befestigt werden mit schrauben.Der einschaltknuppel soll auch nicht so weit nach aussen ragen.
