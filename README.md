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
- **Luftfeuchtesensoren** (Luft) und optional **Luftfeuchtesensoren Boden/unten**: Nur die Luftsensoren bestimmen Status und Beregnung. Die Boden-Sensoren hängen oft nah am feuchten Substrat und werden nur als **Luftfeuchte Boden** angezeigt.
- **Beregnungs-Schalter**: Einschalten stempelt "zuletzt besprüht"; Voraussetzung für die automatische Beregnung
- **Licht-Schalter**: werden nach den Lichtzeiten geschaltet

Alles ist optional. Ohne Sensoren zeigt der Status "keine Daten".

## Pro Terrarium entsteht ein Gerät mit
**Überwachung**
- **Status** (ok / zu warm / zu kalt / kalte Seite zu warm / kalte Seite zu kalt / kein Gradient / zu trocken / zu feucht / keine Daten) und **Außerhalb Sollbereich**
- **Temperatur warm**, **Luftfeuchte** (Mittelwert der Sensoren, `min`/`max` als Attribute), mit kalter Seite zusätzlich **Temperatur kalt** und **Gradient**
- **Sollwerte** als `number`, vorbelegt aus dem Artprofil: Temperatur und Luftfeuchte min/max für Tag und Nacht, Fütterungsintervall
- Die Luftfeuchte wird mit dem **Mittelwert** der Luftsensoren gegen min/max geprüft. Boden-Sensoren (siehe oben) zählen dabei nicht mit.

**Tag und Nacht**
- **Licht: an / Licht: aus** (`time`): dazwischen ist Tag, sonst Nacht. Der Status prüft gegen die Sollwerte der aktuellen Phase. Sensor **Tag** zeigt die Phase.
- Die Lichtzeiten können von einer eigenen Automation gesetzt werden (`time.set_value`), z. B. aus Sonnenstand oder Strompreis.

**Gradient (nur mit Sensoren für die kalte Seite)**
- Am Tag gilt **Temperatur warm min/max (Tag)** für die warme Seite, dazu gibt es **Temperatur kalt min/max (Tag)** und **Gradient: min** (warm minus kalt, 0 = nicht prüfen).
- Nachts, wenn die Seiten sich angleichen, gelten die Nachtwerte für alle Sensoren zusammen, der Gradient wird nicht geprüft.
- Ohne Sensoren für die kalte Seite gilt eine Spanne für alle Sensoren.

**Pflege-Log**
- Zuletzt gefüttert / gehäutet / besprüht (`datetime`) plus Buttons zum Abstempeln
- **Fütterung fällig** und **Nächste Fütterung**

**Lichtsteuerung** (mit Licht-Schaltern)
- Die Schalter folgen den Lichtzeiten. Nach dem Schalten wird der Zustand geprüft: 3 Versuche im Abstand von 5 s, 12 Minuten Pause, 3 weitere Versuche, danach **Licht: Störung**.
- **Licht: Automatik** schaltet das ein oder aus.
**Abkühlung** (mit Licht-Schaltern)
- Liegt die warme Seite 5 Minuten über **Abkühlung: ab Temperatur** (0 = aus), geht das Licht aus (**Abkühlung: aktiv**).
- Es geht wieder an, wenn die warme Seite darunter liegt und der Unterschied zur kältesten Messung kleiner als **Abkühlung: max. Differenz** ist, 10 Minuten lang. Timeout nach 4 Stunden, Tagesende beendet die Abkühlung ebenfalls. Der Zustand überlebt einen Neustart.

**Automatische Beregnung** (mit Beregnungs-Schalter)
- Schalter **Beregnung: Automatik**: Ist er an und die Luftfeuchte unter **Beregnung: unter Luftfeuchte**, wird der Beregnungs-Schalter für **Beregnung: Dauer** eingeschaltet (nur am Tag). Zwischen zwei Beregnungen liegt mindestens der **Beregnung: Mindestabstand**; auch manuelles Beregnen zählt dafür.

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

Optional sind alle Felder außer `name`: `cold_temp_min`, `cold_temp_max`, `gradient_min` (kalte Seite am Tag), sowie Nachtwerte `temp_min_night`, `temp_max_night`, `humidity_min_night`, `humidity_max_night` (sonst gleich den Tagwerten).

## Hinweise
- Die mitgelieferten Werte sind grobe Startwerte (`"verified": false`), bitte gegen die eigene Haltung prüfen.
- Temperaturen werden in °C verglichen.
- Ein Wechsel des Artprofils setzt die Sollwerte auf die Profilwerte zurück.
