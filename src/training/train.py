import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tqdm import tqdm

from ..models.fusion_model import build_fusion_model
from ..utils import load_data

def train_model():
    """Latih model klasifikasi emosi"""
    # 1. Muat data
    print("Memuat data...")
    visual_data, audio_data, labels = load_data()
    
    # 2. Encode label emosi
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    
    # 3. Split data
    (X_visual_train, X_visual_val, 
     X_audio_train, X_audio_val, 
     y_train, y_val) = train_test_split(
        visual_data, audio_data, encoded_labels, 
        test_size=0.2, random_state=42
    )
    
    # 4. Bangun model fusion
    print("Membangun model...")
    fusion_model, _, _ = build_fusion_model(
        visual_shape=X_visual_train.shape[1:],
        audio_shape=X_audio_train.shape[1:]
    )
    
    # 5. Compile model
    fusion_model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # 6. Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=5, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=3
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath='../outputs/models/emotion_model_best.h5',
            save_best_only=True,
            monitor='val_loss'
        )
    ]
    
    # 7. Latih model
    print("Melatih model...")
    history = fusion_model.fit(
        {'visual_input': X_visual_train, 'audio_input': X_audio_train},
        y_train,
        validation_data=({'visual_input': X_visual_val, 'audio_input': X_audio_val}, y_val),
        epochs=30,
        batch_size=8,
        callbacks=callbacks
    )
    
    # 8. Simpan model akhir
    fusion_model.save('../outputs/models/emotion_model_final.h5')
    
    # 9. Evaluasi model
    print("\nEvaluasi model pada data validasi:")
    results = fusion_model.evaluate(
        {'visual_input': X_visual_val, 'audio_input': X_audio_val}, 
        y_val
    )
    
    # 10. Simpan label encoder
    np.save('../outputs/models/label_encoder_classes.npy', label_encoder.classes_)
    
    print("\nPelatihan selesai!")
    return fusion_model, history

if __name__ == "__main__":
    train_model()