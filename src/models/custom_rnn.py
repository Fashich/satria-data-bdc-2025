import tensorflow as tf
from tensorflow.keras import layers, Model

def build_audio_model(input_shape=(40, 64), num_classes=8):
    inputs = layers.Input(shape=input_shape)
    
    # Reshape untuk RNN
    x = layers.Permute((2, 1))(inputs)  # (max_len, n_mfcc)
    
    # Blok RNN kustom
    x = layers.LSTM(128, return_sequences=True)(x)
    x = layers.LSTM(64)(x)
    
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(64, activation='relu')(x)
    
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=inputs, outputs=outputs)
    return model

if __name__ == "__main__":
    model = build_audio_model()
    model.summary()