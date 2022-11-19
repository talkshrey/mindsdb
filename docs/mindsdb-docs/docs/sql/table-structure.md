# MindsDB Default Structure

On start-up, MindsDB consists of one system database (`information_schema`), one default project (`mindsdb`), and two base tables (`models` and `models_versions`) that belong to the default project.

You can verify it by running the following SQL commands:

```sql
SHOW [FULL] DATABASES;
```

On execution, we get:

```sql
+----------------------+---------+--------+
| Database             | TYPE    | ENGINE |
+----------------------+---------+--------+
| information_schema   | system  | [NULL] |
| mindsdb              | project | [NULL] |
| files                | data    | files  |
+----------------------+---------+--------+
```

And:

```sql
SHOW [FULL] TABLES;
```

On execution, we get:

```sql
+----------------------+-------------+
| Tables_in_mindsdb    | Table_type  |
+----------------------+-------------+
| models               | BASE TABLE  |
| models_versions      | BASE TABLE  |
+----------------------+-------------+
```

## The `information_schema` Database

The `information_schema` database contains all the system tables, such as `databases`, `tables`, `columns`, `ml_engines`, etc.

You can query for any system information using this query template:

```sql
SELECT *
FROM information_schema.table_name;
```

Don't forget to replace *table_name* with the table of your interest.

Let's query for the following:

* The `databases` table lists all the databases including their name, type, and engine.

```sql
SELECT *
FROM information_schema.databases;
```

On execution, we get:

```sql
+------------------+-------+--------+
|NAME              |TYPE   |ENGINE  |
+------------------+-------+--------+
|information_schema|system |[NULL]  |
|mindsdb           |project|[NULL]  |
|my_new_project    |project|[NULL]  |
|files             |data   |files   |
+------------------+-------+--------+
```

* The `handlers` table lists all the available ML handlers.

```sql
SELECT *
FROM information_schema.handlers;
-- or
SHOW HANDLERS;
```

On execution, we get:

```sql
+------------------+------------+---------------------------------+-------+------------------------------------------------------------------------------+----------------+----------------------+------+
|NAME              |TITLE       |DESCRIPTION                      |VERSION|CONNECTION_ARGS                                                               |IMPORT_SUCCESS  |IMPORT_ERROR          |FIELD8|
+------------------+------------+---------------------------------+-------+------------------------------------------------------------------------------+----------------+----------------------+------+
|merlion           |Merlion     |MindsDB handler for Merlion      |0.0.1  |[NULL]                                                                        |true            |[NULL]                |      |
|byom              |BYOM        |MindsDB handler for BYOM         |0.0.1  |{'model_code': {'type': 'path', 'description': 'The path name to model code'}}|true            |[NULL]                |      |
|ludwig            |Ludwig      |MindsDB handler for Ludwig AutoML|0.0.2  |[NULL]                                                                        |false           |No module named 'dask'|      |
|lightwood         |Lightwood   |[NULL]                           |1.0.0  |[NULL]                                                                        |true            |[NULL]                |      |
|huggingface       |Hugging Face|MindsDB handler for Higging Face |0.0.1  |[NULL]                                                                        |true            |[NULL]                |      |
+------------------+------------+---------------------------------+-------+------------------------------------------------------------------------------+----------------+----------------------+------+
```

* The `ml_engines` table lists all the ML engines. These are the instantiated ML handlers. Check out our [docs on the `CREATE ML _ENGINE` command](/sql/create/ml_engine/) to learn more.

```sql
SELECT *
FROM information_schema.ml_engines;
-- or
SHOW ML_ENGINES;
```

On execution, we get:

```sql
+------------------+-----------+----------------+
|NAME              |HANDLER    |CONNECTION_DATA |
+------------------+-----------+----------------+
|huggingface       |huggingface|{'password': ''}|
|lightwood         |lightwood  |{'password': ''}|
+------------------+-----------+----------------+
```

## The `mindsdb` Project

You create models and views within projects. The default project is `mindsdb`. But you can create your projects using the `CREATE DATABASE` statement, as below:

```sql
CREATE DATABASE my_new_project;
```

Here is how to create a model within your project:

```sql
CREATE MODEL my_new_project.my_model
FROM integration_name
    (SELECT * FROM table_name)
PREDICT target;
```

And here is how to create a view within your project:

```sql
CREATE VIEW my_new_project.my_view (
    SELECT *
    FROM integration_name.table_name
);
```

Please replace the *integration_name* and *table_name* placeholders with your database name and your table name respectively.

!!! note "What If Names of a Model and a View are the Same?"
    Please note that if you use the same name for a model and a view stored in one project, then MindsDB adds `_view` to the view name.

Now you can verify that the model and view are within your project:

```sql
SHOW FULL TABLES FROM my_new_project;
```

On execution, we get:

```sql
+------------------------------+-------------+
| Tables_in_my_new_project     | Table_type  |
+------------------------------+-------------+
| models                       | BASE TABLE  |
| models_versions              | BASE TABLE  |
| my_model                     | MODEL       |
| my_view                      | VIEW        |
+------------------------------+-------------+
```

## The `models` and `models_versions` Tables

The `mindsdb` project and every project that you create contain these two tables by default:

* The `models` table stores information about the modes within the project, such as `name`, `status`, `accuracy`, and more.

* The `models_versions` table stores information about all present and past versions of each model.

For more information on the `models` and `models_versions` tables, visit our [docs on the `PROJECT` entity](/sql/project/).

## The `files` Database

It is another default database that stores all the files uploaded by you to MindsDB Cloud.

Here is how you can [upload files to MindsDB](/sql/create/file/).
