document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("resume");
  const resumeText = document.getElementById("resumeText").value.trim();
  const jobDesc = document.getElementById("jobDesc").value.trim();
  const resultPane = document.getElementById("resultPane");

  if (!jobDesc) {
    resultPane.innerHTML = "<p class='placeholder'>Please enter job description.</p>";
    return;
  }

  resultPane.innerHTML = "<p class='placeholder'>Analyzing... ⏳</p>";

  try {
    let response;

    // If file uploaded
    if (fileInput.files.length > 0) {
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      formData.append("job_description", jobDesc);

      response = await fetch("http://127.0.0.1:8000/analyze/file", {
        method: "POST",
        body: formData
      });
    }

    // If text pasted
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

    else {
      resultPane.innerHTML = "<p class='placeholder'>Upload or paste resume text.</p>";
      return;
    }

    const data = await response.json();

    if (data.error) {
      resultPane.innerHTML = `<p class="placeholder">❌ ${data.error}</p>`;
      return;
    }

    // Build output UI
    const html = `
      <h3>Match Score: <span style="color:#0b74ff">${data.overall_match}%</span></h3>

      <div class="line">
        <strong>Predicted Domain:</strong> ${data.predicted_domain}
      </div>

      <h4>Top Matched Keywords</h4>
      <ul>${data.top_keywords.map(k => `<li>${k}</li>`).join("")}</ul>

      <h4>Missing Keywords</h4>
      <ul>${data.missing_keywords.map(k => `<li>${k}</li>`).join("")}</ul>

      <h4>Relevant Domain Comparison</h4>
      <img class="chart" src="data:image/png;base64,${data.bar_chart}" />

      <h4>Overall Match Chart</h4>
      <img class="chart" src="data:image/png;base64,${data.pie_chart}" />

      <h4>Summary</h4>
      <p class="summary">
        Your resume matches about <strong>${data.overall_match}%</strong> of the job description.
        The predicted domain is <strong>${data.predicted_domain}</strong>. Boost your resume by
        adding the missing keywords listed above. The charts show how closely your resume aligns
        with relevant domains and the overall match level.
      </p>
    `;

    resultPane.innerHTML = html;

  } catch (err) {
    console.error(err);
    resultPane.innerHTML = "<p class='placeholder'>❌ Something went wrong.</p>";
  }
});
