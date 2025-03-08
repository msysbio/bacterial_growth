# Data export of study {{ study['studyId'] }}

## {{ study['studyName'] }}

{{ study['studyDescription'] }}

## Exported experiments

{% for experiment in experiments: -%}
- {{ experiment.experimentId }}: {{ experiment.experimentDescription }}
{% endfor %}
## More information

DOI: <{{ study['studyURL'] }}>
