import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--experiment_name",
                    
                    
                    )

parser.add_argument("--replicate",
                    type=int
                    
                    )

parser.add_argument("--bacteria",
                    "-b",
                    
                    
                    )

parser.add_argument("--strain",
                    "-s",
                    
                    )

parser.add_argument("--biculture",
                    action="store_true",
                    
                    )

parser.add_argument("--abundance_measurement",
                    
                    )

parser.add_argument("--units",
                    
                    )

args = parser.parse_args()
experiment_name = args.experiment_name

# Cnnection to the DB
# Load into the DB the variables from args