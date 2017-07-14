import defaults from "lodash/fp/defaults";
import {ActionType} from "../../actions/app/timeline";

const modifier = (action) => {
  switch (action.type) {
    case ActionType.RECEIVE_TIMELINE_SINCE:
      return {since: +new Date(action.since)};
    case ActionType.RECEIVE_TIMELINE_UNTIL:
      return {until: +new Date(action.until)};
    case ActionType.RECEIVE_TIMELINE_RANDOM:
      return {random: action.random};
    case ActionType.RECEIVE_TIMELINE_COUNT:
      return {count: action.count};
    case ActionType.RECEIVE_TIMELINE_TAGSETS:
      return {tagSets: action.tagSets};
    case ActionType.RECEIVE_TIMELINE_SOURCES:
      return {sources: action.sources};
    case ActionType.RECEIVE_TIMELINE_ISFETCHING:
      return {isFetching: action.isFetching};
    default:
      return (x) => x;
  }
};

const timeline = (state = {
  since: +new Date(new Date().getTime() - (365 * 60 * 60 * 1000)),
  until: +new Date(),
  radnom: true,
  count: 10,
  isFetching: false,
  tagSets: [],
  sources: [],
}, action) => defaults(state)(modifier(action));


export default timeline;