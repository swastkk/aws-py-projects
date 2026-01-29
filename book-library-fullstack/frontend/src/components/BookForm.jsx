import { useEffect, useState } from "react";

const initial = { name: "", author: "", price: "" };

export default function BookForm({ onSubmit, loading, selected, onCancel }) {
  const [form, setForm] = useState(initial);
  const [file, setFile] = useState(null);

  useEffect(() => {
    if (selected) {
      setForm({
        name: selected.name ?? "",
        author: selected.author ?? "",
        price: selected.price ?? "",
      });
    } else {
      setForm(initial);
    }
    setFile(null);
  }, [selected]);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const submit = (e) => {
    e.preventDefault();
    onSubmit({
      payload: {
        ...form,
        price: Number(form.price),
      },
      file,
    });
  };

  return (
    <form onSubmit={submit} style={styles.card}>
      <h2 style={{ marginTop: 0 }}>{selected ? "Update Book" : "Add Book"}</h2>

      <input
        style={styles.input}
        name="name"
        placeholder="Book name"
        value={form.name}
        onChange={handleChange}
        required
      />

      <input
        style={styles.input}
        name="author"
        placeholder="Author"
        value={form.author}
        onChange={handleChange}
        required
      />

      <input
        style={styles.input}
        name="price"
        placeholder="Price"
        type="number"
        step="0.01"
        value={form.price}
        onChange={handleChange}
        required
      />
      
      {!selected && (
        <input
          style={styles.input}
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      )}

      <div style={styles.row}>
        <button disabled={loading} style={styles.primary} type="submit">
          {loading ? "Saving..." : selected ? "Update" : "Create"}
        </button>

        {selected && (
          <button type="button" style={styles.secondary} onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

const styles = {
  card: {
    padding: 16,
    border: "1px solid #eee",
    borderRadius: 12,
    background: "#fff",
  },
  row: { display: "flex", gap: 10, marginTop: 12 },
  input: {
    width: "95%",
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #ddd",
    marginTop: 10,
  },
  primary: {
    background: "#111",
    color: "#fff",
    border: "none",
    padding: "10px 14px",
    borderRadius: 10,
    cursor: "pointer",
  },
  secondary: {
    background: "#f2f2f2",
    color: "#111",
    border: "none",
    padding: "10px 14px",
    borderRadius: 10,
    cursor: "pointer",
  },
};
