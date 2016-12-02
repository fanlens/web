import keyMirror from 'keymirror'
import Swagger from 'swagger-client'

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
  EEV_RECEIVE_MESSAGES: null,
  EEV_RECEIVE_CLEAR_MESSAGES: null,
});


const receiveAPI = (api) => ({type: EevActionType.EEV_RECEIVE_API, api});

const receiveWS = (ws) => ({type: EevActionType.EEV_RECEIVE_WS, ws});

const receiveMessages = (messages, watermark) => ({type: EevActionType.EEV_RECEIVE_MESSAGES, messages, watermark});

const receiveMessage = (message, watermark) => receiveMessages([message], watermark);

const receiveClearMessages = () => ({type: EevActionType.EEV_RECEIVE_CLEAR_MESSAGES});


export function initEev() {
  return (dispatch) => dispatch(startConversation())
    .then(() => dispatch(receiveMessage({
      "id": 0,
      "conversation": 0,
      "from": "eev",
      "text": "Hi Christian! How can I help you?"
    }, 'eev'), null));
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
        .then(({streamUrl}) => {
          const ws = new WebSocket(streamUrl);
          ws.onmessage = (data) => console.log(data);
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

export function sendMessage(message) {
  return (dispatch, getState) => getState.eev.api.
    if (!getState.api) {
      return Promise.reject('there is no connection to eev')
    } else {
      ws.send()
    }
  };
}
