def check_positive_hp(entity, context, params):
    """
    Check that entity HP is strictly positive.
    Target: EntityBlock
    """
    # Note: entity.resolved_data contains the final values after validation
    hp = entity.resolved_data.get('hp', 0)
    
    # We might be checking an entity that *should* have HP, but validation handled types.
    # Here we check business logic.
    if hp <= 0:
        return False, f"HP ({hp}) must be positive."
    return True

def check_max_weight(entity, context, params):
    """
    Check that item weight does not exceed a limit.
    """
    weight = entity.resolved_data.get('weight', 0.0)
    limit = params.get('limit', 1.0)
    
    if weight > limit:
        return False, f"Weight ({weight}) exceeds limit ({limit})."
    return True
