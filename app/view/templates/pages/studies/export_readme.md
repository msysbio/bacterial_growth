# Data export of study {{ study.publicId }}

## {{ study.name }}

{{ study.description }}

## Exported experiments

{% for experiment in study.experiments: -%}
- {{ experiment.name }}: {{ experiment.description }}
{% endfor %}
{% if study.studyURL: %}
## More information

URL: <{{ study.studyURL }}>
{% endif %}
