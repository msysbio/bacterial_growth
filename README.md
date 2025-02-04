# μgrowthDB

[μGrowthDB](https://mgrowthdb.gbiomed.kuleuven.be) is the first crowd-sourced database for microbial growth data.
It supports a range of measurement techniques: 
Direct Microscopic Count, Colony Forming Units (CFU), Flow Cytometry, Optical Density, sequencing data.
Also, it supports storage of accompanying metabolic data.

In this repo, you can find the code of the resource, known issues and discussions, while you are more than welcome to share your thoughts on the resource and of course [contribute](./CONTRIBUTING.md).


## To use μGrowthDB 

There are two basic 

therefore you are more than welcome to [upload your data](https://bacterial-growth.readthedocs.io/en/latest/submission/upload.html) there. 
To exploit the resource, feel free to 






# Environment set up
First, you need to set up the environment that contain all the packages that will be used by the program. To do so, run the following commands:

```
conda create --name growthdb
source ~/miniconda3/etc/profile.d/conda.sh
conda activate growthdb
conda install -n growthdb python=3.6 mysql-connector-python r-essentials r-base
```

[TODO] The `pages/` directory should be removed once all features have been moved in the `flask_app`.




For this repo
====

- `src/`

We keep code to build basic parts of the resource, i.e. the taxa and metabolite namespaces.
Things that we have to build once, and sometimes periodically update, to enable the app.

- `flask_app/`

We keep the code of the running app. 

- `config/`

Includes the `database.toml` file that is **required** to be set 

- `bin/`

Under `bin` we keep executable files to run the various modules of the tool

-  `data/`

We provide some example datasets both as raw and in the format they should be provided within the template files to be uploaded to the μGrowthDB. 


- `docs/`

We keep the ReadTheDocs related files. 
Remember that there is also the `.readthedocs.yaml` file in the `root` folder of the repo. 

- `tests/`




# How to run the app

First, make sure you have MySQL locally. 







## How to build the ReadTheDocs locally

```bash
cd docs
make clean
make html
```


## References

- CSS reset: <https://piccalil.li/blog/a-more-modern-css-reset/>
- SVG Spinners: <https://github.com/n3r4zzurr0/svg-spinners>
- Web icons: <https://github.com/tabler/tabler-icons>
