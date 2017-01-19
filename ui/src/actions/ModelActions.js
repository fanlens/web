import keyMirror from "keymirror";
import Swagger from "swagger-client";
import {warning} from "./AlertActions";

const modelApi = new Swagger({
  url: '/v3/model/swagger.json',
  usePromise: true,
  authorizations: {
    headerAuth: new Swagger.ApiKeyAuthorization('Authorization-Token', apiKey, 'header')
  }
});

export const ModelActionType = keyMirror({
  MODEL_RECEIVE_SUGGESTION: null,
  MODEL_ENTER_SUGGESTION: null,
});


const receiveSuggestion = (suggestion) => ({type: ModelActionType.MODEL_RECEIVE_SUGGESTION, suggestion});

const enterSuggestion = () => ({type: ModelActionType.MODEL_ENTER_SUGGESTION});

export function fetchSuggestionForText(text) {
  return (dispatch) => {
    dispatch(enterSuggestion())
      .then(modelApi.then(
        (api) => api.suggestion.post_suggestion({body: {text}})
          .then(({status, obj}) => obj)
          .then(({suggestion}) => dispatch(receiveSuggestion(suggestion)))
          .catch((error) => {
            console.log(error);
            dispatch(warning("There was a problem with the provided text! Is it in english?"))
              .then(dispatch(receiveSuggestion([])));
          })));
  };
}