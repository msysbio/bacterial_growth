# REFERENCES - relation of N:M with experiment. We need an intermediate table to relate both of them.
# 1 experiment may have several references that can be shared among many experiments
CREATE TABLE ref (
	reference_id INT primary key auto_increment
);

CREATE TABLE experiment_ref (
	er_id INT PRIMARY KEY auto_increment,
	experiment_id INT NOT NULL,
    reference_id INT NOT NULL,
    FOREIGN KEY (experiment_id) 
		REFERENCES experiment(experiment_id)
        ON DELETE cascade,
    FOREIGN KEY (reference_id) 
		REFERENCES ref(reference_id)
        ON DELETE cascade
);