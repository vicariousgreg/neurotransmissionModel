# Enumeration function.
def enum(**enums):
    return type('Enum', (), enums)
