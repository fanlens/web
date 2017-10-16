import resolveToSelf from "./resolveToSelf";
import Swagger from "swagger-client";

export default new Swagger({
  url: resolveToSelf('/swagger.json', 'api'),
  authorizations: {
    jwt: JWT
  }
});