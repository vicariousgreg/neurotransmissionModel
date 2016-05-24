# Enumeration function.
def enum(**enums):
    enums["size"] = len(enums)
    return type('Enum', (), enums)
