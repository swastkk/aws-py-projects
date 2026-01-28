import axios from "axios";

export const uploadToS3 = async ({ upload_url, file }) => {
  await axios.put(upload_url, file, {
    headers: {
      "Content-Type": file.type,
    },
  });
};
