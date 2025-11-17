document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("resume");
  const resumeText = document.getElementById("resumeText").value.trim();
  const jobDesc = document.getElementById("jobDesc").value.trim();
  const resultPane = document.getElementById("resultPane");

  if (!jobDesc) {
    resultPane.innerHTML = "<p class='placeholder'>Please provide job description.</p>";
    return;
  }

  resultPane.innerHTML = "<p class='placeholder'>Analyzing... ⏳</p>";

  try {
    let response;

    // FILE MODE
    if (fileInput.files.length > 0) {
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      formData.append("job_description", jobDesc);

      response = await fetch("http://127.0.0.1:8000/analyze/file", {
        method: "POST",
        body: formData
      });
    }

    // TEXT MODE
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
      resultPane.innerHTML = "<p class='placeholder'>Upload or paste your resume first.</p>";
      return;
    }

    const data = await response.json();
    if (data.error) {
      resultPane.innerHTML = `<p class='placeholder'>Error: ${data.error}</p>`;
      return;
    }

    // ---------- BUILD UI ----------
    const match = data.overall_match ?? 0;
    const domain = data.predicted_domain ?? "Unknown";
    const topKeywords = data.top_keywords || [];
    const missingKeywords = data.missing_keywords || [];
    const bar = data.bar_chart;
    const pie = data.pie_chart;

    // ---------- GENERATE SUMMARY ----------
    const summary = `
      <div class="summary-box">
        <h4>Summary</h4>
        <p>Your resume matches <strong>${match}%</strong> of the job description. 
        The system predicts that your profile is mostly aligned with 
        <strong>${domain}</strong>. You can improve your resume by adding 
        missing important skills from the job description and strengthening
        the areas where the match percentage is low. Overall, this gives you a 
        clear direction on how to refine your resume for this job role.</p>
      </div>
    `;

    // ---------- FINAL HTML ----------
    const html = `
      <div class="result-block">
        <h3>Match Score: <span style="color:#007bff">${match}%</span></h3>
        <p><strong>Predicted Domain:</strong> ${domain}</p>
      </div>

      <div class="keywords-block">
        <h4>Top Matched Keywords</h4>
        <ul>${topKeywords.map(k => `<li>${k}</li>`).join("")}</ul>

        <h4>Missing Important Keywords</h4>
        <ul>${missingKeywords.map(k => `<li>${k}</li>`).join("")}</ul>
      </div>

      <div class="charts">
        <div class="chart-box">
          <h4>Relevant Domain Match</h4>
          <img src="data:image/png;base64,${bar}" style="max-width:100%">
        </div>

        <div class="chart-box">
          <h4>Overall Resume vs Job Match</h4>
          <img src="data:image/png;base64,${pie}" style="max-width:100%">
        </div>
      </div>

      ${summary}
    `;

    resultPane.innerHTML = html;

  } catch (err) {
    console.error(err);
    resultPane.innerHTML = "<p class='placeholder'>❌ Error analyzing resume.</p>";
  }
});
