import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

export const getBooks = async () => {
  const res = await api.get("/books");
  return res.data;
};

export const createBook = async (payload) => {
  const res = await api.post("/books/add", payload);
  return res.data;
};

export const updateBook = async (id, payload) => {
  const res = await api.put(`/books/${id}`, payload);
  return res.data;
};

export const deleteBook = async (id) => {
  const res = await api.delete(`/books/${id}`);
  return res.data;
};

export const getBookForUpload = async (id) => {
  const res = await api.get(`/books/${id}/upload`);
  return res.data;
};
