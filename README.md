# Masai-Project - Titanic Module 2

## PartB Interpretations (Task 7-15)

### Task 7 - Stratified Split Justification
Survived is 38% minority. Used `stratify=y` in train_test_split (712 train, 179 test) to preserve same 38/62 ratio in both sets.

### Task 8 - Preprocessing Justification
Numeric: median imputer + StandardScaler. Categorical: most_frequent + OneHot with `handle_unknown="ignore"`. All inside Pipeline, fit only on X_train to avoid leakage.

### Task 9 - Decision Tree
Saved to `analytics/decision_tree.png` with `plot_tree(feature_names=get_feature_names_out(), class_names=["Died(0)","Survived(1)"])`

### Task 10 - ROC Curve
ROC with AUC for 3 models saved to `analytics/roc_curve.png`

### Task 11 - Imbalance Comparison
Baseline Prec 0.78 Rec 0.70, balanced Prec 0.75 Rec 0.78, SMOTE train-only Prec 0.74 Rec 0.80. SMOTE via ImbPipeline after preprocessor only train. Best balanced for F1, SMOTE for recall.

### Task 12 - GridSearchCV OOB
`RandomForest(oob_score=True)` required else no oob_score_. Best params 200 estimators depth 10 sqrt, OOB ~0.80 F1 ~0.77

### Task 13 - Regression & Heteroscedasticity
MAE 18.5 RMSE 38.2 R2 0.38 Adj 0.35. Residual fan shape => heteroscedasticity present.

### Task 14 - Final Recommendation
Classification vs regression separate scales not comparable. Deploy RandomForest tuned AUC 0.85 F1 0.75 highest, robust to outliers.

### Task 15 - Saved Pipeline
`best_titanic_pipeline.pkl` is full Pipeline joblib.dump contains imputer+encoder+scaler+estimator, reloadable on raw data.
