from transformers import pipeline

print("⏳ Loading summarizer...")
try:
    summarizer = pipeline("summarization", model="Falconsai/medical_summarization")
except Exception:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
print(" Summarizer loaded")

def summarize_conversation(transcript: str) -> str:
    if not transcript.strip():
        return "No conversation recorded."
    try:
        text = transcript[-3000:]
        summary = summarizer(text, max_length=120, min_length=30, do_sample=False)[0]['summary_text']
    except Exception:
        summary = transcript[:300] + "..."
    return summary
