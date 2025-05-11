# Taxa to be included in the μGrowthDB

In this repo, we build the `unicellular_ncbi_*.tsv` file, and we upload it on μGrowthDB Taxa table.

From [JensenLab FTP](https://download.jensenlab.org) we download the `organisms_dictionary.tar.gz` file.
We use the `organism_entities.tsv` and `organism_groups.tsv` files as input files for `create_groups.pl`.
A few minutes later we get the `growthDB_identifiers.tsv` and the `growthDB_groups.tsv` files.

The [METdb resource](https://metdb.sb-roscoff.fr/metdb/) builds a list of micro-eukaryotic marine species.
By clicking the `CSV` button on the *Strain Descriptions* panel, one can download the `METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv` file which contains the different taxa available on METdb.
Of course this could be also be updated from time to time. 

Then, the `filter_unicellular_ncbi.awk` script (from Savvas Paragkamian) filters unicellular taxa, i.e. Bacteria and small Eukaryotes like the ones in METdb, using the `growthDB_grous.tsv` file built by the `create_groups.pl` script.

Last, we need to **map** the NCBI Taxonomy **Ids** to taxa **names**.
Yet, for a **single NCBI Taxonomy Id** we may have *more than 1 names*. 
To address this and make the dynamic search easier, we will use the `organisms_preferred.tsv` 
(from the `.tar.gz` file we already downloaded from the JensenLab FTP).


> By running the `taxa.sh` script, all previous steps (except of getting the latest METdb table file) are performed.
    ```bash
    ./taxa.sh
    ```

Once completed, we may load the `unicellular_ncbi_ids_preferred_names.tsv` in the `Taxa` table in the `BacterialGrowth` database.
This will be performed by the [`taxa_mets_to_sql.py`](../taxa_mets_to_sql.py) script.

<!-- 
```bash
mv unicellular_ncbi_ids_preferred_names.tsv /var/lib/mysql-files
mysql --local-infile=1 -u <username>  -p
```

```sql
mysql> use BacterialGrowth;
mysql> LOAD DATA INFILE '/var/lib/mysql-files/unicellular_ncbi_ids_preferred_names.tsv' INTO TABLE Taxa FIELDS TERMINATED BY '\t' LINES TERMINATED BY '\n';

``` 
-->

<!-- ```bash
file1="growthDB_unicellular_ncbi.tsv"
file2="names.dmp"
awk -F "\t"  'NR == FNR { file1_entries[$1] = 1; next } $1 in file1_entries { print $1, $3 }' "$file1" "$file2" > unicellular_ncbi_id_name.tsv
``` -->
