*Dataset: [Mining process Data](https://www.kaggle.com/edumagalhaes/quality-prediction-in-a-mining-process)*

*Communtiy Author: [pixpack](https://github.com/pixpack)*

## Pre-requisites

Before you start make sure that you've:

1. Visited [Getting Started Guide](/info)
2. Visited [Getting Started with Cloud](/deployment/cloud)
3. Downloaded the dataset. You can get it from [Kaggle](https://www.kaggle.com/edumagalhaes/quality-prediction-in-a-mining-process).
4. Optional- Visual studio.

# Manufacturing process quality

Predicting process result quality is a common task in manufacturing analytics. Manufacturing plants commonly use quality predictions to gain a competitive edge over their competitors, improve their products or increase their customers satisfaction. **MindsDB** is a tool that can help you solve quality prediction tasks **easily** and **effectively** using machine learning. 
MindsDB abstracts ML models as virtual “AI Tables” in databases and you can make predictions just using normal SQL commands.

In this tutorial you will learn how to predict the quality of a mining process using **MindsDB**.

## Upload a file

1. Fix headers: 
   - `sed -e 's/ /_/g' -e 's/\(.*\)/\L\1/' -e 's/%_//g' MiningProcess_Flotation_Plant_Database.csv > fixed_headers.csv` (for Linux/Unix)
   - edit headers manually: change `space` to `underscore`, upper case to lower case, remove `%` from headers (for Windows)
2. Access MindsDB GUI on local via URL 127.0.0.1:47334/. 
3. If you are using MindsDB Cloud, make sure to add the file to a database and create a database connection to MindsDB's GUI. Cloud has a file size limit of 10MB, therefore for this dataset it would be best to either use MindsDB local instance or if on Cloud [connect via a database.](https://docs.mindsdb.com/sql/create/databases/)
4. Select the `Add data` button or the plug icon on the left side bar.
5. The page will navigate to the 'Select your data source' page. Select 'Files'.
6. Under 'Import a file' select the tab 'Click here to browse local files' and select your data file.
7. Once the file is uploaded 100%, provide a name for the data file that will be saved as a table.
8. Select the button Save and Continue.

You can query the file that has been uploaded to see that the data does pull through.

```sql
SELECT *
FROM files.file_name;
```

## Connect to MindsDB SQL Sever

MindsDB's GUI has a SQL Editor that allows you to create and train predictors and also makes predictions. However you can also do this via the mysql client in a local terminal by accessing MindsDB SQL Server.

1. 
```sql
mysql -h cloud.mindsdb.com --port 3306 -u username@email.com -p
```
2. 
```sql
USE mindsdb;
```

## Create a predictor

In this section you will connect to MindsDB with the MySql API and create a Predictor. It is in MindsDB terms a machine learning model, but all its complexity is automated and abstracted as a virtual “AI Table”. If you are an ML expert and want to tweak the model, MindsDB also allows you that (please refer to documentation).

Use the following query to create a Predictor that will foretell the silica_concentrate at the end of our mining process.
> The row number is limited to 5000 to speed up training but you can keep the whole dataset.

```sql
CREATE MODEL mindsdb.process_quality_predictor
FROM files (
    SELECT iron_feed, silica_feed, starch_flow, amina_flow, ore_pulp_flow,
           ore_pulp_ph, ore_pulp_density,flotation_column_01_air_flow,
           flotation_column_02_air_flow, flotation_column_03_air_flow,
           flotation_column_04_air_flow, flotation_column_05_air_flow,
           flotation_column_06_air_flow,flotation_column_07_air_flow,
           flotation_column_01_level, flotation_column_02_level,
           flotation_column_03_level, flotation_column_04_level,
           flotation_column_05_level, flotation_column_06_level, 
           flotation_column_07_level, iron_concentrate, silica_concentrate
    FROM process_quality
    LIMIT 5000
) PREDICT silica_concentrate;
```

On execution, we get:

```sql
Query OK, 0 rows affected (2 min 27.52 sec)
```

Now the Predictor will begin training. You can check the status with the following query.

```sql
SELECT *
FROM mindsdb.models
WHERE name='process_quality_predictor';
```

On execution, we get:

```sql
+-----------------------------+----------+----------+--------------------+-------------------+------------------+
| name                        | status   | accuracy | predict            | select_data_query | training_options |
+-----------------------------+----------+----------+--------------------+-------------------+------------------+
| process_quality_predictor   | complete | 1        | silica_concentrate |                   |                  |
+-----------------------------+----------+----------+--------------------+-------------------+------------------+
1 row in set (0.28 sec)
```

As you can see the accuracy of the model is 1 (i.e. 100%). This is the result of using a limited dataset of 5000 rows. In reality when using the whole dataset, you will probably see a more reasonable accuracy.

You are now done with creating the predictor! ✨

## Make predictions

In this section you will learn how to make predictions using your trained model.

To run a prediction against new or existing data, you can use the following query.

```sql
SELECT silica_concentrate, silica_concentrate_confidence, silica_concentrate_explain
FROM mindsdb.process_quality_predictor
WHERE iron_feed=48.81
AND silica_feed=25.31
AND starch_flow=2504.94
AND amina_flow=309.448
AND ore_pulp_flow=377.6511682692
AND ore_pulp_ph=10.0607
AND ore_pulp_density=1.68676;
```

On execution, we get:

```sql
+--------------------+-------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
| silica_concentrate | silica_concentrate_confidence | Info                                                                                                                                            |
+--------------------+-------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
| 1.68               | 0.99                          | {"predicted_value": "1.68", "confidence": 0.99, "confidence_lower_bound": null, "confidence_upper_bound": null, "anomaly": null, "truth": null} |
+--------------------+-------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.81 sec)
```

As you can see, the model predicted the `silica concentrate` for our data point. Again we can see a very high confidence due to the limited dataset. When making predictions you can include different fields. As you can notice, we have only included the first 7 fields of our dataset. You are free to test different combinations.

In the previous example, we have made a prediction for a single data point. In a real scenario, you might want to make predictions on multiple data points. In this case, MindsDB allows you to Join this other table with the Predictor. In result, you will get another table as an output with a predicted value as one of its columns.

Let’s see how to make batch predictions.

Use the following command to create the batch prediction.

```sql
SELECT 
    collected_data.iron_feed,
    collected_data.silica_feed,
    collected_data.starch_flow,
    collected_data.amina_flow,
    collected_data.ore_pulp_flow,
    collected_data.ore_pulp_ph,
    collected_data.ore_pulp_density,
    predictions.silica_concentrate_confidence AS confidence,
    predictions.silica_concentrate AS predicted_silica_concentrate
FROM process_quality_integration.process_quality AS collected_data
JOIN mindsdb.process_quality_predictor AS predictions
LIMIT 5;
```

As you can see below, the predictor has made multiple predictions for each data point in the `collected_data` table! You can also try selecting other fields to get more insight on the predictions. See the [JOIN clause documentation](https://docs.mindsdb.com/sql/api/join/) for more information.

```sql
+-----------+-------------+-------------+------------+---------------+-------------+------------------+------------+------------------------------+
| iron_feed | silica_feed | starch_flow | amina_flow | ore_pulp_flow | ore_pulp_ph | ore_pulp_density | confidence | predicted_silica_concentrate |
+-----------+-------------+-------------+------------+---------------+-------------+------------------+------------+------------------------------+
| 58.84     | 11.46       | 3277.34     | 564.209    | 403.242       | 9.88472     | 1.76297          | 0.99       | 2.129567174379606            |
| 58.84     | 11.46       | 3333.59     | 565.308    | 401.016       | 9.88543     | 1.76331          | 0.99       | 2.129548423407259            |
| 58.84     | 11.46       | 3400.39     | 565.674    | 399.551       | 9.88613     | 1.76366          | 0.99       | 2.130100408285386            |
| 58.84     | 11.46       | 3410.55     | 563.843    | 397.559       | 9.88684     | 1.764            | 0.99       | 2.1298757513510136           |
| 58.84     | 11.46       | 3408.98     | 559.57     | 401.719       | 9.88755     | 1.76434          | 0.99       | 2.130438907683961            |
+-----------+-------------+-------------+------------+---------------+-------------+------------------+------------+------------------------------+
```

## What's Next?

Have fun while trying it out yourself!

* Bookmark [MindsDB repository on GitHub](https://github.com/mindsdb/mindsdb).
* Sign up for a free [MindsDB account](https://cloud.mindsdb.com/register).
* Engage with the MindsDB community on [Slack](https://mindsdb.com/joincommunity) or [GitHub](https://github.com/mindsdb/mindsdb/discussions) to ask questions and share your ideas and thoughts.

If this tutorial was helpful, please give us a GitHub star [here](https://github.com/mindsdb/mindsdb).
