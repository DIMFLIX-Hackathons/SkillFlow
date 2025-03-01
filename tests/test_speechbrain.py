from speechbrain.inference import EncoderDecoderASR
# Загрузите предобученную модель ASR
asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-commonvoice-14-en")
# Транскрибируйте аудио
audio_file = "assets/test.ogg"
text = asr_model.transcribe_file(audio_file)

print("Текст из аудио:", text)
