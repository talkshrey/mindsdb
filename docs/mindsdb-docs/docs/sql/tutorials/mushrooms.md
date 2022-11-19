*Dataset: [Mushrooms](https://www.kaggle.com/uciml/mushroom-classification)*

*Community Author: [Chandre Tosca Van Der Westhuizen](https://github.com/chandrevdw31)*

Mushrooms are a fleshy sporocarp of fungi which can either be edible or poisonous. Its usage dates back centuries with ancient Greek, Chinese and African cultures. They can have high nutritional value and medicinal properties which provide great health benefits. On the other side,some of these fungi can be toxic and consuming the wrong mushroom can have deadly consequences. It is important for industries across the world, like the food and health sector, to identify which type of mushrooms are edible and which are poisonous.

We will explore how MindsDB's machine learning predictive model can make it easier classifying mushrooms and predicting which is safe to consume and which can make you ill.

## Pre-requisites

To ensure you can complete all the steps, make sure you have access to the following tools:

1. A MindsDB instance. Check out the installation guide for [Docker](https://docs.mindsdb.com/setup/self-hosted/docker/) or [PyPi](https://docs.mindsdb.com/setup/self-hosted/pip/windows/). You can also use [MindsDB Cloud](https://docs.mindsdb.com/setup/cloud/).
2. Downloaded the dataset. You can get it from [Kaggle](https://www.kaggle.com/uciml/mushroom-classification)
3. Optional: Access to ngrok. You can check the installation details at the [ngrok website](https://ngrok.com/).

## Data Overview

The dataset consists of the following information:

Attribute Information: (classes: edible=e, poisonous=p)

    -  cap_shape: bell=b,conical=c,convex=x,flat=f, knobbed=k,sunken=s
    -  cap_surface: fibrous=f,grooves=g,scaly=y,smooth=s
    -  cap_color: brown=n,buff=b,cinnamon=c,gray=g,green=r,pink=p,purple=u,red=e,white=w,yellow=y
    -  bruises: bruises=t,no=f
    -  odor: almond=a,anise=l,creosote=c,fishy=y,foul=f,musty=m,none=n,pungent=p,spicy=s
    -  gill_attachment: attached=a,descending=d,free=f,notched=n
    -  gill_spacing: close=c,crowded=w,distant=d
    -  gill_size: broad=b,narrow=n
    -  gill_color: black=k,brown=n,buff=b,chocolate=h,gray=g, green=r,orange=o,pink=p,purple=u,red=e,white=w,yellow=y
    -  stalk_shape: enlarging=e,tapering=t
    -  stalk_root: bulbous=b,club=c,cup=u,equal=e,rhizomorphs=z,rooted=r,missing=?
    -  stalk_surface_above_ring: fibrous=f,scaly=y,silky=k,smooth=s
    -  stalk_surface_below_ring: fibrous=f,scaly=y,silky=k,smooth=s
    -  stalk_color_above_ring: brown=n,buff=b,cinnamon=c,gray=g,orange=o,pink=p,red=e,white=w,yellow=y
    -  stalk_color_below_ring: brown=n,buff=b,cinnamon=c,gray=g,orange=o,pink=p,red=e,white=w,yellow=y
    -  veil_type: partial=p,universal=u
    -  veil_color: brown=n,orange=o,white=w,yellow=y
    -  ring_number: none=n,one=o,two=t
    -  ring_type: cobwebby=c,evanescent=e,flaring=f,large=l,none=n,pendant=p,sheathing=s,zone=z
    -  spore_print_color: black=k,brown=n,buff=b,chocolate=h,green=r,orange=o,purple=u,white=w,yellow=y
    -  population: abundant=a,clustered=c,numerous=n,scattered=s,several=v,solitary=y
    -  habitat: grasses=g,leaves=l,meadows=m,paths=p,urban=u,waste=w,woods=d

## Database connection to MindsDB

To establish a database connection we will access MindsDB's GUI. MindsDB has a SQL Editor on Cloud and local via the URL 127.0.0.1:47334/.

First, we need to connect MindsDB to the database where the Mushrooms data is stored:

- Access MindsDB GUI on either cloud or the URL 127.0.0.1:47334/
- On the default page, select the button `Add Data` or alternatively select the plug icon on the left sidebar
- The 'Select your data source' page will populate for you to choose your database type. For this tutorial we will be selecting the postgres database button.

![db](/assets/sql/tutorials/Mushrooms/database.png)

- Once you have selected the database type,the page will automatically navigate to the SQL Editor where the syntax to create a database connection will automatically populate for you to enter the required parameters.


The required parameters are:

- CREATE DATABASE display_name  --- display name for database. 
- WITH ENGINE = "postgres",     --- name of the mindsdb handler 
- PARAMETERS = {
    - "user": " ",              --- Your database user.
    - "password": " ",          --- Your password.
    - "host": " ",              --- host, it can be an ip or an url. 
    - "port": "5432",           --- common port is 5432.
    - "database": " "           --- The name of your database *optional.
}

![integration](/assets/sql/tutorials/Mushrooms/dbintegration.png)

Select the `Run` button or Shift+Enter to execute the syntax. Once the Database connection is created the console will display a message 'Query successfully completed'.
​
> Please note that some database connections require running a Ngrok tunnel to establish a connection.
> Run the ngrok command in a terminal:
> ```bash
> ngrok tcp [db-port]
> ```
> for example,if your port number is 5433 you will see a similar output:
> ```console
> Session Status                online
> Account                       myaccount (Plan: Free)
> Version                       2.3.40
> Region                        United States (us)
> Web Interface                 http://127.0.0.1:4040
> Forwarding                    tcp://6.tcp.ngrok.io:14789 -> localhost:5433
> ```
> The forwarded address information will be required when connecting to MindsDB's GUI. Select and copy the 'Forwarding' information, in this case it is `6.tcp.ngrok.io:14789`, where 6.tcp.ngrok.io will be used for the host parameter and 14789 as the port number.

Once the database integration is successful we can query the table from the database to ensure the data pulls through on MindsDB.

![select](/assets/sql/tutorials/Mushrooms/mushroomsselect.png)


### Create a machine learning model.

Now we are ready to create our own predictor. We will start by using the SQL Editor to execute simple SQL syntax to create and train a machine learning predictive model.

The predictor we will and be trained to determine if a mushroom is edible or poisonous.The following `CREATE MODEL` statement is used to create predictors:

```sql
CREATE MODEL mindsdb.predictor_name
FROM integration_name
    (SELECT column_name, column_name2 FROM table_name)
PREDICT column_name;
```
The required values that we need to provide are:
​
- predictor_name (string): The name of the model
- integration_name (string): The name of the connection to your database.
- column_name (string): The feature you want to predict.

Use the following query to create a predictor that will predict the `target_class` for the specific field parameters.

```sql
CREATE MODEL mushroom_predictor
FROM mindsdb_predictions
    (SELECT * FROM mushrooms)
PREDICT class;
```

Select the `Run` button or Shift+Enter to execute the syntax. Once the predictor is created the console will display a message 'Query successfully completed'.

![create](/assets/sql/tutorials/Mushrooms/create.png)

The predictor was created successfully and has started training. To check the status of the model, use the below query.

```sql
SELECT *
FROM mindsdb.models
WHERE name='mushroom_predictor';
```

After the predictor has finished training, you will see a similar output. Note that MindsDB does model testing for you automatically, so you will immediately see if the predictor is accurate enough.

![create](/assets/sql/tutorials/Mushrooms/statuscheck.png)

The predictor has completed its training, indicated by the status column, and shows the accuracy of the model.
You can revisit training new predictors to increase accuracy by changing the query to better suit the dataset i.e. omitting certain columns etc.

Good job! We have successfully created and trained a predictive model ✨

## Make predictions

In this section you will learn how to make predictions using your trained model.
Now we will use the trained model to make predictions using a SQL syntax.

Use the following query using mock data with the predictor.

```sql
SELECT class
FROM mindsdb.mushroom_predictor
WHERE cap_shape='x'
AND cap_surface='s'
AND cap_color='n' 
AND bruises='t'
AND odor='p'
AND gill_attachment='f'
AND gill_spacing='c' 
AND gill_size='n'
AND gill_color='k'
AND stalk_shape='e'
AND stalk_root='e' 
AND stalk_surface_above_ring='s'
AND stalk_surface_below_ring='s' 
AND stalk_color_above_ring='w'
AND stalk_color_below_ring='w'
AND veil_type='p' 
AND veil_color='w'
AND ring_number='o'
AND ring_type='p'
AND spore_print_color='k' 
AND population='s'
AND habitat='u';
```

The result:

![prediction](/assets/sql/tutorials/Mushrooms/prediction.png)

The machine learning model has predicted that the mushroom is poisonous.

We have successfully created and trained a model that can predict if a model is edible or poisonous.

Want to try it out for yourself? Sign up for a [free MindsDB account](https://cloud.mindsdb.com/signup?utm_medium=community&utm_source=ext.%20blogs&utm_campaign=blog-crop-detection) and join our community!
Engage with MindsDB community on [Slack](https://join.slack.com/t/mindsdbcommunity/shared_invite/zt-o8mrmx3l-5ai~5H66s6wlxFfBMVI6wQ) or [Github](https://github.com/mindsdb/mindsdb/discussions) to ask questions, share and express ideas and thoughts!

For more check out other [tutorials and MindsDB documentation](https://docs.mindsdb.com/).
