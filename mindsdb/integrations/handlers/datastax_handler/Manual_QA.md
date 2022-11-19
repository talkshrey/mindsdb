# Welcome to the MindsDB Manual QA Testing for Datastax Handler

> **Please submit your PR in the following format after the underline below `Results` section. Don't forget to add an underline after adding your changes i.e., at the end of your `Results` section.**

## Testing Datastax Handler with [Dataset Name](URL to the Dataset)

**1. Testing CREATE DATABASE**

```
COMMAND THAT YOU RAN TO CREATE DATABASE.
```

![CREATE_DATABASE](Image URL of the screenshot)

**2. Testing CREATE PREDICTOR**

```
COMMAND THAT YOU RAN TO CREATE PREDICTOR.
```

![CREATE_PREDICTOR](Image URL of the screenshot)

**3. Testing SELECT FROM PREDICTOR**

```
COMMAND THAT YOU RAN TO DO A SELECT FROM.
```

![SELECT_FROM](Image URL of the screenshot)

### Results

Drop a remark based on your observation.
- [ ] Works Great 💚 (This means that all the steps were executed successfuly and the expected outputs were returned.)
- [ ] There's a Bug 🪲 [Issue Title](URL To the Issue you created) ( This means you encountered a Bug. Please open an issue with all the relevant details with the Bug Issue Template)

---

## Testing Datastax Handler with [Car Price Prediction](https://www.kaggle.com/datasets/vijayaadithyanvg/car-price-predictionused-cars?resource=download)

**1. Testing CREATE DATABASE**

![datastax](https://user-images.githubusercontent.com/14253061/198587747-1552b988-4d61-482f-a4f5-efdf0c1b6074.PNG)

There's a Bug with loading the bundle because of which connection could not be established. [[Manual QA] Test Datastax Handler Manually
](https://github.com/mindsdb/mindsdb/issues/3632#)

---
