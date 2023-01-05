# CONDITIONS - relation of N:M with experiment. We need an intermediate table to relate both of them.
# 1 experiment may have several conditions that can be shared among many experiments
CREATE TABLE conditions(
	condition_id INT primary key auto_increment
);

CREATE TABLE experiment_conditions (
	ec_id INT PRIMARY KEY auto_increment,
	experiment_id INT NOT NULL,
    condition_id INT NOT NULL,
    FOREIGN KEY (experiment_id) 
		REFERENCES experiment(experiment_id)
        ON DELETE cascade,
    FOREIGN KEY (condition_id) 
		REFERENCES conditions(condition_id)
        ON DELETE cascade
);

