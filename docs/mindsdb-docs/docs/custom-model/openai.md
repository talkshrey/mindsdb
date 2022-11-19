# MindsDB and OpenAI

OpenAI facilitates building and deploying ML models.

## How to Bring the OpenAI Model to MindsDB

To bring your OpenAI model to MindsDB, run the `#!sql CREATE MODEL` statement as below.

```sql
CREATE MODEL mindsdb.openai_model
PREDICT target_text_column
USING 
    format='openai',
    APITOKEN='yourapitoken'
    data_dtype={"0": "integer", "1": "integer"};
```

Now you can query the `mindsdb.models` table to see your model.

```sql
SELECT *
FROM mindsdb.models
WHERE name='openai_model';
```

Check out the guide on the [`#!sql SELECT`](/sql/api/select/) statement to see how to get the predictions.
