from typing import Any, Callable

import ckan.plugins.toolkit as tk


EXCLUDE_FROM_ORDER = (
    "id",
    "relationships_as_subject",
    "relationships_as_object",
    "organization",
    "creator_user_id",
    "owner_org",
)

EXTRA_ORDER_FIELDS = {
    "metadata_modified": "Metadata Modified",
    "metadata_created": "Metadata Created",
}


def get_helpers() -> dict[str, Callable[..., Any]]:
    return {
        "in_series_choices": in_series_choices,
        "series_order_choices": series_order_choices,
    }


def in_series_choices(field: dict[str, Any]) -> list[dict[str, str]]:
    """Return a list of options for the in_series field.

    Args:
        field: Scheming field definition.

    Returns:
        A list of options for the in_series field.
    """
    result = tk.get_action("package_search")(
        {"user": tk.current_user.name},
        {
            "q": f"type:dataset_series",
            "rows": 1000,
            "fl": "title, id",
            "include_private": True,
        },
    )

    return [
        {"value": package["id"], "label": package["title"]}
        for package in result["results"]
    ]


def series_order_choices(field: dict[str, Any]) -> list[dict[str, str]]:
    """Return a list of options for the series_order field.

    Args:
        field: Scheming field definition.

    Returns:
        A list of options for the series_order field.
    """
    if "scheming_datasets" in tk.g.plugins:
        return _get_order_fields_from_scheming()

    return _get_order_fields_from_package_search()


def _get_order_fields_from_scheming() -> list[dict[str, str]]:
    """
    Get the order fields from the scheming dataset schemas.

    Traverse all the dataset schemas and get the fields that are not in the
    EXCLUDE_FROM_ORDER set.

    If the schema does not have an in_series field, skip it.
    """
    schemas = tk.h.scheming_dataset_schemas()
    fields = {}

    for field_name, field_label in EXTRA_ORDER_FIELDS.items():
        fields[field_name] = {"field_name": field_name, "label": field_label}

    for schema in schemas.values():
        include_fields = False
        schema_fields = {}

        for field in schema.get("dataset_fields", []):
            schema_fields[field["field_name"]] = field

            if field["field_name"] == "in_series":
                include_fields = True

        # if the schema does not have an in_series field, skip it
        if not include_fields:
            continue

        for field_name, field in schema_fields.items():
            if field_name in EXCLUDE_FROM_ORDER:
                continue

            if "label" not in field:
                field["label"] = field["field_name"]

            fields[field_name] = field

    return [
        {"value": field["field_name"], "label": field["label"]}
        for field in fields.values()
    ]


def _get_order_fields_from_package_search() -> list[dict[str, str]]:
    """
    Get the order fields from the package search.

    Traverse all the package types and get the fields that are not in the
    EXCLUDE_FROM_ORDER set.
    """
    result = tk.get_action("package_search")(
        {"user": tk.current_user.name},
        {
            "q": f"in_series:[* TO *]",
            "rows": 0,
            "facet.field": ["type"],
            "include_private": True,
        },
    )

    package_types = list(result["facets"].get("type", {}))
    fields = set()

    for package_type in package_types:
        result = tk.get_action("package_search")(
            {"user": tk.current_user.name},
            {
                "q": f"type:{package_type}",
                "rows": 1,
                "include_private": True,
            },
        )

        if not result["results"]:
            continue

        fields.update(
            [
                field_name
                for field_name in result["results"][0]
                if field_name not in EXCLUDE_FROM_ORDER
            ]
        )

    return [{"value": field_name, "label": field_name} for field_name in fields]
