export async function api(path, { method = "GET", body } = {}) {
  const token = localStorage.getItem("token");
  const res = await fetch("/api" + path, {
    method,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: "Bearer " + token } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const d = err.detail;
    throw new Error(typeof d === "string" ? d : "Something went wrong. Check your details and try again.");
  }
  return res.status === 204 ? null : res.json();
}
