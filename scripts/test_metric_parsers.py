from update_public_metrics import (
    extract_four_metric_row,
    extract_weibo_metric_row,
    extract_number_after_label,
    parse_human_number,
    recursively_find_stats,
)


def main() -> None:
    assert parse_human_number("12.6万") == 126000
    assert parse_human_number("1.1万") == 11000
    assert parse_human_number("5,469") == 5469
    # Douyin profile rows place the counter after the label. The preceding 241
    # is the following count and must never be mistaken for followers.
    profile_row = "关注 241 粉丝 33.0万 获赞 560.2万"
    assert extract_number_after_label(profile_row, "关注") == 241
    assert extract_number_after_label(profile_row, "粉丝") == 330000
    assert extract_number_after_label(profile_row, "获赞") == 5602000
    assert extract_four_metric_row(["12.6万", "5469", "5314", "6942"]) == {
        "likes": 126000,
        "comments": 5469,
        "favorites": 5314,
        "shares": 6942,
    }
    assert extract_weibo_metric_row(["转发 1888 评论 1172 点赞 1.3万"]) == {
        "reposts": 1888,
        "comments": 1172,
        "likes": 13000,
    }
    assert extract_weibo_metric_row(["1888,1172,1.3万"]) == {
        "reposts": 1888,
        "comments": 1172,
        "likes": 13000,
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
    weibo_video_payload = {
        "data": {
            "fid": "1034:5330100514652254",
            "statistics": {
                "attitudes_count": 13000,
                "comments_count": 1172,
                "reposts_count": 1888,
            },
        }
    }
    assert recursively_find_stats(weibo_video_payload, "5330100514652254") == {
        "likes": 13000,
        "comments": 1172,
        "reposts": 1888,
    }
    mixed_payload = {
        "aweme_list": [
            {
                "aweme_id": "7651140292226052590",
                "statistics": {
                    "digg_count": 580293,
                    "comment_count": 2868,
                    "collect_count": 28821,
                    "share_count": 54595,
                },
            }
        ]
    }
    assert recursively_find_stats(mixed_payload, "7664238615464070510") == {}

    weibo_status_payload = {
        "id": "5330103329363208",
        "attitudes_count": 13000,
        "comments_count": 1172,
        "reposts_count": 1888,
    }
    assert recursively_find_stats(weibo_status_payload, "5330103329363208") == {
        "likes": 13000,
        "comments": 1172,
        "reposts": 1888,
    }

    print("parser tests passed")


if __name__ == "__main__":
    main()
