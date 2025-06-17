## Study navigation

A study uploaded to μGrowthDB provides multiple different views of its data. You can navigate between them by using a navigation bar that jumps between 4 different sections:

<p>
    <div style="width: 100%; text-align: center">
    <img style="width: 80%; margin: 0 auto;" title="Study navigation bar" src="/static/images/help/data-analysis/study_show_1.png" />
    </div>
</p>

- **View information**: Shows the study homepage with general information about the study and its experiments
- **Visualize**:        Allows plotting the data of this particular study
- **Export data**:      Provides an interface to download the raw measurements in CSV format
- **Manage**:           Allows the owners of the study to make changes to it and fit models to the data

This particular example is taken from the study <a target="_blank" href="{{ url_for("study_show_page", studyId="SMGDB00000002") }}">SMGDB00000002</a>.

## Study homepage

<div class="image-container" style="width: 40%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        src="/static/images/help/data-analysis/study_show_2.png"
        title="Basic study information" />
    <img
        src="/static/images/help/data-analysis/study_show_4.png"
        title="Biological replicates" />
</div>

The central place that acts as a hub for all the different ways to interact with a study is the study homepage. The study has a permanent unique ID, in these examples "<a target="_blank" href="{{ url_for("study_show_page", studyId="SMGDB00000002") }}">SMGDB00000002</a>", which can be shared in publications. Projects have identifiers starting with "PMGDB" and experiment IDs are prefixed with "EMGDB".

The basic information shown right below the title includes the name of the uploader, and timestamps to indicate when the data was uploaded or updated. Ideally, a study would not be changed after uploading, but it is possible that mistakes are made and corrections are necessary. A study owner is allowed to go back to the submission process and upload new data or change the experimental design. However, every separate submission is stored as a data package that can be accessed and potentially restored by the μGrowthDB administrators if necessary.

The study page continues with separate sections for each of its experiments. There are subsections for each biological replicate and individual list items with the measured subjects. In the images on the right, the "BT\_MUCIN\_1<sub>WC</sub>" notation indicates a measurement of the WC **compartment** within the BT\_MUCIN\_1 **replicate**. A synthetic replicate called "Average(BT\_MUCIN<sub>WC</sub>)" is created during the upload process with the average values for all time points across the biological replicates in that compartment of the BT\_MUCIN experiment.

The double-arrows icon adds the measurements represented by the line to the "Compare" view, described below in "Cross-study comparison". The chart icon sends the user to the "Visualize" section with the measurements added to the chart, examined in more detail in the next section.

## Exploration of a single study

<div class="image-container" style="width: 50%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        src="/static/images/help/data-analysis/bt_mucin_growth.png"
        title="Two different compartments shown on one chart" />
    <img
        src="/static/images/help/data-analysis/chart_left_right_controls.png"
        title="Left/right axis controls" />
</div>

On the visualize page (<a target="_blank" href="{{ url_for("study_show_page", studyId="SMGDB00000002") }}">Example: SMGDB00000002</a>), you can see the form interface shown on the right figure. You can select an experiment from the top-most dropdown and a measurement technique from the one below. As you change these filters, the visible checkboxes show the available measurement subjects.

This example shows the BT\_MUCIN experiment, in which mucin beads were added to a bottle with Wilkins-Chalgrens (WC) medium. Because the WC broth and the mucin beads are in the same biological system, they are considered part of the same **biological replicate** of the experiment. Because they represent different physical locations that the researchers measure separately, they are described by separate **compartments**.

You can move individual measurement traces between the left and right axis using the controls under the chart. Ticking a checkbox aligns the label to the left or right and updates the visuals. This can allow you to fit observations of two different kinds of measurements onto the same chart and observe their correspondence over time. The "Log view" checkboxes control whether the data is log-transformed on either axis.

The software allows you to add multiple incompatible types of measurements on the same axis. Its label is set to "[mixed units]" and the user is free to decide how to organize their data. In some cases, values may be at the right orders of magnitude to provide useful information even when mixed. For instance, the pH level and metabolite concentrations might both be readable on the same axis. You can use the "Log view" checkboxes to apply a natural logarithm to either one of the axes.

From this page, you can copy the "Permalink to this page" hyperlink and send it to other researchers for the purposes of collaboration. You could also add the charts to the "Compare" view by clicking on the bottom-right "Compare across studies" button seen in that same figure.

