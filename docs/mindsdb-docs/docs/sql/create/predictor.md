# `#!sql CREATE MODEL` Statement

## Description

The `CREATE MODEL` statement creates and trains a new ML model.

## Syntax

Here is the syntax:

```sql
CREATE MODEL mindsdb.[predictor_name]
FROM [integration_name]
    (SELECT [column_name, ...] FROM [table_name])
PREDICT [target_column]
[USING [parameter_key]=['parameter_value']];
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

Where:

| Expressions                                     | Description                                                                                                                                     |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `[predictor_name]`                              | Name of the model to be created.                                                                                                                |
| `[integration_name]`                            | Name of the integration created using the [`#!sql CREATE DATABASE`](/sql/create/databases/) statement or [file upload](/sql/api/select_files/). |
| `(SELECT [column_name, ...] FROM [table_name])` | `SELECT` statement for selecting data to be used for training and validation.                                                                   |
| `PREDICT [target_column]`                       | `target_column` is the column to be predicted.                                                                                                  |

!!! TIP "Checking Model Status"
    After you run the `#!sql CREATE MODEL` statement, you can check the status of the training process by querying the `#!sql mindsdb.models` table.

    ```sql
    SELECT *
    FROM mindsdb.models
    WHERE name='[predictor_name]';
    ```

    On execution, we get:

    ```sql
    +------------------------+-----------------------------------+----------------------------------------+-----------------------+-------------+---------------+-----+-----------------+----------------+
    |name                    |status                             |accuracy                                |predict                |update_status|mindsdb_version|error|select_data_query|training_options|
    +------------------------+-----------------------------------+----------------------------------------+-----------------------+-------------+---------------+-----+-----------------+----------------+
    |predictor_name          |generating or training or complete |number depending on the accuracy metric |column_to_be_predicted |up_to_date   |22.7.5.0       |     |                 |                |
    +------------------------+-----------------------------------+----------------------------------------+-----------------------+-------------+---------------+-----+-----------------+----------------+
    ```

## Example

This example shows how to create and train a machine learning model called `home_rentals_model` and predict the rental prices for real estate properties inside the dataset.

```sql
CREATE MODEL mindsdb.home_rentals_model
FROM db_integration 
    (SELECT * FROM house_rentals_data)
PREDICT rental_price;
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

To check the predictor status, query the [`#!sql mindsdb.models`](/sql/table-structure/#the-predictors-table) table.

```sql
SELECT *
FROM mindsdb.models
WHERE name='home_rentals_model';
```

On execution, we get:

```sql
+--------------------+----------+--------------------+--------------+---------------+-----------------+-------+-------------------+------------------+
| name               | status   | accuracy           | predict      | update_status | mindsdb_version | error | select_data_query | training_options |
+--------------------+----------+--------------------+--------------+---------------+-----------------+-------+-------------------+------------------+
| home_rentals_model | complete | 0.9991920992432087 | rental_price | up_to_date    | 22.5.1.0        | NULL  |                   |                  |
+--------------------+----------+--------------------+--------------+---------------+-----------------+-------+-------------------+------------------+
```

## `#!sql CREATE MODEL` with the `#!sql USING` Statement

### Description

