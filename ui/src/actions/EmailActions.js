import keyMirror from "keymirror";
import Swagger from "swagger-client";
import {info, error} from "./AlertActions";
import resolveToSelf from "./resolveToSelf";

const uiApi = new Swagger({
  url: resolveToSelf('/v4/ui/swagger.json'),
  authorizations: {
    api_key: apiKey
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
    (client) => client.apis.enquiries.put_enquiries__tag___email_({
      tag,
      email,
    }).then(({status}) => dispatch(receiveEnquirySuccess(status === 200)))
      .catch((error) => {
        console.log(error);
        return dispatch(receiveEnquirySuccess(false));
      }));

