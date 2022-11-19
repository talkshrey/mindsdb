*Dataset:[Heart Disease Data](https://www.kaggle.com/c/heart-disease-uci/data)*

*Communtiy Author: [Mohd Talha](https://github.com/taltrums)*

Cardiovascular disease remains the leading cause of morbidity and mortality according to the [National Center for Health Statistics](https://www.cdc.gov/nchs/products/databriefs/db328.htm) in the United States, and consequently, early diagnosis is of paramount importance. Machine learning technology, a subfield of artificial intelligence, is enabling scientists, clinicians and patients to detect it in the earlier stages and therefore save lives.
 
Until now, building, deploying and maintaining applied machine learning solutions was a complicated and expensive task, because it required skilled personnel and expensive tools. But not only that. A traditional machine learning project requires building integrations with data and applications, that is not only a technical but also an organizational challenge. So what if machine learning can become a part of the standard tools that are already in use?
 
This is exactly the problem that MindsDB is solving. It makes machine learning easy to use by automating and integrating it into the mainstream instruments for data and analytics, namely databases and business intelligence software. It adds an AI “brain” to databases so that they can learn automatically from existing data, allowing you to generate and visualize predictions using standard data query language like SQL. Lastly, MindsDB is open-source, and anyone can use it for free.
 
In this article, we will show step by step how to use MindsDB inside databases to predict the risk of heart disease for patients. 
 
You can follow this tutorial by connecting to your own database and using different data - the same workflow applies to most machine learning use cases. Let’s get started!

## Pre-requisites

If you want to install MindsDB locally, check out the installation guide for [Docker](https://docs.mindsdb.com/setup/self-hosted/docker/) or [PyPi](https://docs.mindsdb.com/setup/self-hosted/pip/windows/) and you can follow this tutorial.
If you are OK with using MindsDB cloud, then simply [create a free account](https://cloud.mindsdb.com/signup) and you will be up and running in just one minute. 
 
Second, you will need to have a mysql client like DBeaver, MySQL Workbench etc. installed locally to connect to the MindsDB MySQL API. MindsDB contains a SQL Editor which can be accessed on MindsDB cloud or the URL 127.0.0.1:47334/.

### Data Overview

For the example of this tutorial, we will use the heart disease dataset available [publicly in Kaggle](https://www.kaggle.com/c/heart-disease-uci/data). Each row represents a patient and we will train a machine learning model to help us predict if the patient is classified as a heart disease patient. Below is a short description of each feature inside the data.

* age - In Years
* sex - 1 = Male; 0 = Female
* cp - chest pain type (4 values)
* trestbps - Resting blood pressure (in mm Hg on admission to the hospital)
* chol - Serum cholesterol in mg/dl
* fbs - Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)
* restecg - Resting electrocardiographic results
* thalach - Maximum heart rate achieved
* exang - Exercise induced angina (1 = yes; 0 = no)
* oldpeak - ST depression induced by exercise relative to rest
* slope - the slope of the peak exercise ST segment
* ca - Number of major vessels (0-3) colored by fluoroscopy
* thal - 1 = normal; 2 = fixed defect; 3 = reversible defect
* target - 1 or 0 (This is what we will predict)

## How to use MindsDB

MindsDB allows you to automatically create & train machine learning models from the data in your database that you have connected to in the previous step. MindsDB works via MySQL wire protocol, which means you can do all these steps through SQL commands. When it comes to making predictions, SQL queries become even handier, because you can easily make them straight from your existing applications or Business Intelligence tools that already speak SQL. The ML models are available to use immediately after being trained as if they were virtual database tables (a concept called “AI Tables”). 
So, let’s see how it works.

## Connect to your data

First, we need to connect MindsDB to the database where the Heart Disease data is stored:
- Access MindsDB GUI on either cloud or local via the URL 127.0.0.1:47334/
- On the default page, select the button `Add Data` or alternatively select the plug icon on the left sidebar.
- The 'Select your data source' page will populate for you to choose your database type. For this tutorial we will be selecting the postgres database button.

![Connect to DB](/assets/sql/tutorials/heart-disease/database.png)

- Once you have selected the database type,the page will automatically navigate to the SQL Editor where the syntax to create a database connection will automatically populate for you to enter the required parameters.


The required parameters are:

- CREATE DATABASE display_name  --- display name for database. 
- WITH ENGINE = "postgres",     --- name of the mindsdb handler 
- PARAMETERS = {
    - "user": " ",              --- Your database user.
    - "password": " ",          --- Your password.
    - "host": " ",              --- host, it can be an ip or an url. 
    - "port": "5432",           --- common port is 5432.
    - "database": " "           --- The name of your database *optional.}

![Connect to DB](/assets/sql/tutorials/heart-disease/dbintegration.png)

Select the `Run` button or Shift+Enter to execute the syntax. Once the Database connection is created the console will display a message 'Query successfully completed'.
 
### Create a machine learning model.

We can create a machine learning predictive model by using simple SQL statements executed in the SQL Editor.

To create and train a new machine learning model we will need to use the `CREATE MODEL` statement:

```sql
CREATE MODEL mindsdb.predictor_name
FROM integration_name
    (SELECT column_name, column_name2 FROM table_name)
PREDICT column_name;
```

The required values that we need to provide are:

- predictor_name (string): The name of the model
- integration_name (string): The name of the connection to your database.
- column_name (string): The feature you want to predict.

To train the model that will predict the risk of heart disease as target we will run:

```sql
CREATE MODEL patients_target
FROM mindsdb_predictions
    (SELECT * FROM heart_disease)
PREDICT target;
```

Select the `Run` button or Shift+Enter to execute the syntax. Once the machine learning model is created the console will display a message 'Query successfully completed'.
	
![CREATE PREDICTOR](/assets/sql/tutorials/heart-disease/create.png)

What we did here was to create a predictor called `patients_target `to predict the presence of heart disease as `target`. The model has started training. To check if the training has finished you can SELECT the model name from the predictors table:

```sql
SELECT *
FROM mindsdb.models
WHERE name='patients_target';
```

![SELECT status](/assets/sql/tutorials/heart-disease/selectpredictor.png)

The complete status means that the model training has successfully finished.
 
## Using SQL Statements to make predictions

The next steps would be to query the model and predict the heart disease risk. Let’s imagine a patient. This patient’s age is 30, she has a cholesterol level of 177 mg/dl, with slope of the peak exercise ST segment as 2, and thal as 2. Add all of this information to the `WHERE` clause.

```sql
SELECT target AS prediction,
       target_confidence AS confidence,
       target_explain AS info
FROM mindsdb.patients_target
WHERE age=30
AND chol=177
AND slope=2
AND thal=2;
```

![SELECT from model](/assets/sql/tutorials/heart-disease/1prediction.png)

With a confidence of around 83%, MindsDB predicted a high risk of heart disease for this patient.
 
The above example shows how you can make predictions for a single patient. But what if you have a table in your database with many patients’ diagnosis data, and you want to make predictions for them in bulk?
For this purpose, you can join the predictor with such a table.
 
```sql
SELECT *
FROM mindsdb_predictions.heart_disease AS t
JOIN mindsdb.patients_target AS tb
WHERE t.thal=2;
```

![SELECT from model](/assets/sql/tutorials/heart-disease/2ndprediction.png)

![SELECT from model](/assets/sql/tutorials/heart-disease/2.1prediction.png)

![SELECT from model](/assets/sql/tutorials/heart-disease/3rdprediction.png)

Now you can even connect the output table to your BI tool and for more convenient visualization of the results using graphs or pivots.
 
## Conclusion
In this tutorial, you have seen how easy it is to apply machine learning for your predictive needs. MindsDB's innovative open-source technology is making it easy to leverage machine learning for people who are not experts in this field. However, MindsDB is a great tool for ML practitioners as well: if you are a skilled data scientist, you could also benefit from the convenience of deploying custom machine learning solutions within databases by building & configuring models manually through a declarative syntax called [JSON-AI](https://mindsdb.com/JSON-AI).
 
There are other interesting ML use cases where MindsDB is positioned extremely well, like multivariate time-series and real-time data streams, so feel free to [check it yourself](https://mindsdb.com/machine-learning-use-cases/).
