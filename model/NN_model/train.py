import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report
from model import NNModel
from dataset import Dataset
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import seaborn as sns
import matplotlib.pyplot as plt


## Hyperparameters
epochs = 100
lr=1e-4


# Load CSV
df = pd.read_csv('data_csv_out/data.csv')

# Example: assume target column is 'label'
X = df.drop(['weather_main', 'weather_desc'], axis=1).values
y = df['weather_main'].values

# Encode target if it's categorical
le = LabelEncoder()
y = le.fit_transform(y)

# Train-validation split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

train_ds = Dataset(X_train, y_train)
val_ds = Dataset(X_val, y_val)

train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=64)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f'Device: {device}')

model = NNModel(input_dim=X.shape[1], output_dim=3).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

###############################################################################################

for epoch in range(epochs):
    model.train()
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)

        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()

    # Validation accuracy
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            outputs = model(X_batch)
            _, predicted = torch.max(outputs, 1)
            total += y_batch.size(0)
            correct += (predicted == y_batch).sum().item()

    acc = correct / total
    if (epoch+1)%20 == 0:
        print(f'Epoch {epoch+1}, Loss: {loss.item():.4f}, Val Accuracy: {acc:.4f}')



# Get predictions
model.eval()
all_preds, all_labels = [], []
with torch.no_grad():
    for X_batch, y_batch in val_loader:
        X_batch = X_batch.to(device)
        outputs = model(X_batch)
        _, predicted = torch.max(outputs, 1)
        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(y_batch.numpy())

# print(classification_report(all_labels, all_preds, target_names=le.classes_))


# # Compute confusion matrix
# cm = confusion_matrix(all_labels, all_preds)

# # Optionally, use label names
# labels = le.classes_ if 'le' in locals() else [str(i) for i in range(3)]

# # Print numeric confusion matrix
# print("Confusion Matrix:\n", cm)

# # Plot heatmap
# plt.figure(figsize=(6, 4))
# sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
# plt.xlabel('Predicted')
# plt.ylabel('True')
# plt.title('Confusion Matrix')
# plt.show()
