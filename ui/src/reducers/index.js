import {combineReducers} from "redux";

import alerts from "./alerts";
import activities from "./activities";
import app from "./app";

export default combineReducers({
  alerts,
  activities,
  app,
});