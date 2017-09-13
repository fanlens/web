import {combineReducers} from "redux";
import _ from "lodash";
import {ActivitiesActionType} from "../actions/activities";

const comments = (state = {}, action) => {
  switch (action.type) {
    case ActivitiesActionType.ACTIVITIES_RECEIVE_COMMENTS:
      return _.chain(action.comments)
        .keyBy('id')
        .value();
    case ActivitiesActionType.ACTIVITIES_RECEIVE_TAGS:
      return _.defaults({
        [action.comment.id]: _.defaults({tags: _.uniq(action.tags)}, state[action.comment.id])
      }, state);
    default:
      return state;
  }
};

const sources = (state = {}, action) => {
  switch (action.type) {
    case ActivitiesActionType.ACTIVITIES_RECEIVE_SOURCES:
      return _.chain(action.sources).keyBy('id').value();
    default:
      return state;
  }
};

const tagSets = (state = {}, action) => {
  switch (action.type) {
    case ActivitiesActionType.ACTIVITIES_RECEIVE_TAGSETS:
      return _.defaults({
        all: {
          id: 'all',
          title: 'All',
          tags: _.chain(action.tagSets).map('tags').flatten().uniq().value()
        }
      }, _.keyBy(action.tagSets, 'id'));
    default:
      return state;
  }
};

const counts = (state = {}, action) => {
  switch (action.type) {
    case ActivitiesActionType.ACTIVITIES_RECEIVE_TAGCOUNTS:
      return action.counts;
    default:
      return state;
  }
};

const activities = combineReducers({
  comments,
  sources,
  tagSets,
  counts
});

export default activities;