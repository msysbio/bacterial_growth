## Conda environment

```
conda create --name master_thesis23
source ~/miniconda3/etc/profile.d/conda.sh
conda activate master_thesis23
conda install -n master_thesis23 python=3.6 mysql-connector-python r-essentials r-base
```

To work with jupyter: 
```
conda create -n master_thesis23         # creates new virtual env
conda activate master_thesis23          # activate environment in terminal
conda install jupyter                # install jupyter + notebook
jupyter notebook                     # start server + kernel inside my-conda-env
```

### Day to day (everything already installed)
Just do:
```
source ~/miniconda3/etc/profile.d/conda.sh
conda activate master_thesis23
jupyter notebook

```

## Github
```
git add XXX
git commit -m "XXX"
git push -u origin main
```

```
git pull
```

Configure .gitignore:
```
git config --global core.excludesFile ~/.gitignore
```

In order to remove things already committed:
```
git rm -r --cached XXX
```


## MySQL
```
mysql -u root -p
```
