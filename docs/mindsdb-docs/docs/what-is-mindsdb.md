# What is MindsDB?

Data that lives in your database is a valuable asset. MindsDB enables you to use your data and make forecasts. It speeds up the ML development process by bringing machine learning into the database.

With MindsDB, you can build, train, optimize, and deploy your ML models without the need for other platforms. And to get the forecasts, simply query your data and ML models. Read along to see some examples.

![Machine Learning in Database using SQL](/assets/what_is_mindsdb.png)

## What are AI Tables?

MindsDB brings machine learning into databases by employing the concept of AI Tables.

AI Tables are machine learning models stored as virtual tables inside a database. They facilitate making predictions based on your data. You can perform the time series, regression, and classification predictions within your database and get the output almost instantly by querying an AI Table with simple SQL statements.

## Deep Dive into the AI Tables

### Current Challenges

Let’s consider the following `income_table` table that stores the `income` and `debt` values.

```sql
SELECT income, debt 
FROM income_table;
```

On execution, we get:

```sql
+------+-----+
|income|debt |
+------+-----+
|60000 |20000|
|80000 |25100|
|100000|30040|
|120000|36010|
+------+-----+
```

A simple visualization of the data present in the `income_table` table is as follows:

<figure markdown> 
    ![Income vs Debt](/assets/sql/income_vs_debt.png){ width="800", loading=lazy  }
    <figcaption></figcaption>
</figure>

Querying the income table to get the `debt` value for a particular `income` value results in the following:

```sql
SELECT income, debt 
FROM income_table
WHERE income = 80000;
```

On execution, we get:

```sql
+------+-----+
|income|debt |
+------+-----+
|80000 |25100|
+------+-----+
```

And here is what we get:

<figure markdown> 
    ![Income vs Debt chart](/assets/sql/income_vs_debt_known_value.png){ width="800", loading=lazy  }
</figure>

But what happens when querying the table for an `income` value that is not present there?

```sql
SELECT income, debt
FROM income_table
WHERE income = 90000;
```

On execution, we get:

```sql
Empty set (0.00 sec)
```

When the `#!sql WHERE` clause condition is not fulfilled for any of the rows, no value is returned.

<figure markdown> 
    ![Income vs Debt query](/assets/sql/income_vs_debt_unknown_value.png){ width="800", loading=lazy  }
</figure>

When a table doesn’t have an exact match, the query returns an empty set or null value. This is where the AI Tables come into play!

### Solution Offered by MindsDB

Let’s create a `debt_model` model that allows us to approximate the `debt` value for any `income` value. We train the `debt_model` model using the data from the `income_table` table.

```sql
CREATE MODEL mindsdb.debt_model
FROM income_table 
PREDICT debt;
```

On execution, we get:

```sql
Query OK, 0 rows affected (x.xxx sec)
```

MindsDB provides the [`#!sql CREATE MODEL`](/sql/create/predictor/) statement. On execution of this statement, the predictive model works in the background, automatically creating a vector representation of the data that can be visualized as follows:

<figure markdown> 
    ![Income vs Debt model](/assets/sql/income_vs_debt_predictor.png){ width="800", loading=lazy  }
</figure>

Let’s now look for the `debt` value of some random `income` value. To get the approximated `debt` value, we query the `#!sql mindsdb.debt_model` model instead of the `#!sql income_table` table.

```sql
SELECT income, debt
FROM mindsdb.debt_model 
WHERE income = 90000;
```

On execution, we get:

```sql
+------+-----+
|income|debt |
+------+-----+
|90000 |27820|
+------+-----+
```

And here is how it looks:

<figure markdown> 
    ![Income vs Debt model](/assets/sql/income_vs_debt_prediction.png){ width="800", loading=lazy  }
</figure>

## Why Choose MindsDB?

### Shift to Data Analysis Paradigm

There is an ongoing transformational shift within the modern business world from the “what happened and why” based on historical data analysis to the “what will happen and how can we make it happen” based on machine learning predictive modeling.

<figure markdown> 
    ![Analytics](/assets/sql/analytics_shift.png){ width="600", loading=lazy  }
    <figcaption></figcaption>
</figure>

The success of your predictions depends both on the data you have available and the models trained with the data. Data Scientists and Data Engineers require efficient and easy-to-use tools to prepare the data for feature engineering, then training the models, and finally, deploying, monitoring, and managing these implementations for optimal prediction confidence.

### The Machine Learning Lifecycle

The ML lifecycle is a process that consists of the data preparation phase, modeling phase, and deployment phase. The diagram below presents all the steps included in each of the stages.

<figure markdown> 
    ![ML Workflow](/assets/sql/machine_learning_lifecycle.png){ width="600", loading=lazy  }
    <figcaption></figcaption>
</figure>

Current solutions for implementing machine learning encounter various challenges, such as time-consuming preparation, cleaning, and labeling of substantial amouts of data, and difficulties in finding qualified ML/AI data scientists.

The processes that must be followed by the ML/AI data scientists to implement machine learning include the following:
- feature engineering,
- building, training, and optimizing models,
- assembling, verifying, and deploying models to production,
- continuously monitoring and improving the models,
- continuously training the models, as they require multiple training iterations with existing data,
- extracting, transforming, and loading (ETL) data from one system to another, which is complicated and may lead to multiple copies of information.

A recent study has shown it takes 64% of companies a month up to over a year to deploy a machine learning model into production. Leveraging existing databases and automating all the aforementioned processes is called AutoML. AutoML has been gaining traction within enterprises for enabling non-experts to use machine learning models for practical applications.

## Why MindsDB?

Well, as with most names, we needed one. We like science fiction and [The Culture](https://en.wikipedia.org/wiki/The_Culture_(series)) series, where the AI super-smart entities are called *Minds*. So that's for the first part of our name.

As for the second part - the *DB*, it is quite self-explanatory. Although we will support all kinds of data in the future, but currently, our objective is to add intelligence to existing data stores and databases. Hence, the term *DB* comes along.

So there we have it, MindsDB.

And why the bear? We wanted to honor the open-source tradition of animals related to projects. We went for a bear because MindsDB was born at UC Berkeley, where the first codes were written. Then, we went a step further and decided for a polar bear.

## How to Help Democratize Machine Learning?

Here is what you can do:

- [X] Go ahead and try out MindsDB by following our tutorials, and in case of problems, you can always [report an issue here](https://github.com/mindsdb/mindsdb/issues/new/choose).

- [X] Are you familiar with Python? You can then help us out in resolving open issues. At first, have a look at [issues labeled with the `good first issue` tag](https://github.com/mindsdb/mindsdb/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22), as these should be easy to start.

- [X] You can also help us with documentation and tutorials. Here is how you can contribute by writing [documentation](https://docs.mindsdb.com/contribute/docs/) and [tutorials](https://docs.mindsdb.com/sql/tutorials/home-rentals/). Don't forget to follow the [style guide](https://docs.mindsdb.com/docs-rules/).

- [X] Share with your friends and spread the word about MindsDB.

- [X] Join our team! We are a fast-growing company, so we always have [a few open positions](https://mindsdb.com/careers/).
