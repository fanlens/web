import _ from 'lodash';
import keyMirror from 'keymirror';
import Swagger from 'swagger-client';
import uuid from 'node-uuid';

import {fetchUser} from './AppActions';

const tokenApi = new Swagger({
  url: '/v3/eev/swagger.json',
  usePromise: true,
  authorizations: {
    headerAuth: new Swagger.ApiKeyAuthorization('Authorization-Token', apiKey, 'header'),
    headerCsrf: new Swagger.ApiKeyAuthorization('X-CSRFToken', CSRFToken, 'header')
  }
});

const botApi = (token) => new Swagger({
  url: '/cdn/js/botframework.directline.v3.swagger.json',
  usePromise: true,
  authorizations: {
    headerAuth: new Swagger.ApiKeyAuthorization('Authorization', `Bearer ${token}`, 'header')
  }
});


export const EevActionType = keyMirror({
  EEV_RECEIVE_API: null,
  EEV_RECEIVE_WS: null,
  EEV_RECEIVE_CONVERSATION_ID: null,
  EEV_RECEIVE_MESSAGES: null,
  EEV_RECEIVE_CLEAR_MESSAGES: null,
  EEV_RECEIVE_LOADINGSTATE: null,
});


const receiveAPI = (api) => ({type: EevActionType.EEV_RECEIVE_API, api});

const receiveWS = (ws) => ({type: EevActionType.EEV_RECEIVE_WS, ws});

const receiveConversationId = (conversationId) => ({type: EevActionType.EEV_RECEIVE_CONVERSATION_ID, conversationId});

const receiveMessages = (messages) => ({type: EevActionType.EEV_RECEIVE_MESSAGES, messages});

const receiveMessage = (message) => receiveMessages([message]);

const receiveClearMessages = () => ({type: EevActionType.EEV_RECEIVE_CLEAR_MESSAGES});

const receiveLoadingState = (loading) => ({type: EevActionType.EEV_RECEIVE_LOADINGSTATE, loading});


export function initEev() {
  return (dispatch) => dispatch(fetchUser())
    .then(dispatch(startConversation()))
    .then(() => dispatch(receiveLoadingState(false)));
}

export function startConversation() {
  return (dispatch) => tokenApi.then(
    (api) => api.eev.post_token()
      .then(({status, obj}) => obj)
      .then(({token}) => {
        const api = botApi(token);
        dispatch(receiveAPI(api));
        return api;
      })
      .then((botApi) => botApi.Conversations.Conversations_StartConversation()
        .then(({status, obj}) => obj)
        .then(({conversationId, streamUrl}) => {
          dispatch(receiveConversationId(conversationId));
          const ws = new WebSocket(streamUrl);
          ws.onmessage = ({data}) => {
            const {activities} = data ? JSON.parse(data) : {activities: []};
            const loadingStates = activities.map((activity) => {
              switch (activity.type) {
                case 'message':
                  dispatch(receiveMessage(activity));
                  return !activity.from.id.startsWith('eev');
                case 'typing':
                  return true;
              }
            });
            dispatch(receiveLoadingState(_.last(loadingStates) || false));
          };
          ws.onopen = ({type, timeStamp}) => {
            console.log(`${type} channel to eev on ${timeStamp}`);
            return dispatch(receiveWS(ws));
          };
          ws.onclose = (error) => {
            console.log(error);
            return dispatch(receiveWS(null));
          };
          ws.onerror = (error) => ws.onclose(error);
        })
        .catch((error) => console.log(error)))
      .catch((error) => console.log(error)));
}

export function sendMessage(text) {
  return (dispatch, getState) => {
    if (text.trim().toLowerCase() === "clear") {
      return dispatch(receiveClearMessages());
    }
    const {conversationId} = getState().eev;
    dispatch(receiveLoadingState(true));
    const activity = {
      type: 'message',
      from: {id: 'user'},
      pending: uuid.v1(),
      text
    };
    dispatch(receiveMessage(activity));
    return getState().eev.api.then(
      (api) => api.Conversations.Conversations_PostActivity({
        conversationId,
        activity
      }));
  }
}