## Cross-study comparison

After investigating data in a particular study using the "Visualize" interface, you can add the selected traces and copy them to the "Compare" view by pressing the "Compare across studies" button. It is also possible to click on any of the buttons with a left-right icon (↔️) in the study homepage. Once either of these types of buttons are clicked, you can visit the "Compare" page from the navigation sidebar. The number of data traces currently loaded in the compare view is shown in that same sidebar link.

After picking data from different studies, you can click the sidebar menu button to go to the "Compare" page. In the example below, we see a comparison between the growth curves of _R. intestinalis_ and _B. thetaiotaomicron_ in two studies, <a target="_blank" href="{{ url_for("study_show_page", studyId="SMGDB00000001") }}">SMGDB00000001</a> and <a target="_blank" href="{{ url_for("study_show_page", studyId="SMGDB00000003") }}">SMGDB00000003</a>. Both of these experiments grow the cultures in a chemostat and we can see a correspondence in the shapes of the curves in both cases.

<p>
    <div style="width: 100%; text-align: center">
    <img style="width: 80%; margin: 0 auto;" title="Compare view" src="/static/images/help/data-analysis/compare_view_1.png" />
    </div>
</p>


The chart works in a very similar way to the one described in section the previous section. Checkboxes at the top of the page control which data traces will be placed on the chart. Below, there is a section that controls their positioning on the left or right axis. There are controls to log-transform the data and convert between units (which are automatically unified if possible). The chart is rendered in a wider container to account for the fact that more contextual information needs to be added to the descriptions of the data traces. The zoom level automatically focuses on the shortest data trace.

## Modeling

<div class="image-container" style="width: 40%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        src="/static/images/help/data-analysis/modeling_interface_1_2.png"
        title="Modeling form" />
    <img
        src="/static/images/help/data-analysis/modeling_params_2.png"
        title="Model visualization chart" />
    <img
        src="/static/images/help/data-analysis/modeling_params_3.png"
        title="Parameter information" />
</div>

The modeling functionality can be found on a study's "Manage" page. You can reach it by pressing the rightmost button on the navigation interface. This page and the button that links to it are only visible to users that have managing permissions on the study, which is why the button is colored orange to highlight its different nature. Executing code to fit models is a potentially time- and resource-consuming action, which is why it is limited to the owners of the study and not to all visitors. Additionally, models can be parameterized in different ways, which is an active choice that should be made by the researchers the data belongs to in the first place.

On the "Manage" page, you can scroll down to the "Growth models" section where you can see a similar interface to the one in the "Visualize" page. In both forms, experiments and measurement techniques are available in dropdowns to select individual measurement subjects. A difference in the modeling form is that you can only examine one subject at a time, selecting it with a radio button.

The form submits a request to model a particular collection of data points that enqueues a background job. The code fits the requested model with the given input parameters and saves it in the database with an updated status. The interface is updated once the task is completed. Refreshing the page does not disrupt the process.

Be advised that the specific parameters you pick can make a big difference in the results. The application will attempt to fit the data you provide, but it might fail, depending on its form. The models provided are intended for the lag, exponential, and stationary phases of microbial growth.

For the logistic model and Baranyi-Roberts, the current parameterization is for the end time for the data points that will be fitted. For the "Easy linear" method, you can pick the number of data points used to determine the slope of the fit. Once you have fitted the separate models to the desired data traces, you can download all the model parameters by using a button at the top of the page labeled "Download completed models as CSV". The resulting file has one row per fitted model and columns for its individual parameters.

## Data exports

<img
    style="width: 50%; float: right; margin-left: 20px;"
    src="/static/images/help/data-analysis/export_ui_1_2.png"
    title="Export interface" />

The study navigation interface includes an "Export data" button. Pressing it leads to a page where you can download data from selected biological replicates of a study in CSV format. The form allows selecting individual biological replicates to export and changing the checkboxes updates the preview on the right-hand side.

Once the desired combination of data is selected, the "Download ZIP file" button groups it into CSV files and compresses them into a single zip archive. A "README" file is also included with information about the study and the selected experiments.

The URL shown next to the download button can be used to fetch the selected subset of data on the command-line. This can be particularly useful when working on a remote server, or when the data from multiple studies needs to be processed in batches.
