import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models

# 1. Define Paths and Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_SAVE_DIR = os.path.join(BASE_DIR, "models")
MODEL_SAVE_PATH = os.path.join(MODEL_SAVE_DIR, "tomato_disease_model.keras")

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10  # You can increase this (e.g., 15 or 20) for better accuracy

def train_model():
    # Ensure the dataset directory exists
    if not os.path.exists(DATASET_DIR):
        print(f"❌ Error: 'dataset' folder not found at {DATASET_DIR}")
        print("Please create a 'dataset/' folder containing subfolders for each disease class.")
        return

    # Ensure models directory exists
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    print("🔄 Loading and preparing dataset with Augmentation...")
    
    # 2. Data Augmentation & Splitting (80% Train, 20% Validation)
    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        validation_split=0.2  # 20% used for checking validation accuracy
    )

    train_generator = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )

    val_generator = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )

    num_classes = len(train_generator.class_indices)
    print(f"📊 Detected Classes: {train_generator.class_indices}")
    
    if num_classes != 4:
        print(f"⚠️ Warning: Expected 4 classes, but found {num_classes}. Check your dataset folder structures.")

    print("🏗️ Building deep learning model architecture using MobileNetV2...")
    
    # 3. Build Model (Transfer Learning via MobileNetV2)
    base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    base_model.trainable = False  # Freeze the pre-trained weights

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.summary()

    # 4. Train the Neural Network
    print(f"🚀 Starting training for {EPOCHS} epochs... Please wait.")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS
    )

    # 5. Save the trained weight file
    print(f"💾 Saving trained model asset to: {MODEL_SAVE_PATH}")
    model.save(MODEL_SAVE_PATH)
    print("✅ Model training complete! You are ready to launch your application.")

if __name__ == "__main__":
    train_model()