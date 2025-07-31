def set_value_to_immutable_dict(immutable, key, value):
    # IMPORTANT NOTE OF THIS METHOD:
    # CHANGING IMMUTABLE TYPES IS BAD PRACTICE
    # but sometimes, we don't have other solutions as easy
    mutable = immutable.copy()
    if type(value) is list:
        mutable.setlist(key, value)
    else:
        mutable[key] = value
    return mutable
