import json

import pytest

from ckan.tests import factories
from ckan.plugins.toolkit import Invalid
from ckanext.dataset_series.validators import series_validator


def test_series_validator_valid_series():

    user = factories.User()
    dataset_series = factories.Dataset(type="dataset_series")

    value = json.dumps([dataset_series["id"]])
    context = {"user": user["name"]}

    assert series_validator(value, context)


def test_series_validator_valid_multiple_series():

    user = factories.User()
    dataset_series1 = factories.Dataset(type="dataset_series")
    dataset_series2 = factories.Dataset(type="dataset_series")

    value = json.dumps([dataset_series1["id"], dataset_series2["id"]])
    context = {"user": user["name"]}

    assert series_validator(value, context)


def test_series_validator_invalid_dataset_not_found():

    value = json.dumps(["some_id"])

    with pytest.raises(Invalid) as e:
        series_validator(value, {})

    assert e.value.error == "Dataset series not found"


def test_series_validator_invalid_dataset_wrong_type():
    dataset_series = factories.Dataset()

    value = json.dumps([dataset_series["id"]])

    with pytest.raises(Invalid) as e:
        series_validator(value, {})

    assert e.value.error == "Wrong dataset type for dataset series"


def test_series_validator_auth():
    user = factories.User()
    org = factories.Organization(users=[{"name": user["name"], "capacity": "admin"}])
    dataset_series = factories.Dataset(type="dataset_series", owner_org=org["id"])

    value = json.dumps([dataset_series["id"]])
    context = {"user": user["name"], "ignore_auth": False}

    assert series_validator(value, context)


def test_series_validator_auth_failed():
    user = factories.User()
    # User does not belong to the organization
    org = factories.Organization()
    dataset_series = factories.Dataset(type="dataset_series", owner_org=org["id"])

    value = json.dumps([dataset_series["id"]])
    context = {"user": user["name"], "ignore_auth": False}

    with pytest.raises(Invalid) as e:
        series_validator(value, context)

    assert e.value.error == "User not authorized to add datasets to this series"
