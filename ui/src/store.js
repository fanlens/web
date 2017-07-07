import {createStore, applyMiddleware} from "redux";
import {logger} from "redux-logger";
import thunkMiddleware from "redux-thunk";
import defaults from "lodash/fp/defaults";
import pick from "lodash/fp/pick";

import rootReducer from "./reducers";

const STORAGE_KEY = '__fanlens_state';

const load = (storage) => JSON.parse(storage.getItem(STORAGE_KEY)) || {};
const initialState = defaults(load(sessionStorage))(load(localStorage));

const middlewares = applyMiddleware(
  thunkMiddleware,
  logger
);

const store = createStore(
  rootReducer,
  initialState,
  middlewares
);

const persist = (selector) =>
  (storage) => storage.setItem(
    STORAGE_KEY,
    JSON.stringify(selector(store.getState())));

const selectForSession = pick(['activities.tagSets', 'activities.sources']);
const persistSession = () => persist(selectForSession)(sessionStorage);

const selectForLocal = pick(['app.drawer', 'app.timeline', 'app.user']);
const persistLocal = () => persist(selectForLocal)(localStorage);

store.subscribe(persistLocal);
store.subscribe(persistSession);

export default store;
