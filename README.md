# R6 Stats Discord Bot

Discord bot der linker Discord-brugere til deres Rainbow Six Siege / Ubisoft-konto og holder deres rank-rolle opdateret på serveren.

Botten bruger Stats.cc API'et til at hente spillerdata, gemmer links i `jsons/users.json`, og opdaterer rank-roller automatisk hver time.

## Hvad botten gør

- Brugere linker deres Ubisoft-konto med `!link <ubisoftnavn>`.
- Botten gemmer brugerens Discord ID sammen med Ubisoft `profileId`.
- Hver time gennemgår botten alle linkede brugere på serverne.
- Den henter spillerens rank fra Stats.cc API'et.
- Den opretter rank-roller hvis de mangler: `Copper`, `Bronze`, `Silver`, `Gold`, `Platinum`, `Emerald`, `Diamond`, `Champion`.
- Den fjerner gamle rank-roller og giver brugeren den rank-rolle de skal have.
- Brugere kan se stats, rank, bans og fjerne deres link igen.

## Krav

- Python 3.10 eller nyere anbefales.
- En Discord bot token.
- En Stats.cc API key.
- Botten skal have de rigtige Discord intents og permissions.

Installer Python libraries med:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Hvis du ikke har en virtual environment endnu:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Opsætning

Lav en `.env` fil i projektets rodmappe:

```env
DISCTOKEN=din_discord_bot_token
APIKEY=din_statscc_api_key
PREFIX=!
```

Den nuværende kode læser fra `.env` bruges ikke af den aktuelle version.

Sørg også for at `jsons/users.json` findes. Den kan starte som:

```json
{}
```

Start botten med:

```powershell
.venv\Scripts\python.exe main.py
```

## Discord setup

I Discord Developer Portal skal du aktivere:

- Server Members Intent
- Message Content Intent

Botten skal bruge permissions til:

- Read Messages/View Channels
- Send Messages
- Manage Roles
- Manage Nicknames, hvis den skal kunne ændre nickname ved `!link`

Vigtigt: Bottens rolle skal ligge højere end rank-rollerne i Discords role list, ellers kan den ikke tilføje eller fjerne dem.

## Kommandoer

Hvis `PREFIX=!`, bruges kommandoerne sådan:

| Kommando | Hvem kan bruge den | Beskrivelse |
| --- | --- | --- |
| `!link <ubisoftnavn>` | Alle | Linker din Discord bruger til en Ubisoft-konto. |
| `!unlink` | Alle | Fjerner dit link og fjerner dine rank-roller. |
| `!minrank` | Alle | Viser rank for din linkede konto. |
| `!stats <ubisoftnavn>` | Alle | Viser stats for en spiller. |
| `!bugreport <besked>` | Alle | Sender en bug report til bot owner. |
| `!r6help` | Alle | Viser hjælp i Discord. |
| `!reload` | Owner | Kører rank-opdateringen manuelt. |
| `!remove @bruger` | Owner/admin | Fjerner en brugers link og rank-roller. |
| `!checkban @bruger` | Owner/admin/rolle | Tjekker om brugerens linkede Ubisoft-konto har bans. |

## Projektstruktur

| Fil/mappe | Formål |
| --- | --- |
| `main.py` | Starter botten, loader cogs og kører den automatiske rank-opdatering. |
| `apiClass.py` | Indeholder Stats.cc API-kald til profiler, ranks, KD, winrate og bans. |
| `cogs/commands.py` | Indeholder botkommandoerne. |
| `cogs/events.py` | Håndterer command errors. |
| `jsons/users.json` | Gemmer Discord ID -> Ubisoft profileId links. |
| `.env` | Indeholder secrets og config. Skal ikke deles offentligt. |
| `linklogs.txt` | Bliver oprettet automatisk når brugere linker/unlinker. |

## Nyttige noter

- Stats.cc API key kan fås via Stats.cc, typisk ved at kontakte dem via deres Discord.
- Botten opdaterer roller automatisk hvert 60. minut.
- Rank-opdateringen kører i batches på 20 brugere med 2 sekunders pause mellem batches.
- `PREFIX` i `.env` bestemmer kommando-prefixet.
- Del aldrig din `.env`, Discord token eller API key offentligt.

## Fejlsøgning

**Botten starter ikke på grund af missing module**

Kør:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Botten svarer ikke på kommandoer**

Tjek at `PREFIX` i `.env` er korrekt, at botten er online, og at Message Content Intent er slået til.

**Botten kan ikke give roller**

Tjek at botten har `Manage Roles`, og at bottens rolle ligger over rank-rollerne i Discord.

**Stats/rank virker ikke**

Tjek at `APIKEY` i `.env` er korrekt, og at Ubisoft-navnet findes hos Stats.cc.
