from transformers import pipeline

pipe = pipeline(
    "automatic-speech-recognition",
    model="dg96/whisper-finetuning-phoneme-transcription-g2p-large-dataset-space-seperated-phonemes",
    device="cuda:0",
)

result = pipe(
    "assets/4.ogg",
    generate_kwargs={
        "language": "en",
    },
)

print(result["text"])
