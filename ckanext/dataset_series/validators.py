import json

from ckan import model
from ckan.plugins.toolkit import Invalid, NotAuthorized, check_access


def series_validator(value, context):

    if not value:
        return

    try:
        value = json.loads(value)
    except ValueError:
        raise Invalid("Wrong format, expected list of ids")

    for series_id in value:

        # Dataset exists and is of type series
        pkg = model.Package.get(series_id)
        if not pkg:
            raise Invalid("Dataset series not found")

        if not pkg.type == "dataset_series":
            raise Invalid("Wrong dataset type for dataset series")

        # Check user can update this dataset series
        try:
            check_access("package_update", {"user": context["user"]}, {"id": series_id})
        except NotAuthorized:
            raise Invalid("User not authorized to add datasets to this series")

    return json.dumps(value)


def get_validators():
    return {"series_validator": series_validator}
