import logging
from typing import Any, Optional, Union, Tuple
from dateutil.parser import parse as parse_date, ParserError as DateParserError

import ckan.plugins.toolkit as toolkit
import ckan.types as types
from ckan.lib.search import SearchError

log = logging.getLogger(__name__)

@toolkit.side_effect_free
@toolkit.chained_action
def package_show(
    up_func: types.Action, context: types.Context, data_dict: types.DataDict
) -> types.DataDict:

    dataset_dict = up_func(context, data_dict)

    for_indexing = (
        toolkit.asbool(data_dict.get("for_indexing"))
        or context.get("use_cache") is False
    )

    if for_indexing or context.get("for_update", False):
        return dataset_dict

    if dataset_dict.get("type") == "dataset_series":
        _add_series_navigation(dataset_dict)

    elif dataset_dict.get("in_series"):
        _add_series_member_navigation(dataset_dict)

    return dataset_dict


def _add_series_member_navigation(dataset_dict: dict[str, Any]) -> None:
    """Add series navigation to the dataset dictionary.

    Args:
        dataset_dict (dict[str, Any]): The dataset dictionary to add series navigation to.

    Returns:
        The dataset dictionary with series navigation added.
    """
    for series_id in dataset_dict["in_series"]:
        series_navigation = _add_single_series_navigation(series_id, dataset_dict)

        if series_navigation:
            dataset_dict["series_navigation"].append(series_navigation)


def _add_single_series_navigation(
    series_id: str, dataset_dict: dict[str, Any]
) -> Optional[dict[str, Any]]:
    try:
        series_dict = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": series_id}
        )
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        return None

    dataset_dict.setdefault("series_navigation", [])

    series_navigation = {
        "id": series_id,
        "name": series_dict["name"],
        "title": series_dict["title"],
        "type": series_dict["type"],
    }

    if not series_dict.get("series_order_field"):
        return series_navigation

    try:
        prev, next_ = _get_series_prev_and_next(
            series_id,
            series_dict["series_order_field"],
            dataset_dict.get(series_dict["series_order_field"]) or "*",
            is_date=series_dict.get("series_order_type", "").lower() == "date",
        )
    except SearchError:
        return series_navigation

    series_navigation["previous"] = _build_navigation_item(prev) if prev else None
    series_navigation["next"] = _build_navigation_item(next_) if next_ else None

    return series_navigation


def _build_navigation_item(package_dict: dict[str, Any]) -> dict[str, Any]:
    """Build a navigation item for a package.

    Args:
        package_dict: The package dictionary to build a navigation item for.

    Returns:
        The navigation item for the package.
    """
    return {
        "id": package_dict["id"],
        "name": package_dict["name"],
        "title": package_dict["title"],
        "type": package_dict["type"],
    }


def _get_series_prev_and_next(
    series_id: str, order_field: str, current_value: Any, is_date: bool = False
) -> Tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:

    prev = None
    next_ = None

    if is_date and current_value != "*":
        try:
            date = parse_date(current_value)
            current_value = date.isoformat()
            if not date.tzinfo:
                current_value += "Z"
        except DateParserError:
            log.warning(f"Wrong date value for series navigation: {current_value}")
            return None, None

    prev_result = toolkit.get_action("package_search")(
        {},
        {
            "fq_list": [
                f"vocab_in_series:{series_id}",
                f"{order_field}:[* TO {current_value}]",
            ],
            "sort": f"{order_field} desc",
            "start": 1,
            "rows": 1,
            "include_private": True,
        },
    )
    if prev_result["results"]:
        prev = prev_result["results"][0]

    next_result = toolkit.get_action("package_search")(
        {},
        {
            "fq_list": [
                f"vocab_in_series:{series_id}",
                f"{order_field}:[{current_value} TO *]",
            ],
            "sort": f"{order_field} asc",
            "start": 1,
            "rows": 1,
            "include_private": True,
        },
    )
    if next_result["results"]:
        next_ = next_result["results"][0]

    return prev, next_


def _add_series_navigation(series_dict: dict[str, Any]) -> None:
    if not series_dict.get("series_order_field"):
        return

    first, last, count = _get_series_first_last_and_count(
        series_dict["id"], series_dict["series_order_field"]
    )

    series_dict["series_navigation"] = {
        "count": count,
        "first": _build_navigation_item(first) if first else None,
        "last": _build_navigation_item(last) if last else None,
    }


def _get_series_first_last_and_count(
    series_id: str, order_field: str
) -> Tuple[Optional[dict[str, Any]], Optional[dict[str, Any]], int]:
    search_params = {"fq": f"vocab_in_series:{series_id}", "rows": 1}
    first_result = toolkit.get_action("package_search")(
        {}, dict(search_params, sort=f"{order_field} asc", include_private=True)
    )

    if not first_result["results"]:
        return None, None, 0

    if first_result["count"] == 1:
        return first_result["results"][0], first_result["results"][0], 1

    last_result = toolkit.get_action("package_search")(
        {}, dict(search_params, sort=f"{order_field} desc", include_private=True)
    )

    return (
        first_result["results"][0],
        last_result["results"][0],
        last_result["count"],
    )
