export default function BookList({ books, onEdit, onDelete, onUpdateImage, loading }) {
  return (
    <div style={styles.card}>
      <h2 style={{ marginTop: 0 }}>Books</h2>

      {loading && <p>Loading...</p>}

      {!loading && books.length === 0 && <p>No books found.</p>}

      <div style={{ display: "grid", gap: 10 }}>
        {books.map((b) => (
        <div key={b.id} style={styles.item}>
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <div style={styles.thumb}>
                {b.image_url ? (
                    <img src={b.image_url} alt={b.name} style={styles.img} />
                ) : (
                    <div style={styles.noimg}>No Image</div>
                )}
                </div>

                <div>
                <div style={{ fontWeight: 700 }}>{b.name}</div>
                <div style={{ fontSize: 14, opacity: 0.8 }}>{b.author}</div>
                <div style={{ fontSize: 14 }}>₹ {b.price}</div>
                </div>
            </div>

            <div style={styles.actions}>
                <button style={styles.btn} onClick={() => onEdit(b)}>Edit</button>
                  <button style={styles.btn} onClick={() => onUpdateImage(b)}>Update Image</button>
                <button style={styles.danger} onClick={() => onDelete(b.id)}>Delete</button>
            </div>
            </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  card: {
    padding: 16,
    border: "1px solid #eee",
    borderRadius: 12,
    background: "#fff",
  },
  item: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 12,
    border: "1px solid #eee",
    borderRadius: 12,
  },
  actions: { display: "flex", gap: 8 },
  btn: {
    border: "1px solid #ddd",
    background: "#fff",
    padding: "8px 12px",
    borderRadius: 10,
    cursor: "pointer",
  },
  danger: {
    border: "1px solid #f3b4b4",
    background: "#ffecec",
    padding: "8px 12px",
    borderRadius: 10,
    cursor: "pointer",
  },
  thumb: {
    width: 60,
    height: 60,
    borderRadius: 12,
    border: "1px solid #eee",
    overflow: "hidden",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#fafafa",
    },
    img: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    },
    noimg: {
    fontSize: 11,
    opacity: 0.6,
    },
};
