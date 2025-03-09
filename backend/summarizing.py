from transformers import pipeline

summarizer = pipeline("summarization")
text = """Today, the President addressed the importance of economic stability..."""
summary = summarizer(text, max_length=50, min_length=20, do_sample=False)
print(summary[0]["summary_text"])