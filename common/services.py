from typing import List, Dict, Any, Tuple

from .types import DjangoModelType


def model_update(
        *,
        instance: DjangoModelType,
        fields: List[str],
        data: Dict[str, Any]
) -> Tuple[DjangoModelType, bool]:
    """
    Source: Hacksoftware Django Styleguide

    Generic update service meant for reusage. Return value: Tuple with the following elements:
        1. Updated instance
        2. A boolean indicating whether update was performed
    """
    was_updated = False

    for field in fields:
        if field not in data:
            continue

        if getattr(instance, field) != data[field]:
            was_updated = True
            setattr(instance, field, data[field])

    # Perform an update only if any of the fields was actually changed
    if was_updated:
        instance.full_clean()
        instance.save(update_fields=fields)

    return instance, was_updated
