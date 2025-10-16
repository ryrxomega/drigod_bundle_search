from outfit_engine.config.bootstrap import get_command_handler
from outfit_engine.domain.commands import AddItem, GenerateOutfit, ItemDto, SetProfile


def setup_user_with_items(handler):
    handler.handle_set_profile(
        SetProfile(
            user_id="user-1",
            baseline_dressiness=3,
            default_occasion="casual_day",
            guardrails={},
            style_signature={"tags": ["smart", "minimal"]},
        )
    )

    handler.handle_add_item(
        AddItem(
            user_id="user-1",
            item=ItemDto(
                user_item_id="top-1",
                role="top-1",
                slot="top",
                formality=3,
                seasonality=["warm"],
                style_tags=["smart"],
            ),
        )
    )

    handler.handle_add_item(
        AddItem(
            user_id="user-1",
            item=ItemDto(
                user_item_id="bottom-1",
                role="bottom-1",
                slot="bottom",
                formality=3,
                seasonality=["warm"],
                style_tags=["smart"],
            ),
        )
    )

    handler.handle_add_item(
        AddItem(
            user_id="user-1",
            item=ItemDto(
                user_item_id="footwear-1",
                role="footwear-1",
                slot="footwear",
                formality=3,
                seasonality=["warm"],
                style_tags=["smart"],
            ),
        )
    )


def test_generate_outfit_success():
    handler = get_command_handler()
    setup_user_with_items(handler)

    response = handler.handle_generate_outfit(
        GenerateOutfit(
            user_id="user-1",
            mode="ad_hoc",
            allow_catalog=False,
        )
    )

    assert "outfit_id" in response
    assert response["slots"]
    assert response["scores"]


def test_generate_outfit_deterministic():
    handler = get_command_handler()
    setup_user_with_items(handler)

    command = GenerateOutfit(
        user_id="user-1",
        mode="ad_hoc",
        allow_catalog=False,
        determinism_key="stable",
    )

    response1 = handler.handle_generate_outfit(command)
    response2 = handler.handle_generate_outfit(command)

    assert response1["slots"] == response2["slots"]
