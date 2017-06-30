import {combineReducers} from "redux";
import _ from "lodash";
import md5 from "md5";
import {AppActionType} from "../actions/AppActions";


const user = (state = {}, action) => {
  switch (action.type) {
    case AppActionType.RECEIVE_USER:
      return _.defaults(_.defaults({email_md5: md5(action.user.email)}, action.user), state);
    default:
      return state;
  }
};

const drawer = (state = {
  open: false
}, action) => {
  switch (action.type) {
    case AppActionType.RECEIVE_DRAWER_STATE:
      return _.defaults({open: action.open}, state);
    default:
      return state;
  }
};

const help = (state = {
  active: true
}, action) => {
  switch (action.type) {
    case AppActionType.RECEIVE_HELP_STATE:
      return _.defaults({active: action.active}, state);
    default:
      return state;
  }
};

const app = combineReducers({
  user,
  drawer,
  help,
});

export default app;