import fetch from 'isomorphic-fetch'
import keyMirror from 'keymirror'
import _ from 'lodash'
import jsonheaders from '../utils/jsonheaders'

export const EevActionType = keyMirror({
  EEV_RECEIVE_TOKEN: null,
  EEV_RECEIVE_MESSAGES: null,
  EEV_RECEIVE_CLEAR_MESSAGES: null,
  EEV_RECEIVE_CONVERSATION: null,
  EEV_RECEIVE_STATE: null
});

const TOKEN_URI = '/v2/tagger/eev/token';
const BASE_URI = 'https://directline.botframework.com';
const MAX_TOKEN_LIFETIME = 30 * 60 * 1000;

const receiveToken = (token) => {
  return {type: EevActionType.EEV_RECEIVE_TOKEN, token};
};

const receiveConversation = (conversation) => {
  return {type: EevActionType.EEV_RECEIVE_CONVERSATION, conversation};
};

const receiveMessages = (messages, watermark) => {
  return {type: EevActionType.EEV_RECEIVE_MESSAGES, messages, watermark};
};

const receiveMessage = (message, watermark) => receiveMessages([message], watermark);

const receiveClearMessages = () => {
  return {type: EevActionType.EEV_RECEIVE_CLEAR_MESSAGES}
};

const receiveState = (active) => {
  return {type: EevActionType.EEV_RECEIVE_STATE, active};
};

function eevHeader(token) {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  headers.append("Authorization", `BotConnector ${token}`);
  return headers;
}

function startConversation() {
  return (dispatch, getState) => fetch(BASE_URI + '/api/conversations', {
    method: 'POST',
    headers: eevHeader(getState().eev.token),
  }).then(response => response.json())
    .then(conversation => dispatch(receiveConversation(conversation)))
}


export function fetchToken() {
  return (dispatch) => {
    return fetch(TOKEN_URI, {
      headers: jsonheaders(),
    }).then(response => response.json())
      .then(token => dispatch(receiveToken(token.token)))
      .then(() => setTimeout(() => dispatch(fetchToken()), MAX_TOKEN_LIFETIME / 3));
  }
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

function init() {
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

function loop(func, delay = 1000) {
  return (dispatch, getState) => {
    const {active} = getState().eev;
    if (active) {
      return dispatch(func()).then(() => active && setTimeout(() => dispatch(loop(func)), delay));
    } else {
      return Promise.resolve();
    }
  }
}

export function enter() {
  return (dispatch) => dispatch(init())
    .then(Promise.all([
      dispatch(receiveState(true)),
      dispatch(loop(getMessages)),
    ]));
}

export function exit() {
  return (dispatch) => dispatch(receiveState(false));
}
