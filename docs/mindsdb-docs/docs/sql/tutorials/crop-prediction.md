# Crop Recomendation

*Dataset: [Crop recomendation Data](https://www.kaggle.com/atharvaingle/crop-recommendation-dataset)*

*Communtiy Author: [pixpack](https://github.com/pixpack)*

Modern agriculture is becoming very dependent on technology. From advanced machinery to specially selected crops. All the technology produces a lot of data that can be used for better adjustment of the farming process. One use case of machine learning in agriculture could be the selection of the best crop for a specific field to maximize the potential yield. Such problems are often called *Classification Problems* in machine learning. With **MindsDB** you can easily make automated machine learning predictions straight from your existing database. Even without advanced ML engineering skills, you can start leveraging predictive models that help you make better business decisions.

In this tutorial, you will learn how to predict the best crop type based on field parameters using **MindsDB**.

## Pre-requisites

Before you start make sure you have:

1. Access to MindsDB. In this tutorial, we will use [MindsDB Cloud GUI](https://cloud.mindsdb.com/). If you want you can also deploy mindsdb on your premises, Check out the installation guide for [Docker](https://docs.mindsdb.com/setup/self-hosted/docker/) or [PyPi](https://docs.mindsdb.com/setup/self-hosted/pip/windows/). 

2. Downloaded the dataset. You can get it from [Kaggle](https://www.kaggle.com/atharvaingle/crop-recommendation-dataset).

## Add your file to MindsDB

MindsDB can integrates with many databases, in most scenarios your data will be stored in a database, if you decide to load this dataset into your database of choice, please follow instructions here as to how to connect mindsdb to your [database.](https://docs.mindsdb.com/sql/create/databases/)

In this tutorial, we will be adding the dataset directly to MindsDB's GUI. For this example [MindsDB Cloud GUI](https://cloud.mindsdb.com/) will be used.If you need to create an account you can find the guide on how to do it [here](https://docs.mindsdb.com/setup/cloud/).
Alternatively, you can also use MindsDB's local deployment and access the GUI in your browser with [127.0.0.1:47334](https://127.0.0.1:47334).

**The first step will be to access MindsDB cloud where we will also make use of the SQL Editor:**

 - Once you are logged onto the Cloud GUI,navigate to either the `Add Data` button or the plug icon on the left side bar to select it.
 - The screen will navigate to the `Select your datasource` page, select the option Files.
 
 ![datasource](/assets/tutorials/crops/database.png)
 
 - Select Import Files.
 
 ![selectfromsource](/assets/tutorials/crops/select_datasource.png)
 
 - Click on `Import a File` to select your dataset from your local drive. Your dataset should be a maximum size of 10MB.
 - Under `Table name` type in the name you would like to give your dataset which will be stored in MindsDB files.
 
 Once the dataset has been successfully uploaded into a table, you can query the dataset directly from the table.
 
 In the SQL Editor,type in the following syntax and select the button `Run` or Shift+Enter to execute the code:
 
 ```sql
 SELECT *
 FROM files.crops;
 ```
![file_select](/assets/tutorials/crops/selectfromfiles.png)

This confirms that the dataset has been successfully uploaded with all its rows.

# Create a predictor

Now we can create a machine learning model with `crops` columns serving as features, and MindsDB takes care of the rest of the ML workflow automatically. There is a way to get your hands into the insides of the model to fine tune it, but we will not cover it in this tutorial.


In the SQL Editor, type in the below syntax to create and train a machine learning predictive model:

```sql
CREATE MODEL crop_predictor
FROM files
    (SELECT * FROM crops)
PREDICT label;
```

Select the button `Run` or Shift+Enter to execute the code. If the predictor is successfully created the console will display a message `Query successfully completed`.

![create_predictor](/assets/tutorials/crops/createcropspredictor.png)

Now the predictor will begin training. You can check the status of the predictor with the following query.

```sql
SELECT *
FROM mindsdb.models
WHERE name='crop_predictor';
```

After the predictor has finished training, you will see a similar output. Note that MindsDB does model testing for you automatically, so you will immediately see if the predictor is accurate enough.

![statuscheck](/assets/tutorials/crops/statuscheck.png)

You are now done with creating the predictor! ✨

## Make predictions

In this section you will learn how to make predictions using your trained model.

To run a prediction against new or existing data, you can use the following query.

```sql
SELECT label
FROM mindsdb.crop_predictor
WHERE N = 77
AND P = 52
AND K = 17
AND temperature = 24
AND humidity = 20.74
AND ph = 5.71
AND rainfall = 75.82;
```

![statuscheck](/assets/tutorials/crops/cropprediction.png)

As we have used a real data point from our dataset we can verify the prediction.
```text
N,  P,  K,  temperature,  humidity,   ph,           rainfall,     label
77, 52, 17, 24.86374934,  65.7420046, 5.714799723,  75.82270467,  maize
```
 
As you can see, the model correctly predicted the most appropriate crop type for our field.

OK, we made a prediction using a single query, but what if you want to make a batch prediction for a large set of data in your database? In this case, MindsDB allows you to Join this other table with the Predictor. In result, you will get another table as an output with a predicted value as one of its columns.

Let’s see how it works.

Use the following command to create the batch prediction and execute with the `Run` button.

```sql
SELECT
    collected_data.N,
    collected_data.P,
    collected_data.K,
    collected_data.temperature,
    collected_data.humidity,
    collected_data.ph,
    collected_data.rainfall,
    predictions.label AS predicted_crop_type
FROM crops_integration.crops AS collected_data
JOIN mindsdb.crop_predictor AS predictions
LIMIT 5;
```

As you can see below, the predictor has made multiple predictions for each data point in the `collected_data` table. You can also try selecting other fields to get more insight on the predictions. See the [JOIN clause documentation](https://docs.mindsdb.com/sql/api/join/) for more information.

![2ndprediction](/assets/tutorials/crops/2ndprediction.png)

You are now done with the tutorial! 🎉

Please feel free to try it yourself. Sign up for a [free MindsDB account](https://cloud.mindsdb.com/signup?utm_medium=community&utm_source=ext.%20blogs&utm_campaign=blog-crop-detection) to get up and running in 5 minutes, and if you need any help, feel free to ask in [Slack](https://join.slack.com/t/mindsdbcommunity/shared_invite/zt-o8mrmx3l-5ai~5H66s6wlxFfBMVI6wQ) or [Github](https://github.com/mindsdb/mindsdb/discussions).

For more check out other [tutorials and MindsDB documentation](https://docs.mindsdb.com/).
