const form = document.getElementById("ad-form");
const submitBtn = document.getElementById("submitBtn");
const result = document.getElementById("result");
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // guard
  if (!window.API_BASE_URL) {
    result.innerHTML = `<div class="card">Error: window.API_BASE_URL is not set.</div>`;
    result.classList.remove("hidden");
    return;
  }

  submitBtn.disabled = true;
  result.classList.add("hidden");

  const fd = new FormData(form);
  const file = fd.get("file");
  const hasFile = file instanceof File && !!file.name;

  try {
    let res, data;

    if (hasFile) {
      // Convert CTR from % to fraction in form-data
      const ctrRaw = fd.get("current_ctr");
      const pct = parseFloat(ctrRaw);
      fd.set("current_ctr", Number.isFinite(pct) ? String(pct / 100) : "0");

      res = await fetch(`${window.API_BASE_URL}/optimize-file`, {
        method: "POST",
        body: fd,
      });
    } else {
      // JSON path (no file)
      const payload = {
        title: String(fd.get("title") || "").trim(),
        description: String(fd.get("description") || "").trim(),
        current_ctr: (parseFloat(fd.get("current_ctr")) || 0) / 100,
      };

      res = await fetch(`${window.API_BASE_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }

    if (!res.ok) throw new Error(`API ${res.status}`);

    data = await res.json();

    result.innerHTML = `
      <div><strong>Optimized Ad</strong></div>
      <div class="card">
        <h3>${data.new_title}</h3>
        <p>${data.new_description}</p>
      </div>
      <div class="card">
        Predicted CTR Improvement: ${(
          data.probability_higher_ctr * 100
        ).toFixed(1)}%
      </div>
    `;
    result.classList.remove("hidden");
  } catch (err) {
    result.innerHTML = `<div class="card">Error: ${err.message}. Check API_BASE_URL and CORS.</div>`;
    result.classList.remove("hidden");
  } finally {
    submitBtn.disabled = false;
  }
});
