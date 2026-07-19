import { io } from "socket.io-client";

const token = localStorage.getItem('access_token');

const socket = io(import.meta.env.VITE_API_BASE_URL, {
  withCredentials: true,
  transports: ['websocket', 'polling'],
  auth: { token: token },
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
});

export default socket;