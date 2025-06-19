from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE


# Load CSV
df = pd.read_csv('data_csv_out/data.csv')

# Example: assume target column is 'label'
# X = df.drop(['weather_main', 'weather_desc'], axis=1).values
# y = df['weather_main'].values

X = df.drop(['weather_main', 'weather_desc'], axis=1)  # ← KEEP as DataFrame
y = df['weather_main']

# Encode target if it's categorical
le = LabelEncoder()
y = le.fit_transform(y)

# Train-validation split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# Convert back to DataFrame
X_train = pd.DataFrame(X_train, columns=X.columns)
y_train = pd.Series(y_train)


models = [RandomForestClassifier(), 
          GradientBoostingClassifier(),
          DecisionTreeClassifier(),
          xgb.XGBClassifier(),
          ]

models_name = [
    "Random Forest",
    "Random Forest with FS",
    "Gradient Boosting",
    "Gradient Boosting with FS",
    "Decision Tree",
    "Decision Tree with FS",
    "XGBoost",
    "XGBoost with FS"
]


accu = []
for i in range(len(models)):
    model = models[i]
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    accu.append(accuracy)
    print(f'{models_name[i*2]} accuracy: {accuracy}')


    importances = model.feature_importances_
    feat_importances = pd.Series(importances, index=X.columns)
    top_features = feat_importances.sort_values(ascending=False).head(10).index
    X_train_selected = X_train[top_features]
    X_test_selected = X_val[top_features]
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    accu.append(accuracy)
    print(f'{models_name[2*i + 1]} accuracy: {accuracy}')

max_idx = accu.index(max(accu))
print(f'Best ML model: {models_name[max_idx]}')
