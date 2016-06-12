import {combineReducers} from 'redux'
import _ from 'lodash';

import {TaggerActionType} from '../actions/TaggerActions'

const comments = (state = {}, action) => {
  switch (action.type) {
    case TaggerActionType.TAGGER_RECEIVE_COMMENTS:
      // todo: maybe hand off in a _.mapValue to comment() to perform some checks
      return _.mapKeys(action.comments, (v, k) => v.id)
    case TaggerActionType.TAGGER_RECEIVE_TAGS:
      return _.defaults({
        [action.id]: _.defaults({tags: _.uniq(action.tags)}, state[action.id])
      }, state);
    default:
      return state;
  }
}

const sources = (state = JSON.parse(sessionStorage.getItem('tagger_sources')) || {}, action) => {
  let newState = null;
  switch (action.type) {
    case TaggerActionType.TAGGER_RECEIVE_SOURCES:
      newState = _.chain(action.sources).uniq().map(source => [source, {id: source, active: true}]).fromPairs().value();
      break;
    case TaggerActionType.TAGGER_TOGGLE_SOURCE:
      newState = _.defaults({
        [action.id]: _.defaults({active: !state[action.id].active}, state[action.id])
      }, state);
      if (_.every(newState, ['active', false])) {
        newState = _.mapValues(newState, source => _.defaults({active: true}, source));
      }
      break;
    default:
      newState = state;
  }
  sessionStorage.setItem('tagger_sources', JSON.stringify(newState));
  return newState;
}

const tagSets = (state = JSON.parse(sessionStorage.getItem('tagger_tagSets')) || {}, action) => {
  let newState = null
  switch (action.type) {
    case TaggerActionType.TAGGER_TOGGLE_TAGSET:
      newState = _.defaults({
        [action.id]: _.defaults({active: !state[action.id].active}, state[action.id])
      }, state)
      break;
    case TaggerActionType.TAGGER_RECEIVE_TAGSETS:
      newState = _.keyBy(action.tagSets, 'id');
      break;
    default:
      newState = state;
  }
  sessionStorage.setItem('tagger_tagSets', JSON.stringify(newState));
  return newState
}

const stats = (state = {}, action) => {
  switch (action.type) {
    case TaggerActionType.TAGGER_RECEIVE_STATS:
      return _.defaults({[action.source]: action.stats}, state);
    case TaggerActionType.TAGGER_DISMISS_STATS:
      return _.omit(state, action.source)
    default:
      return state;
  }
}

const tagger = combineReducers({
  comments,
  sources,
  tagSets,
  stats
});

export default tagger