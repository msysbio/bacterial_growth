# Metabolites to be included in the μGrowthDB

Scripts and files in this folder provide the metabolites and their metadata to be supported by μGrowthDB. 

More specifically, we use the Microbial Conditions Ontology (MCO) to build a corpus of metabolites of interest in microbial ecology studies, and the Chemical Entities of Biological Interest (ChEBI) dictionary of molecular entities to identify those. 

First, we run `metabolites.py` that gets as input either:
- the `mco.owl` (Version 2019-05-15, downloaded from [here](https://raw.githubusercontent.com/microbial-conditions-ontology/microbial-conditions-ontology/master/mco.owl)) (`--mco`), 
- and/or the `Supplementary_Data_1_metabolites.txt` file ([v1.07](https://github.com/raeslab/GMMs/blob/master/GMMs.v1.07.txt)), including [metabolites found relative](https://doi.org/10.1038/nmicrobiol.2016.88) to human gut by the Raes lab (`--raes`), 
- and/or any **single-column** file with metabolite names (`--other`).

Add flags based on the input files you'd like to consider:

```bash
./metabolites.py --raes --mco
```

After a couple of minutes (~10 min) the `metabolites.py` script will return a pair of files that will then be loaded in the database:
`metabolites.csv` and `metabolites_synonyms.csv` files


To load those in the database, one needs to run: 
```bash
./populate_metadb.py --mode replace
```
* 
This will replace any duplicates with the new entries and will add any new records. 
Run 
```bash
./populate_metadb.py --help
```
to check other modes.

**Remember** to check for the latest version of MCO. 
Further metabolites of interest can be added, simply by providing a file with their names 
