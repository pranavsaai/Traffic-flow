import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder,LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE

df = pd.read_csv(r'/content/gretel_generated_table_2024-08-30-05-03-41.csv')
df.head()

df.drop('timestamp' , axis = 1 , inplace = True)

df.head()

X = df.drop('congestion_level', axis=1)
y = df['congestion_level']

num_features = ['vehicle_count', 'traffic_volume', 'temperature', 'humidity', 'precipitation','accident_count','hour']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X[num_features])

cat_features = ['weather_condition', 'road_type']
encoder=OneHotEncoder(handle_unknown='ignore')
X_encoded = encoder.fit_transform(X[cat_features])


X_encoded_dense = X_encoded.toarray()

X_preprocessed = np.c_[X_scaled, X_encoded_dense]


le=LabelEncoder()

y_encoded = le.fit_transform(y)

print(X_preprocessed.shape)

X_train, X_test, y_train, y_test = train_test_split(X_preprocessed, y_encoded, test_size=0.3, random_state=42)

print(X_train.shape)

from sklearn.ensemble import GradientBoostingClassifier
gb = GradientBoostingClassifier(random_state=42)
gb.fit(X_train, y_train)


y_pred = gb.predict(X_test)
accuracy = accuracy_score(y_test,y_pred)
print(f"Accuracy: {accuracy}")

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train_res, y_train_res)

y_pred_rf = rf_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred_rf)
print(f"Accuracy: {accuracy}")
print(classification_report(y_test, y_pred_rf))

from xgboost import XGBClassifier

model = XGBClassifier()
model.fit(X_train , y_train)
train_predictions = model.predict(X_train)

print(f'Training Accuracy : {accuracy_score(train_predictions , y_train)}')

predictions = model.predict(X_test)
print(f'Testing Accuracy : {accuracy_score(predictions , y_test)}')

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0],
    'gamma': [0, 0.1, 0.2]
}

grid_search = GridSearchCV(estimator=model,
                           param_grid=param_grid,
                           scoring='accuracy',
                           cv=5,
                           verbose=2,
                           n_jobs=-1)

grid_search.fit(X_train, y_train)

best_params = grid_search.best_params_
best_model = grid_search.best_estimator_

print("Best Parameters:", best_params)

y_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Test Accuracy: {accuracy * 100:.2f}%")

congestion_levels = le.inverse_transform(y_pred)

unique_congestion_levels = np.unique(congestion_levels)
unique_congestion_levels

def route_suggestion(predicted_level):
    if predicted_level == 'Low':
        return "Suggested: Take the route."
    elif predicted_level == 'Moderate':
        return "Caution: Consider taking the route."
    elif predicted_level == 'High':
        return "Warning: Consider alternative routes."
    elif predicted_level == 'Severe':
        return "Avoid: Find an alternative route."

suggestions = [route_suggestion(level) for level in congestion_levels]

output_df = pd.DataFrame({'Predicted Congestion Level': congestion_levels, 'Route Suggestion': suggestions})
output_df.head(10)
