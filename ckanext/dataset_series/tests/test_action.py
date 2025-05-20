import pytest

from ckan.tests import factories
from ckan.tests.helpers import call_action


@pytest.fixture
def series_fixtures():
    dataset_series = factories.Dataset(type="dataset_series", series_order_field="name")

    dataset1 = factories.Dataset(
        name="test-series-member-1", in_series=dataset_series["id"]
    )
    dataset2 = factories.Dataset(
        name="test-series-member-2", in_series=dataset_series["id"]
    )
    dataset3 = factories.Dataset(
        name="test-series-member-3", in_series=dataset_series["id"]
    )

    return {
        "dataset_series": dataset_series,
        "dataset1": dataset1,
        "dataset2": dataset2,
        "dataset3": dataset3,
    }


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dataset_series scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dataset_series.schemas:dataset_series.yaml "
    "ckanext.dataset_series.schemas:dataset_in_series.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dataset_series.schemas:presets.yaml",
)
def test_series_navigation(series_fixtures):

    series_dict = call_action(
        "package_show", id=series_fixtures["dataset_series"]["id"]
    )

    assert "series_navigation" in series_dict

    assert series_dict["series_navigation"]["count"] == 3

    fields = ("id", "name", "title", "type")
    for item, dataset in [("first", "dataset1"), ("last", "dataset3")]:
        for field in fields:
            assert (
                series_dict["series_navigation"][item][field]
                == series_fixtures[dataset][field]
            ), (item, dataset, field)


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dataset_series scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dataset_series.schemas:dataset_series.yaml "
    "ckanext.dataset_series.schemas:dataset_in_series.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dataset_series.schemas:presets.yaml",
)
def test_empty_series_navigation(series_fixtures):

    dataset_series = factories.Dataset(type="dataset_series", series_order_field="name")
    series_dict = call_action("package_show", id=dataset_series["id"])

    assert series_dict["series_navigation"]["count"] == 0

    assert series_dict["series_navigation"]["first"] is None
    assert series_dict["series_navigation"]["last"] is None


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dataset_series scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dataset_series.schemas:dataset_series.yaml "
    "ckanext.dataset_series.schemas:dataset_in_series.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dataset_series.schemas:presets.yaml",
)
def test_series_first_dataset(series_fixtures):

    dataset_dict = call_action("package_show", id=series_fixtures["dataset1"]["id"])

    assert len(dataset_dict["series_navigation"]) == 1

    for field in ("id", "name", "title", "type"):
        assert (
            dataset_dict["series_navigation"][0][field]
            == series_fixtures["dataset_series"][field]
        ), field

        assert (
            dataset_dict["series_navigation"][0]["next"][field]
            == series_fixtures["dataset2"][field]
        ), field

    assert dataset_dict["series_navigation"][0]["previous"] is None


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dataset_series scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dataset_series.schemas:dataset_series.yaml "
    "ckanext.dataset_series.schemas:dataset_in_series.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dataset_series.schemas:presets.yaml",
)
def test_series_middle_dataset(series_fixtures):

    dataset_dict = call_action("package_show", id=series_fixtures["dataset2"]["id"])

    assert len(dataset_dict["series_navigation"]) == 1

    for field in ("id", "name", "title", "type"):
        assert (
            dataset_dict["series_navigation"][0][field]
            == series_fixtures["dataset_series"][field]
        ), field

        assert (
            dataset_dict["series_navigation"][0]["previous"][field]
            == series_fixtures["dataset1"][field]
        ), field

        assert (
            dataset_dict["series_navigation"][0]["next"][field]
            == series_fixtures["dataset3"][field]
        ), field


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dataset_series scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dataset_series.schemas:dataset_series.yaml "
    "ckanext.dataset_series.schemas:dataset_in_series.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dataset_series.schemas:presets.yaml",
)
def test_series_last_dataset(series_fixtures):

    dataset_dict = call_action("package_show", id=series_fixtures["dataset3"]["id"])

    assert len(dataset_dict["series_navigation"]) == 1

    for field in ("id", "name", "title", "type"):
        assert (
            dataset_dict["series_navigation"][0][field]
            == series_fixtures["dataset_series"][field]
        ), field

        assert (
            dataset_dict["series_navigation"][0]["previous"][field]
            == series_fixtures["dataset2"][field]
        ), field

    assert dataset_dict["series_navigation"][0]["next"] is None


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dataset_series scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dataset_series.schemas:dataset_series.yaml "
    "ckanext.dataset_series.schemas:dataset_in_series.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dataset_series.schemas:presets.yaml",
)
def test_series_only_dataset():

    dataset_series = factories.Dataset(type="dataset_series", series_order_field="name")

    dataset_only = factories.Dataset(
        name="test-series-only-member", in_series=dataset_series["id"]
    )

    dataset_dict = call_action("package_show", id=dataset_only["id"])

    assert len(dataset_dict["series_navigation"]) == 1

    assert dataset_dict["series_navigation"][0]["id"] == dataset_series["id"]

    assert dataset_dict["series_navigation"][0]["previous"] is None
    assert dataset_dict["series_navigation"][0]["next"] is None


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dataset_series scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dataset_series.schemas:dataset_series.yaml "
    "ckanext.dataset_series.schemas:dataset_in_series.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dataset_series.schemas:presets.yaml",
)
def test_series_date_field():

    dataset_series = factories.Dataset(
        type="dataset_series",
        series_order_field="metadata_created",
        series_order_type="date",
    )

    dataset1 = factories.Dataset(
        name="test-series-member-1", in_series=dataset_series["id"]
    )
    dataset2 = factories.Dataset(
        name="test-series-member-2", in_series=dataset_series["id"]
    )
    dataset3 = factories.Dataset(
        name="test-series-member-3", in_series=dataset_series["id"]
    )

    dataset_dict = call_action("package_show", id=dataset1["id"])

    assert dataset_dict["series_navigation"][0]["previous"] is None
    assert dataset_dict["series_navigation"][0]["next"]["id"] == dataset2["id"]

    dataset_dict = call_action("package_show", id=dataset2["id"])

    assert dataset_dict["series_navigation"][0]["previous"]["id"] == dataset1["id"]
    assert dataset_dict["series_navigation"][0]["next"]["id"] == dataset3["id"]

    dataset_dict = call_action("package_show", id=dataset3["id"])

    assert dataset_dict["series_navigation"][0]["previous"]["id"] == dataset2["id"]
    assert dataset_dict["series_navigation"][0]["next"] is None
