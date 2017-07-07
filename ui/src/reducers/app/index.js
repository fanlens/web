import {combineReducers} from "redux";
import _ from "lodash";
import md5 from "md5";
import {ActionType as UserActionType} from "../../actions/app/user";
import {ActionType as DrawerActionType} from "../../actions/app/drawer";

import timeline from "./timeline";
import evaluator from "./evaluator";

const user = (state = {}, action) => {
  switch (action.type) {
    case UserActionType.RECEIVE_USER:
      return _.defaults(_.defaults({email_md5: md5(action.user.email)}, action.user), state);
    default:
      return state;
  }
};

const drawer = (state = {
  open: false
}, action) => {
  switch (action.type) {
    case DrawerActionType.RECEIVE_DRAWER_STATE:
      return _.defaults({open: action.open}, state);
    default:
      return state;
  }
};

export default combineReducers({
  user,
  drawer,
  timeline,
  evaluator
});
