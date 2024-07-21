import os
from jinja2 import Template, Environment, FileSystemLoader


def get_parameters(template):
    params = template.get('Parameters')
    if not params:
        params = template.get('parameters')
    if not params:
        params = []
    return params


def get_resources(template):
    resources = template.get('Resources')
    if not resources:
        resources = template.get('resources')
    if not resources:
        resources = []
    return resources


def get_outputs(template):
    outputs = template.get('Outputs')
    if not outputs:
        outputs = template.get('outputs')
    if not outputs:
        outputs = []
    return outputs


def get_description(template):
    description = template.get("Description")
    if not description:
        description = template.get('description')
    if not description:
        description = "No Template description set"
    return description

def add_breaks(text):
    # This is intended to loop through the multiline string and append each line with a break
    # cfn-flip is used within this tool to convert to json which does not support multiline
    # so currently this just adds a break to the single line that is returned.
    #
    # In future we will remove cfn-flip and support multiline in yaml so leaving it in

    return "".join([line+" <br>" for line in text.splitlines()])

def strip_newlines(text):
    # Removes line breaks from text and returns a single string, lines seperated with a space
    return " ".join([line for line in text.splitlines()])

func_dict = {
    "add_breaks": add_breaks,
    "strip_newlines": strip_newlines
}

TEMPLATE = """
## Description

{{ description }}
### Parameters

{% if parameters %}
| Parameter        | Type   | Default   | Description |
|------------------|--------|-----------|-------------|
{% for parameter in parameters %}
| {{ parameter }} | {{ parameters[parameter].Type }} | {% if parameters[parameter].Default %}{{ parameters[parameter].Default}}{% endif %} | {% if parameters[parameter].Description %}{{ strip_newlines(parameters[parameter].Description) }}{% endif %} |
{% endfor %}
{% else %}
*No parameters defined.*
{% endif %}

### Resources

{% if resources %}
| Resource         | Type   |
|------------------|--------|
{% for resource in resources %}
| {{ resource }} | {{ resources[resource].Type }} |
{% endfor %}
{% else %}
*No resources defined.*
{% endif %}

### Outputs

{% if outputs %}
| Output           | Description   |
|------------------|---------------|
{% for output in outputs %}
| {{ output }} | {% if outputs[output].Description %}{{ strip_newlines(outputs[output].Description) }}{% endif %} |
{% endfor %}
{% else %}
*No outputs defined.*
{% endif %}
"""

CHILD_TEMPLATE = """{% extends baseTemplate %}
{% block description %}
## Description

{{ description }}{% endblock %}

{% block parameters %}
### Parameters

{% if parameters %}
The list of parameters for this template:

| Parameter        | Type   | Default   | Description |
|------------------|--------|-----------|-------------|
{% for parameter in parameters %}
| {{ parameter }} | {{ parameters[parameter].Type }} | {% if parameters[parameter].Default %}{{ parameters[parameter].Default}}{% endif %} | {% if parameters[parameter].Description %}{{ strip_newlines(parameters[parameter].Description) }}{% endif %} |
{% endfor %}
{% else %}
*No parameters defined.*
{% endif %}
{% endblock %}

{% block resources %}
### Resources

{% if resources %}
The list of resources this template creates:

| Resource         | Type   |
|------------------|--------|
{% for resource in resources %}
| {{ resource }} | {{ resources[resource].Type }} |
{% endfor %}
{% else %}
*No resources defined.*
{% endif %}
{% endblock %}

{% block outputs %}
### Outputs

{% if outputs %}
| Output           | Description   |
|------------------|---------------|
{% for output in outputs %}
| {{ output }} | {% if outputs[output].Description %}{{ strip_newlines(outputs[output].Description) }}{% endif %} |
{% endfor %}
{% else %}
*No outputs defined.*
{% endif %}
{% endblock %}
"""


def generate(template, name, baseTemplatePath):
    description = get_description(template)
    parameters = get_parameters(template)
    resources = get_resources(template)
    outputs = get_outputs(template)
    try:
        env = Environment(loader=FileSystemLoader(baseTemplatePath))
        baseTemplate=env.get_template('README.jinja')
        childTemplate=Template(CHILD_TEMPLATE, trim_blocks=True, lstrip_blocks=True)
        childTemplate.globals.update(func_dict)
        return childTemplate.render(
            baseTemplate=baseTemplate,
            name=name,
            description=description,
            parameters=parameters,
            resources=resources,
            outputs=outputs,
        )
    except:
        template = Template(TEMPLATE, trim_blocks=True, lstrip_blocks=True)
        template.globals.update(func_dict)
        return template.render(
            name=name,
            description=description,
            parameters=parameters,
            resources=resources,
            outputs=outputs,
        )
