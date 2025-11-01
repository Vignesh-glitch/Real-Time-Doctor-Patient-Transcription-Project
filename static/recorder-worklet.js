class RecorderWorklet extends AudioWorkletProcessor {
  process(inputs) {
    const input = inputs[0][0];
    if (input) {
      const int16 = new Int16Array(input.length);
      for (let i = 0; i < input.length; i++) {
        int16[i] = input[i] * 0x7FFF;
      }
      this.port.postMessage(int16.buffer);
    }
    return true;
  }
}
registerProcessor('recorder.worklet', RecorderWorklet);
