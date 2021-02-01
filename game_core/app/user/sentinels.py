from typing import NewType

# sentinel for when there's no UID for the user
NoUidType = NewType("NoUidType", object)
NoUid = NoUidType(object())
