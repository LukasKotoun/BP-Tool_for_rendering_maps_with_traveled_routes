# Nástroj pro vykreslování map s prošlými trasami
Nástroj umožňující nastavení a vygenerování vektorové mapy ve formátu PDF, která je určena k tisku. Mapa umožňuje přidání vlastních tras pomocí GPX souborů a nastylování těchto tras podle vlastních preferencí.

# Spuštění
1. Vytvořte .env na zakladě .env.example

2. Stáhněte potřebné soubory OpenStreetMap ve formátu **.osm.pbf**, například ze stránky: https://download.geofabrik.de/   
   
3. Stažené soubory přesuňte do složky BE/osm_files. Pokud stahujete soubory jednotlivých zemí a chcete je v konfigurátoru zobrazit s českými názvy, pojmenujte je podle [kódů zemí](https://asep-portal.lib.cas.cz/pro-zpracovatele/manual/kody-zemi/) (např. cz.osm.pbf)
   
4. Nainstalujte Docker
   
5. První spuštění, a také každé další po změně nebo přidání OpenStreetMap souborů, proveďte pomocí skriptu `run.sh` s parametry, které reprezentují cesty ke konkrétním souborům nebo ke složce (`./osm_files`). OSM soubory v parametrech budou před spuštěním přefiltrovány od nevalidních objektů. Například: `sh run.sh ./osm_files` nebo `sh run.sh ./osm_files/cz.osm.pbf`. Pokud nechcete žádný soubor přefiltrovat, můžete skript `run.sh` spustit bez parametrů. Po spuštění `run.sh` se automaticky spustí server i s konfigurátorem. URL, na kterých server a konfigurátor běží, se vypíší do konzole (konfigurátor je nejčastěji na adrese http://localhost:4173/ nebo http://localhost:5173/).
   
6. Pokud žádná změna nebyla provedena a již byl script `sh run.sh` spuštěn, stačí nástroj spustit pomocí příkazu docker compose up (případně docker-compose up).