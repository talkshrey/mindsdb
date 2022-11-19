*Communtiy Author: [PWiederspan](https://github.com/PWiederspan)*

## Pre-requisites
This tutorial will be easier to follow if you have first read:
- [Getting Started Guide](/info)
- [Getting Started with Cloud](/setup/cloud)

And have downloaded [this](https://www.kaggle.com/datasets/yasserh/spamemailsdataset?select=Spam.csv) dataset.

# Filtering Spam Emails
Anyone with an email address has experienced it, you open your inbox to find a random email promising a cash reward if you click now. Or maybe it’s sneakier, a tracking link for a package you don’t remember ordering. Spam emails are annoying for anyone, they clutter your inbox and send unnecessary push notifications, but they can be security risks as well. Whether a malicious tracking link in an official looking email, or a phishing scam asking you to confirm credentials, Spam emails are a serious concern for any IT department. Luckily, modern email clients have robust spam filters which remove potentially harmful emails from the inbox and label them as spam. Many major email providers use Machine Learning to analyze incoming emails and determine whether or not they are spam. Let's take a look at how MindsDB can be used to do this from a dataset of about 4600 emails.

## Upload the Dataset File
If you are planning on using MindsDB to make predictions based on your own dataset, you probably have that data in a database, in which case you would want to follow the steps described in the [Getting Started Guide](/info), mentioned in the prerequisite section, to connect MindsDB to your database.

For this tutorial we will be using the MindsDB cloud editor. If you haven’t familiarized yourself with it, now is a great time to do so.

From the main page in the editor, select the “Upload File” button in the top right corner. Then from the new page, browse local files and select the correct Spam Emails CSV, name it appropriately (in this tutorial we use spam_predict), and select the “Save and Continue” button.

When the upload is complete it should take you back to the main editor page with something like this in the query box:

```sql
--- MindsDB ships with a filesystem database called 'files'
--- Each file you uploaded is saved as a table there.
---
--- You can always check the list tables in files as follows:

SHOW TABLES FROM files;
```

Selecting the “Run” button in the top left corner, or pressing Shift+Enter, will run the query and you should see a list of all files uploaded in the bottom section.

## Create A Predictor

For this particular dataset each row represents a single email, with each column representing the frequency of a given word or symbol in that email. There are also columns for the total, average, and longest run of capital letters throughout the email.

First we need to switch to using the mindsdb database.

```sql
USE mindsdb;
```

We will start by training a model with the CREATE MODEL command using all columns from the dataset we uploaded.

```sql
CREATE MODEL mindsdb.spam_predictor
FROM files
    (SELECT * FROM spam_predict)
PREDICT Spam;
```

We can check the status of the model by querying the name we used as the predictor. As this is a larger dataset, the status may show “Generating” or “Training” for a few minutes. Re-run the query to refresh.

```sql
SELECT *
FROM mindsdb.models
WHERE name='spam_predictor';
```

When the model has finished training the status will change to "complete".

On execution, we get:

```sql
+----------------+----------+--------------------+-------------+------------------+------------------+-------+--------------------+------------------+
| name           | status   | accuracy           | predict     | update_status    | mindsdb_version  | error | select_data_query  | training_options |
+----------------+----------+--------------------+-------------+------------------+------------------+-------+--------------------+------------------+   
| spam_predictor | complete | 0.9580387730450108 | Spam        | up_to_date       | 22.4.2.1         | null  |                    |                  |
+----------------+----------+--------------------+-------------+------------------+------------------+-------+--------------------+------------------+
```

You have just created and trained the Machine Learning Model with approximately 96% accuracy!


## Make Predictions

We will now begin to make predictions about whether a given email is spam using the model we just trained.

The generic syntax to make predictions is:

```sql
SELECT t.column_name1, t.column_name2
FROM integration_name.table AS t
JOIN mindsdb.predictor_name AS p
WHERE t.column_name IN (value1, value2, ...);
```

For our prediction we will query the spam, spam_confidence, and spam_explain columns from the spam_predictor model we trained. To simulate a test email we will provide values for several in the WHERE clause representing various word frequencies and capital letter runs.

```sql
SELECT spam, spam_confidence, spam_explain
FROM mindsdb.spam_predictor
WHERE word_freq_internet=2.5
AND word_freq_email=2
AND word_freq_credit=0.9
AND word_freq_money=0.9
AND word_freq_report=1.2
AND word_freq_free=1.2
AND word_freq_your=0.9
AND word_freq_all=2.4
AND capital_run_length_average = 20
AND word_freq_mail=1
AND capital_run_total=20
AND capital_run_longest=20;
```

On execution, we get:

```sql
+-------+-------------------+-------------------------------------------------------------------------------------------+
| spam  | spam_confidence   | spam_explain                                                                              |
+-------+-------------------+-------------------------------------------------------------------------------------------+
| 1     | 0.956989247311828 | {"predicted_value": "1", "confidence": 0.956989247311828, "anomaly": null, "truth": null} |
+-------+-------------------+-------------------------------------------------------------------------------------------+
```

With this output we can see that MindsDB predicts that this is a spam email with approximately 96% accuracy.

You can change these values and add additional word frequency columns to the query as you see fit to get different predictions.


## Batch Predictions

In the example above, we saw how we can use MindsDB to determine if a single email is spam, however, in a lot of cases we want to determine if any email in an inbox is spam. We can do batch predictions using the JOIN command. By joining our spam_predictor table on a query of our dataset, we can see MindsDB prediction for each row alongside the actual spam value for each email.

The generic syntax to do this is:

```sql
SELECT t.column_name1, t.column_name2
FROM integration_name.table AS t
JOIN mindsdb.predictor_name AS p
WHERE t.column_name IN (value1, value2, ...);
```
As we are using the original dataset, which contains 58 columns, we will only include a few of them. The important column for the purposes of this tutorial is the “spam” column for both tables, which we can use to check the predictions accuracy.

```sql
SELECT t.word_freq_internet, t.word_freq_email, t.word_freq_credit,
       t.word_freq_money, t.word_freq_report, t.capital_run_length_longest,
       t.spam, p.spam AS predicted_spam
FROM files.spam_predict AS t
JOIN mindsdb.spam_predictor AS p;
```

On execution, we get:

```sql
+--------------------+-----------------+------------------+-----------------+------------------+---------------------------+-------+----------------+
| word_freq_internet | word_freq_email | word_freq_credit | word_freq_money | word_freq_report | capital_run_length_longest| spam  | spam_predictor |
+--------------------+-----------------+------------------+-----------------+------------------+---------------------------+-------+----------------+   
| 0                  | 0               | 0                | 0               | 0                | 9989                      | 1     | 1              |   
| 0                  | 0               | 0                | 0               | 0                | 99                        | 1     | 1              |   
| 0                  | 0.21            | 0                | 0               | 0                | 99                        | 1     | 1              |   
| 0                  | 0               | 0                | 0               | 0                | 99                        | 1     | 1              |   
| 0                  | 0               | 0                | 0               | 0                | 99                        | 1     | 1              |
+--------------------+-----------------+------------------+-----------------+------------------+---------------------------+-------+----------------+
```

With the ability to scroll through all 4600 rows, broken up 100 per page. You can now see predictions for a whole dataset!

## What we learned

In this tutorial we learned how to :
- Upload a dataset into MindsDB Cloud
- Create a MindsDB Predictor
- Train our Model using MindsDB
- Make individual predictions by providing sample data
- Make batch predictions by joining a Predictor with a Dataset
