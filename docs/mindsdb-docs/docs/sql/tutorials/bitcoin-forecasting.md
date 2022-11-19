# Forecast Bitcoin price using MindsDB

*Level: Easy*  
*Dataset: [Coinbase 2017-2018 Bitcoin data](https://www.kaggle.com/gorgia/Bitcoin-markets?select=btc_usd_Coinbase.csv)*

Bitcoin is a digital currency that uses blockchain technology, Bitcoin can be sent from user to user on the peer-to-peer Bitcoin network without the need for intermediaries. Note that this is just a task for fun so use it at your own risk.

In this tutorial, you will learn how to forecast Bitcoin using MindsDB. And all you need to know is just SQL. Behind the scenes, MindsDB will create the complete machine learning workflow, like determine, normalize & encode the data, train & test the model, etc. But we don’t need to bother with all this complexity. Of course, if you want to, you can tune things manually inside MindsDB with a declarative syntax called JSON-AI, but we will not cover it in this article.

DISCLAIMER: Please note that predicting Bitcoin price is just an example for showing MindsDB technology and you are solely responsible for any results you may get in real life, if you use this information for real trading purposes. Please note, that you can also follow this tutorial with other data you have.

## Pre-requisites

First, you need MindsDB installed. If you want to use MindsDB locally, you need to install MindsDB with
[Docker](https://docs.mindsdb.com/setup/self-hosted/docker/) or [Python](https://docs.mindsdb.com/setup/self-hosted/pip/windows/). 
However, if you want to use MindsDB without installing it locally, you can use [Cloud Mindsdb](https://cloud.mindsdb.com/signup). 
In this tutorial, I'm using MindsDB Cloud, because it is easy to set up in just 2 minutes and it has a great free tier.

Second, you need a MySQL client to connect to MindsDB MYSQL API.

## Connect your database

You must first connect MindsDB to the database where the record is stored. 
In the left navigation, click  Database, click  ADD DATABASE. 
And you must provide all the necessary parameters to connect to the database.

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/add-database-cloud-mindsdb-sql.png)

* Supported Database - select the database that you want to connect to
* Integrations Name - add a name to the integration, here I'm using 'mysql' but you can name it as you like
* Database - the database name
* Host - database hostname
* Port - database port
* Username - database user
* Password - user's password

Then, click on CONNECT.  
The next step is to use the MySQL client to connect to MindsDB’s MySQL API, train a new model, and make a prediction.

## Connect to MindsDB’s MySQL API

In this tutorial I'm using MySQL command-line client, but you can also follow up with the one that works the best for you, like Dbeaver.  
The first step is to use the MindsDB Cloud user to connect to the MindsDB MySQL API, using this command:

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/connect-mindsdb-sql.png)

You need to specify the hostname and user name explicitly, as well as a password for connecting. Click enter and you are connected to MindsDB API.

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/success-connect-sql.png)

If you have an authentication error, please make sure you are providing the email address you have used to create an account on MindsDB Cloud.

## Data

Now, let's show the databases.

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/show-databases-sql.png)

There are 4 databases, and the MySQL database is the database that I've connected to MindsDB.

Let's check the MySQL database.

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/show-tables-sql.png)

There are 3 tables, and in this tutorial, we will use the Bitcoin table.  
And let's check what is inside this table.

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/show-bitcoin-table.png)

These tables have 5 columns: date, open price, the highest price of the day, lowest price of the day, and close price. 
The column we want to forecast is close price.


## Create the model

Now, to create the model let's move to MindsDB database. and let's see what's inside.

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/show-tables-sql-2.png)

There are 2 tables, predictors, and commands. Predictors contain your predictors record, and commands contain your last commands used.  
To train a new machine learning model we will need to `CREATE MODEL` as a new record inside the predictors table, and using this command:

```sql
CREATE MODEL mindsdb.predictor_name
FROM integration_name
(SELECT column_name, column_name2 FROM table_name) as ds_name
PREDICT column_target as column_alias
ORDER BY column_orderby
WINDOW num_window
HORIZON num_horizon
USING {"is_timeseries": "Yes"}
```

The values that we need to provide are:

* predictor_name (string) - The name of the model.
* integration_name (string) - The name of the connection to your database.
* ds_name (string) - the name of the dataset you want to create, it's optional if you don't specify this value MindsDB will generate by itself.
* column_target (string) - The feature you want to predict.
* column_alias - Alias name of the feature you want to predict.
* column_orderby - The column to order the data, for time series this should be the date/time column.
* num_window - keyword specifies the number of rows to "look back" into when making a prediction after the rows are ordered by the order_by column and split into groups. 
This could be used to specify something like "Always use the previous 10 rows".
* num_horizon - keyword specifies the number of future predictions. 

So, use this command to create the models:

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/create-predictor-bitcoin-sql.png)

If there's no error, that means your model is created and training. To see if your model is finished, use this command:

```sql
SELECT * 
FROM mindsdb.models 
WHERE name = predictor_name;
```

And values that we need to provide are:

* predictor_name (string) - The name of the model.

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/show-predictor-bitcoin-sql.png)

If the model is finished, it will look like this. The model has been created! and the accuracy is 99%!

## Create the prediction

Now you are in the last step of this tutorial, creating the prediction. To create a prediction you can use this command:

```sql
SELECT target_variable, target_variable_explain FROM model_table 
WHERE when_data={"column3": "value", "column2": "value"};
```

And you need to set these values:
- target_variable - The original value of the target variable.
- target_variable_confidence - Model confidence score.
- target_variable_explain - JSON object that contains additional information as confidence_lower_bound, confidence_upper_bound, anomaly, truth.
- when_data - The data to make the predictions from(WHERE clause params).

![](https://github.com/kinkusuma/mindsdb/blob/add-regression-tutorial-sql/docs/mindsdb-docs/docs/assets/sql/tutorials/insurance-cost-prediction/create-prediction-bitcoin-sql.png)

Finally, we have created a Bitcoin forecasting model using SQL and MindsDB. Yayyy!

## Conclusions

As you can see it is very easy to start making predictions with machine learning even without being a data scientist! Feel free to check this yourself! MindsDB [free cloud account](https://cloud.mindsdb.com/signup?utm_medium=community&utm_source=dev.to&utm_campaign=predict%20Bitcoin%20price) is fast to set up and has more than enough to give it a try. Or use the open source version if you want to.
