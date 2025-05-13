# Data export of study {{ study['studyId'] }}

## {{ study['studyName'] }}

{{ study['studyDescription'] }}

## Exported experiments

{% for experiment in experiments: -%}
- {{ experiment.name }}: {{ experiment.description }}
{% endfor %}
## More information

DOI: <{{ study['studyURL'] }}>
