# Masai-Project - Titanic Survival Analysis
## Module 1 + Module 2 (Part A & Part B)

### Module 1 - EDA (01_eda.ipynb)

**Task 1-2: Dataset Overview**
- Original: `titanic.csv` 891 rows, 12 cols.
- Target `survived` imbalanced 38.38% survived vs 61.62% died.

**Task 3: Missing Values**
- `age` 19.86% (177), `cabin` 77.1% dropped, `embarked` 2 missing.
- Age imputed median (robust to skew), embarked imputed mode 'S'.

**Task 4: Duplicates & Data Types**
- No exact duplicates, `survived` cast int, `pclass` categorical.

**Task 5: Univariate & Bivariate**
- `sex`: female 74% survived vs male 18% -> strong predictor.
- `pclass`: 1st 63% survived vs 3rd 24% -> strong predictor.
- `fare` right skewed, `age` slightly right skewed.

**Task 6: Correlation**
- `fare` vs `pclass` negative -0.55, `sibsp` vs `parch` positive 0.41.

---

### Module 2 - Part A - Data Cleaning (titanic_cleaned.csv)

**Final Shape:** (889, 14) after cleaning.

**Outlier Handling:**
- `age`: IQR cap at 60, >60 capped.
- `fare`: IQR method, fare > 300 capped to 300 (kept as real luxury tickets but limited to avoid model bias).
- Justification: Z-score not used due to skew, IQR robust.

**Encoding:**
- `sex` binary 0/1, `embarked` one-hot later in pipeline (not in cleaned csv to avoid leakage).
- Kept raw `sex, embarked` in cleaned file for pipeline encoding.

**Feature Engineering:**
- `family_size = sibsp + parch + 1`, `is_alone = 1 if family_size==1 else 0`
- Justification: family_size shows 2-4 have higher survival.

**Saved File:**
- `analytics/titanic_cleaned.csv` is model-ready, no nulls in critical cols.

---

### Module 2 - Part B - Modeling (02_modelling.ipynb)

**Task 7: Stratified Split**
- Used `train_test_split(test_size=0.2, stratify=y, random_state=42)` -> Train 712 Test 179.
- Reason: Preserve 38/62 ratio, else recall unreliable.

**Task 8: Preprocessing Pipeline**
- Numeric `['age','fare','sibsp','parch','pclass']`: `SimpleImputer(median)` + `StandardScaler`
- Categorical `['sex','embarked']`: `SimpleImputer(most_frequent)` + `OneHotEncoder(handle_unknown='ignore')`
- Leakage prevention: Full ColumnTransformer inside Pipeline, fit() only on X_train.

**Task 9: Decision Tree**
- `max_depth=5` to avoid overfit, visualized with `plot_tree(feature_names=get_feature_names_out())`
- Saved `analytics/decision_tree.png`

**Task 10: ROC Comparison**
- Models: LogisticRegression, DecisionTree, RandomForest.
- RandomForest best AUC 0.85, saved `analytics/roc_curve.png`

**Task 11: Imbalance Handling**
- Original train 38.2% survived.
- Baseline RF Prec 0.78 Rec 0.70 F1 0.74
- `class_weight='balanced'` Prec 0.75 Rec 0.78 F1 0.76
- `SMOTE` (ImbPipeline, train-only after preprocessor) Prec 0.74 Rec 0.80 F1 0.77
- Conclusion: SMOTE applied only train to prevent leakage. Balanced improves F1, SMOTE best for recall.

**Task 12: GridSearchCV + OOB**
- `RandomForestClassifier(oob_score=True)` must be set at construction else AttributeError.
- Grid: `n_estimators [100,200], max_depth [5,10,None], max_features [sqrt, log2]`
- Best: 200, depth 10, sqrt. OOB ~0.80, CV F1 ~0.77.

**Task 13: Regression (fare)**
- X = pclass,sex,age,sibsp,parch,embarked, y=fare
- MAE 18.5 RMSE 38.2 R2 0.38 AdjR2 0.35
- Residual plot fan shape -> heteroscedasticity present, variance increases with fare, violates homoscedasticity assumption.
- Saved `analytics/residual_plot.png`

**Task 14: Final Recommendation**
- Classification vs regression metrics not comparable (F1 vs R2 different scales).
- For deployment: Tuned RandomForest (Task 12) with AUC 0.85 F1 0.75 best, handles non-linear sex*pclass interaction, robust to fare outliers vs Logistic.
- Regression keep separate, needs log-transform for heteroscedasticity.

**Task 15: Saved Pipeline**
- `joblib.dump(full_pipeline, "analytics/best_titanic_pipeline.pkl")` not bare estimator.
- Contains preprocessor + model, reloadable on raw data: `joblib.load(...).predict(X_test_raw[:5])`

**Artifacts:**
- `analytics/titanic_cleaned.csv`, `decision_tree.png`, `roc_curve.png`, `residual_plot.png`, `best_titanic_pipeline.pkl`
