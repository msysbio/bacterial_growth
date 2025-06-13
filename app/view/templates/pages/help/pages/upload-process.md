To upload a study, first you need to log in using an {{ "https://orcid.org/"|external_link("ORCID iD") }}. After that, you can follow the step-by-step process in the "Upload data" section of the navigation sidebar.

## Form components

Many of the forms in the upload process use similar components, some of which are illustrated in the figure below:

<p>
    <div style="width: 100%; text-align: center">
    <img style="width: 80%; margin: 0 auto;" title="Form components" src="/static/images/help/upload-process/submission_form_components.png" />
    </div>
</p>

<ol type="a">
<li>
An input box that allows you to choose metabolites that have been measured in the study. The list is populated as you type. Results are sorted by prefix first, so that, for instance, searching for "glucose" finds the more common name "glucose" before its stereoisomer name "d-glucose". If a query contains multiple terms, they are split by whitespace and searched separately, in the order the words are given, to enable a form of "fuzzy" matching.

The data is taken from {{ "https://www.ebi.ac.uk/chebi/init.do"|external_link("ChEBI") }} and the identifiers in that database are shown in brackets. A similar interface is used for microbial strains taken from {{ "https://www.ncbi.nlm.nih.gov/datasets/"|external_link("NCBI") }}.
</li>

<li>
Once a particular step is submitted, the interface shows the sub-forms in the next step and renders a "status" view for the other ones. In this subfigure, we can see green check-marks that indicate completed steps and yellow minus signs for pending ones. You do not have to navigate steps in order, even if the forms are interconnected. You can investigate the submission process in its entirety before entering the data in order.
</li>

<li>
A composable sub-form that is used to describe multiple different records of the same type in one step. This particular example is a form to describe communities. Each sub-form consists of the name and strain composition of a single community. Pressing the bottom-right button saves the current partial state and adds another form. That way, reloading the page does not discard previously-typed information. A new form that is not persisted yet is surrounded with a dashed line, while the ones that have been saved have a solid border.

The sub-form can be duplicated, repeating the contents of the fields, other than the ones that are required to be unique. In the community form shown here, duplicating would copy the list of strains, but it would leave the name blank. In some cases, for convenience, the duplication logic checks if the name contains a number and increments it in the next form. If a biological replicate is defined with the name "biorep3", the next one is likely to be "biorep4", so a newly-added form pre-fills that field with that name, letting you edit it manually if they need to. Duplication is intended for large and complex forms that are likely to share similarities.
</li>

<li>
During partial submission on "Add" or "Duplicate", or after the final submission of a step, validation errors may be shown.
</li>
</ol>

<h2 id="step-1">Step 1: Project and study information</h2>

The first step requests basic information about the study that is being uploaded, including its name and description, but also a description of its parent project:

<p>
    <div style="width: 100%; text-align: center">
    <img style="width: 80%; margin: 0 auto;" title="Step 1: Project and study form" src="/static/images/help/upload-process/step_1.png" />
    </div>
</p>

Each of the two dropdowns can either be "New project"/"New study" or it can be a selection of projects/studies that the user has access to. If you've uploaded a study before, its data will show up in these dropdowns. If someone has shared a study for you, it will also be available.

Depending on whether you pick existing uploads or new ones, the submission process will result in updating a new version of a study, adding a new study to an existing project, or starting a new project and study. The first two cases also allow you to change the textual descriptions or add a publication link if it is available.

The bottom dropdown allows you to copy a previous study's design for the following steps. This is only useful if you're creating a new study, but you'd like to avoid entering some of the details. In this particular example, we have an existing "Controls" study that contains some of the vessels in the larger project and we are adding a "Perturbations" study with another set of vessels. Many parts of the experimental design will be the same, so we can reuse the previous upload.

<h2 id="step-2">Step 2: Microbial strains</h2>

In step 2, all microbial strains that your study examines should be described:

<p>
    <div style="width: 100%; text-align: center">
    <img style="width: 80%; margin: 0 auto;" title="Step 1: Project and study form" src="/static/images/help/upload-process/step_2.png" />
    </div>
</p>

The textual input completes species and strains from an NCBI export. As you type, you should see a dropdown with names that match your text input. If you don't find your specific strain or you have a custom strain, you can use the "Add custom strain" button to define them. In that case, please provide a short description with information for your strain that might be relevant to your study.

<h2 id="step-3">Step 3: Measurement methods</h2>

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        class="no-border"
        src="/static/images/help/upload-process/step_3_1.png"
        title="Step 3: Community-level subform" />
    <img
        class="no-border"
        src="/static/images/help/upload-process/step_3_2.png"
        title="Step 3: Strain-level subform" />
    <img
        class="no-border"
        src="/static/images/help/upload-process/step_3_3.png"
        title="Step 3: Metabolite subform" />
</div>

The methods of measurement need to be described by the technique that was used, the units that were measured, and the specific details of the methodology. Some additional notes on the types of techniques follow:

- **Plate counts** are expected be measured in CFUs, so when selecting this option, the units will be automatically changed to "CFUs/mL". The interface won't stop you from picking a different unit afterwards.
- **Optical density** defaults to "N/A" units, but if you have a standard curve, you could map them to absolute cell concentrations, so feel free to change that value as well. The app assumes that the entered measurements are after subtraction of blanks.
- **Flow cytometry** measurements are expected to be recorded after gating. These are available either for entire communities or per strain. FC per strain could also be calculated based on other techniques that produce relative abundance ratios, like qPCR or 16S.
- **pH** measurements are included in the "Community" measurements, since they are considered a property of the growth vessel/compartment.
- **Metabolite** measurements do not require describing the specific measurement technique, but it is encouraged to enter it in the "description" field. Units can be either molar concentrations (e.g. mM) or mass concentrations (e.g. g/L), or they could be unitless AUC values that can be used for relative comparisons.

