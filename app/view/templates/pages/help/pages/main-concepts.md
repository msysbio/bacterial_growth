## Project

A project represents a distinct research endeavor focused on microbial growth. It serves as the overarching container for organizing related studies and experiments. A user may upload a study that stands alone, in which case the project name can match the study name.

## Study

A study conducted within the framework of a project refers to a focused investigation aimed at exploring a specific aspect of microbial growth. Each study is carefully designed to address particular research questions or hypotheses and may involve multiple experiments.

## Experiment

An experiment represents a unique set of experimental conditions or treatments applied to a set/group of biological replicates. Control cases should be considered as distinct experiments.

An experiment entry is described by:

- A single **community** that may change because of a **perturbation**.
- One or more **compartments** that describe a specific set of environmental conditions. These may also change because of a **perturbation**.
- One or more **biological replicates** that represent specific growth vessels that implement the experimental design.

## Biological replicate (bioreplicate)

A biological replicate is a distinct biological system that implements the experimental design of a particular experiment. Multiple biological replicates are recommended for each experiment. Once uploaded, a synthetic "average" replicate is created for each experiment for each possible measurement.

The bioreplicate is considered to be a single biological system. All measurements are performed within the context of this replicate.

## Compartment

A compartment is a distinct section or partition within the growth environment (or "vessel") where biological samples are grown under specific environmental conditions. Each compartment corresponds to a different set of environmental parameters (e.g. temperature, pH, medium, etc.) tailored to the requirements of the experiment. An experiment needs to have at least one compartment.

In the user interface, compartments will be seen in the context of bioreplicates. For instance, if an experiment E has a bioreplicate BR1 with compartments C1 and C2, these will be indicated as "BR1<sub>C1</sub>" and "BR1<sub>C2</sub>". If an experiment only has one compartment, its bioreplicates will not have subscripts.

A change in the environment of an experiment is encoded within the application as a change in compartments. For instance, an experiment might start with a compartment "C0", which is then changed to an acidic or neutral pH, which we encode as new compartments, "C-" and "C+". This change can be described by a **perturbation**.

## Community

Consists of one or more members. Each experiment needs to have at least one community, unless it consists of a control without any microbial community.

Microbial strains within a community always reference an NCBI identifier (<https://www.ncbi.nlm.nih.gov/datasets/>). A custom strain needs to be annotated with its NCBI taxon.

## Perturbation

Refers to a deliberate disturbance or alteration applied to a specific experiment. It may refer to a perturbation in the environmental conditions described in the corresponding compartment and/or changes to the community (e.g., introducing new strains).

## Measurement

A single observation of cell or metabolite abundance, or of an environmental value (pH), at a particular time point. A group of measurements of a single "subject" within a single compartment can be plotted on a chart.
