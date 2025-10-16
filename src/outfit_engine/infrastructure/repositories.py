from __future__ import annotations

import hashlib
from dataclasses import asdict
from typing import Dict, List, Optional

from outfit_engine.domain.models import (
    CatalogItem,
    Feedback,
    Outfit,
    Profile,
    WardrobeItem,
)


class WardrobeRepository:
    def __init__(self) -> None:
        self._items: Dict[str, Dict[str, WardrobeItem]] = {}

    def add_item(self, item: WardrobeItem) -> None:
        self._items.setdefault(item.user_id, {})[item.user_item_id] = item

    def update_item(self, item: WardrobeItem) -> None:
        self._items[item.user_id][item.user_item_id] = item

    def remove_item(self, user_id: str, user_item_id: str) -> None:
        if user_id in self._items and user_item_id in self._items[user_id]:
            del self._items[user_id][user_item_id]

    def get_item(self, user_id: str, user_item_id: str) -> Optional[WardrobeItem]:
        return self._items.get(user_id, {}).get(user_item_id)

    def list_items(self, user_id: str) -> List[WardrobeItem]:
        return list(self._items.get(user_id, {}).values())


class CatalogRepository:
    def __init__(self) -> None:
        self._items: Dict[str, CatalogItem] = {}

    def add_item(self, item: CatalogItem) -> None:
        self._items[item.catalog_item_id] = item

    def update_item(self, item: CatalogItem) -> None:
        self._items[item.catalog_item_id] = item

    def remove_item(self, catalog_item_id: str) -> None:
        self._items.pop(catalog_item_id, None)

    def get_item(self, catalog_item_id: str) -> Optional[CatalogItem]:
        return self._items.get(catalog_item_id)

    def list_items(self) -> List[CatalogItem]:
        return list(self._items.values())


class ProfileRepository:
    def __init__(self) -> None:
        self._profiles: Dict[str, Profile] = {}

    def save(self, profile: Profile) -> None:
        self._profiles[profile.user_id] = profile

    def get(self, user_id: str) -> Optional[Profile]:
        return self._profiles.get(user_id)


class OutfitRepository:
    def __init__(self) -> None:
        self._outfits: Dict[str, Dict[str, Outfit]] = {}

    def save(self, outfit: Outfit) -> None:
        self._outfits.setdefault(outfit.user_id, {})[outfit.outfit_id] = outfit

    def get(self, user_id: str, outfit_id: str) -> Optional[Outfit]:
        return self._outfits.get(user_id, {}).get(outfit_id)

    def list_recent(self, user_id: str, limit: int = 20) -> List[Outfit]:
        return list(self._outfits.get(user_id, {}).values())[-limit:]


class FeedbackRepository:
    def __init__(self) -> None:
        self._feedback: Dict[str, Feedback] = {}

    def save(self, feedback: Feedback) -> None:
        self._feedback[feedback.feedback_id] = feedback


class SearchIndex:
    def __init__(self) -> None:
        self._docs: Dict[str, Dict[str, dict]] = {}

    def upsert_doc(self, scope: str, doc_id: str, document: dict) -> None:
        self._docs.setdefault(scope, {})[doc_id] = document

    def remove_doc(self, scope: str, doc_id: str) -> None:
        if scope in self._docs:
            self._docs[scope].pop(doc_id, None)

    def search(self, scope: str, filters: dict, limit: int = 50) -> List[dict]:
        results = []
        documents = self._docs.get(scope, {})

        for doc in documents.values():
            if self._match_filters(doc, filters):
                results.append(doc)

        results.sort(key=lambda d: d.get("updated_at", 0), reverse=True)

        return results[:limit]

    def _match_filters(self, document: dict, filters: dict) -> bool:
        for key, value in filters.items():
            if value is None:
                continue

            if key not in document:
                return False

            doc_value = document[key]

            if isinstance(value, list):
                if not any(v in doc_value for v in value if isinstance(doc_value, list)):
                    return False
            elif isinstance(value, tuple) and len(value) == 2 and all(
                isinstance(v, int) for v in value
            ):
                low, high = value
                if not (low <= doc_value <= high):
                    return False
            else:
                if doc_value != value:
                    return False

        return True


def attributes_hash(attributes: dict) -> str:
    serialized = repr(sorted(attributes.items())).encode()
    return hashlib.sha256(serialized).hexdigest()
