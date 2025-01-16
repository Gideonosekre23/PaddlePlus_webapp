export const saveToLocalStorage = (data) => {
    Object.keys(data).forEach((key) => {
      localStorage.setItem(key, data[key]);
    });
};

export const createNgrokSocketUrl = (webSocketUrl) => {
  const ngrokLink = "https://b685-2a02-2f09-3707-ae00-3de1-ebab-ed07-3a39.ngrok-free.app"
  const updatedWebSocketUrl = webSocketUrl.replace(/^ws:\/\/127\.0\.0\.1:8000/, ngrokLink.replace(/^https?/, "wss"));

  return updatedWebSocketUrl;
}

export const createNgrokSocketUrlAlt = (webSocketUrl) => {
  const ngrokLink = "https://b685-2a02-2f09-3707-ae00-3de1-ebab-ed07-3a39.ngrok-free.app"
  const updatedWebSocketUrl = ngrokLink.replace(/^https?/, "wss") + webSocketUrl;
  console.log(updatedWebSocketUrl);

  return updatedWebSocketUrl;
}
  