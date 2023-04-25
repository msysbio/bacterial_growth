## Conda environment

```
conda create --name growth_curves_env
source ~/miniconda3/etc/profile.d/conda.sh
conda activate growth_curves_env
conda install -n growth_curves_env python=3.6 mysql-connector-python r-essentials r-base
```

To work with jupyter: 
```
conda create -n growth_curves_env         # creates new virtual env
conda activate growth_curves_env          # activate environment in terminal
conda install jupyter                # install jupyter + notebook
jupyter notebook                     # start server + kernel inside my-conda-env
```

### Day to day (everything already installed)
Just do:
```
source ~/miniconda3/etc/profile.d/conda.sh
conda activate growth_curves_env
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
