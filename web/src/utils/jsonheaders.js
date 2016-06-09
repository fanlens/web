const jsonheaders = () => {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Accept", "application/json");
  headers.append("X-CSRFToken", CSRFToken);
  return headers;
}
export default jsonheaders