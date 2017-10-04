import keyMirror from "keymirror";


export const ActionType = keyMirror({
  RECEIVE_TIMELINE_SINCE: null,
  RECEIVE_TIMELINE_UNTIL: null,
  RECEIVE_TIMELINE_RANDOM: null,
  RECEIVE_TIMELINE_COUNT: null,
  RECEIVE_TIMELINE_TAGSETS: null,
  RECEIVE_TIMELINE_SOURCES: null,
  RECEIVE_TIMELINE_ISFETCHING: null,
});

const receiveSince = (since) => ({type: ActionType.RECEIVE_TIMELINE_SINCE, since});
const receiveUntil = (until) => ({type: ActionType.RECEIVE_TIMELINE_UNTIL, until});
const receiveRandom = (random) => ({type: ActionType.RECEIVE_TIMELINE_RANDOM, random});
const receiveCount = (count) => ({type: ActionType.RECEIVE_TIMELINE_COUNT, count});
const receiveTagSets = (tagSets) => ({type: ActionType.RECEIVE_TIMELINE_TAGSETS, tagSets});
const receiveSources = (sources) => ({type: ActionType.RECEIVE_TIMELINE_SOURCES, sources});
const receiveIsFetching = (isFetching) => ({type: ActionType.RECEIVE_TIMELINE_ISFETCHING, isFetching});


export const setSince = (since) =>
  (dispatch) => dispatch(receiveSince(since));

export const setUntil = (until) =>
  (dispatch) => dispatch(receiveUntil(until));

export const setRange = (since, until) =>
  (dispatch) => {
    dispatch(receiveSince(since));
    dispatch(receiveUntil(until));
  };


export const setRandom = (random) =>
  (dispatch) => dispatch(receiveRandom(random));

export const setCount = (count) =>
  (dispatch) => dispatch(receiveCount(count));

export const setTagSets = (tagSets) =>
  (dispatch) => dispatch(receiveTagSets(tagSets));

export const setSources = (sources) =>
  (dispatch) => dispatch(receiveSources(sources));

export const setIsFetching = (isFetching) =>
  (dispatch) => Promise.resolve(dispatch(receiveIsFetching(isFetching)));
