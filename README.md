# CabinGerman

> 🛟 **Need help or found a bug?** Get support at [support.doodesch.de/german](https://support.doodesch.de/german).

Deutsche Texte und ein deutsch gesprochenes Radiointro für the cabin game. Übersetzt Menüs, Einstellungen, Karten, Hinweise, Spielhandbuch und Shop. Mit Begriffen wie Charakter, Level, XP und Goodie-Bag. Der Katalog enthält 743 Einträge und zusätzliche Regeln für Meldungen mit Zahlen.

![CabinGerman - deutsche Texte und deutsches Intro](https://raw.githubusercontent.com/DooDesch-Mods/TheCabinGame-German/main/docs/img/header.jpg)

Spielernamen, Lobbyeinträge, Chatnachrichten, Passwörter und eingegebene Texte werden nicht übersetzt. Umlaute und ß bleiben erhalten. Die UI nutzt eine bereits im Spiel enthaltene Schrift mit deutschen Zeichen; die dekorativen Hauptmenükarten behalten ihre Schrift.

## Installation

Benötigt die Steam-Version, Build `25553694`, und [UE4SS 3.0.1](https://www.nexusmods.com/thecabingame/mods/4). UE4SS separat installieren.

1. Spiel schließen.
2. Für das Nexus-Archiv `CabinGerman_0.2.0_nexus.zip`: den enthaltenen Ordner `the_cabin_game` in den Steam-Spielordner `the cabin game` kopieren. Dort liegt auch `the_cabin_game.exe`.
3. Für das Archiv `CabinGerman-0.2.0.zip`: `Mods/CabinGerman` nach `the_cabin_game/Binaries/Win64/ue4ss/Mods/CabinGerman` und die drei Dateien aus `Content/Paks/~mods` nach `the_cabin_game/Content/Paks/~mods` kopieren.
4. Spiel wie gewohnt über Steam starten.

Die deutsche Übersetzung ist nach dem Start aktiv. Andere Übersetzungsmods vorher deaktivieren, damit sie sich nicht gegenseitig überschreiben. Bestehende UE4SS-Dateien und Modlisten müssen nicht ersetzt werden.

Das Radiointro wird auf Deutsch abgespielt. F8 schaltet die deutschen Untertitel um. Die neue Aufnahme behält die Gesamtdauer des Original-Audios bei; der Ablauf im Spiel wird dadurch nicht verkürzt. Der Audio-Override enthält ausschließlich die neu erzeugte deutsche Sprachaufnahme und die dazugehörigen SoundWave-Daten.

Wer nur die Texte möchte, kopiert nur den Mod-Ordner und lässt die drei Dateien `CabinGermanVoice_P.*` weg. Die Untertitel sind auf das deutsche Audio abgestimmt.

## Screenshots

| Spielhandbuch | Einstellungen |
| --- | --- |
| ![Kurzanleitung auf Deutsch](https://raw.githubusercontent.com/DooDesch-Mods/TheCabinGame-German/main/docs/img/02-kurzanleitung.jpg) | ![Deutsche Einstellungen](https://raw.githubusercontent.com/DooDesch-Mods/TheCabinGame-German/main/docs/img/03-einstellungen.jpg) |

![Weitere Seiten des deutschen Spielhandbuchs](https://raw.githubusercontent.com/DooDesch-Mods/TheCabinGame-German/main/media/handbuch.gif)

## Entfernen

Spiel schließen und `ue4ss/Mods/CabinGerman` sowie die drei Dateien `CabinGermanVoice_P.pak`, `CabinGermanVoice_P.utoc` und `CabinGermanVoice_P.ucas` aus `Content/Paks/~mods` entfernen. Spielstände und Einstellungen bleiben erhalten.

## Stand dieser Fassung

Version `0.2.0` übersetzt unterstützte Text-Widgets, keine fest in Bilder oder Modelle eingebrannte Schrift. Neue Texte aus späteren Spielupdates können noch Englisch erscheinen. Menüs, Einstellungen und alle zehn Handbuchseiten wurden in der Spiel-Engine geprüft. Ein vollständiger Multiplayer-Durchlauf ist nicht Teil der bisherigen Prüfung. Die Mod verändert keine Spielregeln und enthält keine Server-Komponente; Mehrspieler-Kompatibilität ist damit noch nicht vollständig nachgewiesen.

Der deutsche Audio-Override wurde mit dem Original-Radio-SoundCue in der Engine vollständig abgespielt. Untertiteltexte und Ein-/Ausblenden wurden geprüft; die Bildprüfung von Schrift und Position erfolgte in einer Canvas-Vorschau. Die Untertitelanzeige im Gameplay-HUD während einer vollständigen Runde ist noch nicht separat abgenommen.

Bei Problemen enthält `ue4ss/UE4SS.log` Meldungen mit dem Präfix `[CabinGerman]`. Fehler werden mit Ursache protokolliert. Der Mod benötigt einen Neustart; Hot Reload gehört nicht zum unterstützten Ablauf.

## Entwicklung

Quelltexte: `Mods/CabinGerman/Scripts`. Der bearbeitbare Katalog liegt in `translations.de.json`; `de.lua` enthält die zur Laufzeit geladene Fassung. Beide Fassungen müssen übereinstimmen.

Prüfung: `python tests/check_lua.py` mit `lupa`. Paketbau: `python tools/package.py`. Das Paket enthält den Lua-Mod, den deutschen Audio-Override und die Dokumentation. Es enthält weder UE4SS noch die Original-Sprachaufnahme oder Encoder-Werkzeuge.

Danke an das UE4SS-Projekt. Das vom Nutzer bereitgestellte spanische Übersetzungspaket 0.1.14 diente als Referenz für Textabdeckung und Spiel-Widgetnamen; dessen Code und spanische Texte sind nicht Bestandteil dieses Mods.

Die deutsche Sprachaufnahme wurde lokal mit [Qwen3-TTS 1.7B Base](https://github.com/QwenLM/Qwen3-TTS) erzeugt. Die Originalaufnahme diente als Stimmreferenz; der deutsche Text wurde separat überarbeitet. Es wird kein Qwen-Modell mitgeliefert. Die ursprüngliche Stimme und das Spiel stammen vom jeweiligen Rechteinhaber. Lizenz und weitere Hinweise stehen in `CREDITS.md`.
