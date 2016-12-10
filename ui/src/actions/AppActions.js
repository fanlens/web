import Swagger from "swagger-client";
import keyMirror from "keymirror";

const userApi = new Swagger({
  url: '/v3/user/swagger.json',
  usePromise: true,
  authorizations: {
    headerAuth: new Swagger.ApiKeyAuthorization('Authorization-Token', apiKey, 'header'),
    headerCsrf: new Swagger.ApiKeyAuthorization('X-CSRFToken', CSRFToken, 'header')
  }
});

export const AppActionType = keyMirror({
  RECEIVE_USER: null,

  RECEIVE_DRAWER_STATE: null,

  RECEIVE_INPUT_TEXT: null,
  RECEIVE_INPUT_ACTIVE: null,

  RECEIVE_HELP_STATE: null,

  RECEIVE_SUGGESTIONS_STATE: null,
  RECEIVE_SUGGESTIONS_ADD: null,
});

const receiveUser = (user) => ({type: AppActionType.RECEIVE_USER, user});
const receiveDrawerState = (open) => ({type: AppActionType.RECEIVE_DRAWER_STATE, open});

const receiveInputText = (text) => ({type: AppActionType.RECEIVE_INPUT_TEXT, text});
const receiveInputActive = (active) => ({type: AppActionType.RECEIVE_INPUT_ACTIVE, active});

const receiveHelpState = (active) => ({type: AppActionType.RECEIVE_HELP_STATE, active});

const receiveSuggestionsState = (active) => ({type: AppActionType.RECEIVE_SUGGESTIONS_STATE, active});
const receiveAddedSuggestion = (suggestion) => ({type: AppActionType.RECEIVE_SUGGESTIONS_ADD, suggestion});

export const fetchUser = () =>
  (dispatch) => userApi.then(
    (api) => api.user.get_user()
      .then(({status, obj}) => obj)
      .then((user) => dispatch(receiveUser(user)))
      .catch((error) => console.log(error)));


export const setDrawerState = (open) =>
  (dispatch) => dispatch(receiveDrawerState(open));

export const toggleDrawer = () =>
  (dispatch, getState) => dispatch(setDrawerState(!getState().app.drawer.open));

export const updateInputText = (text) =>
  (dispatch) => dispatch(receiveInputText(text));

export const setInputActive = (active, closeDrawerOnActive = true) =>
  (dispatch) => {
    if (active && closeDrawerOnActive) {
      dispatch(setDrawerState(false));
    }
    dispatch(receiveInputActive(active));
  };


export const setHelpState = (active) =>
  (dispatch) => dispatch(receiveHelpState(active));

export const toggleHelp = () =>
  (dispatch, getState) => dispatch(setHelpState(!getState().app.help.active));


export const setSuggestionsState = (active) =>
  (dispatch) => dispatch(receiveSuggestionsState(active));

export const toggleSuggestions = () =>
  (dispatch, getState) => dispatch(setSuggestionsState(!getState().app.suggestions.active));

export const addSuggestion = (suggestion) =>
  (dispatch) => dispatch(receiveAddedSuggestion(suggestion));

export const addSuggestions = (suggestions) =>
  (dispatch) => suggestions.forEach((suggestion) => dispatch(addSuggestion(suggestion)));