# Nástroj pro vykreslování map s prošlými trasami
Nástroj umožnuje nastavení a vygenerování vektorové mapy ve formátu PDF, která je poté určena k tisku. Také umožňuje přidání vlastních tras na mapu pomocí GPX souborů a nastylování těchto tras podle vlastních preferencí.

# Spuštění
1. Vytvořte `.env ` na zakladě `.env.example ` pro konfigurátor (složka FE) a server (složka BE)

2. Stáhněte potřebné soubory OpenStreetMap dat ve formátu **.osm.pbf**, například ze stránky: https://download.geofabrik.de/. Pokud chcete soubory spojovat (používat data z více zemí najednou), měly by pocházet ze stejné verze OSM databáze, tedy měly by být staženy ve stejný čas.
   
3. Stažené soubory přesuňte do složky BE/osm_files. Pokud stahujete soubory jednotlivých zemí a chcete je v konfigurátoru zobrazit s českými názvy, pojmenujte je podle [kódů zemí](https://asep-portal.lib.cas.cz/pro-zpracovatele/manual/kody-zemi/) (např. cz.osm.pbf)
   
4. Nainstalujte Docker
   
5. První spuštění, a také každé další po změně nebo přidání OpenStreetMap souborů, proveďte pomocí skriptu `run.sh` s parametry, které reprezentují cesty ke konkrétním souborům (které chcete používat) nebo ke složce (`./osm_files`). OSM soubory v parametrech budou před spuštěním přefiltrovány od nevalidních objektů. Například: `sh run.sh ./osm_files` nebo `sh run.sh ./osm_files/cz.osm.pbf`. Pokud nechcete žádný soubor přefiltrovat (není doporučeno - může přerušit generování mapy), můžete skript `run.sh` spustit bez parametrů. Po spuštění `run.sh` se automaticky spustí server i s konfigurátorem a URL, na kterých běží server a konfigurátor, se vypíší do konzole.
   
6. Pokud nebyla provedena žádná změna souborů a skript `sh run.sh` již byl spuštěn, stačí nástroj spustit pomocí příkazu `docker compose up` (případně `docker-compose up`).