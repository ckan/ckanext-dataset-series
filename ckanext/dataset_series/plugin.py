import json

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit

from ckanext.dataset_series.actions import package_show
from ckanext.dataset_series.helpers import get_helpers
from ckanext.dataset_series.validators import get_validators


class DatasetSeriesPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IValidators)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "dataset_series")

    # IActions

    def get_actions(self):
        return {
            "package_show": package_show,
        }

    # IPackageController

    def before_dataset_index(self, dataset_dict):
        if dataset_dict.get("in_series"):
            try:
                dataset_dict["vocab_in_series"] = json.loads(dataset_dict["in_series"])
            except ValueError:
                pass
        return dataset_dict

    # ITemplateHelpers
    def get_helpers(self):
        return get_helpers()

    # IValidators
    def get_validators(self):
        return get_validators()
