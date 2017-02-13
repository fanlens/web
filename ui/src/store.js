import {createStore, combineReducers, applyMiddleware} from "redux";
import createLogger from "redux-logger";
import thunkMiddleware from "redux-thunk";
import alerts from "./reducers/alerts";
import eev from "./reducers/eev";
import activities from "./reducers/activities";
import app from "./reducers/app";

const store = createStore(
  combineReducers({
    alerts,
    eev,
    activities,
    app,
  }),
  applyMiddleware(
    thunkMiddleware,
    createLogger()
  )
);

export default store;
