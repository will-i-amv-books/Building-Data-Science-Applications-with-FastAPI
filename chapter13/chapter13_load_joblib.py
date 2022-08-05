import os
from typing import List, Tuple
import joblib
from sklearn.pipeline import Pipeline


# Load the model
parent_folder = os.path.dirname(__file__)
filename = "newsgroups_model.joblib"
model_file = os.path.join(parent_folder, filename)
loaded_model: Tuple[Pipeline, List[str]] = joblib.load(model_file)
model, targets = loaded_model

# Run a prediction
p = model.predict(["computer cpu memory ram"])
print(f'Predicted topic is: {targets[p[0]]}')
