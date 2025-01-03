# Data export of study {{ study['studyId'] }}

## {{ study['studyName'] }}

{{ study['studyDescription'] }}

## Exported experiments

{% for experiment in experiments: -%}
- {{ experiment.experiment_id }}: {{ experiment.experiment_description }}
{% endfor %}
## More information

DOI: <{{ study['studyURL'] }}>
