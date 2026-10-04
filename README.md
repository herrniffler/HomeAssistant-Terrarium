<picture>
  <source media="(prefers-color-scheme: dark)" srcset="custom_components/terrarium/brand/dark_logo@2x.png">
  <img alt="Terrarium" src="custom_components/terrarium/brand/logo@2x.png" height="64">
</picture>

# Terrarium für Home Assistant

Artprofile, Sollbereiche, Pflege-Log, Lichtsteuerung und Beregnung pro Terrarium (Idee: OpenPlantbook, aber für Terrarien).

## Installation
- HACS → Custom repository (Integration) oder `custom_components/terrarium` nach `/config/custom_components/` kopieren
- Neustart, dann *Einstellungen → Geräte & Dienste → Terrarium*

## Einrichtung
Beim Anlegen (und später unter *Konfigurieren*) wählst du ein Artprofil und optional:
- **Temperatursensoren** (warme Seite bzw. alle) und **Temperatursensoren kalte Seite** (für Gradienten)
- **Luftfeuchtesensoren**
- **Beregnungs-Schalter**: Einschalten stempelt "zuletzt besprüht"; Voraussetzung für die automatische Beregnung
- **Licht-Schalter**: werden nach den Lichtzeiten geschaltet

Alles ist optional. Ohne Sensoren zeigt der Status "keine Daten".

## Pro Terrarium entsteht ein Gerät mit
**Überwachung**
- **Status** (ok / zu warm / zu kalt / kalte Seite zu warm / kalte Seite zu kalt / kein Gradient / zu trocken / zu feucht / keine Daten) und **Außerhalb Sollbereich**
- **Temperatur**, **Luftfeuchte** (Mittelwert der Sensoren, `min`/`max` als Attribute), mit kalter Seite zusätzlich **Temperatur kalte Seite** und **Gradient**
- **Sollwerte** als `number`, vorbelegt aus dem Artprofil: Temperatur und Luftfeuchte min/max für Tag und Nacht, Fütterungsintervall

**Tag und Nacht**
- **Licht an / Licht aus** (`time`): dazwischen ist Tag, sonst Nacht. Der Status prüft gegen die Sollwerte der aktuellen Phase. Sensor **Tag** zeigt die Phase.
- Die Lichtzeiten können von einer eigenen Automation gesetzt werden (`time.set_value`), z. B. aus Sonnenstand oder Strompreis.

**Gradient (nur mit Sensoren für die kalte Seite)**
- `Temperatur min/max` gelten dann für die warme Seite, dazu eigene Werte für die kalte Seite und ein **Mindest-Gradient** (warm minus kalt, nur am Tag geprüft, 0 = aus).
- Ohne Sensoren für die kalte Seite gilt eine Spanne für alle Sensoren.

**Pflege-Log**
- Zuletzt gefüttert / gehäutet / besprüht (`datetime`) plus Buttons zum Abstempeln
- **Fütterung fällig** und **Nächste Fütterung**

**Lichtsteuerung** (mit Licht-Schaltern)
- Die Schalter folgen den Lichtzeiten. Nach dem Schalten wird der Zustand geprüft: 3 Versuche im Abstand von 5 s, 12 Minuten Pause, 3 weitere Versuche, danach **Lichtstörung**.
- **Lichtautomatik** schaltet das ein oder aus.

**Abkühlung** (mit Licht-Schaltern)
- Liegt die warme Seite 5 Minuten über **Abkühlung ab** (0 = aus), geht das Licht aus (**Kühlt ab**).
- Es geht wieder an, wenn die warme Seite darunter liegt und der Unterschied zur kältesten Messung kleiner als **max. Differenz warm/kalt** ist, 10 Minuten lang. Timeout nach 4 Stunden, Tagesende beendet die Abkühlung ebenfalls. Der Zustand überlebt einen Neustart.

**Automatische Beregnung** (mit Beregnungs-Schalter)
- Schalter **Automatische Beregnung**: Ist er an und die Luftfeuchte unter **Beregnen unter**, wird der Beregnungs-Schalter für **Beregnungsdauer** eingeschaltet (nur am Tag). Zwischen zwei Beregnungen liegt mindestens der **Mindestabstand**; auch manuelles Beregnen zählt dafür.

## Events für Automationen
Das Event `terrarium_event` hat die Felder `terrarium` (Name), `entry_id` und `type`:
`cooling_started`, `cooling_ended`, `light_fault`, `light_fault_cleared`, `misting_started`.
Damit lassen sich Benachrichtigungen bauen, die Integration verschickt selbst keine.

## Eigene Artprofile
`/config/terrarium_species.json` (überschreibt/ergänzt die mitgelieferten):

```json
{
  "mein_tier": {
    "name": "Genus species", "common": "Trivialname",
    "temp_min": 20, "temp_max": 30,
    "humidity_min": 50, "humidity_max": 80,
    "feeding_interval": 3,
    "cold_temp_min": 20, "cold_temp_max": 26, "gradient_min": 3
  }
}
```

Optional sind alle Felder außer `name`: `cold_temp_min`, `cold_temp_max`, `gradient_min` (kalte Seite), sowie Nachtwerte `temp_min_night`, `temp_max_night`, `humidity_min_night`, `humidity_max_night` (sonst gleich den Tagwerten).

## Hinweise
- Die mitgelieferten Werte sind grobe Startwerte (`"verified": false`), bitte gegen die eigene Haltung prüfen.
- Temperaturen werden in °C verglichen.
- Ein Wechsel des Artprofils setzt die Sollwerte auf die Profilwerte zurück.
