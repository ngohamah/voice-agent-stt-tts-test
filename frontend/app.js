const recordBtn = document.getElementById("recordBtn");
const resetBtn = document.getElementById("resetBtn");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const player = document.getElementById("player");

let mediaRecorder;
let chunks = [];
let isRecording = false;

function addTurn(who, text) {
  const div = document.createElement("div");
  div.className = "turn";
  div.innerHTML = `<span class="who">${who}:</span>${text}`;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

function micErrorMessage(err) {
  if (!navigator.mediaDevices?.getUserMedia) {
    return "This browser doesn't support microphone access. Try a recent Chrome, Firefox, or Safari, and make sure you're on localhost or HTTPS.";
  }
  switch (err.name) {
    case "NotAllowedError":
    case "SecurityError":
      return "Microphone access was blocked. Allow it in your browser's site settings and try again.";
    case "NotFoundError":
      return "No microphone was found. Connect one and try again.";
    case "NotReadableError":
      return "The microphone is already in use by another application.";
    default:
      return `Couldn't access the microphone: ${err.message || err.name}`;
  }
}

async function startRecording() {
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (err) {
    console.error(err);
    statusEl.textContent = micErrorMessage(err);
    return;
  }

  chunks = [];
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = onRecordingStop;
  mediaRecorder.start();
  isRecording = true;
  recordBtn.textContent = "Stop Recording";
  recordBtn.classList.add("recording");
  statusEl.textContent = "Listening...";
}

function stopRecording() {
  mediaRecorder.stop();
  mediaRecorder.stream.getTracks().forEach((track) => track.stop());
  isRecording = false;
  recordBtn.textContent = "Start Recording";
  recordBtn.classList.remove("recording");
}

async function onRecordingStop() {
  statusEl.textContent = "Thinking...";
  const blob = new Blob(chunks, { type: "audio/webm" });

  const formData = new FormData();
  formData.append("audio", blob, "recording.webm");

  try {
    const res = await fetch("/api/converse", { method: "POST", body: formData });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();

    addTurn("You", data.transcript);
    addTurn("Agent", data.reply);

    const audioBytes = Uint8Array.from(atob(data.audio_base64), (c) => c.charCodeAt(0));
    const audioBlob = new Blob([audioBytes], { type: "audio/wav" });
    player.src = URL.createObjectURL(audioBlob);
    await player.play();

    statusEl.textContent = "";
  } catch (err) {
    console.error(err);
    statusEl.textContent = `Error: ${err.message}`;
  }
}

recordBtn.addEventListener("click", () => {
  if (isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
});

resetBtn.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  logEl.innerHTML = "";
  statusEl.textContent = "Conversation reset.";
});
