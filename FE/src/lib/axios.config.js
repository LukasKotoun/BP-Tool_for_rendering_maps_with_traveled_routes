/**
 * Axios instance config for API requests.
 * @author Lukáš Kotoun, xkotou08
 */
import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL;
const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;