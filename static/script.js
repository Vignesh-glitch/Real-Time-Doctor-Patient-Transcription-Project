let ws;
let audioContext;
let processor;
let stream;
const chatBox = document.getElementById('chatBox');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const roleSelect = document.getElementById('role');
function addMessage(role, text) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;

  const avatar = document.createElement('img');
  avatar.className = 'avatar';
  avatar.src = role === 'doctor' 
    ? '/static/doctor.jpg' 
    : role === 'patient' 
      ? '/static/patient.png'
      : '/static/system.png';

  const content = document.createElement('div');
  const timestamp = document.createElement('span');
  timestamp.className = 'timestamp';
  const now = new Date().toLocaleTimeString();
  timestamp.textContent = now;

  content.textContent = `${text}`;
  content.appendChild(timestamp);

  msg.appendChild(avatar);
  msg.appendChild(content);
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

startBtn.onclick = async () => {
  const role = roleSelect.value;
  ws = new WebSocket(`ws://${location.host}/ws/whisper?role=${role}`);
  ws.onopen = async() => {
    console.log("WebSocket connected");
    try {
    ws.send(JSON.stringify({ type: "meta", sampleRate: audioContext.sampleRate }));
  } catch (e) {
    console.warn("Could not send meta sampleRate", e);
  }
    startBtn.disabled = true;
    stopBtn.disabled = false;
  };
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("📩 Message from server:", data);
    if (data.type === "stt") {
      addMessage(data.role, data.text || "(no text)");
       const playbackEnabled = document.getElementById('playback').checked;
    if (playbackEnabled && data.text) {
  const utterance = new SpeechSynthesisUtterance(data.text);
  const voices = speechSynthesis.getVoices();
  utterance.voice = voices.find(v => v.name.includes(
    data.role === "doctor" ? "Male" : "Female"
  ));
  speechSynthesis.speak(utterance);
}

    } else if (data.type === "summary") {
      addMessage("system", "🧾 " + data.text);
    }
  };
  ws.onclose = () => {
    console.log(" WebSocket closed");
    startBtn.disabled = false;
    stopBtn.disabled = true;
  };
  stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  audioContext = new AudioContext({ sampleRate: 16000 });
  const source = audioContext.createMediaStreamSource(stream);
  try {
    await audioContext.audioWorklet.addModule('/static/recorder-worklet.js');
    const workletNode = new AudioWorkletNode(audioContext, 'recorder.worklet');
    workletNode.port.onmessage = (e) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(e.data);
      }
    };
    source.connect(workletNode).connect(audioContext.destination);
  } catch (err) {
    console.warn("⚠️ AudioWorklet unavailable, using ScriptProcessor fallback", err);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    source.connect(processor);
    processor.connect(audioContext.destination);
    processor.onaudioprocess = (event) => {
      if (ws.readyState === WebSocket.OPEN) {
        const input = event.inputBuffer.getChannelData(0);
        const int16 = new Int16Array(input.length);
        for (let i = 0; i < input.length; i++) {
          int16[i] = input[i] * 0x7FFF;
        }
        ws.send(int16.buffer);
      }
    };
  }
};
stopBtn.onclick = () => {
  ws?.close();
  audioContext?.close();
  stream?.getTracks().forEach(t => t.stop());
  startBtn.disabled = false;
  stopBtn.disabled = true;
};
