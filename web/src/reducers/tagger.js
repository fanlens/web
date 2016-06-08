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
  switch (action.type) {
    case TaggerActionType.TAGGER_RECEIVE_SOURCES:
      return _.chain(action.sources).uniq().map(source => [source, {id: source, active: true}]).fromPairs().value();
    case TaggerActionType.TAGGER_TOGGLE_SOURCE:
      let newState = _.defaults({
        [action.id]: _.defaults({active: !state[action.id].active}, state[action.id])
      }, state);
      if (_.every(newState, ['active', false])) {
        newState = _.mapValues(newState, source => _.defaults({active: true}, source));
      }
      sessionStorage.setItem('tagger_sources', JSON.stringify(newState));
      return newState;
    default:
      return state;
  }
}

const tagSets = (state = JSON.parse(sessionStorage.getItem('tagger_tagSets')) || {
  0: {id: 0, active: false, title: 'Spam vs Ham', tags: ['spam', 'ham']},
  1: {id: 1, active: false, title: 'Relevancy', tags: ['spam', 'irrelevant', 'fraud']},
  2: {id: 2, active: false, title: 'Sentiment', tags: ['happy', 'sad', 'thankful', 'angry', 'neutral']}
}, action) => {
  switch (action.type) {
    case TaggerActionType.TAGGER_TOGGLE_TAGSET:
      const newState = _.defaults({
        [action.id]: _.defaults({active: !state[action.id].active}, state[action.id])
      }, state)
      sessionStorage.setItem('tagger_tagSets', JSON.stringify(newState));
      return newState;
    default:
      return state;
  }
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