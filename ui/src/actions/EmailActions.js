import keyMirror from "keymirror";
import Swagger from "swagger-client";
import {info, error} from "./AlertActions";

const uiApi = new Swagger({
  url: '/v3/ui/swagger.json',
  usePromise: true,
  authorizations: {
    headerAuth: new Swagger.ApiKeyAuthorization('Authorization-Token', apiKey, 'header'),
    headerCsrf: new Swagger.ApiKeyAuthorization('X-CSRFToken', CSRFToken, 'header')
  }
});

export const EmailActionType = keyMirror({
  EMAIL_SEND_ENQUIRY: null,
});

const receiveEnquirySuccess = (success = true) => {
  if (success) {
    return info("We received your enquiry, thank you!");
  } else {
    return error("We're sorry, there seems to be an error");
  }
};

export const sendEnquiry = (tag, email) =>
  (dispatch) => uiApi.then(
    (api) => api.enquiries.put_enquiries_tag_email({
      tag,
      email,
    }).then(({status}) => dispatch(receiveEnquirySuccess(status === 200)))
      .catch((error) => {
        console.log(error);
        return dispatch(receiveEnquirySuccess(false));
      }));

