# bacterial_growth

# Environment set up
First, you need to set up the environment that contain all the packages that will be used by the program. To do so, run the following commands:
````
cd envs/
conda env create -f environment.yml
````

## To init the app 

Under `app/.streamlit` we need to have a file called `secrets.toml` with the following:
```yaml
[connections.BacterialGrowth]
dialect = "mysql"
username = ""
password = ""
host = ""
database = "BacterialGrowth"
```


```bash
streamlit run streamlit_app.py --server.fileWatcherType none
```

without the `--server.fileWatcherType` argument I get the following error:

```bash
    raise OSError(errno.ENOSPC, "inotify watch limit reached")
OSError: [Errno 28] inotify watch limit reached
```


### Dependencies

```bash
pip install -U Flask-SQLAlchemy
```
The `Flask-SQLAlchemy` is required for the `st.connection` to work. 


```bash
pip install streamlit-tags
```
for the tags in the upload page.


### To periodically update 

<!-- From [NCBI Taxonomy FTP](https://ftp.ncbi.nih.gov/pub/taxonomy/), we get the latest `taxdump.tar.gz`. -->

From [JensenLab FTP](https://download.jensenlab.org) we download the `organisms_dictionary.tar.gz` file. 

In the `METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv` file there is a list of *small* Eukaryotes.
Of course this could be also be updated from time to time. 

We keep the `organism_entities.tsv` and `organism_groups.tsv` files in the same directory with the `create_groups.pl` script and run it to build the `growthDB_groups.tsv`

```bash
./filter_unicellular_ncbi.awk  METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv  database_groups.tsv  >  growthDB_unicellular_ncbi.tsv
```

<!-- ```bash
file1="growthDB_unicellular_ncbi.tsv"
file2="names.dmp"
awk -F "\t"  'NR == FNR { file1_entries[$1] = 1; next } $1 in file1_entries { print $1, $3 }' "$file1" "$file2" > unicellular_ncbi_id_name.tsv
``` -->

Now we need to map the NCBI Taxonomy Ids to taxa names.
Yet, for a single NCBI Taxonomy Id we may have more than 1 names. 
To address this and make the dynamic search easier, we will use the `organisms_preferred.tsv` as well. 

First, we make an overall file with NCBI Taxonomy Ids and their corresponding preferred names:

```bash
file1="organisms_entities.tsv"
file2="organisms_preferred.tsv"
awk -F "\t" 'NR == FNR { file1_org_ids[$1] = 1; file1_ncbi_ids[$1] = $3; next } $1 in file1_org_ids { print file1_ncbi_ids[$1], $2 }' "$file1" "$file2" > ncbi_ids_preferred_names.tsv
sed -i 's/ /\t/' ncbi_ids_preferred_names.tsv
```


Now, we keep the NCBI Taxonomy Ids returned from the `filter_unicellular_ncbi.awk` script which are present in the `organisms_entities.tsv`:
```bash
file1="growthDB_unicellular_ncbi.tsv"
file2="organisms_entities.tsv"
awk -F "\t"  'NR == FNR { file1_entries[$1] = 1; next } $3 in file1_entries { print $3 }' "$file1" "$file2" > unicellular_ncbi_ids.tsv
```

Finally, we get only NCBI Taxonomy Ids along with their corresponding preferred names of the unicellular taxa:
```bash
file1="unicellular_ncbi_ids.tsv"
file2="ncbi_ids_preferred_names.tsv"
awk 'NR == FNR { file1_ncbi_ids[$1] = 1 ; next } $1 in file1_ncbi_ids { print $0 }' "$file1" "$file2" > unicellular_ncbi_ids_preferred_names.tsv
```

Once completed, we may load the `unicellular_ncbi_ids_preferred_names.tsv` in the `Taxa` table in the `BacterialGrowth` database.
```bash
mv unicellular_ncbi_ids_preferred_names.tsv /var/lib/mysql-files
mysql --local-infile=1 -u <username>  -p
```

and now

```sql
mysql> use BacterialGrowth;
mysql> LOAD DATA INFILE '/var/lib/mysql-files/unicellular_ncbi_ids_preferred_names.tsv' INTO TABLE Taxa FIELDS TERMINATED BY '\t' LINES TERMINATED BY '\n';

```

