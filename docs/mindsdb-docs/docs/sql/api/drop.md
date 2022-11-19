# `#!sql DROP MODEL` Statement

## Description

The `#!sql DROP MODEL` statement deletes the model table.

## Syntax

Here is the syntax:

```sql
DROP MODEL [predictor_name];
```

On execution, we get:

```sql
Query OK, 0 rows affected (0.058 sec)
```

Where:

| Name               | Description                      |
| ------------------ | -------------------------------- |
| `[predictor_name]` | Name of the model to be deleted. |

## Example

Let's list all the available predictor tables.

```sql
SELECT name
FROM mindsdb.models;
```

On execution, we get:

```sql
+---------------------+
| name                |
+---------------------+
| other_model         |
| home_rentals_model  |
+---------------------+
```

Now we delete the `home_rentals_model` table.

```sql
DROP MODEL home_rentals_model;
```

On execution, we get:

```sql
Query OK, 0 rows affected (0.058 sec)
```

We can check if the deletion was successful by querying the `mindsdb.models` table again.

```sql
SELECT name
FROM mindsdb.models;
```

On execution, we get:

```sql
+---------------------+
| name                |
+---------------------+
| other_model         |
+---------------------+
```
