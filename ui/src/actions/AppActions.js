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
});

const receiveUser = (user) => ({type: AppActionType.RECEIVE_USER, user});
const receiveDrawerState = (open) => ({type: AppActionType.RECEIVE_DRAWER_STATE, open});

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
