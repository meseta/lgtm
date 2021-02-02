from environs import Env
import firebase_admin  # type:  ignore
from firebase_admin import firestore  # type:  ignore

env = Env()
DB_COLLECTION = env("DB_COLLECTION", "")

app = firebase_admin.initialize_app()
db = firestore.client()

if DB_COLLECTION:
    db = db.collection(DB_COLLECTION).document(DB_COLLECTION)
