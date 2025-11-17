document.getElementById("analyzeBtn").addEventListener("click", async () => {

  const btn = document.getElementById("analyzeBtn");
  const inputSection = document.getElementById("inputSection");
  const resultSection = document.getElementById("resultSection");
  const resultPane = document.getElementById("resultPane");

  // Change button state
  btn.innerText = "Analyzing... ⌛";
  btn.classList.add("loading");
  btn.disabled = true;

  const fileInput = document.getElementById("resume");
  const resumeText = document.getElementById("resumeText").value.trim();
  const jobDesc = document.getElementById("jobDesc").value.trim();

  // -------------------------------
  // VALIDATION (DO NOT HIDE INPUT!)
  // -------------------------------

  // If job description is empty
  if (!jobDesc) {

      // Only show resultSection; DO NOT hide inputSection
      resultSection.classList.remove("hidden");

      resultPane.innerHTML = `
          <div class="result-message">
              ❗ Please enter a job description to continue.
          </div>
      `;

      resetButton();
      return;
  }

  // If both resume file & resume text are empty
  if (fileInput.files.length === 0 && resumeText.length === 0) {

      resultSection.classList.remove("hidden");

      resultPane.innerHTML = `
          <div class="result-message">
              ❗ Please upload a resume or paste resume text.
          </div>
      `;

      resetButton();
      return;
  }

  // Show loading message
  resultPane.innerHTML = "<p>Analyzing... ⏳</p>";

  try {
      let response;

      if (fileInput.files.length > 0) {
          const formData = new FormData();
          formData.append("file", fileInput.files[0]);
          formData.append("job_description", jobDesc);

          response = await fetch("http://127.0.0.1:8000/analyze/file", {
              method: "POST",
              body: formData
          });
      } 
      else if (resumeText.length > 0) {
          response = await fetch("http://127.0.0.1:8000/analyze/text", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  resume_text: resumeText,
                  job_description: jobDesc
              })
          });
      }

      const data = await response.json();

      if (data.error) {
          resultPane.innerHTML = `<p>${data.error}</p>`;
          return;
      }

      // --------------------------------------------------
      // ONLY NOW: HIDE INPUT & SHOW OUTPUT
      // --------------------------------------------------
      inputSection.classList.add("hidden");
      resultSection.classList.remove("hidden");

      // Output UI
      resultPane.innerHTML = `
        <h3 class="result-title">Resume Analysis Result</h3>

        <div class="keyword-box">
          <strong>Match Percentage:</strong> ${data.overall_match}% <br>
          <strong>Predicted Domain:</strong> ${data.predicted_domain}
        </div>

        <div class="keyword-box">
          <strong>Top Matched Keywords:</strong>
          <ul>${data.top_keywords.map(k => `<li>${k}</li>`).join("")}</ul>
        </div>

        <div class="missing-box">
          <strong>Missing Important Keywords:</strong>
          <ul>${data.missing_keywords.map(k => `<li>${k}</li>`).join("")}</ul>
        </div>

        <div class="keyword-box">
          <strong>Domain Match Chart</strong><br>
          <img class="chart-img" src="data:image/png;base64,${data.bar_chart}" />
        </div>

        <div class="keyword-box">
          <strong>Overall Match Chart</strong><br>
          <img class="chart-img" src="data:image/png;base64,${data.pie_chart}" />
        </div>

        <div class="summary-box">
          <strong>Summary:</strong>
          <p>${data.summary}</p>
        </div>
      `;

  } catch (err) {
      console.error(err);
      resultPane.innerHTML = "<p>❌ Something went wrong.</p>";
  }

  function resetButton() {
      const btn = document.getElementById("analyzeBtn");
      btn.innerText = "Analyze";
      btn.classList.remove("loading");
      btn.disabled = false;
  }
});
