#  our brainstorming 



## general bioinfo tips and hints


reg. arguments in python see [here](https://docs.python.org/dev/library/argparse.html)

Front-end options: 
* PHP-Ajax ([example](https://www.w3schools.com/xml/ajax_database.asp))
* Rshiny app ([example](https://github.com/Tychobra/shiny_crud)) - check the posts and the videos. 
 Also, a really short [online book](https://bookdown.org/msharkey3434/ShinyDB_Book/) that could be of help (probably..)


## Examples of PHP-Ajax codes:

* [Multi tab example](https://www.webslesson.info/2016/11/multi-tab-shopping-cart-by-using-php-ajax-jquery-bootstrap-mysql.html) -> we would have a tab for loading data and another for visualizing data (at least for the moment)

## Notes from meeting with Karoline (17th January)

* Write a list with the possible ways to measure metabolites
* Make a table for XXX species abundances


### Replicates
* core table with indices
* biological and technical replicates
* separate species in a table like metabolites

.
* Both temperature and pH can change during the experiment
* Dilution rate (not in our data but happens a lot) ==> binary logic

* Perturbations --> split them as different experiments and link them --> keep track of them in the outcome
* Same experiment can have dif perturbation ==> this makes diff experiments

* Preculture densities of the inoculum . Initial abundances of the bacterias if known.
* Preculture --> bacteria. You already have some OD. Preconditions. Initial abundance of the species (if known)


* RELATIONAL OBJECT: [ORMs instead of DROP](https://www.fullstackpython.com/object-relational-mappers-orms.html#:~:text=An%20object%2Drelational%20mapper%20).

* Think of checkboxes in templates for users.
