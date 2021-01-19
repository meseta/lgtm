import firebase_admin  # type:  ignore
from firebase_admin import firestore  # type:  ignore

if firebase_admin._apps:
    app = firebase_admin.get_app()
else:
    app = firebase_admin.initialize_app()
db = firestore.client()
