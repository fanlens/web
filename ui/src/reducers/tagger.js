import {combineReducers} from 'redux'
import _ from 'lodash';

import {TaggerActionType} from '../actions/TaggerActions'

const comments = (state = {}, action) => {
  switch (action.type) {
    case TaggerActionType.TAGGER_RECEIVE_COMMENTS:
      return _.chain(action.comments)
        .map((comment) => _.defaults({
          prediction: _.chain(comment.prediction)
            .mapValues(s => s > 0.9 ? 0 : s > 0.75 ? 1 : s > 0.6 ? 2 : 3)  // 0 excellent, 1 good, 2 fair, 3 ignore
            .value()
        }, comment))
        .keyBy('id')
        .value();
    case TaggerActionType.TAGGER_RECEIVE_TAGS:
      return _.defaults({
        [action.comment.id]: _.defaults({tags: _.uniq(action.tags)}, state[action.comment.id])
      }, state);
    default:
      return state;
  }
};

const sources = (state = {}, action) => {
  switch (action.type) {
    case TaggerActionType.TAGGER_RECEIVE_SOURCES:
      return _.chain(action.sources).map((source) => _.defaults({active: true}, source)).keyBy('id').value();
    case TaggerActionType.TAGGER_TOGGLE_SOURCE:
      const newState = _.defaults({
        [action.source.id]: _.defaults({active: !state[action.source.id].active}, state[action.source.id])
      }, state);
      if (_.every(newState, ['active', false])) {
        return _.mapValues(newState, source => _.defaults({active: true}, source));
      } else {
        return newState;
      }
    default:
      return state;
  }
};

const tagSets = (state = {}, action) => {
  switch (action.type) {
    case TaggerActionType.TAGGER_TOGGLE_TAGSET:
      return _.defaults({
        [action.id]: _.defaults({active: !state[action.id].active}, state[action.id])
      }, state);
      break;
    case TaggerActionType.TAGGER_RECEIVE_TAGSETS:
      return _.defaults({
        all: {
          id: 'all',
          title: 'All',
          tags: _.chain(action.tagSets).map('tags').flatten().uniq().value()
        }
      }, _.keyBy(action.tagSets, 'id'));
      break;
    default:
      return state;
  }
};

const counts = (state = {}, action) => {
  switch (action.type) {
    case TaggerActionType.TAGGER_RECEIVE_TAGCOUNTS:
      return action.counts;
    default:
      return state;
  }
};

const tagger = combineReducers({
  comments,
  sources,
  tagSets,
  counts
});

export default tagger