At the bottom of each sub-form, a preview shows the names of the columns that will be requested in the data spreadsheet in step 6. Depending on the type of measurement, the column may be a static string like "Community OD" or the name of the measurement subject like "Roseburia intestinalis rRNA reads". You can check the "Include STD" checkbox to add columns to the data spreadsheet for standard deviation measurements. If you have multiple technical replicates, you can upload point averages and standard deviations to quantify the variability of the measurements.

<h2 id="step-4">Step 4: Compartments and communities</h2>

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        class="no-border"
        src="/static/images/help/upload-process/step_4_1.png"
        title="Step 4: Compartment subform" />
    <img
        class="no-border"
        src="/static/images/help/upload-process/step_4_2.png"
        title="Step 4: Community subforms" />
</div>

You can describe the physical containers of microbial communities as "compartments". You might have a single compartment per vessel, but it's also possible to define e.g. broth and mucin beads floating inside as separate "compartments" that you measure separately as well. Even if they are separate, they are still in the same biological system, so microbes can move between them. If there is more than one compartment associated with a particular experiment, its replicates will have subscripts for the different compartments, for example "BiorepA1<sub>C1</sub>".

Compartments also define sets of environmental conditions. If you change environments e.g. by modifying pH from neutral to acidic, you can describe the two environments as two separate compartments and describe the change in pH in a **perturbation** by switching from e.g. compartment C0 to compartment C- or C+.

To describe the medium, it is recommended to provide a link to {{ "https://mediadive.dsmz.de/media"|external_link("MediaDive") }}. You can define a custom medium using their {{ "https://mediadive.dsmz.de/docs/medium-builder"|external_link("medium builder") }}.

Communities are defined based on the strains that were entered in step 2. Each experiment will be defined with a single community. If your experiment involves changing the species composition (e.g. adding a new strain) during the experiment, you will be able to describe that by adding a perturbation from one defined community to another.

<h2 id="step-5">Step 5: Experimental design</h2>

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        class="no-border"
        src="/static/images/help/upload-process/step_5_1.png"
        title="Step 5: Experiment form" />
</div>


The definition of an "experiment" combines the information that has been entered in the previous steps. In the example figure, a particular experiment has been defined with one community, two compartments, and three biological replicates. The replicates are concrete implementations of the experiment design and can be added in a nested sub-form. There is another nested sub-form for defining "perturbations", which are changes to the experiment applied at particular time points. These changes may involve adding or removing strains or modifying environmental conditions. These are described, respectively, by changing the community of the experiment, and by changing one of its compartments to a different one.

Some example cases:

- You're studying how bacteria grow in different nutrient environments, you set up 3 separate flasks, each containing the same culture of bacteria in a different nutrient solution. Each flask represents a different experiment with only one biological replicate for each of them. You have **3 experiments** with **1 biological replicate** for each. The experiments have the **same community**, but **different compartments**.
- You're studying how 5 bacterial strains grow in a particular medium, you set up 5 separate flasks, each containing a culture of one of the strains in the same nutrient solution. Each flask represents a separate experiment. You have **5 experiments** with **1 biological replicate** for each. The experiments have **different communities**, but the **same compartment**.

The number of time points that have been measured for this experiment also needs to be entered, and will determine the number of rows per biological replicate per compartment that are generated in the data spreadsheet template.

The names of both the experiment and the biological replicate should be chosen to be short, but distinct enough for readers to associate. The name "BT_MUCIN" suggests a <em>Bacteroides thetaiotaomicron</em> culture with mucin beads in the vessel.

<h2 id="step-6">Step 6: Data upload</h2>

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        class="no-border"
        src="/static/images/help/upload-process/submission_12.png"
        title="Step 6: Data upload form" />
    <img
        class="no-border"
        src="/static/images/help/upload-process/step_6_1.png"
        title="Step 6: Spreadsheet example" />
</div>

Once the study design is entered, you can download a spreadsheet template to fill in with your data. The template is pre-filled with rows for each combination of biological replicate, compartment, and time point. There are three sheets for community-level, strain-level, and metabolite measurements. The columns each have a different subject of measurement.

Once the data is uploaded, its cells are validated, and errors may be shown that guide you to missing or invalid values. You can see a preview of the spreadsheet and examine it in the browser to look for any issues. The file will be stored in the submission, so if you lose your local copy, you can always come back to this submission and download it.

**Empty cells** represent missing data. This could happen due to missing or invalid measurements for a particular biological replicate, or simply because a particular measurement subject is not present in a particular experiment. In the example to the right, the biological replicate RI\_WC\_3 only contains _Roseburia intestinalis_, but no _Bacteroides thetaiotaomicron_.

If a particular cell does not have a value, a measurement will not be recorded for it in the database. If you want to record a measurement of zero, you need to actually put the value 0 in a cell. However, all time points need to be entered in the "Time" column, even if they are not associated with any data.

<h2 id="step-7">Step 7: Publish</h2>

In step 7, the data will already have been processed and your study should be created:

<p>
    <div style="width: 100%; text-align: center">
    <img style="width: 80%; margin: 0 auto;" title="Step 7: Publish" src="/static/images/help/upload-process/submission_13.png" />
    </div>
</p>

You can review your study, but it will only be visible to the public once you click the "Publish" button. This will only be allowed after a 24-hour period. If you are just experimenting with the interface, you can simply avoid publishing altogether. In the future, the application may have a "test mode" to more clearly separate "test" studies and ones intended for publishing.

After submitting and publishing your study, you can still come back to this submission to update it, if necessary. To retract a study, please send us an email to explain your situation. You can find contact details on our lab's website, {{ "http://msysbiology.com/"|external_link() }}.
