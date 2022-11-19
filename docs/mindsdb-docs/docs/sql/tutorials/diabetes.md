<div style="float:right;" ><img src="/assets/tutorials/diabetes/pg4admin/images.png" width="200" height="150" /></div><div> <img src="/assets/tutorials/diabetes/pg4admin/diabetes_logo.png" style="float:left;" width="50" height="50" /><h1><strong>Diabetes</strong></h1></div>

*Dataset:[Diabetes Data](https://github.com/mindsdb/mindsdb-examples/blob/a43f66f0250c460c0c4a0793baa941307b09c9f2/others/diabetes_example/dataset/diabetes-train.csv)*

*Communtiy Author: [Chandre Tosca Van Der Westhuizen](https://github.com/chandrevdw31)*

Diabetes is a metabolic disease that causes high blood sugar and if left untreated can damage your nerves, eyes, kidneys and other organs. It is known as a silent killer, as recent studies have shown that by the year 2040 the world's diabetic patients will reach 642 million. The need to analyze vast medical data to assist in the diagnoses, treatment and management of illnesses is increasing for the medical community. With the rapid development of machine learning, it has been applied to many aspects of medical health and is transforming the healthcare system.

The vitality to intelligently transform information into valuable knowledge through machine learning has become more present in biosciences. With the use of predictive models, MindsDB can assist in classifying diabetic and non-diabetic patients or those who pose a high risk. This is just a small showcase on how MindsDB's machine learning will be able to assist in vastly enhancing the reach of illnesses, thereby making it more efficient and can revolutionize businesses and most importantly the health care system.

In this tutorial we will be exploring how we can use a machine learning model to classify negative and positive cases for diabetes.
**MindsDB** allows you to train your model from CSV data directly, however for this tutorial you will:

1. Establish a connection between your database and MindsDB via MindsDB GUI(Cloud and local instance).
2. Allow connections to the database using Ngrok.
3. Create a machine learning model using SQL.
4. Make a prediction.

## Connect your database to MindsDB GUI

MindsDB has a functionality to upload your dataset directly to MindsDB. However in this tutorial, you will be shown how to connect your database to MindsDB cloud and local instance.

For this example we will be using a local postgres database, therefore we will connect using an ngrok tunnel.

### Running a Ngrok Tunnel

To make our database publicly avaiable, we will use `ngrok`.

The following command can be run in docker or a terminal on your device to set up a ngrok tunnel.

```bash
ngrok tcp [db-port]
```

For this example the port number used is 5432.

You should see a similar output:

```console
Session Status                online
Account                       chandre (Plan: Free)
Version                       2.3.40
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    tcp://4.tcp.ngrok.io:13096 -> localhost:5432
```

The information required is by the forwarded address, next to 'Forwarding' select and copy `4.tcp.ngrok.io:13096`. Once you have copied the information, you can add it to the information requested by the MindsDB GUI which we will get to in a moment.

For the next steps we will log into the MindsDB cloud interface and local gui. MindsDB Cloud is perfect if you are unable to install MindsDB on your device. If you are not registered yet, feel free to follow the below guide. If you have already registered, skip the next steps to connect your database.

### MindsDB GUI- Cloud MySQL Editor & MySQL CLI

The next step will be to connect your database to MindsDB.

You can visit this [link](https://docs.mindsdb.com/setup/cloud/) and follow the steps to create a MindsDB Cloud account. Access the MySQL Editor [here](https://cloud.mindsdb.com/).

If you are using MindsDB through Docker, you can run the command below to start MindsDB:

```bash
docker run -p 47334:47334 -p 47335:47335 mindsdb/mindsdb
```

Once you are connected,head over to your browser and in the browser tab type in the host number `127.0.0.1:47334` to access the local MindsDB GUI.

### Establish connection between your database and MindsDB GUI

Once you have accessed the GUI, you will be able to select a database type and enter the required parameters:
- On the user interface,select the plug icon on the left sidebar.
- A page will populate with different datasources to select from. For this tutorial we are choosing PostgreSQL.

![choosingdb](/assets/tutorials/diabetes/database.png)

- The page will automatically direct to the SQL editor defaulting the syntax parameters required to create a connection with PostgreSQL:
    - CREATE DATABASE : This will be the chosen display name for your database. For this tutorial we will choose airbyte.
    - WITH ENGINE : name of the mindsdb handler,in this example it will be Postgres.
    PARAMETERS = 
    - "user": Your database user. for this tutorial it is postgres
    - "password": Your password.
    - "host":host, it can be an ip or an url. For this tutorial it will be the forwarding address 4.tcp.ngrok.io
    - "port": "13096",common port is 5432, for this tutorial we will use 15076.
    - "database":The name of your database (optional). For this tutorial we will be using postgres.

Select the button RUN or select Shift+Enter to execute the query.

![db_connection](/assets/tutorials/diabetes/DBdiabetes.png)

You are now done with connecting MindsDB to your database! 🚀

### Create a predictor

Now we are ready to create our own predictor! We will start by using the MySQL API to connect to MindsDB and with a single SQL command create a predictor.

The predictor we will create will be trained to determine negative and positive cases for diabetes.

Use the following query to create a predictor that will predict the `Class` (*positive or negative*) for the specific field parameters.

```sql
CREATE MODEL diabetes_predictor
FROM mindsdb_prediction
    (SELECT * FROM diabetes)
PREDICT class;
```

Select the `RUN` button,alternatively select Shift+Enter to execute the query. You will receive the message 'Query successfully completed' if the machine learning model is successfully created.

![create_predictor](/assets/tutorials/diabetes/create_predictor.png)

The predictor was created successfully and has started training. To check the status of the model, use the below query.

```sql
SELECT *
FROM mindsdb.models
WHERE name='diabetes_predictor';
```

After the predictor has finished training, you will see a similar output. Note that MindsDB does model testing for you automatically, so you will immediately see if the predictor is accurate enough.

![select_predictor](/assets/tutorials/diabetes/select_predictor.png)

The predictor has completed its training, indicated by the status column, and shows the accuracy of the model.
You can revisit training new predictors to increase accuracy by changing the query to better suit the dataset i.e. omitting certain columns etc.

Good job! We have successfully created and trained a predictive model ✨

### Make predictions

In this section you will learn how to make predictions using your trained model.
Now we will use the trained model to make predictions using a SQL query

Use the following query using mock data with the predictor.


```sql
SELECT Class
FROM mindsdb.diabetes_predictor
WHERE number_of_times_pregnant=0
AND plasma_glucose_concentration=135.0 
AND diastolic_blood_pressure=65.0
AND triceps_skin_fold_thickness=30 
AND two_Hour_serum_insulin=0
AND body_mass_index=23.5 
AND diabetes_pedigree_function=0.366
AND age=31;
```

MindsDB will provide you with results similar to below:

![prediction](/assets/tutorials/diabetes/prediction.png)

The machine learning model predicted the diabetic class to be negative.

Viola! We have successfully created and trained a model and made our own prediction. How easy and amazing is MindsDB? 🎉

Want to try it out?

* Sign up for a [free MindsDB account](https://cloud.mindsdb.com/signup?utm_medium=community&utm_source=ext.%20blogs&utm_campaign=blog-crop-detection)
* Join MindsDB community on [Slack](https://join.slack.com/t/mindsdbcommunity/shared_invite/zt-o8mrmx3l-5ai~5H66s6wlxFfBMVI6wQ) and [GitHub](https://github.com/mindsdb/mindsdb/discussions) to ask questions, share and express ideas and thoughts!
