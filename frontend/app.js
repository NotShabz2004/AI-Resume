const form = document.getElementById("quote-form");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const submitBtn = document.getElementById("submit-btn");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#ff8d8d" : "#a2d1ff";
}

function speakWithBrowser(text) {
  if (!("speechSynthesis" in window)) {
    throw new Error("Browser speech synthesis is not supported in this browser.");
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

async function speakWithElevenLabs(text) {
  const response = await fetch("/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, provider: "elevenlabs" }),
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Failed to generate ElevenLabs speech.");
  }

  const data = await response.json();
  const audioUrl = `data:${data.mime_type};base64,${data.audio_base64}`;
  const audio = new Audio(audioUrl);
  audio.play();
}

function renderQuotes(quotes, source, ttsProvider) {
  resultsEl.innerHTML = "";
  quotes.forEach((quote) => {
    const item = document.createElement("article");
    item.className = "quote";

    const p = document.createElement("p");
    p.textContent = quote;
    item.appendChild(p);

    const actionWrap = document.createElement("div");
    actionWrap.className = "actions";

    const speakBtn = document.createElement("button");
    speakBtn.type = "button";
    speakBtn.textContent = "🔊 Speak";
    speakBtn.addEventListener("click", async () => {
      try {
        if (ttsProvider === "elevenlabs") {
          await speakWithElevenLabs(quote);
        } else {
          speakWithBrowser(quote);
        }
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    actionWrap.appendChild(speakBtn);
    item.appendChild(actionWrap);
    resultsEl.appendChild(item);
  });

  setStatus(`Generated ${quotes.length} quote(s) using ${source}.`);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitBtn.disabled = true;
  setStatus("Generating quotes...");

  const formData = new FormData(form);
  const payload = {
    name: formData.get("name"),
    running_for: formData.get("running_for"),
    main_challenge: formData.get("main_challenge"),
    race_type: formData.get("race_type"),
    quote_count: Number(formData.get("quote_count") || 5),
    tone: formData.get("tone"),
  };

  const ttsProvider = formData.get("tts_provider");

  try {
    const response = await fetch("/api/quotes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Quote generation failed.");
    }

    const data = await response.json();
    renderQuotes(data.quotes, data.source, ttsProvider);
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    submitBtn.disabled = false;
  }
});
