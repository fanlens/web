import _ from 'lodash';

import {EevActionType} from '../actions/EevActions';

const eev = (state = {
  token: null,
  conversation: {
    conversationId: null,
    token: null,
  },
  watermark: null,
  messages: [],
  active: false
}, action) => {
  switch (action.type) {
    case EevActionType.EEV_RECEIVE_TOKEN:
      return _.defaults({token: action.token}, state);
    case EevActionType.EEV_RECEIVE_MESSAGES:
      if (action.watermark !== state.watermark) {
        return _.defaults({
          messages: _.unionWith(state.messages, action.messages, (a, b) => a.id == b.id),
          watermark: action.watermark
        }, state);
      } else {
        return state;
      }
    case EevActionType.EEV_RECEIVE_CLEAR_MESSAGES:
      return _.defaults({messages: []}, state);
    case EevActionType.EEV_RECEIVE_CONVERSATION:
      return _.defaults({
        conversation: action.conversation
      }, state);
    case EevActionType.EEV_RECEIVE_STATE:
      return _.defaults({active: action.active}, state)
    default:
      return state;
  }
};

export default eev;