In MindsDB, the underlying AutoML models are based on the [Lightwood](https://lightwood.io/) engine by default. This library generates models automatically based on the data and declarative problem definition. But the default configuration can be overridden using the `#!sql USING` statement that provides an option to configure specific parameters of the training process.

In the upcoming version of MindsDB, it will be possible to choose another ML framework. Please note that the Lightwood engine is used by default.

### Syntax

Here is the syntax:

```sql
CREATE MODEL mindsdb.[predictor_name]
FROM [integration_name]
    (SELECT [column_name, ...] FROM [table_name])
PREDICT [target_column]
USING [parameter_key] = ['parameter_value'];
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

#### `#!sql encoders` Key

It grants access to configure how each column is encoded. By default, the AutoML engine tries to get the best match for the data.

```sql
...
USING encoders.[column_name].module='value';
```

To learn more about `#!sql encoders` and their options, visit the [Lightwood documentation page on `#!sql encoders`](https://lightwood.io/encoder.html).

#### `#!sql model` Key

It allows you to specify the type of machine learning algorithm to learn from the encoder data.

```sql
...
USING model.args={"key": value};
```

Module options:

| Module                                                                   | Description                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [**BaseMixer**](https://lightwood.io/mixer.html#mixer.BaseMixer)         | Base class for all mixers.                                                                                                                                                                                                                                                |
| [**LightGBM**](https://lightwood.io/mixer.html#mixer.LightGBM)           | This mixer configures and uses LightGBM for regression or classification tasks depending on the problem definition.                                                                                                                                                       |
| [**LightGBMArray**](https://lightwood.io/mixer.html#mixer.LightGBMArray) | This mixer consists of several LightGBM mixers in regression mode aimed at time series forecasting tasks.                                                                                                                                                                 |
| [**NHitsMixer**](https://lightwood.io/mixer.html#mixer.NHitsMixer)       | Wrapper around an MQN-HITS deep learning model.                                                                                                                                                                                                                           |
| [**Neural**](https://lightwood.io/mixer.html#mixer.Neural)               | The Neural mixer trains a fully connected dense network from concatenated encoded outputs of each feature in the dataset to predict the encoded output.                                                                                                                   |
| [**ProphetMixer**](https://lightwood.io/mixer.html#mixer.ProphetMixer)   | This mixer is a wrapper around the popular time series library sktime.                                                                                                                                                                                                    |
| [**Regression**](https://lightwood.io/mixer.html#mixer.Regression)       | The Regression mixer inherits from [scikit-learn’s Ridge class](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html).                                                                                                                       |
| [**SkTime**](https://lightwood.io/mixer.html#mixer.SkTime)               | This mixer is a wrapper around the popular time series library sktime.                                                                                                                                                                                                    |
| [**Unit**](https://lightwood.io/mixer.html#mixer.Unit)                   | Special mixer that passes along whatever prediction is made by the target encoder without modifications. It is used for single-column predictive scenarios that may involve complex and/or expensive encoders (e.g. free-form text classification with transformers).     |

To learn more about all the `#!sql model` options, visit the [Lightwood documentation page](https://lightwood.io/mixer.html).

#### Other Keys Supported by Lightwood in JsonAI

The most common use cases of configuring predictors use `#!sql encoders` and `#!sql model` keys explained above. To see all the available keys, check out the [Lightwood documentation page on JsonAI](https://lightwood.io/api/types.html#api.types.JsonAI).

### Example

Here we use the `home_rentals` dataset and specify particular `#!sql encoders` for some columns and a LightGBM `#!sql model`.

```sql
CREATE MODEL mindsdb.home_rentals_model
FROM db_integration
    (SELECT * FROM home_rentals)
PREDICT rental_price
USING
    encoders.location.module='CategoricalAutoEncoder',
    encoders.rental_price.module = 'NumericEncoder',
    encoders.rental_price.args.positive_domain = 'True',
    model.args={"submodels":[
                    {"module": "LightGBM",
                     "args": {
                          "stop_after": 12,
                          "fit_on_dev": true
                          }
                    }
                ]};
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

## `#!sql CREATE MODEL` From File

To create a predictor from a file, you should first upload a file to MindsDB. Follow [this guide](https://docs.mindsdb.com/sql/create/file/) to see how to do that.

### Description

This statement is used to create and train a model from a file or a database table.

### Syntax

Here is the syntax:

```sql
CREATE MODEL mindsdb.[predictor_name]
FROM files
    (SELECT * FROM [file_name])
PREDICT target_column;
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

Where:

| Name                          | Description                                                                       |
| ----------------------------- | --------------------------------------------------------------------------------- |
| `[predictor_name]`            | Name of the model to be created.                                                  |
| `[file_name]`                 | Name of the file uploaded via the MindsDB editor.                                 |
| `(SELECT * FROM [file_name])` | `SELECT` statement for selecting the data to be used for training and validation. |
| `target_column`               | `target_column` is the column to be predicted.                                    |

### Example

Here we uploaded the `home_rentals` dataset as a file.

```sql
CREATE MODEL mindsdb.home_rentals_model
FROM files
    (SELECT * from home_rentals)
PREDICT rental_price;
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

## `#!sql CREATE MODEL` For Time Series Models

### Description

To train a time series model, MindsDB provides additional statements.

### Syntax

Here is the syntax:

```sql
CREATE MODEL mindsdb.[predictor_name]
FROM [integration_name]
    (SELECT [sequential_column], [partition_column], [other_column], [target_column]
     FROM [table_name])
PREDICT [target_column]

ORDER BY [sequential_column]
GROUP BY [partition_column]

WINDOW [int]
HORIZON [int];
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

Where:

| Expressions                              | Description                                                                                                                                                                                                                                                        |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ORDER BY [sequential_column]`           | The column by which time series is ordered. It can be a date or anything that defines the sequence of events.                                                                                                                                                      |
| `GROUP BY [partition_column]`            | It is optional. The column by which rows that make a partition are grouped. For example, if you want to forecast the inventory for all items in the store, you can partition the data by `product_id`, so each distinct `product_id` has its own time series.      |
| `WINDOW [int]`                           | The number of rows to look back at when making a prediction. It comes after the rows are ordered by the column defined in `ORDER BY` and split into groups by the column(s) defined in `GROUP BY`. This could be interpreted as "Always use the previous 10 rows". |
| `HORIZON [int]`                          | It is optional. The number of future predictions (it is 1 by default).                                                                                                                                                                                             |

!!! warning "Getting a Prediction from a Time Series Model"
    Due to the nature of time series forecasting, you need to use the [`#!sql JOIN`](/sql/api/join) statement to get results.

### Example

Here is an example:

```sql
CREATE MODEL mindsdb.inventory_model
FROM db_integration
    (SELECT * FROM inventory)
PREDICT units_in_inventory
ORDER BY date
GROUP BY product_id
WINDOW 20
HORIZON 7;
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

Now, to get the results, we use the [`#!sql JOIN`](/sql/api/join) statement.

```sql
SELECT im.product_id, im.date, im.units_in_inventory AS predicted_units_in_inventory
FROM db_integration.inventory AS i
JOIN mindsdb.inventory_model AS im
WHERE i.date > LATEST
LIMIT 10;
```

The data source table (`db_integration.inventory`) and the predictor table (`mindsdb.inventory_model`) are joined to let us fetch the predictions for future dates.
