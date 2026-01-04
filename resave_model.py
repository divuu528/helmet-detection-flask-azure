import tensorflow as tf

# Load existing model
model = tf.keras.models.load_model("helmet_model.keras", compile=False)

# Re-save with TF 2.17 compatible metadata
model.save("helmet_model_tf217.keras")

print("✅ Model re-saved successfully as helmet_model_tf217.keras")
