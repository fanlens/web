import Swagger from "swagger-client";
import keyMirror from "keymirror";
import isEmpty from "lodash/fp/isEmpty";

import resolveToSelf from "../resolveToSelf";

const userApi = new Swagger({
  url: resolveToSelf('/v4/user/swagger.json', 'ui'),
  authorizations: {
    api_key: apiKey
  }
});

export const ActionType = keyMirror({
  RECEIVE_USER: null,
});

const receiveUser = (user) => ({type: ActionType.RECEIVE_USER, user});

export const fetchUser = (force = false) =>
  (dispatch, getState) => (force || isEmpty(getState().app.user)) && userApi.then(
    (client) => client.apis.user.get_user()
      .then(({status, obj}) => obj)
      .then((user) => dispatch(receiveUser(user)))
      .catch((error) => console.log(error))
  );
