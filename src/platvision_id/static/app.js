const form = document.querySelector("#recognition-form");
const imageInput = document.querySelector("#image-input");
const fileLabel = document.querySelector("#file-label");
const previewFrame = document.querySelector(".preview-frame");
const previewImage = document.querySelector("#preview-image");
const resultPanel = document.querySelector(".result-panel");
const statusPill = document.querySelector("#status-pill");
const plateOutput = document.querySelector("#plate-output");
const regionOutput = document.querySelector("#region-output");
const confidenceOutput = document.querySelector("#confidence-output");
const detectorOutput = document.querySelector("#detector-output");
const notesOutput = document.querySelector("#notes-output");
const submitButton = document.querySelector(".primary-action");

imageInput.addEventListener("change", () => {
  const selectedFile = imageInput.files[0];
  if (!selectedFile) {
    return;
  }

  fileLabel.textContent = selectedFile.name;
  previewImage.src = URL.createObjectURL(selectedFile);
  previewImage.alt = `Preview of ${selectedFile.name}`;
  previewFrame.dataset.empty = "false";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  setLoadingState();

  try {
    const response = await fetch("/api/recognize", {
      method: "POST",
      body: formData
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.message || "Recognition failed.");
    }
    showRecognition(payload);
  } catch (error) {
    showError(error.message);
  } finally {
    submitButton.disabled = false;
    resultPanel.setAttribute("aria-busy", "false");
  }
});

function setLoadingState() {
  submitButton.disabled = true;
  resultPanel.setAttribute("aria-busy", "true");
  statusPill.textContent = "Scanning";
  statusPill.dataset.state = "";
  notesOutput.textContent = "Running YOLO localization and OCR.";
  triggerScan(previewFrame);
  triggerScan(resultPanel);
}

function showRecognition(payload) {
  plateOutput.textContent = payload.normalizedPlate || payload.plate || "UNREADABLE";
  regionOutput.textContent = payload.region?.name || "Unknown region";
  confidenceOutput.textContent = `${Math.round((payload.confidence || 0) * 100)}%`;
  detectorOutput.textContent = payload.diagnostics?.detector || "-";
  const notes = payload.diagnostics?.notes || [];
  notesOutput.textContent = notes.length ? notes.join(" ") : "Recognition completed without fallback notes.";
  statusPill.textContent = payload.diagnostics?.fallbackUsed ? "Fallback" : "Detected";
  statusPill.dataset.state = "success";
}

function showError(message) {
  statusPill.textContent = "Error";
  statusPill.dataset.state = "error";
  plateOutput.textContent = "-- ---- ---";
  regionOutput.textContent = "No result";
  confidenceOutput.textContent = "-";
  detectorOutput.textContent = "-";
  notesOutput.textContent = message;
}

function triggerScan(element) {
  element.classList.remove("is-scanning");
  window.requestAnimationFrame(() => {
    element.classList.add("is-scanning");
  });
}
