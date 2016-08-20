import fetch from 'isomorphic-fetch'
import keyMirror from 'keymirror'
import _ from 'lodash'
import jsonheaders from '../utils/jsonheaders'
import {warning} from './AlertActions'

export const TaggerActionType = keyMirror({
  TAGGER_RECEIVE_TAGS: null,
  TAGGER_RECEIVE_TAGSETS: null,
  TAGGER_RECEIVE_COMMENTS: null,
  TAGGER_RECEIVE_SOURCES: null,
  TAGGER_RECEIVE_STATS: null,
  TAGGER_RECEIVE_SUGGESTION: null,

  TAGGER_ENTER_SUGGESTION: null,

  TAGGER_DISMISS_STATS: null,

  TAGGER_TOGGLE_SOURCE: null,
  TAGGER_TOGGLE_TAGSET: null
});

const BASE_URI = '/v2/tagger/';

const receiveTags = (id, tags) => {
  return {type: TaggerActionType.TAGGER_RECEIVE_TAGS, id, tags};
}

const receiveTagSets = (tagSets) => {
  return {type: TaggerActionType.TAGGER_RECEIVE_TAGSETS, tagSets};
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

const receiveSuggestion = (suggestion) => {
  return {type: TaggerActionType.TAGGER_RECEIVE_SUGGESTION, suggestion};
}

const enterSuggestion = () => {
  return {type: TaggerActionType.TAGGER_ENTER_SUGGESTION};
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
    dispatch(fetchTagCounts());
    dispatch(fetchTagSets());
    return dispatch(fetchSources())
      .then(() => {
        const activeSources = _.chain(getState().tagger.sources).filter('active').map('id').value();
        dispatch(fetchRandomComments(8, activeSources));
      });
  }
}

export function fetchTagSets(includeAll = true, force = false) {
  return (dispatch, getState) => {
    if (!force && !_.isEmpty(getState().tagger.tagSets)) {
      return Promise.resolve();
    } else {
      return fetch(BASE_URI + 'tagsets/' + (includeAll ? "?include_all=true" : ""), {
        headers: jsonheaders(),
      }).then(response => response.json())
        .then(json => dispatch(receiveTagSets(json.tagSets)));
    }
  }
}

export function fetchSources(force = false) {
  return (dispatch, getState) => {
    if (!force && !_.isEmpty(getState().tagger.sources)) {
      return Promise.resolve();
    } else {
      return fetch(BASE_URI + 'sources/', {
        headers: jsonheaders(),
      }).then(response => response.json())
        .then(json => dispatch(receiveSources(json.sources)));
    }
  }
}

export function fetchRandomComments(count, sources = [], withEntity = true, withSuggestion = true) {
  return (dispatch) => {
    return fetch(BASE_URI + 'comments/_random?' + $.param({
        count: count,
        with_entity: withEntity,
        with_suggestion: withSuggestion,
        sources: _.values(sources).join()
      }), {
      headers: jsonheaders(),
    }).then(response => response.json())
      .then(json => dispatch(receiveComments(json.comments)));
  }
}

export function toggleCommentTag(id, currentTags, tag) {
  return (dispatch) => {
    return fetch(`${BASE_URI}comments/${id}/tags`, {
      method: 'PATCH',
      body: JSON.stringify({
        add: _.difference([tag], currentTags),
        remove: _.intersection(currentTags, [tag])
      }),
      headers: jsonheaders(),
    }).then(response => response.json())
      .then(({id, tags}) => dispatch(receiveTags(id, tags)));
  }
}

export function addCommentTag(id, tag) {
  return (dispatch) => {
    return fetch(`${BASE_URI}comments/${id}/tags`, {
      method: 'PATCH',
      body: JSON.stringify({
        add: [tag]
      }),
      headers: jsonheaders(),
    }).then(response => response.json())
      .then(({id, tags}) => dispatch(receiveTags(id, tags)));
  }
}

export function resetCommentTags(id, tags) {
  return (dispatch) => {
    return fetch(BASE_URI + 'comments/' + id, {
      method: 'PATCH',
      body: JSON.stringify({remove: tags}),
      headers: jsonheaders(),
    }).then(response => response.json())
      .then(({id, tags}) => dispatch(receiveTags(id, tags)));
  }
}

export function fetchTagCounts() {
  return (dispatch) => {
    return fetch(BASE_URI + 'tags/_counts', {
      headers: jsonheaders(),
    }).then(response => response.json())
      .then(stats => dispatch(receiveStats('__all', stats)));
  }
}

export function fetchSuggestionForText(text) {
  return (dispatch) => {
    dispatch(enterSuggestion())
    return fetch(BASE_URI + 'suggestion', {
      method: 'POST',
      body: JSON.stringify({text}),
      headers: jsonheaders(),
    }).then(response => {
      console.log(response)
      if (response.status >= 400) {
        return Promise.reject(new Error())
      } else {
        return Promise.resolve(response)
      }
    }).then(response => response.json())
      .then(suggestion => dispatch(receiveSuggestion(suggestion)))
      .catch(_ => {
        dispatch(warning("There was a problem with the provided text! Is it in english?"));
        dispatch(receiveSuggestion([]));
      });
  }
}