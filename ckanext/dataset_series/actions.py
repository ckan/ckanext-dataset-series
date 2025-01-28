import logging

from dateutil.parser import parse as parse_date, ParserError as DateParserError

import ckan.plugins.toolkit as toolkit


log = logging.getLogger(__name__)


@toolkit.side_effect_free
@toolkit.chained_action
def package_show(up_func, context, data_dict):

    dataset_dict = up_func(context, data_dict)

    for_indexing = toolkit.asbool(data_dict.get("for_indexing")) or toolkit.asbool(
        context.get("use_cache") is False
    )

    if not for_indexing:
        if dataset_dict.get("type") == "dataset_series":
            dataset_dict = _add_series_navigation(dataset_dict)

        elif dataset_dict.get("in_series"):
            dataset_dict = _add_series_member_navigation(dataset_dict)

    return dataset_dict


def _add_series_member_navigation(dataset_dict: dict) -> dict:

    for series_id in dataset_dict["in_series"]:
        # Is the series ordered?
        try:
            series_dict = toolkit.get_action("package_show")(
                {"ignore_auth": True}, {"id": series_id}
            )

            if series_dict.get("series_order_field"):

                is_date = series_dict.get("series_order_type", "").lower() == "date"
                prev, next_ = _get_series_prev_and_next(
                    series_id,
                    series_dict["series_order_field"],
                    dataset_dict[series_dict["series_order_field"]],
                    is_date=is_date,
                )
                if "series_navigation" not in dataset_dict:
                    dataset_dict["series_navigation"] = []
                    series_nav = {
                        "id": series_id,
                        "name": series_dict["name"],
                        "title": series_dict["title"],
                        "previous": None,
                        "next": None,
                    }
                    if prev:
                        series_nav["previous"] = {
                            "id": prev["id"],
                            "name": prev["name"],
                            "title": prev["title"],
                        }
                    if next_:
                        series_nav["next"] = {
                            "id": next_["id"],
                            "name": next_["name"],
                            "title": next_["title"],
                        }
                dataset_dict["series_navigation"].append(series_nav)

        except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
            continue

    return dataset_dict


def _get_series_prev_and_next(series_id, order_field, current_value, is_date=False):

    prev = None
    next_ = None

    if is_date:
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
        },
    )
    if next_result["results"]:
        next_ = next_result["results"][0]

    return prev, next_


def _add_series_navigation(series_dict: dict) -> dict:

    # Is the Dataset Series ordered?
    if not series_dict.get("series_order_field"):
        return series_dict

    first, last, count = _get_series_first_last_and_count(
        series_dict["id"], series_dict["series_order_field"]
    )

    series_dict["series_navigation"] = {
        "count": count,
        "first": None,
        "last": None,
    }
    if first:
        series_dict["series_navigation"]["first"] = {
            "id": first["id"],
            "name": first["name"],
            "title": first["title"],
        }
    if last:
        series_dict["series_navigation"]["last"] = {
            "id": last["id"],
            "name": last["name"],
            "title": last["title"],
        }

    return series_dict


def _get_series_first_last_and_count(series_id, order_field):
    search_params = {"fq": f"vocab_in_series:{series_id}", "rows": 1}
    first_result = toolkit.get_action("package_search")(
        {}, dict(search_params, sort=f"{order_field} asc")
    )

    if not first_result["results"]:
        return None, None, 0

    if first_result["count"] == 1:
        return first_result["results"][0], first_result["results"][0], 1

    last_result = toolkit.get_action("package_search")(
        {}, dict(search_params, sort=f"{order_field} desc")
    )
    return first_result["results"][0], last_result["results"][0], last_result["count"]
