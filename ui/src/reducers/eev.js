import _ from 'lodash';

import {EevActionType} from '../actions/EevActions';

const messageComparator = (a, b) => a.pending && b.pending && a.pending === b.pending || a.id === b.id;

const eev = (state = {
  ws: null,
  api: null,
  conversationId: null,
  watermark: null,
  messages: [],
  loading: true,
}, action) => {
  switch (action.type) {
    case EevActionType.EEV_RECEIVE_CONVERSATION_ID:
      return _.defaults({conversationId: action.conversationId}, state);
    case EevActionType.EEV_RECEIVE_API:
      return _.defaults({api: action.api}, state);
    case EevActionType.EEV_RECEIVE_WS:
      return _.defaults({ws: action.ws}, state);
    case EevActionType.EEV_RECEIVE_LOADINGSTATE:
      return state.loading === action.loading ? state : _.defaults({loading: action.loading}, state);
    case EevActionType.EEV_RECEIVE_MESSAGES:
      return _.defaults({
        messages: _.unionWith(action.messages, state.messages, messageComparator),
      }, state);
    case EevActionType.EEV_RECEIVE_CLEAR_MESSAGES:
      return _.defaults({messages: []}, state);
    default:
      return state;
  }
};

export default eev;