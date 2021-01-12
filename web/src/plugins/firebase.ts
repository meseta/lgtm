import firebase from 'firebase/app';
import 'firebase/auth';
import 'firebase/firestore';
import 'firebase/functions';

const firebaseConfig = {
  apiKey: 'AIzaSyDGNwlLZpK_scAiDzVE7knnHuA3eDImabk',
  authDomain: 'meseta-lgtm.firebaseapp.com',
  projectId: 'meseta-lgtm',
  storageBucket: 'meseta-lgtm.appspot.com',
  messagingSenderId: '820564282876',
  appId: '1:820564282876:web:cbfd5cc1237a378a05f679'
};

const app = firebase.initializeApp(firebaseConfig);

const auth = app.auth();
const firestore = app.firestore();
const functions = app.functions();

export {
  firebase,
  auth,
  firestore,
  functions,
};