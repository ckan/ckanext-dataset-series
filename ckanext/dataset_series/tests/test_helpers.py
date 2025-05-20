import json
from unittest import mock

import pytest

from ckan.tests import factories
from ckan.plugins.toolkit import Invalid
from ckanext.dataset_series.helpers import in_series_choices


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_in_series_choices():

    dataset_series1 = factories.Dataset(type="dataset_series", title="Series 1")
    dataset_series2 = factories.Dataset(type="dataset_series", title="Series 2")

    assert in_series_choices({}) == [
        {"value": dataset_series1["id"], "label": dataset_series1["title"]},
        {"value": dataset_series2["id"], "label": dataset_series2["title"]},
    ]


class MockUser:

    def __init__(self, name):
        self.name = name


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_in_series_choices_auth():
    user = factories.User()
    org1 = factories.Organization(users=[{"name": user["name"], "capacity": "admin"}])
    org2 = factories.Organization()

    dataset_series1 = factories.Dataset(
        type="dataset_series", title="Series 1", owner_org=org1["id"]
    )
    factories.Dataset(
        type="dataset_series", title="Series 2", owner_org=org2["id"]
    )

    with mock.patch(
        "ckanext.dataset_series.helpers.current_user", MockUser(user["name"])
    ):
        assert in_series_choices({}) == [
            {"value": dataset_series1["id"], "label": dataset_series1["title"]},
        ]
