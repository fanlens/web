import {combineReducers} from "redux";
import _ from "lodash";
import md5 from "md5";
import {AppActionType} from "../actions/AppActions";
// todo move component code away from reducer!
import React from "react";
import SvgIconHelp from "material-ui/svg-icons/action/help";
import SvgIconFace from "material-ui/svg-icons/action/face";
import SvgIconGavel from "material-ui/svg-icons/action/gavel";
import SvgIconContacts from "material-ui/svg-icons/communication/contacts";
import SvgIconSearch from "material-ui/svg-icons/action/search";
import SvgIconThumbsUpDown from "material-ui/svg-icons/action/thumbs-up-down";
import SvgIconReplay from "material-ui/svg-icons/av/replay";

const input = (state = {
  active: false,
  text: ""
}, action) => {
  switch (action.type) {
    case AppActionType.RECEIVE_INPUT_TEXT:
      return _.defaults({text: action.text}, state);
    case AppActionType.RECEIVE_INPUT_ACTIVE:
      return _.defaults({active: action.active}, state);
    default:
      return state;
  }
};

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

const _makeSuggestion = (text, icon = <SvgIconReplay/>) => ({text, icon});
const _compareSuggestion = ({text: a}, {text: b}) => _.isEqual(a, b);

const suggestions = (state = {
  active: true,
  quick: [
    _makeSuggestion('What can you do?', <SvgIconHelp />),
    _makeSuggestion('Show me the team', <SvgIconFace />),
    _makeSuggestion('What are the Terms?', <SvgIconGavel />),
    _makeSuggestion('Let\'s stay connected!', <SvgIconContacts />),
  ],
  defaults: [
    _makeSuggestion('Show me 2 angry comments', <SvgIconSearch />),
    _makeSuggestion('How about ...', <SvgIconThumbsUpDown />),
    _makeSuggestion('Review 5 happy tweets', <SvgIconSearch />),
    _makeSuggestion('Test out ...', <SvgIconThumbsUpDown />),
    _makeSuggestion('Evaluate ...', <SvgIconThumbsUpDown />),
  ],
  user: [],
  get all() {
    return _.concat(this.quick, this.defaults, this.user);
  }
}, action) => {
  switch (action.type) {
    case AppActionType.RECEIVE_SUGGESTIONS_STATE:
      return _.defaults({active: action.active}, state);
    case AppActionType.RECEIVE_SUGGESTIONS_ADD:
      return _.defaults({
        user: _.unionWith(state.quick, state.defaults, state.user, [_makeSuggestion(action.suggestion)], _compareSuggestion)
      }, state);
    default:
      return state;
  }
};

const app = combineReducers({
  input,
  user,
  drawer,
  help,
  suggestions
});

export default app;