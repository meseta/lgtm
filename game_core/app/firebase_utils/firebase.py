from environs import Env
import firebase_admin  # type:  ignore
from firebase_admin import firestore  # type:  ignore

env = Env()
environment = env("ENVIRONMENT", "production")

app = firebase_admin.initialize_app()
db = firestore.client()

if environment == "testing":
    db = db.collection("test").document("testing")
