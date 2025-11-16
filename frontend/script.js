async function analyzeResume() {
  const fileInput = document.getElementById("resume");
  const resumeText = document.getElementById("resumeText").value.trim();
  const jobDesc = document.getElementById("jobDesc").value.trim();
  const resultDiv = document.getElementById("result");

  if (!jobDesc) {
    alert("Please enter a job description.");
    return;
  }

  resultDiv.innerHTML = "Analyzing... ⏳";

  try {
    let response;

    // -------------------- FILE UPLOAD --------------------
    if (fileInput.files.length > 0) {
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      formData.append("job_description", jobDesc);

      response = await fetch("http://127.0.0.1:8000/analyze/file", {
        method: "POST",
        body: formData,
      });
    }

    // -------------------- TEXT INPUT --------------------
    else if (resumeText.length > 0) {
      const formData = new FormData();
      formData.append("resume_text", resumeText);
      formData.append("job_description", jobDesc);

      response = await fetch("http://127.0.0.1:8000/analyze/text", {
        method: "POST",
        body: formData,      // ⬅️ FORM DATA (NOT JSON!)
      });
    }

    else {
      resultDiv.innerHTML = "❌ Please upload resume or paste text.";
      return;
    }

    // -------------------- RESPONSE --------------------
    const data = await response.json();

    if (data.error) {
      resultDiv.innerHTML = "❌ " + data.error;
    } else {
      resultDiv.innerHTML =
        `<h3>Top Matches:</h3><pre>${JSON.stringify(data.result, null, 2)}</pre>`;
    }

  } catch (error) {
    resultDiv.innerHTML = "❌ Error analyzing resume.";
    console.error(error);
  }
}
