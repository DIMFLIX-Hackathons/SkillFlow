import whisper
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("medium").to(device)

result = model.transcribe("assets/test.ogg", language="en", task="transcribe", temperature=0, fp16=True)

print(result["text"])
