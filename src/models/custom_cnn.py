"""
Model CNN dari nol untuk fitur visual
"""
import tensorflow as tf
from tensorflow.keras import layers, Model

def build_visual_model(input_shape=(30, 224, 224, 3), num_classes=8):
    # Input layer
    inputs = layers.Input(shape=input_shape)
    
    # Reshape untuk menggabungkan batch dan frame
    x = layers.Reshape((input_shape[0] * input_shape[1], input_shape[2], input_shape[3]))(inputs)
    
    # Blok CNN kustom
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    x = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    # Global pooling dan fully connected layers
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    
    # Output layer
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=inputs, outputs=outputs)
    return model

if __name__ == "__main__":
    model = build_visual_model()
    model.summary()