# Quickstart

Follow the steps below to start making data forecasts with MindsDB using standard SQL.

Check out our [Getting Started Guide](/getting-started/) to set up and work with MindsDB using your own data and models.

## 1. Create a MindsDB Cloud Account

Create your [free MindsDB Cloud account](https://cloud.mindsdb.com/register) to start practicing right away using the MindsDB Cloud Editor.

If you prefer a local MindsDB installation, follow the **Deployment** guides of MindsDB documentation. You can install MindsDB in [Docker](setup/self-hosted/docker/) or follow the standard installation using [pip](setup/self-hosted/pip/source/).

## 2. Connect to MindsDB from a SQL Client

You can use the MindsDB Cloud SQL Editor or open your preferred SQL client, such as DBeaver or MySQL CLI, and connect to MindsDB.

=== "Using the MindsDB Cloud SQL Editor"
    Log in to your MindsDB Cloud account. The [Editor](https://cloud.mindsdb.com/editor) is the first thing you'll see!

=== "Using a third-party SQL Client"
    To connect to MindsDB from a third-party SQL client, use the connection details below.

    ```txt
      "user":[your_mindsdb_cloud_username],   # your Mindsdb Cloud email address is your username
      "password":[your_mindsdb_cloud_password],
      "host":"cloud.mindsdb.com",
      "port":"3306"
    ```

    !!! Tip ""
        If you do not have a preferred SQL client yet, we recommend using the [MindsDB SQL Editor](https://cloud.mindsdb.com/editor) or [DBeaver Community Edition](https://dbeaver.io/download/). Follow [this guide](setup/cloud/) to set up your MindsDB SQL Editor. And [here](connect/dbeaver/), you'll find how to connect to MindsDB from DBeaver.

## 3. Connecting a Database Using [`#!sql CREATE DATABASE`](/sql/create/databases/)

We have a sample database that you can use right away. To connect a database to your MindsDB Cloud account, use the [`#!sql CREATE DATABASE`](/sql/create/databases/) statement, as below.

```sql
CREATE DATABASE example_data
WITH ENGINE = "postgres",
PARAMETERS = { 
  "user": "demo_user",
  "password": "demo_password",
  "host": "3.220.66.106",
  "port": "5432",
  "database": "demo"
};
```

On execution, we get:

```sql
Query OK, 0 rows affected (3.22 sec)
```

## 4. Previewing Available Data

You can now preview the available data with a standard `#!sql SELECT` statement.

```sql
SELECT * 
FROM example_data.demo_data.home_rentals
LIMIT 10;
```

On execution, we get:

```sql
+-----------------+---------------------+------+----------+----------------+---------------+--------------+--------------+
| number_of_rooms | number_of_bathrooms | sqft | location | days_on_market | initial_price | neighborhood | rental_price |
+-----------------+---------------------+------+----------+----------------+---------------+--------------+--------------+
| 0.0             | 1.0                 | 484  | great    | 10             | 2271          | south_side   | 2271         |
| 1.0             | 1.0                 | 674  | good     | 1              | 2167          | downtown     | 2167         |
| 1.0             | 1.0                 | 554  | poor     | 19             | 1883          | westbrae     | 1883         |
| 0.0             | 1.0                 | 529  | great    | 3              | 2431          | south_side   | 2431         |
| 3.0             | 2.0                 | 1219 | great    | 3              | 5510          | south_side   | 5510         |
| 1.0             | 1.0                 | 398  | great    | 11             | 2272          | south_side   | 2272         |
| 3.0             | 2.0                 | 1190 | poor     | 58             | 4463          | westbrae     | 4124         |
| 1.0             | 1.0                 | 730  | good     | 0              | 2224          | downtown     | 2224         |
| 0.0             | 1.0                 | 298  | great    | 9              | 2104          | south_side   | 2104         |
| 2.0             | 1.0                 | 878  | great    | 8              | 3861          | south_side   | 3861         |
+-----------------+---------------------+------+----------+----------------+---------------+--------------+--------------+
```

You could also browse the databases of MindsDB using the command below.

```sql
SHOW databases;
```

On execution, we get:

```sql
+---------------------+
| Database            |
+---------------------+
| information_schema  |
| mindsdb             |
| files               |
| example_data        |
+---------------------+
```

To learn more about MindsDB tables structure, check out [this guide](sql/table-structure/).

## 5. Creating a Predictor Using [`#!sql CREATE MODEL`](/sql/create/predictor/)

Now you are ready to create your first predictor. Use the [`#!sql CREATE MODEL`](/sql/create/predictor/) statement, as below.

```sql 
CREATE MODEL mindsdb.home_rentals_predictor
FROM example_data
  (SELECT * FROM demo_data.home_rentals)
PREDICT rental_price;
```

On execution, we get:

```sql
Query OK, 0 rows affected (9.79 sec)
```

## 6. Checking the Status of a Predictor

It may take a couple of minutes until the predictor is trained. You can monitor the status of your predictor by executing the following command:

```sql
SELECT status
FROM mindsdb.models
WHERE name='home_rentals_predictor';
```

On execution, we get:

```sql
+----------+
| status   |
+----------+
| training |
+----------+
```

Or:

```sql
+----------+
| status   |
+----------+
| complete |
+----------+
```

Alternatively, you can use the `SHOW MODELS` command as below.

```sql
SHOW MODELS [FROM *database_project_name*] [LIKE *model_name*] [WHERE *filter*];
```

Here is an example:

```sql
SHOW MODELS FROM mindsdb LIKE 'home_rentals_predictor' WHERE status='complete';
```

!!! attention "The status of the predictor must be `complete` before you can start making predictions."

## 7. Making a Prediction Using [`#!sql SELECT`](/sql/api/select/)

The [`SELECT`](/sql/api/select/) statement allows you to make predictions based on features, where features are the input variables, or input columns, that are used to make forecasts.

Let's predict what would be the rental price of a 1000 square feet house with two bathrooms.

```sql
SELECT rental_price
FROM mindsdb.home_rentals_predictor
WHERE number_of_bathrooms=2
AND sqft=1000;
```

On execution, we get:

```sql
+--------------+
| rental_price |
+--------------+
| 1130         |
+--------------+
```

!!! done "Congratulations"
      If you got this far, you have successfully trained a predictive model using SQL and got the future data!
