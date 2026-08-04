from update_public_metrics import extract_four_metric_row, parse_human_number, recursively_find_stats


def main() -> None:
    assert parse_human_number("12.6万") == 126000
    assert parse_human_number("1.1万") == 11000
    assert parse_human_number("5,469") == 5469
    assert extract_four_metric_row(["12.6万", "5469", "5314", "6942"]) == {
        "likes": 126000,
        "comments": 5469,
        "favorites": 5314,
        "shares": 6942,
    }
    payload = {
        "aweme_detail": {
            "aweme_id": "7667876245400742346",
            "statistics": {
                "digg_count": 126000,
                "comment_count": 5469,
                "collect_count": 5314,
                "share_count": 6942,
            },
        }
    }
    assert recursively_find_stats(payload, "7667876245400742346")["shares"] == 6942
    print("parser tests passed")


if __name__ == "__main__":
    main()
