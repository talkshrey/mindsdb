# Loan Default Prediction

## Introduction

A loan is money borroed to somone (debtor) with the intent to pay back at an agreed date. Ideally, things should go as planned but when the debtor fails to pay the person they borrowed the loan from (creditor), the debtor is said to have defaulted on the loan. This is what loan default is

**It is the event of a debtor not paying their loan...**

It is then important for creditors/loan companies to know/predict if a certain debtor will default or not. This is a problem that machine learning solves, this is a classification machine learning problem.

As with every machine learning problem, data is the major ingredient to solving it. The [dataset](https://zindi.africa/competitions/data-science-nigeria-challenge-1-loan-default-prediction/data) for this problem is from the [Zindi](https://zindi.africa) [Loan Default Prediction Challenge](https://zindi.africa/competitions/data-science-nigeria-challenge-1-loan-default-prediction) for [DSN](https://www.datasciencenigeria.org/)

This tutorial is to showcase how [MindsDB](https://docs.mindsdb.com) performs in solveing this problem. We will be exploring how we can use a machine learning model to classify negative and positive cases for predicitng loan default. MindsDB allows you to train your model from a .CSV format directly, and you will:

- Load your dataset 
- Create a predictor, and,
- Make predictions

## Load your dataset
### Data wrangling

if you go through the dataset, you will find that it is split into three different files, you will first wrangle the data to suit your requirements, 

Here, i use python to wrangle the data, you can however use your desired tool (excel perhaps...) or copy my snippet below...

```
# code snipet to join data

# iomport dependencies and read in data files
import pandas as pd 
import functools as ft
trainPerf = pd.read_csv('trainperf.csv')
trainDemographics = pd.read_csv('traindemographics.csv')

# join data together, clean and write to .csv
data = trainPerf.merge(trainDemographics, left_on='customerid', right_on='customerid')
data.drop_duplicates(inplace=True)
data.dropna(axis=1, inplace=True)
data.drop(['customerid', 'systemloanid'], axis=1, inplace=True) # remove id columns
data.to_csv('loanData.csv')
```

Now that the dataset has been cleaned and stored into a .csv file, you can upload it to MindsDB cloud...

### Using the MindsDB GUI

To use the MindsDB GUI, you will need to access the [MindsDB cloud tool](https://cloud.mindsdb.com/) and sign uo for an account if you haven't yet, and you will be automatically directed to the editor.

While on the editor, you can [add your data](https://cloud.mindsdb.com/data) via several means, but as earlier mentioned, you will upload your dataset as a .csv...

On the "Select your data source" screen, click on "Files" next to "Databaes" and you should see the screen below:

![import your file](mindsdb/docs/mindsdb-docs/docs/contribute/tutorials/screen1.png)

Click on the "Import File" icon and select your .csv file. 

Give your table a name and hit the "Save and Con"tinue" button. **NOTE: Use snake or camel casing when uploading files**

If you do all things well, you should see a result like this:

![View your first 10 rows](mindsdb/docs/mindsdb-docs/docs/contribute/tutorials/screen2.png)

Now that you have loaded your dataset, you are now to...

## Create a Predictor
Creating a predictor in MindsDB is as easy as four lines of code. Copy and paste the code below into your SQL editor to make a predictor

```
CREATE MODEL mindsdb.loanPredictor
FROM files (
    SELECT * FROM files.loanData
) PREDICT good_bad_flag;
```

If all is successfull, you should see this screen below:

![Query successfully completed](mindsdb/docs/mindsdb-docs/docs/contribute/tutorials/screen3.png)

To confirm this and view details of your model like the accuracy, use the following code:

```
SELECT * 
FROM mindsdb.models 
WHERE name='loanPredictor';
```

and you can see details of your model...

![Model details](mindsdb/docs/mindsdb-docs/docs/contribute/tutorials/screen4.png)

**PS: You can see the accuracy is low, this is probably due to low data...**

Now that you have created your prdictor model, now is time to...

## Make a prediction

You can use the folowing query to make a prediction... pay attention to use new/unseen/untrained data... 
**PS: Pay attention to highlight your prediction query and run it**

```
SELECT good_bad_flag
FROM mindsdb.loanPredictor
WHERE loannumber=1 AND approveddate='2022-07-04 10:12:66.000000' AND
creationdate='2022-07-04 08:10:00.000000' AND loanamount=100000 AND
totaldue=110000 AND termdays=30 AND birthdate='1986-11-04 00:00:00.000000' AND
bank_account_type='Savings' AND longitude_gps=3.3269784 AND latitude_gps=5.799699 AND
bank_name_clients='UBA';
```

and viola! you just made a prediction!

![Prediction!](mindsdb/docs/mindsdb-docs/docs/contribute/tutorials/screen5.png)

## Conclusion
And that's it you shining rockstar! you are now an ML Wizard making predictions straight from the data! This is a taste of the awesome power of MindsDB.
Some important things to note:

- More data improves the accuracy of the model
- Your table names should not contain spaces but should rather be in snake or camel casing
- Highlight your prediction query and run it to see result
- MinsDB is fast and very helpfull 

If you like this tutorial, kindly share and follow us for more.