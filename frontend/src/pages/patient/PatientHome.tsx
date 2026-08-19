//To become patient home

import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";

function Home() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    apiFetch("/")
      .then((data) => setMessage(data.message))
      .catch((error) => console.error("Backend error:", error));
  }, []);

  return (
    <main>
      <h1>Patient Home</h1>
      <p>{message}</p>
    </main>
  );
}

export default Home;