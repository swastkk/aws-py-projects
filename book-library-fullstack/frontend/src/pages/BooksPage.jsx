import { useEffect, useState } from "react";
import BookForm from "../components/BookForm";
import BookList from "../components/BookList";
import { uploadToS3 } from "../api/s3";
import { createBook, deleteBook, getBookForUpload, getBooks, updateBook } from "../api/books";

export default function BooksPage() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [selected, setSelected] = useState(null);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const data = await getBooks();
      setBooks(data.books ?? data ?? []);
    } catch (e) {
      console.error(e);
      alert("Failed to fetch books");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const uploadImageForBook = async (bookId, file) => {
    const data = await getBookForUpload(bookId);
    const uploadUrl = data.upload_image_url;

    if (!uploadUrl) throw new Error("upload_image_url missing from /books/{id}/upload");

    await uploadToS3({ upload_url: uploadUrl, file });
  };

  const handleSubmit = async ({ payload, file }) => {
    setSaving(true);

    try {
      if (selected) {
        await updateBook(selected.id, payload);
        setSelected(null);
        await fetchBooks();
        return;
      }

      const created = await createBook(payload);
      const bookId = created?.id ?? created?.book?.id ?? created?.data?.id;

      if (!bookId) throw new Error("createBook response does not contain book id");

      if (file) {
        await uploadImageForBook(bookId, file);
      }

      await fetchBooks();
    } catch (e) {
      console.error(e);
      alert("Failed to save book");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    const ok = confirm("Delete this book?");
    if (!ok) return;

    try {
      await deleteBook(id);
      await fetchBooks();
    } catch (e) {
      console.error(e);
      alert("Failed to delete book");
    }
  };

  const handleUpdateImage = async (book) => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";

    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;

      try {
        await uploadImageForBook(book.id, file);
        await fetchBooks();
        alert("Image updated");
      } catch (e) {
        console.error(e);
        alert("Failed to update image");
      }
    };

    input.click();
  };

  return (
    <div style={styles.page}>
      <h1 style={{ marginTop: 0 }}>Book Library (Sw.)</h1>

      <div style={styles.grid}>
        <BookForm
          onSubmit={handleSubmit}
          loading={saving}
          selected={selected}
          onCancel={() => setSelected(null)}
        />

        <BookList
          books={books}
          loading={loading}
          onEdit={(b) => setSelected(b)}
          onDelete={handleDelete}
          onUpdateImage={handleUpdateImage}
        />
      </div>
    </div>
  );
}

const styles = {
  page: {
    // maxWidth: 1100,
    margin: "0 auto",
    padding: 18,
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial",
    background: "#fafafa",
    minHeight: "100vh",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1.4fr",
    gap: 16,
    marginTop: 16,
  },
};
