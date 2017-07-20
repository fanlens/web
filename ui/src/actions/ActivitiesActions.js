import keyMirror from "keymirror";
import _ from "lodash";
import defaults from "lodash/fp/defaults";
import flow from "lodash/fp/flow";
import Swagger from "swagger-client";
import {orNop} from "./nop";

import resolveToSelf from "./resolveToSelf";

const activitiesApi = new Swagger({
  url: resolveToSelf('/v3/activities/swagger.json'),
  authorizations: {
    api_key: apiKey
  }
});

export const ActivitiesActionType = keyMirror({
  ACTIVITIES_RECEIVE_TAGS: null,
  ACTIVITIES_RECEIVE_TAGSETS: null,
  ACTIVITIES_RECEIVE_COMMENTS: null,
  ACTIVITIES_RECEIVE_SOURCES: null,
  ACTIVITIES_RECEIVE_TAGCOUNTS: null,
});

const receiveTags = (comment, tags) => ({type: ActivitiesActionType.ACTIVITIES_RECEIVE_TAGS, comment, tags});

const receiveTagSets = (tagSets) => ({type: ActivitiesActionType.ACTIVITIES_RECEIVE_TAGSETS, tagSets});

const receiveComments = (comments) => ({type: ActivitiesActionType.ACTIVITIES_RECEIVE_COMMENTS, comments});

const receiveSources = (sources) => ({type: ActivitiesActionType.ACTIVITIES_RECEIVE_SOURCES, sources});

const receiveTagCounts = (counts) => ({type: ActivitiesActionType.ACTIVITIES_RECEIVE_TAGCOUNTS, counts});


let initialized = false; // ugly but no better idea atm

export const initActivities = (force = false) => orNop(!initialized || force)(
  (dispatch) => {
    initialized = true;
    return Promise.all([
      // dispatch(fetchTagCounts()),
      dispatch(fetchTagSets()),
      dispatch(fetchSources())])
      .catch(() => {
        initialized = false;
      });
  }
);

export const fetchTagSets = () =>
  (dispatch) => activitiesApi.then(
    (client) => client.apis.tagsets.get_tagsets_()
      .then(({status, obj}) => obj)
      .then(({tagSets}) => dispatch(receiveTagSets(tagSets)))
      .catch((error) => console.log(error)));


export const fetchSources = () =>
  (dispatch) => activitiesApi.then(
    (client) => client.apis.sources.get_sources_()
      .then(({status, obj}) => obj)
      .then(({sources}) => dispatch(receiveSources(sources)))
      .catch((error) => console.log(error)));

export const fetchTagCounts = () =>
  (dispatch, getState) => activitiesApi.then(
    (client) => client.apis.tags.get_tags_({with_count: true})
      .then(({status, obj}) => obj)
      .then(({counts}) => dispatch(receiveTagCounts(counts)))
      .catch((error) => console.log(error))
  );

const conditionalDefaults = (condition) =>
  (value) =>
    (key) => condition ?
      defaults({[key]: value}) :
      (obj) => obj;

const definedDefaults = (value) => conditionalDefaults(!_.isUndefined(value) && !_.isNull(value))(value);

export const fetchComments = ({count, sources, since, until, tagSets = [], random = false}) =>
  (dispatch) => activitiesApi.then(
    (client) => client.apis.activity.get__source_ids__(
      flow(
        definedDefaults(since)('since'),
        definedDefaults(until)('until')
        // definedDefaults(_.chain(tagSets).reject({'id':'all'}).map('id').value().join(',') || null)('tagset_ids')
      )({
        source_ids: _.chain(sources).map('id').value(),
        count: count,
        random: random
      })).then(({status, obj}) => obj)
      .then(({activities}) => dispatch(receiveComments(activities)))
      .catch((error) => console.log(error))
  );

export const fetchCommentsTagSet = (count, tagSetId, random = true) =>
  (dispatch) => activitiesApi.then(
    (client) => client.apis.activity.get_tagsets__tagset_id__activities_({
      tagset_id: tagSetId,
      count: count,
      random: random
    }).then(({status, obj}) => obj)
      .then(({activities}) => dispatch(receiveComments(activities)))
      .catch((error) => console.log(error)));

const manipulateTags = (comment, add, remove) =>
  (dispatch) => activitiesApi.then(
    (client) => client.apis.activity.patch__source_id___activity_id__tags({
      source_id: comment.source.id,
      activity_id: comment.id,
      body: {
        add: add,
        remove: remove,
      }
    }).then(({status, obj}) => obj)
      .then(({tags}) => dispatch(receiveTags(comment, tags)))
      .then(() => dispatch(fetchTagCounts()))
      .catch((error) => console.log(error)));

export const toggleCommentTag = (comment, tag) =>
  manipulateTags(comment, _.difference([tag], comment.tags), _.intersection(comment.tags, [tag]));

export const addCommentTag = (comment, tag) => manipulateTags(comment, Array.isArray(tag) ? tag : [tag], []);

export const resetCommentTags = (comment) => manipulateTags(comment, [], comment.tags);
