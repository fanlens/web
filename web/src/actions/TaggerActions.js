import fetch from 'isomorphic-fetch'
import keyMirror from 'keymirror'
import _ from 'lodash'
import jsonheaders from '../utils/jsonheaders'

export const TaggerActionType = keyMirror({
  TAGGER_RECEIVE_TAGS: null,
  TAGGER_RECEIVE_COMMENTS: null,
  TAGGER_RECEIVE_SOURCES: null,
  TAGGER_RECEIVE_STATS: null,

  TAGGER_DISMISS_STATS: null,

  TAGGER_TOGGLE_SOURCE: null,
  TAGGER_TOGGLE_TAGSET: null
});

const BASE_URI = '/tagger/';


const receiveTags = (id, tags) => {
  return {type: TaggerActionType.TAGGER_RECEIVE_TAGS, id, tags};
}

const receiveComments = (comments) => {
  return {type: TaggerActionType.TAGGER_RECEIVE_COMMENTS, comments};
}

const receiveSources = (sources) => {
  return {type: TaggerActionType.TAGGER_RECEIVE_SOURCES, sources};
}

const receiveStats = (source, stats) => {
  return {type: TaggerActionType.TAGGER_RECEIVE_STATS, source, stats};
}

const dismissStats = (source) => {
  return {type: TaggerActionType.TAGGER_DISMISS_STATS, source};
}

export const toggleSource = (id) => ({type: TaggerActionType.TAGGER_TOGGLE_SOURCE, id});

export const toggleTagSet = (id) => {
  return {type: TaggerActionType.TAGGER_TOGGLE_TAGSET, id};
}

export function initApp() {
  return (dispatch, getState) => {
    return dispatch(fetchSources()).then(() => {
      const activeSources = _.chain(getState().tagger.sources).filter('active').map('id').value();
      dispatch(fetchRandomComments(5, activeSources));
      _.each(activeSources, (source) => dispatch(fetchStats(source)));
    });
  }
}

export function fetchSources(force = false) {
  return (dispatch, getState) => {
    if (!force && !_.isEmpty(getState().tagger.sources)) {
      return Promise.resolve();
    } else {
      return fetch(BASE_URI + '_sources', {
        headers: jsonheaders(),
        credentials: 'include'
      }).then(response => response.json())
        .then(json => dispatch(receiveSources(json.sources)));
    }
  }
}

export function fetchRandomComments(count, sources = [], withEntity = true, withSuggestion = true) {
  return (dispatch) => {
    return fetch(BASE_URI + '?' + $.param({
        count: count,
        with_entity: withEntity,
        with_suggestion: withSuggestion,
        sources: _.values(sources).join()
      }), {
      headers: jsonheaders(),
      credentials: 'include'
    }).then(response => response.json())
      .then(json => dispatch(receiveComments(json.comments)));
  }
}

export function toggleCommentTag(id, currentTags, tag) {
  return (dispatch) => {
    return fetch(BASE_URI + id, {
      method: 'PATCH',
      body: JSON.stringify({
        add: _.difference([tag], currentTags),
        remove: _.intersection(currentTags, [tag])
      }),
      headers: jsonheaders(),
      credentials: 'include'
    }).then(response => response.json())
      .then(({id, tags}) => dispatch(receiveTags(id, tags)));
  }
}

export function resetCommentTags(id, tags) {
  return (dispatch) => {
    return fetch(BASE_URI + id, {
      method: 'PATCH',
      body: JSON.stringify({remove: tags}),
      headers: jsonheaders(),
      credentials: 'include'
    }).then(response => response.json())
      .then(({id, tags}) => dispatch(receiveTags(id, tags)));
  }
}

export function fetchStats(source) {
  return (dispatch) => {
    return fetch(`/meta/_stats/${source}/tags`, {
      headers: jsonheaders(),
      credentials: 'include'
    }).then(response => response.json())
      .then(stats => dispatch(receiveStats(source, stats)));
  }
}