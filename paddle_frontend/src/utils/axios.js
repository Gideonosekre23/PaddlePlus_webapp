import axios from "axios";

const backendUrl = process.env.REACT_APP_BACKEND_URL;
const backend2 = "https://86c4-86-125-92-90.ngrok-free.app"
const backend3 = "https://b685-2a02-2f09-3707-ae00-3de1-ebab-ed07-3a39.ngrok-free.app"
const axiosInstance = axios.create({
  baseURL: backend3, // Replace with your API base URL
  timeout: 10000, // Request timeout (optional)
  headers: {
    "Content-Type": "application/json",
    'ngrok-skip-browser-warning': 'true'
  },
});

axiosInstance.interceptors.request.use(
    (config) => {
      console.log("Request URL:", config.baseURL + config.url);
      const token = localStorage.getItem("access");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
);
  
// Response interceptor to handle errors globally (optional)
// axiosInstance.interceptors.response.use(
//     (response) => response,
//     async (error) => {
//       if (error.response?.status === 401 && error.config && !error.config._retry) {
//         // Attempt token refresh if a 401 occurs
//         const refreshToken = localStorage.getItem("refresh_token");
//         if (refreshToken) {
//           try {
//             const response = await axios.post(
//               `${process.env.REACT_APP_API_BASE_URL}/token/refresh/`,
//               { refresh: refreshToken }
//             );
//             const newAccessToken = response.data.access;
//             localStorage.setItem("access_token", newAccessToken);
//             // Retry the failed request with the new token
//             error.config.headers.Authorization = `Bearer ${newAccessToken}`;
//             error.config._retry = true;
//             return axiosInstance(error.config);
//           } catch (refreshError) {
//             console.error("Token refresh failed. Logging out...");
//             // Optionally clear tokens and redirect to login
//             localStorage.removeItem("access_token");
//             localStorage.removeItem("refresh_token");
//             window.location.href = "/login";
//           }
//         }
//       }
//       return Promise.reject(error);
//     }
// );

export default axiosInstance;