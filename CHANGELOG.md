# Changelog

## 0.2.0

Aus der reinen Überwachung wird eine Steuerung: Tag/Nacht, Licht, Abkühlung und Beregnung.

### Neu
- **Tag und Nacht:** Lichtzeiten als `time`-Entities, Sensor **Tag**, getrennte Sollwerte für Tag und Nacht. Die Zeiten lassen sich per Automation setzen (`time.set_value`).
- **Übergang:** Die Grenzen laufen nach Licht an/aus linear über die einstellbare **Übergang: Dauer** (Standard 2 h) von der alten zur neuen Phase, weil ein Terrarium langsam abkühlt und aufheizt.
- **Gradient:** Rollen **warme Seite** und **kalte Seite** mit eigenen Grenzen und Mindest-Gradient. Neuer Status *kalte Seite zu warm/kalt* und *kein Gradient*, Sensoren **Temperatur warm/kalt** und **Gradient**.
- **Luftfeuchte:** Luftsensoren bestimmen den Status (Mittelwert). Optionale **Boden-Sensoren** werden nur als **Luftfeuchte Boden** angezeigt.
- **Lichtsteuerung:** Schalter nach Zeitplan, auf die Sekunde genau. Prüfung nach dem Schalten mit Wiederholungen, **Licht: Störung**, **Licht: Automatik**. Die Entity **Licht** zeigt und schaltet die Licht-Schalter gemeinsam.
- **Abkühlung:** Das Licht bleibt aus, solange die warme Seite zu heiß ist. Der Zustand überlebt einen Neustart.
- **Beregnung:** Der Beregnungs-Schalter stempelt "zuletzt besprüht". **Beregnung: Automatik** beregnet nach Luftfeuchte (nur am Tag, mit Mindestabstand und einstellbarer Dauer).
- **Events:** `terrarium_event` (`cooling_started`, `cooling_ended`, `light_fault`, `light_fault_cleared`, `misting_started`) mit Name, Art und passenden Werten für Benachrichtigungen.
- Logo und Brand-Icons, README und Changelog.

### Geändert
- Entity-Namen folgen dem Schema "Thema: Eigenschaft" (z. B. *Abkühlung: ab Temperatur*, *Beregnung: Dauer*). Temperaturen heißen *Temperatur warm/kalt*. Die Entity-IDs bestehender Geräte bleiben unverändert.
- Die Artprofile haben jetzt Nacht- und Kalte-Seite-Werte und großzügigere Feuchte-Maxima.

### Hinweise
- Neue Einstellungen gelten für neu angelegte Geräte aus dem Artprofil. Bei bestehenden Geräten die Werte an den Number-Entities anpassen.
- Die Werte der mitgelieferten Artprofile sind grobe Startwerte (`"verified": false`).
- Temperaturen werden in °C verglichen.

## 0.1.0

Erste Version: Artprofile, Sollwerte für Temperatur und Luftfeuchte, Status, Pflege-Log mit Buttons, Fütterungsintervall.
