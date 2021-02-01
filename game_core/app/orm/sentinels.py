from typing import NewType

# sentinel for when ORM query returns nothing
OrmNotFoundType = NewType("OrmNotFoundType", object)
OrmNotFound = OrmNotFoundType(object())

# sentinel for no docref assigned
DocRefNotFoundType = NewType("DocRefNotFoundType", object)
DocRefNotFound = DocRefNotFoundType(object())

# sentinel for no parent
NoParentType = NewType("NoParentType", object)
NoParent = NoParentType(object())

# sentinel for no key assigned
NoKeyType = NewType("NoKeyType", object)
NoKey = NoKeyType(object())
