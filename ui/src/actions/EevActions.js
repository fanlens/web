import keyMirror from 'keymirror'
import Swagger from 'swagger-client'
import io from 'socket.io'

const tokenApi = new Swagger({
  url: '/v3/eev/swagger.json',
  usePromise: true,
  authorizations: {
    headerAuth: new Swagger.ApiKeyAuthorization('Authorization-Token', apiKey, 'header')
  }
});

const botApi = (token) => new Swagger({
  url: 'https://docs.botframework.com/en-us/restapi/directline3/swagger.json',
  usePromise: true,
  authorizations: {
    headerAuth: new Swagger.ApiKeyAuthorization('Authorization', `Bearer ${token}`, 'header')
  }
});


export const EevActionType = keyMirror({
  EEV_RECEIVE_TOKEN: null,
  EEV_RECEIVE_MESSAGES: null,
  EEV_RECEIVE_CLEAR_MESSAGES: null,
  EEV_RECEIVE_CONVERSATION: null,
});


const receiveConversation = (conversation) => ({type: EevActionType.EEV_RECEIVE_CONVERSATION, conversation});

const receiveMessages = (messages, watermark) => ({type: EevActionType.EEV_RECEIVE_MESSAGES, messages, watermark});

const receiveMessage = (message, watermark) => receiveMessages([message], watermark);

const receiveClearMessages = () => ({type: EevActionType.EEV_RECEIVE_CLEAR_MESSAGES});


function initEev() {
  return (dispatch, getState) => {
    const ready = getState().eev.conversation.token !== null;
    if (ready) {
      return Promise.resolve();
    } else {
      return dispatch(fetchToken())
        .then(() => dispatch(startConversation()))
        .then(() => dispatch(receiveMessage({
          "id": 0,
          "conversation": 0,
          "from": "eev",
          "text": "Hi Christian! How can I help you?"
        }, 'eev'), null));
    }
  }
}

export function startConversation() {
  return (dispatch) => {
    tokenApi.then((api) => api.post_token())
      .then(({token}) => botApi(token))
      .then((botApi) => botApi.Conversations_StartConversation())
      .then(({streamUrl}) => {
        const ws = io.connect(streamUrl);
        ws.on('message', (data) => console.log(data));//dispatch(receiveMessage()))
        ws.on('error', (error) => console.log(error));//dispatch(receiveMessage()))
      })
      .catch((error) => console.log(error));
  }
}

function startConversation() {
  return (dispatch, getState) => fetch(BASE_URI + '/api/conversations', {
    method: 'POST',
    headers: eevHeader(getState().eev.token),
  }).then(response => response.json())
    .then(conversation => dispatch(receiveConversation(conversation)))
}


function timeoutPromise(ms, promise) {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      reject(new Error("promise timeout"))
    }, ms);
    promise.then(
      (res) => {
        clearTimeout(timeoutId);
        resolve(res);
      },
      (err) => {
        clearTimeout(timeoutId);
        reject(err);
      }
    );
  })
}

export function getMessages() {
  return (dispatch, getState) => {
    const {conversation, watermark} = getState().eev;
    const {token, conversationId} = conversation;
    if (conversationId === null) {
      return Promise.resolve();
    } else {
      const watermarkQuery = watermark ? `?watermark=${watermark}` : '';
      return timeoutPromise(2000, fetch(BASE_URI + `/api/conversations/${conversationId}/messages${watermarkQuery}`, {
        headers: eevHeader(token)
      }).then(response => response.json())
        .then(json => dispatch(receiveMessages(json.messages, json.watermark))))
        .catch(() => Promise.resolve());
    }
  };
}

export function sendChatbotMessage(text) {
  return (dispatch, getState) => {
    if (text.trim().toLowerCase() === "clear") {
      return dispatch(receiveClearMessages());
    }
    const {token, conversationId} = getState().eev.conversation;
    return fetch(BASE_URI + `/api/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({
        from: 'user',
        text
      }),
      headers: eevHeader(token)
    }).then(() => setTimeout(() => dispatch(getMessages()), 300));
  }
}


