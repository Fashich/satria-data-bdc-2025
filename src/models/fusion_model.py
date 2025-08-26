import tensorflow as tf
from tensorflow.keras import layers, Model
from .custom_cnn import build_visual_model
from .custom_rnn import build_audio_model

def build_fusion_model(visual_shape=(30, 224, 224, 3), 
                      audio_shape=(40, 64), 
                      num_classes=8):
    """
    Bangun model fusion untuk menggabungkan fitur visual dan audio
    
    Args:
        visual_shape (tuple): Shape input visual
        audio_shape (tuple): Shape input audio
        num_classes (int): Jumlah kelas emosi
        
    Returns:
        tuple: (fusion_model, visual_model, audio_model)
    """
    # Input untuk visual dan audio
    visual_input = layers.Input(shape=visual_shape, name='visual_input')
    audio_input = layers.Input(shape=audio_shape, name='audio_input')
    
    # Model visual
    visual_model = build_visual_model(visual_shape, num_classes)
    visual_output = visual_model(visual_input)
    
    # Model audio
    audio_model = build_audio_model(audio_shape, num_classes)
    audio_output = audio_model(audio_input)
    
    # Fusion layer - menggabungkan prediksi dari kedua model
    combined = layers.Average()([visual_output, audio_output])
    
    # Model akhir
    fusion_model = Model(inputs=[visual_input, audio_input], outputs=combined)
    
    return fusion_model, visual_model, audio_model

if __name__ == "__main__":
    fusion_model, visual_model, audio_model = build_fusion_model()
    fusion_model.summary()