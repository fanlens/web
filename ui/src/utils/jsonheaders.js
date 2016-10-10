const jsonheaders = () => {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  headers.append("X-CSRFToken", CSRFToken);
  headers.append("Authorization-Token", apiKey);
  return headers;
}
export default jsonheaders