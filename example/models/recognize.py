from transformers import Wav2Vec2Model, Wav2Vec2Processor
import torch
import torchaudio
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

# Загрузка модели и процессора
processor = Wav2Vec2Processor.from_pretrained("models/path_to_save_processor")
model = Wav2Vec2Model.from_pretrained("models/path_to_save_model")

# Загрузка аудиофайлов
def load_audio(file_path):
    waveform, sample_rate = torchaudio.load(file_path)
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)
    return waveform.squeeze().numpy()

# Извлечение признаков
def extract_features(audio):
    input_values = processor(audio, return_tensors="pt", sampling_rate=16000).input_values
    with torch.no_grad():
        hidden_states = model(input_values).last_hidden_state
    return hidden_states.squeeze().numpy()

# Функция для сравнения произношения
def compare_pronunciation(user_audio):

    reference_audio = "voices/ideal1.ogg"
    # Извлечение признаков
    reference_features = extract_features(load_audio(reference_audio))
    user_features = extract_features(load_audio(user_audio))

    # Вычисление DTW расстояния для многомерных данных
    distance, _ = fastdtw(reference_features, user_features, dist=euclidean)

    # Нормализация расстояния (например, деление на длину последовательности)
    normalized_distance = distance / max(len(reference_features), len(user_features))

    return normalized_distance
