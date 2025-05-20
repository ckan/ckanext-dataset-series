[![Tests](https://github.com/ckan/ckanext-dataset-series/workflows/Tests/badge.svg)](https://github.com//ckanext-dataset-series/actions)

# ckanext-dataset-series

> [!WARNING]
> This is extension is a work in progress and may change at any point. Use with caution.

A fast and simple implementation of Dataset Series.

Dataset Series are loosely defined as collections of datasets that share some common characteristics.
These can be related to the nature of the data, scope, publishing process, etc. For instance:

* Budget data release monthly or yearly
* Data split by country / region
* Data big in size split into smaller chunks
* Geospatial data distributed in grids

Dataset Series can be ordered or unordered.


## How does it work?

This extension uses a custom dataset type (`dataset_series`) to define the parent series entities. These are
just datasets and can have any of the standard dataset fields defined.

If the series is ordered, the only mandatory fields they need
are the following (shown in the [ckanext-scheming](https://github.com/ckan/ckanext-scheming) schema file definition):

```yaml
scheming_version: 2
dataset_type: dataset_series

dataset_fields:

# [...]

# Series fields

- field_name: series_order_field
  preset: dataset_series_order

- field_name: series_order_type
  preset: dataset_series_order_type
```

At the dataset level, the series membership is defined with the `in_series` field. Datasets can belong to multiple series:

```yaml
scheming_version: 2
dataset_type: dataset

dataset_fields:

# [...]

# Series fields

- field_name: in_series
  preset: dataset_series_in_series
```

Once these are in place, datasets can be assigned to a series by setting the `in_series` field via the API or the UI form.

> [!NOTE]
> Only users that can update the Dataset Series dataset can add dataset members to it

## API

If a dataset belongs to a series, a new `series_navigation` key is added to the response of the `package_show` action, showing details of the series it belongs to:

```json
{
   "name": "test-dataset-in-series",
   "type": "dataset",
   "series_navigation": [
      {
          "id": "20f41df2-0b50-4b6b-9a75-44eb39411dca",
          "name": "test-dataset-series",
          "title": "Test Dataset series",
      }
  ]
}
```

If that series is ordered, it will include links to the previous and next dataset on the series (or `None` if they don't exist):

```json
{
   "name": "test-series-member-2",
   "type": "dataset",
   "series_navigation": [
      {
          "id": "20f41df2-0b50-4b6b-9a75-44eb39411dca",
          "name": "test-dataset-series",
          "title": "Test Dataset series",
          "next": {
              "id": "ce8fb09a-f285-4ba8-952e-46dbde08c509",
              "name": "test-series-member-3",
              "title": "Test series member 3"
              "type": "dataset"
          },
          "previous": {
              "id": "826bd499-40e5-4d92-bfa1-f777775f0d76",
              "name": "test-series-member-1",
              "title": "Test series member 1",
              "type": "dataset"
          }
      }
  ]
}

```

Querying the series dataset will also return a `series_navigation` link if ordered, in this case linking to the first and last members:

```json
{
   "name": "test-dataset-series",
   "type": "dataset_series",
   "series_navigation": {
      "count": 4,
 	  "first": {
 		  "id": "826bd499-40e5-4d92-bfa1-f777775f0d76",
 		  "name": "test-series-member-1",
 		  "title": "Test series member 1",
          "type": "dataset"
 	  },
 	  "last": {
 		  "id": "ce8fb09a-f285-4ba8-952e-46dbde08c509",
 		  "name": "test-series-member-3",
 		  "title": "Test series member 3",
          "type": "dataset"
 	  }
   }
}

```

## UI

The extension includes a `series_navigation.html` snippet that adds a series navigation to the dataset page, with links to the previous and next datasets in the series. The snippet is left deliberately unstyled so sites can tweak it to fit their own design.

For example, you can adjust your `package/read.html` template to include the snippet in the following way:

```Jinja
{% ckan_extends %}

{% block package_description %}
    {% snippet "package/snippets/series_navigation.html", package=pkg %}

    {{ super() }}
{% endblock %}
```
> [!NOTE]
> The snippet only works with the first series a dataset belongs to. You can adjust it to show the navigation for other series if needed

> [!NOTE]
> TODO

* Series page showing a navigation of the member datasets

## Requirements

If your extension works across different versions you can add the following table:

Compatibility with core CKAN versions:

| CKAN version    | Compatible? |
|-----------------|-------------|
| 2.9             | not tested  |
| 2.10            | yes         |
| 2.11            | yes         |


## Installation

To install ckanext-dataset-series:

1. Activate your CKAN virtual environment, for example:
   ```sh
   . /usr/lib/ckan/default/bin/activate
   ```

2. Clone the source and install it on the virtualenv
   ```sh
   git clone https://github.com/ckan/ckanext-dataset-series.git
   cd ckanext-dataset-series
   pip install -e .
   pip install -r requirements.txt
   ```

3. Add `dataset_series` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN.


## Developer installation

To install ckanext-dataset-series for development, activate your CKAN virtualenv and
do:

    git clone https://github.com//ckanext-dataset-series.git
    cd ckanext-dataset-series
    pip install -e .
    pip install -r dev-requirements.txt

## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
