from fastapi import APIRouter, Body, Depends

from outfit_engine.config.bootstrap import get_command_handler
from outfit_engine.domain.commands import (
    AddCatalogItem,
    AddItem,
    ColorDto,
    GenerateOutfit,
    ItemDto,
    PatternDto,
    RecordFeedback,
    RemoveCatalogItem,
    RemoveItem,
    ReplaceSlot,
    SetAppearanceProfile,
    SetBodySignature,
    SetProfile,
    UpdateCatalogItem,
    UpdateItem,
)
from outfit_engine.services.command_handlers import CommandHandler

router = APIRouter(prefix="/api/v1")


@router.post("/commands/add-item")
def add_item(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    item_data = body.get("item", {})
    color_data = item_data.get("color")
    pattern_data = item_data.get("pattern")
    
    color = ColorDto(**color_data) if color_data else None
    pattern = PatternDto(**pattern_data) if pattern_data else None
    
    item = ItemDto(
        user_item_id=item_data.get("user_item_id"),
        role=item_data.get("role", ""),
        slot=item_data.get("slot", ""),
        formality=item_data.get("formality", 3),
        seasonality=item_data.get("seasonality", []),
        color=color,
        pattern=pattern,
        style_tags=item_data.get("style_tags", []),
    )
    
    command = AddItem(
        idempotency_key=body.get("idempotency_key", ""),
        user_id=body.get("user_id", ""),
        item=item,
    )
    return handler.handle_add_item(command)


@router.post("/commands/update-item")
def update_item(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = UpdateItem(**body)
    return handler.handle_update_item(command)


@router.post("/commands/remove-item")
def remove_item(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = RemoveItem(**body)
    return handler.handle_remove_item(command)


@router.post("/commands/add-catalog-item")
def add_catalog_item(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    item_data = body.get("item", {})
    item = ItemDto(**item_data)
    command = AddCatalogItem(item=item)
    return handler.handle_add_catalog_item(command)


@router.post("/commands/update-catalog-item")
def update_catalog_item(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = UpdateCatalogItem(**body)
    return handler.handle_update_catalog_item(command)


@router.post("/commands/remove-catalog-item")
def remove_catalog_item(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = RemoveCatalogItem(**body)
    return handler.handle_remove_catalog_item(command)


@router.post("/commands/set-profile")
def set_profile(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = SetProfile(**body)
    return handler.handle_set_profile(command)


@router.post("/commands/set-appearance-profile")
def set_appearance_profile(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = SetAppearanceProfile(**body)
    return handler.handle_set_appearance_profile(command)


@router.post("/commands/set-body-signature")
def set_body_signature(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = SetBodySignature(**body)
    return handler.handle_set_body_signature(command)


@router.post("/commands/generate-outfit")
def generate_outfit(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = GenerateOutfit(**body)
    return handler.handle_generate_outfit(command)


@router.post("/commands/replace-slot")
def replace_slot(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = ReplaceSlot(**body)
    return handler.handle_replace_slot(command)


@router.post("/commands/record-feedback")
def record_feedback(body: dict = Body(...), handler: CommandHandler = Depends(get_command_handler)):
    command = RecordFeedback(**body)
    return handler.handle_record_feedback(command)
