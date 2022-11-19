# Predicting Home Rental Prices with MindsDB

## Introduction

In this tutorial, we'll create and train a machine learning model, or as we call it, an `AI Table` or a `predictor`. By querying the model, we'll predict the rental prices of the properties based on their attributes, such as the number of rooms, area, or neighborhood.

Make sure you have access to a working MindsDB installation, either locally or at [MindsDB Cloud](https://cloud.mindsdb.com/).

If you want to learn how to set up your account at MindsDB Cloud, follow [this guide](https://docs.mindsdb.com/setup/cloud/). Another way is to set up MindsDB locally using [Docker](https://docs.mindsdb.com/setup/self-hosted/docker/) or [Python](https://docs.mindsdb.com/setup/self-hosted/pip/source/).

Let's get started.

## Data Setup

### Connecting the Data

There are a couple of ways you can get the data to follow through with this tutorial.

=== "Connecting as a database"

    You can connect to a demo database that we've prepared for you. It contains the data used throughout this tutorial (the `#!sql example_db.demo_data.home_rentals` table).

    ```sql
    CREATE DATABASE example_db
    WITH ENGINE = "postgres",
    PARAMETERS = {
        "user": "demo_user",
        "password": "demo_password",
        "host": "3.220.66.106",
        "port": "5432",
        "database": "demo"
    };
    ```

    Now you can run queries directly on the demo database. Let's preview the data that we'll use to train our predictor.

    ```sql
    SELECT * 
    FROM example_db.demo_data.home_rentals 
    LIMIT 10;
    ```

=== "Connecting as a file"

    You can download [the `CSV` data file here](https://mindsdb-test-file-dataset.s3.amazonaws.com/home_rentals.csv) and upload it via [MindsDB SQL Editor](/connect/mindsdb_editor/).

    Follow [this guide](/sql/create/file/) to find out how to upload a file to MindsDB.

    Now you can run queries directly on the file as if it were a table. Let's preview the data that we'll use to train our predictor.

    ```sql
    SELECT *
    FROM files.home_rentals
    LIMIT 10;
    ```

!!! Warning "Pay Attention to the Queries"
    From now on, we'll use the `#!sql example_db.demo_data.home_rentals` table. Make sure you replace it with `files.home_rentals` if you connect the data as a file.

### Understanding the Data

We use the home rentals dataset, where each row is one property, to predict the `rental_price` column value for all the newly added properties.

Below is the sample data stored in the `#!sql example_db.demo_data.home_rentals` table.

```sql
+-----------------+---------------------+------+----------+----------------+----------------+--------------+
| number_of_rooms | number_of_bathrooms | sqft | location | days_on_market | neighborhood   | rental_price |
+-----------------+---------------------+------+----------+----------------+----------------+--------------+
|               2 |                   1 |  917 | great    |             13 | berkeley_hills |         3901 |
|               0 |                   1 |  194 | great    |             10 | berkeley_hills |         2042 |
|               1 |                   1 |  543 | poor     |             18 | westbrae       |         1871 |
|               2 |                   1 |  503 | good     |             10 | downtown       |         3026 |
|               3 |                   2 | 1066 | good     |             13 | thowsand_oaks  |         4774 |
+-----------------+---------------------+------+----------+----------------+----------------+--------------+
```

Where:

| Column                | Description                                                                                  | Data Type           | Usage   |
| --------------------- | -------------------------------------------------------------------------------------------- | ------------------- | ------- |
| `number_of_rooms`     | Number of rooms in a property `[0,1,2,3]`.                                                   | `integer`           | Feature |
| `number_of_bathrooms` | Number of bathrooms in a property `[1,2]`.                                                   | `integer`           | Feature |
| `sqft`                | Area of a property in square feet.                                                           | `integer`           | Feature |
| `location`            | Rating of the location of a property `[poor, great, good]`.                                  | `character varying` | Feature |
| `days_on_market`      | Number of days a property has been on the market.                                            | `integer`           | Feature |
| `neighborhood`        | Neighborhood `[alcatraz_ave, westbrae, ..., south_side, thowsand_oaks]`.                     | `character varying` | Feature |
| `rental_price`        | Rental price of a property in USD.                                                           | `integer`           | Label   |

!!!Info "Labels and Features"
    A **label** is a column whose values will be predicted (the y variable in simple linear regression).<br/>
    A **feature** is a column used to train the model (the x variable in simple linear regression).

## Training a Predictor

Let's create and train the machine learning model. For that, we use the [`#!sql CREATE MODEL`](/sql/create/predictor) statement and specify the input columns used to train `#!sql FROM` (features) and what we want to `#!sql PREDICT` (labels).

```sql
CREATE MODEL mindsdb.home_rentals_model
FROM example_db
  (SELECT * FROM demo_data.home_rentals)
PREDICT rental_price;
```

We use all of the columns as features, except for the `rental_price` column, whose values will be predicted.

## Status of a Predictor

A predictor may take a couple of minutes for the training to complete. You can monitor the status of the predictor by using this SQL command:

```sql
SELECT status
FROM mindsdb.models
WHERE name='home_rentals_model';
```

If we run it right after creating a predictor, we get this output:

```sql
+------------+
| status     |
+------------+
| generating |
+------------+
```

A bit later, this is the output:

```sql
+----------+
| status   |
+----------+
| training |
+----------+
```

And at last, this should be the output:

```sql
+----------+
| status   |
+----------+
| complete |
+----------+
```

Now, if the status of our predictor says `complete`, we can start making predictions!

## Making Predictions

### Making a Single Prediction

You can make predictions by querying the predictor as if it were a table. The [`SELECT`](/sql/api/select/) statement lets you make predictions for the label based on the chosen features.

```sql
SELECT rental_price, rental_price_explain
FROM mindsdb.home_rentals_model
WHERE sqft = 823
AND location='good'
AND neighborhood='downtown'
AND days_on_market=10;
```

On execution, we get:

```sql
+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| rental_price | rental_price_explain                                                                                                                          |
+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| 4394         | {"predicted_value": 4394, "confidence": 0.99, "anomaly": null, "truth": null, "confidence_lower_bound": 4313, "confidence_upper_bound": 4475} |
+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
```

### Making Batch Predictions

Also, you can make bulk predictions by joining a data table with your predictor using [`#!sql JOIN`](/sql/api/join).

```sql
SELECT t.rental_price AS real_price, 
       m.rental_price AS predicted_price,
       t.number_of_rooms,  t.number_of_bathrooms, t.sqft, t.location, t.days_on_market 
FROM example_db.demo_data.home_rentals AS t 
JOIN mindsdb.home_rentals_model AS m
LIMIT 100;
```

On execution, we get:

```sql
+------------+-----------------+-----------------+---------------------+------+----------+----------------+
| real_price | predicted_price | number_of_rooms | number_of_bathrooms | sqft | location | days_on_market |
+------------+-----------------+-----------------+---------------------+------+----------+----------------+
| 3901       | 3886            | 2               | 1                   | 917  | great    | 13             |
| 2042       | 2007            | 0               | 1                   | 194  | great    | 10             |
| 1871       | 1865            | 1               | 1                   | 543  | poor     | 18             |
| 3026       | 3020            | 2               | 1                   | 503  | good     | 10             |
| 4774       | 4748            | 3               | 2                   | 1066 | good     | 13             |
+------------+-----------------+-----------------+---------------------+------+----------+----------------+
```

## What's Next?

Have fun while trying it out yourself!

* Bookmark [MindsDB repository on GitHub](https://github.com/mindsdb/mindsdb).
* Sign up for a free [MindsDB account](https://cloud.mindsdb.com/register).
* Engage with the MindsDB community on [Slack](https://mindsdb.com/joincommunity) or [GitHub](https://github.com/mindsdb/mindsdb/discussions) to ask questions and share your ideas and thoughts.

If this tutorial was helpful, please give us a GitHub star [here](https://github.com/mindsdb/mindsdb).
