import firebase_admin  # type:  ignore
from firebase_admin import firestore  # type:  ignore

app = firebase_admin.initialize_app()
db = firestore.client()
