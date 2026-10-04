# Terrarium für Home Assistant

Artprofile, Sollbereiche und Pflege-Log pro Terrarium (Idee: OpenPlantbook, aber für Terrarien).

## Installation
- HACS → Custom repository (Integration) oder `custom_components/terrarium` nach `/config/custom_components/` kopieren
- Neustart, dann *Einstellungen → Geräte & Dienste → Terrarium*

## Pro Terrarium entsteht ein Gerät mit
- **Status** (ok / zu warm / zu kalt / zu trocken / zu feucht / keine Daten), **Außerhalb Sollbereich**
- **Sollwerte** (Temperatur min/max, Luftfeuchte min/max, Fütterungsintervall) als `number`, vorbelegt aus dem Artprofil
- **Pflege-Log**: zuletzt gefüttert / gehäutet / besprüht (`datetime`) plus Buttons zum Abstempeln
- **Fütterung fällig** und **Nächste Fütterung**

Mehrere Sensoren pro Terrarium sind möglich: der kälteste und wärmste Messwert werden gegen den Bereich geprüft (Gradient).

## Eigene Artprofile
`/config/terrarium_species.json` (überschreibt/ergänzt die mitgelieferten):

```json
{
  "mein_tier": {
    "name": "Genus species", "common": "Trivialname",
    "temp_min": 20, "temp_max": 30,
    "humidity_min": 50, "humidity_max": 80,
    "feeding_interval": 3
  }
}
```

## Hinweise
- Die mitgelieferten Werte sind grobe Startwerte (`"verified": false`), bitte gegen die eigene Haltung prüfen.
- v1 kennt keinen Tag/Nacht-Unterschied und rechnet in °C.
- Die Integration steuert keine Hardware, sie überwacht und protokolliert nur.
