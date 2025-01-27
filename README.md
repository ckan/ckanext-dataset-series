[![Tests](https://github.com//ckanext-dataset-series/workflows/Tests/badge.svg)](https://github.com//ckanext-dataset-series/actions/workflows/test.yml)

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

This extension uses a custom dataset type (`dataset-series`) to define the parent series entities. These are
just datasets and can have any of the standard dataset fields defined.

If the series is ordered, the only mandatory fields they need 
are the following (shown in the [ckanext-scheming](https://github.com/ckan/ckanext-scheming) schema file definition):

```yaml
scheming_version: 2
dataset_type: dataset-series

dataset_fields:

# [...]

# Series fields

# Empty for un-ordered series
- field_name: series_order_field
  label: Series order field

- field_name: series_order_type
  label: Series order type
```

At the dataset level, the series membership is defined with the `in_series` field. Datasets can belong to multiple series:

```yaml
scheming_version: 2
dataset_type: dataset

dataset_fields:

# [...]

# Series fields

- field_name: in_series
  label: In Series
  preset: multiple_text
```

Once these are in place, datasets can be assigned to a series by setting the `in_series` field via the API or the UI form.

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
          "title": "Test Dataset series"
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
          "next": {
              "id": "ce8fb09a-f285-4ba8-952e-46dbde08c509",
              "name": "test-series-member-3",
              "title": "Test series member 3"
          },
          "previous": {
              "id": "826bd499-40e5-4d92-bfa1-f777775f0d76",
              "name": "test-series-member-1",
              "title": "Test series member 1"
          },
          "title": "Test Dataset series"
      }
  ]
}

```

Querying the series dataset will also return a `series_navigation` link if ordered, in this case linking to the first and last members:

```json
{
   "name": "test-dataset-series",
   "type": "dataset-series",
   "series_navigation": {
 	  "first": {
 		  "id": "826bd499-40e5-4d92-bfa1-f777775f0d76",
 		  "name": "test-series-member-1",
 		  "title": "Test series member 1"
 	  },
 	  "last": {
 		  "id": "ce8fb09a-f285-4ba8-952e-46dbde08c509",
 		  "name": "test-series-member-3",
 		  "title": "Test series member 3"
 	  }
   }
}

```

## UI

> [!NOTE]
> TODO

* Form snippet for `in_series` displaying available dataset series
* Series navigation in dataset member pages linking to next and previous datasets
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
   git clone https://github.com//ckanext-dataset-series.git
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
