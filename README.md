# Nástroj pro vykreslování map s prošlými trasami
Nástroj umožnuje nastavení a vygenerování vektorové mapy ve formátu PDF, která je poté určena k tisku. Také umožňuje přidání vlastních tras na mapu pomocí GPX souborů a nastylování těchto tras podle vlastních preferencí.

# Spuštění
1. Vytvořte `.env ` na zakladě `.env.example ` pro konfigurátor (složka FE) a server (složka BE)

2. Stáhněte potřebné soubory OpenStreetMap dat ve formátu **.osm.pbf**, například ze stránky: https://download.geofabrik.de/. Pokud chcete soubory spojovat (používat data z více zemí najednou), měly by pocházet ze stejné verze OSM databáze, tedy měly by být staženy ve stejný čas.
   
3. Stažené soubory přesuňte do složky BE/osm_files. Pokud stahujete soubory jednotlivých zemí a chcete je v konfigurátoru zobrazit s českými názvy, pojmenujte je podle [kódů zemí](https://asep-portal.lib.cas.cz/pro-zpracovatele/manual/kody-zemi/) (např. cz.osm.pbf)

4. Nainstalujte Docker

5. Spusťte nástroj
   - První spuštění a každé další po změně OpenStreetMap souborů (nebo `config.py` souboru) proveďte pomocí jednoho z příkazů:
      -  `run.sh ./osm_files` - připraví (předfiltruje) všechny soubory ve složce (doporučeno)
      -  `run.sh ./osm_files/soubor1.osm.pbf ./osm_files/soubor2.osm.pbf` - připraví (předfiltruje) konkrétní soubory
      -  `run.sh` - bez přípravy (předfiltrování) (není doporučeno - může přerušit generování mapy)
   - Každé další spuštění bez změny OpenStreetMap souborů (nebo `config.py` souboru):
     - `docker compose up` (případně `docker-compose up`) - spustí nástroj bez změny souborů

6. Po provedení požadovaných akcí můžete ukončit běh nástroje pomocí `docker compose down` (případně `docker-compose down`)