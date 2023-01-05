CREATE TABLE experiment (
	experiment_id INT PRIMARY KEY auto_increment,
    experiment_name varchar(20) NOT NULL,
    replicate int NOT NULL,
    
    bacteria varchar(30) NOT NULL,
    bacteria_strain varchar(30),
    
    abundance_measurement varchar(15) NOT NULL,
    abundance_unit varchar(5) NOT NULL,
    pH float,
    temperature float,
    inoculum varchar(20), #DOES IT GO WITH CULTIVATION?
    duration time,
    
    cultivation_id INT,
    reactor_id INT,
    
    bacterial_growth_file varchar(100) NOT NULL,
    metabolites_growth_file varchar(100) NOT NULL,
    
	FOREIGN KEY (cultivation_id) 
		REFERENCES cultivation(cultivation_id)
        ON DELETE NO ACTION,
	
    FOREIGN KEY (reactor_id) 
		REFERENCES reactor(reactor_id)
        ON DELETE NO ACTION
);
