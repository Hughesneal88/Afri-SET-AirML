## Notes

What is the Project.
Improving Low-Cost Sensor Prediction




5m 50.8s
Just now



``` {'best_params': {'mlpregressor__solver': 'adam',
  'mlpregressor__hidden_layer_sizes': (128,),
  'mlpregressor__batch_size': 64,
  'mlpregressor__alpha': 0.01,
  'mlpregressor__activation': 'tanh'}}

  'estimator': Pipeline(steps=[('standardscaler', StandardScaler()),
                 ('mlpregressor',
                  MLPRegressor(activation='tanh', alpha=0.01, batch_size=64,
                               early_stopping=True, hidden_layer_sizes=(128,),
                               max_iter=1000, random_state=42))]),
```
Presence = 80.603055


### Benchmark

```
R2: 0.5580772524685484
MAE: 6.221306418683423
RMSE: 8.916936249589217
```


### Random Forest Regressor Model

**R2:** `0.90`

**MAE:** `1.90`

**RMSE:** `4.34`




` replace missing data using mean or rh and temp to pm2.5 calc `

add the maximum for each month and each hour


Parameters : ['pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week', 'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction', 'is_harmattan_month', 'harmattan_score', 'is_harmattan']

## TODO

1. * Daily, Monthly, Seasonal, Annual *
2. * Correlate other parameters *



