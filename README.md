# Visibility Nowcasting

Visibility Nowcasting is a research codebase for predicting Korean regional visibility conditions from meteorological and air-pollution observations. The workflow merges ASOS weather data with DataOn air-quality data, handles severe class imbalance with SMOTENC and CTGAN sampling, trains multiple regional models, and evaluates/ensembles the best candidates with a CSI-focused objective.

## Publication

This repository accompanies the published visibility-nowcasting article:

- **Paper:** [Visibility nowcasting in South Korea: a machine learning approach to class imbalance and distribution shift](https://link.springer.com/article/10.1007/s00704-026-06219-6)
- **DOI:** [10.1007/s00704-026-06219-6](https://doi.org/10.1007/s00704-026-06219-6)
- **Journal:** Theoretical and Applied Climatology, Volume 157, Article 283 (2026)
- **Published:** 10 April 2026
- **Code:** [GitHub repository](https://github.com/singbong/Visibility_Nowcasting)

## What this repository contains

- Data-preparation notebooks for weather/air-pollution merging and train/test creation.
- Oversampling scripts for SMOTE-only, CTGAN-only, and SMOTENC+CTGAN datasets.
- Region-specific model optimization/training scripts for LightGBM, XGBoost, ResNet-like, FT-Transformer, and DeepGBM models.
- Reusable model, prediction, ensemble, and SHAP-analysis utilities.
- CSV summaries of hyperparameter optimization and ensemble-validation results.

Large input data and trained model artifacts are intentionally kept outside the repository. See [Data and model artifacts](#data-and-model-artifacts).

## Repository layout

```text
.
├── README.md
└── Analysis_code/
    ├── 1.data_preprocessing/        # Data merge and train/test notebook workflow
    ├── 2.make_oversample_data/      # SMOTE, CTGAN, and SMOTENC+CTGAN sampling scripts
    │   ├── only_ctgan/
    │   ├── smote_only/
    │   └── smotenc_ctgan/
    ├── 3.sampled_data_analysis/     # Sampling-analysis notebooks, plots, and hyperparameter CSVs
    ├── 4.oversampling_data_test/    # Oversampled-data model test notebooks
    ├── 5.optima/                    # Per-model/per-region optimization and training scripts
    │   ├── lgb_*                    # LightGBM scripts
    │   ├── xgb_*                    # XGBoost scripts
    │   ├── resnet_like_*            # ResNet-like tabular neural network scripts
    │   ├── ft_transformer_*         # FT-Transformer scripts
    │   ├── deepgbm_*                # DeepGBM scripts
    │   └── run_bash/                # Batch runners for major model/sample combinations
    ├── 6.optima_models_analysis/    # Optimization result extraction and best-model CSV summaries
    ├── 7.ensemble/                  # Validation/test ensembling and SHAP analysis
    │   ├── model_utils/             # Prediction, preprocessing, tree, and DL helper APIs
    │   └── shap_analysis/           # Tree/DL SHAP analyzers and statistical calculators
    ├── baseline_model_analysis/     # Baseline model notebooks and summary tables
    ├── models/                      # PyTorch model definitions
    └── optimization_history/        # Stored optimization histories included in this checkout
```

Expected external artifact folders when running the full workflow:

```text
data/
├── ASOS/
├── dataon/
├── data_for_modeling/
└── data_oversampled/

Analysis_code/save_model/
├── lgb_optima/
├── xgb_optima/
├── resnet_like_optima/
├── ft_transformer_optima/
└── deepgbm_optima/
```

## Data and model artifacts

The full `data/` and `save_model/` directories are large and are not committed here. They can be retrieved from the Hugging Face repository:

```bash
git clone https://huggingface.co/bong9513/visibility_prediction
```

After cloning, copy artifacts into this repository as needed:

```bash
# From the cloned Hugging Face repository
cp -R visibility_prediction/data ./data
cp -R visibility_prediction/save_model ./Analysis_code/save_model

# Optional, if you want to replace or supplement optimization histories
cp -R visibility_prediction/optimization_history ./Analysis_code/optimization_history
```

## Environment

The project was developed in the Docker image `teddylee777/deepko:preview`, which is expected to include the core Python/GPU stack used by the notebooks and scripts.

```bash
# Pull the image
docker pull teddylee777/deepko:preview

# GPU container
docker run --gpus all -it -v "$(pwd):/workspace/Visibility_Nowcasting" teddylee777/deepko:preview

# CPU-only container
docker run -it -v "$(pwd):/workspace/Visibility_Nowcasting" teddylee777/deepko:preview
```

Primary dependencies used across the codebase include:

- Python 3.8+
- pandas, numpy, scipy
- scikit-learn, imbalanced-learn
- LightGBM, XGBoost
- PyTorch
- CTGAN
- Optuna, hyperopt
- SHAP, statsmodels
- matplotlib, seaborn
- joblib

No `requirements.txt` or lockfile is currently provided, so the Docker image is the recommended environment.

## End-to-end workflow

### 1. Prepare modeling data

Run the preprocessing notebooks in order:

1. `Analysis_code/1.data_preprocessing/0.air_data_merge.ipynb`
2. `Analysis_code/1.data_preprocessing/1.data_merge.ipynb`
3. `Analysis_code/1.data_preprocessing/3.make_train_test.ipynb`

These notebooks produce region-level modeling datasets such as `seoul_train.csv` and `seoul_test.csv` under `data/data_for_modeling/`.

### 2. Generate oversampled datasets

From the repository root:

```bash
cd Analysis_code/2.make_oversample_data

# SMOTE/SMOTENC-only data
python3 smote_only/smote_sample_1.py

# CTGAN-only data
python3 only_ctgan/ctgan_sample_10000_1.py

# SMOTENC followed by CTGAN
python3 smotenc_ctgan/smotenc_ctgan_sample_10000_1.py
```

Scripts are split by fold/sample size. Available CTGAN sample-size families include `7000`, `10000`, and `20000` variants.

### 3. Train and optimize models

Training scripts live under `Analysis_code/5.optima/` and are organized by model family, data sample, and region.

Examples:

```bash
cd Analysis_code/5.optima

# Tree models
python3 lgb_smote/LGB_smote_seoul.py
python3 xgb_smote/XGB_smote_seoul.py

# Deep tabular models
python3 resnet_like_smote/resnet_like_smote_seoul.py
python3 ft_transformer_ctgan10000/ft_transformer_ctgan10000_seoul.py
python3 deepgbm_smotenc_ctgan10000/deepgbm_smotenc_ctgan10000_seoul.py
```

Batch runners are available in `run_bash/` when working from `Analysis_code/5.optima/`, for example:

```bash
bash run_bash/xgb/run_xgb_smote.sh
bash run_bash/resnet_like/run_resnet_like_ctgan10000.sh
```

Supported regions are `seoul`, `incheon`, `busan`, `daegu`, `daejeon`, and `gwangju`.

### 4. Analyze optimized models

Use the notebook and CSVs in `Analysis_code/6.optima_models_analysis/` to review model/sample/region optimization results:

- `optimization_result.csv`
- `best_params_lgb.csv`
- `best_params_xgb.csv`
- `best_params_resnet_like.csv`
- `best_params_ft_transformer.csv`
- `best_params_deepgbm.csv`
- `best_samples_best_datasample_per_model_per_region_sorted.csv`

### 5. Ensemble and explain predictions

Main ensemble notebooks:

- `Analysis_code/7.ensemble/7-1.ensemble_for_vali.ipynb`
- `Analysis_code/7.ensemble/7-2.ensemble_for_test.ipynb`
- `Analysis_code/7.ensemble/7-3.analysis_of_shap.ipynb`

Reusable APIs are provided under `Analysis_code/7.ensemble/model_utils/` and `Analysis_code/7.ensemble/shap_analysis/`. Key entry points include `Analysis_code/7.ensemble/model_utils/predict_api.py` for prediction probabilities and `Analysis_code/7.ensemble/shap_analysis/api.py` for SHAP/statistical analysis wrappers.

Example prediction API usage from inside `Analysis_code/7.ensemble/`:

```python
from model_utils.predict_api import predict_test_proba, predict_val_proba

probs, y_test = predict_test_proba(
    model_name="xgb",
    region="seoul",
    data_sample="smote",
    device="cpu",
)

val_probs, val_pred, val_true = predict_val_proba(
    model_name="ft_transformer",
    region="seoul",
    data_sample="ctgan10000",
    device="cuda",
)
```

Example SHAP API usage:

```python
from shap_analysis.api import analyze_shap_values_across_folds, analyze_dl_model_shap

# Tree model SHAP
result = analyze_shap_values_across_folds(
    model_name="xgb",
    region="seoul",
    data_sample="smote",
)

# Deep learning model SHAP
result = analyze_dl_model_shap(
    model_name="resnet_like",
    region="seoul",
    data_sample="ctgan10000",
    device="cuda",
)
```

## Modeling details

### Target labels

- `visi`: continuous visibility value.
- `multi_class`: three-class target label.
- `binary_class`: binary helper label, recalculated as `0 if multi_class == 2 else 1` in sampling/training workflows.

Synthetic-sample filtering rules used in the oversampling scripts include:

- Class `0`: `0 <= visi < 100`
- Class `1`: `100 <= visi < 500`
- Class `2`: remaining/high-visibility range used as the majority class

### Feature groups

Main feature groups used by the modeling utilities:

- Meteorology: `temp_C`, `precip_mm`, `wind_speed`, `wind_dir`, `hm`, `vap_pressure`, `dewpoint_C`, `loc_pressure`, `sea_pressure`, `solarRad`, `snow_cm`, `cloudcover`, `lm_cloudcover`, `low_cloudbase`, `groundtemp`
- Air pollution: `O3`, `NO2`, `PM10`, `PM25`
- Time: `year`, `month`, `hour`, `hour_sin`, `hour_cos`, `month_sin`, `month_cos`
- Derived: `ground_temp - temp_C`

Preprocessing expectations:

- `wind_dir == '정온'` is converted to `0` before integer casting.
- `year`, `month`, `hour`, `wind_dir`, `cloudcover`, and `lm_cloudcover` are treated as categorical/integer features where appropriate.
- Deep-learning workflows apply per-fold scaling and categorical handling through stored scalers and helper utilities.

### Model families

- **LightGBM**: multiclass one-vs-all objective with custom CSI metric and Hyperopt search.
- **XGBoost**: multiclass probability output with custom CSI evaluation and Hyperopt search.
- **ResNet-like**: residual MLP for mixed numerical/categorical tabular features.
- **FT-Transformer**: transformer encoder over tabular tokens.
- **DeepGBM**: neural tabular model combining numerical projection and categorical embeddings.

## Evaluation

The primary optimization metric is Critical Success Index (CSI). In this project, the multiclass CSI helper computes:

```python
H = cm[0, 0] + cm[1, 1]
F = cm[1, 0] + cm[2, 0] + cm[0, 1] + cm[2, 1]
M = cm[0, 2] + cm[1, 2]
CSI = H / (H + F + M + 1e-10)
```

Common validation strategy:

- Fold 1: train on 2018-2019, validate on 2020
- Fold 2: train on 2018 and 2020, validate on 2019
- Fold 3: train on 2019-2020, validate on 2018
- Test year: 2021

Additional reporting includes accuracy, F1, probability ensembles, entropy/uncertainty calculations, Wasserstein-distance comparisons, and SHAP-based feature attribution.

## Reproducibility notes

- Most model/sampling scripts use `random_state=42` or equivalent PyTorch seed setup.
- GPU, CUDA, LightGBM, XGBoost, and PyTorch versions can affect exact reproducibility.
- Relative paths are common in the scripts; run commands from the directory shown in each section.
- Long-running scripts save models under `Analysis_code/save_model/` and optimization histories under `Analysis_code/optimization_history/`.

## Troubleshooting

- **Missing data/model files**: download the Hugging Face artifacts and copy `data/` plus `save_model/` into the expected paths.
- **Relative-path errors**: run scripts from `Analysis_code/2.make_oversample_data/`, `Analysis_code/5.optima/`, or `Analysis_code/7.ensemble/` as documented above.
- **GPU not detected**: start Docker with `--gpus all` and verify CUDA availability inside the container.
- **Model loading errors**: ensure model artifact names match the pattern used by the utilities, e.g. `Analysis_code/save_model/xgb_optima/xgb_smote_seoul.pkl`.
- **Large memory usage**: DataOn and CTGAN workflows can be memory intensive; run by region/fold and prefer the Docker/GPU environment.
