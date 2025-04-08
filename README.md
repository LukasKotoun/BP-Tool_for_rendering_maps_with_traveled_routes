# Nástroj pro vykreslování map s prošlými trasami
Nástroj umožňující nastavení a vygenerování vektorové mapy ve formátu PDF, která je určena k tisku. Mapa umožňuje přidání vlastních tras pomocí GPX souborů a nastylování těchto tras podle vlastních preferencí.

# Spuštění
1.  Stáhněte potřebné soubory OpenStreetMap ve formátu **.osm.pbf**, například ze stránky: https://download.geofabrik.de/   
   
2. Stažené soubory přesuňte do složky BE/osm_files. Pokud stahujete soubory jednotlivých zemí a chcete je v konfigurátoru zobrazit s českými názvy, pojmenujte je podle [kódů zemí](https://asep-portal.lib.cas.cz/pro-zpracovatele/manual/kody-zemi/) (např. cz.osm.pbf)
   
3. Nainstalujte Docker
   
4. První spuštění (může zabrat delší čas), a také každé další po změně nebo přidání OpenStreetMap souboru, proveďte pomocí skriptu `run.sh` s parametry, které reprezentují cesty ke konkrétním souborům nebo ke složce (`./osm_files`), kde mají být soubory přefiltrovány od nevalidních objektů. Například: `sh run.sh ./osm_files` `sh run.sh ./osm_files/cz.osm.pbf`. Pokud nechcete žádný soubor přefiltrovat, můžete `run.sh` spustit bez parametrů.
   
5. Po spuštění `run.sh` se automaticky spustí server i s konfigurátorem na adrese: http://localhost:4173/.
   
6. Pokud žádná změna nebyla provedena a již byl script `sh run.sh` spuštěn, stačí nástroj spustit pomocí příkazu docker compose up (případne docker-compose up).

# .env soubory
## BE
    - JWT_SECRET_KEY="dev_key" - tajný klíč použitý pro vytvoření a validaci tokenu, bez uvedení se použije výchozí klíč.
    - FRONTEND_URL=http://localhost:4173,... - url, které mají povolen přístup k serveru (alowed origins). Bez uvedení se povolí všechny url (*)
## FE
    - VITE_API_BASE_URL=http://localhost:8000 - url na které běží server
    - VITE_API_NOMINATIM_URL=https://nominatim.openstreetmap.org/search - url na kterou se mají odesílat dotazy pro napovídání oblastí