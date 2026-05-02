const form = document.querySelector("#recognition-form");
const imageInput = document.querySelector("#image-input");
const fileLabel = document.querySelector("#file-label");
const previewFrame = document.querySelector(".preview-frame");
const previewImage = document.querySelector("#preview-image");
const bboxOverlay = document.querySelector("#bbox-overlay");
const resultPanel = document.querySelector(".result-panel");
const statusPill = document.querySelector("#status-pill");
const plateOutput = document.querySelector("#plate-output");
const regionOutput = document.querySelector("#region-output");
const confidenceOutput = document.querySelector("#confidence-output");
const detectorOutput = document.querySelector("#detector-output");
const notesOutput = document.querySelector("#notes-output");
const cropInspection = document.querySelector("#crop-inspection");
const cropPreview = document.querySelector("#crop-preview");
const taxLookup = document.querySelector("#tax-lookup");
const taxSourceLink = document.querySelector("#tax-source-link");
const taxStatus = document.querySelector("#tax-status");
const taxDueDate = document.querySelector("#tax-due-date");
const taxTotal = document.querySelector("#tax-total");
const taxOwner = document.querySelector("#tax-owner");
const taxAddress = document.querySelector("#tax-address");
const taxVehicle = document.querySelector("#tax-vehicle");
const taxMessage = document.querySelector("#tax-message");
const submitButton = document.querySelector(".primary-action");
let currentImageUrl = "";
let lastDetectionBox = null;

