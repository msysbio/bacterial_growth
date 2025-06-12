## Study navigation

To explore the data of a study, we need to navigate...

## Study homepage

TODO

## Exploration of a single study

TODO

## Cross-study comparison

TODO

## Modeling

<div style="width: 40%; float: right; margin-left: 20px; margin-top: 20px;">
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

On the "Manage" page, you can scroll down to the "Growth models" section where you can see a similar interface to the one in the "Visualize" page. In both forms, experiments and measurement techniques are available in dropdowns to select individual measurement subjects. A difference in the modeling form is that we can only examine one subject at a time, selecting it with a radio button.

The form submits a request to model a particular collection of data points that enqueues a background job. The code fits the requested model with the given input parameters and saves it in the database with an updated status. The interface is updated once the task is completed. Refreshing the page does not disrupt the process.

Be advised that the specific parameters you pick can make a big difference in the results. The application will attempt to fit the data you provide, but it might fail, depending on its form. The models provided are intended for the lag, exponential, and stationary phases of microbial growth.

For the logistic model and Baranyi-Roberts, the current parameterization is for the end time for the data points that will be fitted. For the "Easy linear" method, we can pick the number of data points used to determine the slope of the fit. Once you have fitted the separate models to the desired data traces, you can download all the model parameters by using a button at the top of the page labeled "Download completed models as CSV". The resulting file has one row per fitted model and columns for its individual parameters.

## Data exports

<img
    style="width: 50%; float: right; margin-left: 20px;"
    src="/static/images/help/data-analysis/export_ui_1_2.png"
    title="Export interface" />

The study navigation interface includes an "Export data" button. Pressing it leads to a page where you can download data from selected biological replicates of a study in CSV format. The form allows selecting individual biological replicates to export and changing the checkboxes updates the preview on the right-hand side.

Once the desired combination of data is selected, the "Download ZIP file" button groups it into CSV files and compresses them into a single zip archive. A "README" file is also included with information about the study and the selected experiments.

The URL shown next to the download button can be used to fetch the selected subset of data on the command-line. This can be particularly useful when working on a remote server, or when the data from multiple studies needs to be processed in batches.
