# Predict Insurance Cost using MindsDB

*Dataset: [Medical Cost Personal Data](https://www.kaggle.com/mirichoi0218/insurance)* 

*Communtiy Author: [Kinie K Kusuma](https://github.com/kinkusuma)*

## Pre-requisites

First, you need MindsDB installed. So please make sure you've visited [Getting Started Guide](/info) and [Getting Started with Cloud](/setup/cloud).
You may start to use MindsDB by installing it locally or you can use the [Cloud](https://cloud.mindsdb.com/signup) service. 
Let’s use the cloud for this tutorial. 
Second, you need a MySQL client to connect to the MindsDB MySQL API.

## Can you accurately predict insurance costs?  

In this tutorial, you will learn how to predict insurance costs using MindsDB.
This tutorial is very easy because you don't need to learn any machine learning algorithms, all you need to know is just SQL.

The process looks like the following:
First we will connect MindsDB to a database with past data so it can learn from it
We will use a single SQL command that will tell MindsDB to train its predictor
We will use the standard SQL Select statement to get predictions from AI Tables in MindsDB. Like if this data already exists!

MindsDB will execute a complete Machine Learning workflow behind the scenes, it will determine data types for each column, normalize and encode it, train and test ML model. All this happens automatically, so it is very cool! Those who want to get their hands dirty with manual hyperparameters optimization, you can also do that with MindsDB using a declarative syntax called JSON-AI.

So let's look at how it works using a real use case. For the demo purpose we will use a public dataset from Kaggle, but you are free to follow this tutorial with your own data.

## Connect your database

First, you need to connect MindsDB to the database where the data is stored. Open MindsDB GUI and in the left navigation click on Database, then click on the ADD DATABASE.
Here, you need to provide all of the required parameters for connecting to the database.

![Connect](/assets/sql/tutorials/insurance-cost/create_db.png)

* Supported Database - select the database that you want to connect to
* Integrations Name - add a name to the integration, here I'm using 'mysql' but you can name it differently
* Database - the database name
* Host - database hostname
* Port - database port
* Username - database user
* Password - user's password

Then, click on CONNECT.  
The next step is to use the MySQL client to connect to MindsDB’s MySQL API, train a new model, and make a prediction.

## Connect to MindsDB’s MySQL API

Here I'm using MySQL command-line client, but you can also follow up with the one that works the best for you, like Dbeaver.  
The first step is to use the MindsDB Cloud user to connect to the MindsDB MySQL API, using this command:

![Connect mysql-client](/assets/sql/tutorials/insurance-cost/connect-mindsdb-sql.png)

You need to specify the hostname and user name explicitly, as well as a password for connecting. Click enter and you are connected to MindsDB API.

![Connect mysql-client](/assets/sql/tutorials/insurance-cost/success-connect-sql.png)

If you have an authentication error, please make sure you are providing the email address you have used to create an account on MindsDB Cloud.

## Data

Now, let's show the databases.

![Show dbs](/assets/sql/tutorials/insurance-cost/show-databases-sql.png)

There are 4 databases, and the MySQL database is the database that I've connected to MindsDB.

Let's check the MySQL database.

![Show tables](/assets/sql/tutorials/insurance-cost/show-tables-sql.png)

There are 3 tables, and because the tutorial is about insurance cost prediction, we will use the insurance table.  
Let's check what is inside this table.

![Insurance table](/assets/sql/tutorials/insurance-cost/show-insurance-table.png)

So, these tables have 7 columns:

- age: The age of the person (integer)
- sex: Gender (male or female)
- bmi: Body mass index is a value derived from the mass and height of a person. 
The BMI is defined as the body mass divided by the square of the body height, and is expressed in units of kg/m², 
resulting from mass in kilograms and height in meters (float)
- children: The number of children (integer)
- smoker: Indicator if the person smoke (yes or no)
- region: Region where the insured lives (southeast, northeast, southwest or northwest)
- charges: The insurance cost, this is the target of prediction (float)

## Create the model

Now, to create the model, let's move to the MindsDB database, and see what's inside.

![Show mindsdb](/assets/sql/tutorials/insurance-cost/show-tables-sql-2.png)

There are 2 tables, predictors, and commands. Predictors contain your predictors record, and commands contain your last commands used.  
To train a new machine learning model we will need to `CREATE MODEL` as a new record inside the predictors table, and using this command:

```sql
CREATE MODEL mindsdb.predictor_name
FROM integration_name
    (SELECT column_name, column_name2 FROM table_name)
PREDICT column_name;
```

The values that we need to provide are:

* predictor_name (string) - The name of the model.
* integration_name (string) - The name of the connection to your database.
* ds_name (string) - the name of the dataset you want to create, it's optional if you don't specify this value MindsDB will generate by itself.
* column_name (string) - The feature you want to predict.
* column_alias - Alias name of the feature you want to predict.

So, use this command to create the models:

```sql
CREATE MODEL insurance_cost_predictor
FROM insurance_costs
    (SELECT * FROM insurance)
PREDICT charges;
```

![Create model](/assets/sql/tutorials/insurance-cost/insurance_predictor.png)

If there's no error, that means your model is created and training has started. To see if your model is finished, use this command:

```sql
SELECT *
FROM mindsdb.models
WHERE name = predictor_name;
```

And values that we need to provide are:

* predictor_name (string) - The name of the model.

```sql
SELECT *
FROM mindsdb.models
WHERE name='insurance_cost_predictor';
```

![Show model](/assets/sql/tutorials/insurance-cost/select_insurance.png)

If the predictor is ready, it will look like this. The model has been created and trained! The reported accuracy is 75%. If you want to have more control over the model, head to lightwood.io to see how that can be customized.

## Make prediction

Now you are in the last step of this tutorial, making the prediction. To make a prediction you can use this command:

```sql
SELECT target_variable, target_variable_explain
FROM model_table 
WHERE column3="value"
AND column2=value;
```

You need to set these values:

- target_variable - The original value of the target variable.
- target_variable_confidence - Model confidence score.
- target_variable_explain - JSON object that contains additional information as confidence_lower_bound, confidence_upper_bound, anomaly, truth.
- when_data - The data to make the predictions from(WHERE clause params).

```sql
SELECT charges, charges_confidence, charges_explain AS info
FROM insurance_cost_predictor
WHERE age=20
AND sex='male'
AND bmi=33.20
AND children=0
AND smoker='no'
AND region='southeast';
```

![Query model](/assets/sql/tutorials/insurance-cost/prediction_insurance.png)

Finally, we have trained an insurance model using SQL and MindsDB.

## Conclusions

As you can see it is very easy to start making predictions with machine learning even without being a data scientist! Feel free to check this yourself, MindsDB has an option of a [free cloud account](https://cloud.mindsdb.com/signup?utm_medium=referral&utm_source=community&utm_campaign=insurance%20cost%20prediction) that is more than enough to give it a try.