imageInput.addEventListener("change", () => {
  const selectedFile = imageInput.files[0];
  if (!selectedFile) {
    return;
  }

  if (currentImageUrl) {
    URL.revokeObjectURL(currentImageUrl);
  }
  currentImageUrl = URL.createObjectURL(selectedFile);
  fileLabel.textContent = selectedFile.name;
  previewImage.src = currentImageUrl;
  previewImage.alt = `Preview of ${selectedFile.name}`;
  previewFrame.dataset.empty = "false";
  clearLocalization();
  renderCropPreview(null);
  renderTaxLookup(null);
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
  clearLocalization();
  renderTaxLookup(null);
  triggerScan(previewFrame);
  triggerScan(resultPanel);
}

function showRecognition(payload) {
  plateOutput.textContent = payload.normalizedPlate || payload.plate || "UNREADABLE";
  regionOutput.textContent = payload.region?.name || "Unknown region";
  confidenceOutput.textContent = `${Math.round((payload.confidence || 0) * 100)}%`;
  detectorOutput.textContent = formatDetector(payload.diagnostics);
  const notes = payload.diagnostics?.notes || [];
  const diagnosticSummary = formatDiagnosticSummary(payload.diagnostics);
  notesOutput.textContent = [diagnosticSummary, ...notes].filter(Boolean).join(" ");
  statusPill.textContent = payload.diagnostics?.fallbackUsed ? "Fallback" : "Detected";
  statusPill.dataset.state = "success";
  renderLocalization(payload.box);
  renderCropPreview(payload.cropPreview);
  renderTaxLookup(payload.tax);
}

function showError(message) {
  statusPill.textContent = "Error";
  statusPill.dataset.state = "error";
  plateOutput.textContent = "-- ---- ---";
  regionOutput.textContent = "No result";
  confidenceOutput.textContent = "-";
  detectorOutput.textContent = "-";
  notesOutput.textContent = message;
  clearLocalization();
  renderCropPreview(null);
  renderTaxLookup(null);
}

function triggerScan(element) {
  element.classList.remove("is-scanning");
  window.requestAnimationFrame(() => {
    element.classList.add("is-scanning");
  });
}

function renderLocalization(box) {
  lastDetectionBox = box || null;
  if (!box || !previewImage.naturalWidth || !previewImage.naturalHeight) {
    bboxOverlay.hidden = true;
    return;
  }

  const frameRect = previewFrame.getBoundingClientRect();
  const scale = Math.min(
    frameRect.width / previewImage.naturalWidth,
    frameRect.height / previewImage.naturalHeight
  );
  const renderedWidth = previewImage.naturalWidth * scale;
  const renderedHeight = previewImage.naturalHeight * scale;
  const offsetX = (frameRect.width - renderedWidth) / 2;
  const offsetY = (frameRect.height - renderedHeight) / 2;

  bboxOverlay.style.left = `${offsetX + box.x1 * scale}px`;
  bboxOverlay.style.top = `${offsetY + box.y1 * scale}px`;
  bboxOverlay.style.width = `${Math.max(0, (box.x2 - box.x1) * scale)}px`;
  bboxOverlay.style.height = `${Math.max(0, (box.y2 - box.y1) * scale)}px`;
  bboxOverlay.hidden = false;
}

function renderCropPreview(dataUrl) {
  if (!dataUrl) {
    cropInspection.hidden = true;
    cropPreview.removeAttribute("src");
    return;
  }

  cropPreview.src = dataUrl;
  cropInspection.hidden = false;
}

function renderTaxLookup(tax) {
  if (!tax) {
    taxLookup.hidden = true;
    return;
  }

  taxStatus.textContent = formatTaxStatus(tax);
  taxDueDate.textContent = tax.taxDueDate || tax.stnkExpiryDate || "-";
  taxTotal.textContent = tax.totalDue || tax.pkbTotal || "-";
  taxOwner.textContent = tax.ownerName || "Not provided";
  taxAddress.textContent = tax.ownerAddress || "Not provided";
  taxVehicle.textContent = formatVehicle(tax);
  taxMessage.textContent = tax.message || "Tax lookup completed.";

  if (tax.sourceUrl) {
    taxSourceLink.href = tax.sourceUrl;
    taxSourceLink.textContent = tax.source || "Source";
    taxSourceLink.hidden = false;
  } else {
    taxSourceLink.hidden = true;
  }

  taxLookup.hidden = false;
}

function clearLocalization() {
  lastDetectionBox = null;
  bboxOverlay.hidden = true;
}

function formatDetector(diagnostics) {
  if (!diagnostics) {
    return "-";
  }
  if (!diagnostics.fallbackUsed) {
    return diagnostics.detector || diagnostics.selectedDetector || "-";
  }
  const primary = diagnostics.primaryDetector || "detector";
  const selected = diagnostics.selectedDetector || diagnostics.detector || "fallback";
  return `${primary} -> ${selected}`;
}

function formatDiagnosticSummary(diagnostics) {
  if (!diagnostics) {
    return "";
  }

  const parts = [];
  if (Number.isInteger(diagnostics.primaryDetections)) {
    parts.push(`YOLO detections: ${diagnostics.primaryDetections}.`);
  }
  if (typeof diagnostics.primaryBestConfidence === "number") {
    parts.push(`Best YOLO confidence: ${Math.round(diagnostics.primaryBestConfidence * 100)}%.`);
  }
  return parts.join(" ");
}

function formatTaxStatus(tax) {
  if (tax.status === "found") {
    if (tax.paymentStatus === "overdue_amount") {
      return "Amount with penalty";
    }
    if (tax.paymentStatus === "amount_due") {
      return "Amount due";
    }
    if (tax.paymentStatus === "no_amount_due") {
      return "No amount due";
    }
    return "Found";
  }
  if (tax.status === "not_found") {
    return "Not found";
  }
  if (tax.status === "unsupported_region") {
    return "Unsupported";
  }
  if (tax.status === "manual_source_only") {
    return "Manual source";
  }
  if (tax.status === "lookup_failed") {
    return "Lookup failed";
  }
  return tax.status || "-";
}

function formatVehicle(tax) {
  const main = [tax.vehicleBrand, tax.vehicleModel].filter(Boolean).join(" ");
  const detail = [tax.vehicleType, tax.vehicleYear, tax.vehicleColor].filter(Boolean).join(" / ");
  return [main, detail].filter(Boolean).join(" - ") || "-";
}

previewImage.addEventListener("load", () => {
  if (lastDetectionBox) {
    renderLocalization(lastDetectionBox);
  }
});

window.addEventListener("resize", () => {
  if (lastDetectionBox) {
    renderLocalization(lastDetectionBox);
  }
});
