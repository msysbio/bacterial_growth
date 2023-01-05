# METABOLITES - relation of N:M with experiment. We need an intermediate table to relate both of them.
CREATE TABLE metabolites(
	metabolite_id INT primary key auto_increment,
    metabolite varchar(20) NOT NULL,
    abundance_measurement varchar(15) NOT NULL,
    abundance_unit varchar(5) NOT NULL
);

CREATE TABLE experiment_metabolites(
	em_id INT PRIMARY KEY auto_increment,
	experiment_id INT NOT NULL,
    metabolite_id INT NOT NULL,
    FOREIGN KEY (experiment_id) 
		REFERENCES experiment(experiment_id)
        ON DELETE cascade,
    FOREIGN KEY (metabolite_id) 
		REFERENCES metabolites(metabolite_id)
        ON DELETE cascade
);