import numpy as np
import torch
import torchaudio.functional as F_torchaudio
from scipy.signal import resample as scipy_resample

from core.config import VAD_RMS_THRESHOLD, SAMPLE_RATE

def is_speech(audio, rms_threshold=VAD_RMS_THRESHOLD):
    if audio.size == 0:
        return False
    rms = float(np.sqrt(np.mean(audio ** 2) + 1e-12))
    return rms >= rms_threshold

def resample_audio_if_needed(audio_float, orig_sr, target_sr=SAMPLE_RATE):
    if orig_sr == target_sr:
        return audio_float
    try:
        tensor = torch.from_numpy(audio_float).float().unsqueeze(0)
        resampled = F_torchaudio.resample(tensor, orig_freq=orig_sr, new_freq=target_sr)
        return resampled.squeeze(0).numpy()
    except Exception:
        num_samples = int(len(audio_float) * target_sr / orig_sr)
        res = scipy_resample(audio_float, num_samples)
        return res.astype(np.float32)

def trim_silence(audio, threshold=0.01):
    idx = np.where(np.abs(audio) > threshold)[0]
    if idx.size:
        return audio[idx[0]: idx[-1] + 1]
    return audio
