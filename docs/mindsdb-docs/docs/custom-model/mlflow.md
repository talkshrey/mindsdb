# MindsDB and MLflow

MLflow allows you to create, train, and serve machine learning models, apart from other features, such as organizing experiments, tracking metrics, and more.

Here, we present two usage examples of the MLflow.

## Simple Example of Logistic Regression

Currently, there is no way to train an MLflow-wrapped model using the API. The training of the model takes place outside of MindsDB. The data must be pulled manually, for example, with a script. It is a good idea to use an MLflow run or experiment.

### Creating the MLflow Model

We start by writing a script that creates and trains the model. After that, the script is saved using one of the saving methods offered by MLflow.

Here, we use the model from [this simple tutorial](https://github.com/mlflow/mlflow#saving-and-serving-models) and [the `mlflow.sklearn.log_model` method](https://github.com/mlflow/mlflow/blob/9781af9c0898827bf616a8f159168477a69036dd/examples/sklearn_logistic_regression/train.py#L15). Please note that the model must be a scikit-learn model.

Once your model is trained, ensure that it is served and listens for input at a URL of your choice. Please note that your model may run on a different machine than the one where MindsDB runs. Here, we assume the URL to be `http://localhost:5000/invocations`, as in the tutorial.

Let's run the `train.py` script that provides us with the `<run-id>` value for the model.

```bash
$ python examples/sklearn_logistic_regression/train.py
Score: 0.666
Model saved in run <run-id>
```

Now, let's execute the following command from the directory where the model resides, providing the `<run-id>` value.

```bash
$ mlflow models serve --model-uri runs:/<run-id>/model
```

We're ready to move to MindsDB.

### Bringing the MLflow Model to MindsDB

We execute the command below to create a predictor in MindsDB based on the created model.

```sql
CREATE MODEL mindsdb.byom_mlflow 
PREDICT `1`  -- `1` is the target column name
USING 
    url.predict='http://localhost:5000/invocations', 
    format='mlflow', 
    data_dtype={"0": "integer", "1": "integer"};
```

Now, you can fetch predictions using the standard MindsDB syntax. Follow the guide on the [`#!sql SELECT`](/sql/api/select/) statement to learn more.

```sql
SELECT `1`
FROM byom_mlflow
WHERE `0`=2;
```

## Advanced Example of Keras NLP Model

Before we start, download [the natural language processing (NLP) dataset from Kaggle](https://www.kaggle.com/c/nlp-getting-started) to reproduce the steps of this example.

Here, we look at the best practices when your model needs custom data preprocessing, which is quite common.

We use the `mlflow.pyfunc` module to complete the following:

- Save the model using `mlflow.pyfunc.save_model`.
- Subclass `mlflow.pyfunc.PythonModel` to wrap the model in a way compatible with MLflow that enables our custom inference logic to be called.

### Creating the MLflow Model

In the script that trains the model, like [this one](/custom-model/ray-serve/#example-keras-nlp-model) or [that one](#full-script), there should be a call to the `mlflow.pyfunc.save_model` function at the end. It is to save every produced artifact.

```python
mlflow.pyfunc.save_model(
    path="nlp_kaggle",
    python_model=Model(),
    conda_env=conda_env,
    artifacts=artifacts
)
```

Here, `artifacts` is a dictionary storing all the expected output after running the training phase. In this case, we want both a model and a tokenizer to preprocess the input text. And `conda_env` specifies the environment in which your model is executed when it is served in a self-contained conda environment. It should include all the required packages and dependencies, like below:

```python
# these are accessible inside the Model() wrapper
artifacts = {
    'model': model_path,
    'tokenizer_path': tokenizer_path,
}

# specs for an environment that is created when serving the model
conda_env = {
    'name': 'nlp_keras_env',
    'channels': ['defaults'],
    'dependencies': [
        'python=3.8',
        'pip',
        {
            'pip': [
                'mlflow',
                'tensorflow',
                'cloudpickle',
                'nltk',
                'pandas',
                'numpy',
                'scikit-learn',
                'tqdm',
            ],
        },
    ],
}
```

Finally, to store the model, you need to provide the wrapper class that loads all the produced artifacts into an accessible "context" and implements all the required inference logic.

```python
class Model(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # we use paths in the context to load everything
        self.model_path = context.artifacts['model']
        self.model = load_model(self.model_path)
        with open(context.artifacts['tokenizer_path'], 'rb') as f:
            self.tokenizer = pickle.load(f)

    def predict(self, context, model_input):
        # preprocess input, tokenize, pad, and call the model
        df = preprocess_df(model_input)
        corpus = create_corpus(df)
        sequences = self.tokenizer.texts_to_sequences(corpus)
        tweet_pad = pad_sequences(sequences, 
                                  maxlen=MAX_LEN, 
                                  truncating='post', 
                                  padding='post')
        df = tweet_pad[:df.shape[0]]

        y_pre = self.model.predict(df)
        y_pre = np.round(y_pre).astype(int).flatten().tolist()

        return list(y_pre)
```

Here, we load multiple artifacts and use them to guarantee the input data is in the same format that was used for training. Ideally, you would abstract this even further into a single `preprocess` method that is called both at the training time and at the inference time.

Finally, we start serving by going to the directory where you called the script above and executing the `mlflow models serve --model-uri ./nlp_kaggle` command.

### Bringing the MLflow Model to MindsDB

We execute the command below to create a predictor in MindsDB based on the created model.

```sql
CREATE MODEL mindsdb.byom_mlflow_nlp
PREDICT `target`
USING 
    url.predict='http://localhost:5000/invocations',
    format='mlflow',
    dtype_dict={"text": "rich text", "target": "binary"};
```

Now, you can fetch predictions using the standard MindsDB syntax. Follow the guide on the [`#!sql SELECT`](/sql/api/select/) statement to learn more.

You can directly pass input data in the `#!sql WHERE` clause to get a single prediction.

```sql
SELECT target
FROM mindsdb.byom_mlflow_nlp
WHERE text='The tsunami is coming, seek high ground';
```

Or you can `#!sql JOIN` the model with a data table to get bulk predictions. Here, ensure that the data table exists and the database it belongs to is connected to your MindsDB instance.

```sql
SELECT ta.text,
       tb.target AS predicted
FROM db_byom.test.nlp_kaggle_test AS ta
JOIN mindsdb.byom_mlflow_nlp AS tb;
```

### Full Script

For your reference, here is the full script that trains and saves the model.

```python
import re
import pickle
import string

import mlflow.pyfunc

import nltk
import tqdm
import sklearn
import tensorflow
import cloudpickle
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from tensorflow.keras.initializers import Constant
from tensorflow.keras.layers import Embedding, LSTM, Dense, SpatialDropout1D
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import load_model


stop = set(stopwords.words('english'))

MAX_LEN = 100
GLOVE_DIM = 50
EPOCHS = 10


def preprocess_df(df):
    df = df[['text']]
    funcs = [remove_URL, remove_html, remove_emoji, remove_punct]
    for fn in funcs:
        df['text'] = df['text'].apply(lambda x: fn(x))
    return df


def remove_URL(text):
    url = re.compile(r'https?://\S+|www\.\S+')
    return url.sub(r'', text)


def remove_html(text):
    html = re.compile(r'<.*?>')
    return html.sub(r'', text)


def remove_punct(text):
    table = str.maketrans('', '', string.punctuation)
    return text.translate(table)


def remove_emoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def create_corpus(df):
    corpus = []
    for tweet in tqdm.tqdm(df['text']):
        words = [word.lower() for word in word_tokenize(tweet) if ((word.isalpha() == 1) & (word not in stop))]
        corpus.append(words)
    return corpus


class Model(mlflow.pyfunc.PythonModel):

    def load_context(self, context):

        self.model_path = context.artifacts['model']
        with open(context.artifacts['tokenizer_path'], 'rb') as f:
            self.tokenizer = pickle.load(f)
        self.model = load_model(self.model_path)

    def predict(self, context, model_input):

        df = preprocess_df(model_input)
        corpus = create_corpus(df)
        sequences = self.tokenizer.texts_to_sequences(corpus)
        tweet_pad = pad_sequences(sequences, maxlen=MAX_LEN, truncating='post', padding='post')
        df = tweet_pad[:df.shape[0]]

        y_pre = self.model.predict(df)
        y_pre = np.round(y_pre).astype(int).flatten().tolist()

        return list(y_pre)


if __name__ == '__main__':
    train_model = True

    model_path = './'
    tokenizer_path = './tokenizer.pkl'
    run_name = 'test_run'
    mlflow_pyfunc_model_path = "nlp_kaggle"
    mlflow.set_tracking_uri("sqlite:///mlflow.db")

    if train_model:

        # preprocess data
        df = pd.read_csv('./train.csv')
        target = df[['target']]
        target_arr = target.values
        df = preprocess_df(df)
        train_corpus = create_corpus(df)

        # load embeddings
        embedding_dict = {}
        with open('./glove.6B.50d.txt', 'r') as f:
            for line in f:
                values = line.split()
                word = values[0]
                vectors = np.asarray(values[1:], 'float32')
                embedding_dict[word] = vectors
        f.close()

        # generate and save tokenizer
        tokenizer_obj = Tokenizer()
        tokenizer_obj.fit_on_texts(train_corpus)

        with open(tokenizer_path, 'wb') as f:
            pickle.dump(tokenizer_obj, f)

        # tokenize and pad
        sequences = tokenizer_obj.texts_to_sequences(train_corpus)
        tweet_pad = pad_sequences(sequences, maxlen=MAX_LEN, truncating='post', padding='post')
        df = tweet_pad[:df.shape[0]]

        word_index = tokenizer_obj.word_index
        num_words = len(word_index) + 1
        embedding_matrix = np.zeros((num_words, GLOVE_DIM))

        # fill embedding matrix
        for word, i in tqdm.tqdm(word_index.items()):
            if i > num_words:
                continue

            emb_vec = embedding_dict.get(word)
            if emb_vec is not None:
                embedding_matrix[i] = emb_vec

        X_train, X_test, y_train, y_test = train_test_split(df, target_arr, test_size=0.15)

        # generate model
        model = Sequential()
        embedding = Embedding(num_words,
                              GLOVE_DIM,
                              embeddings_initializer=Constant(embedding_matrix),
                              input_length=MAX_LEN,
                              trainable=False)
        model.add(embedding)
        model.add(SpatialDropout1D(0.2))
        model.add(LSTM(64, dropout=0.2, recurrent_dropout=0.2))
        model.add(Dense(1, activation='sigmoid'))

        optimizer = Adam(learning_rate=1e-5)
        model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

        # train and save
        model.fit(X_train, y_train, batch_size=4, epochs=EPOCHS, validation_data=(X_test, y_test), verbose=2)
        model.save(model_path)

    # save in mlflow format
    artifacts = {
        'model': model_path,
        'tokenizer_path': tokenizer_path,
    }

    conda_env = {
        'channels': ['defaults'],
        'dependencies': [
            'python=3.8',
            'pip',
            {
                'pip': [
                    'mlflow',
                    'tensorflow=={}'.format(tensorflow.__version__),
                    'cloudpickle=={}'.format(cloudpickle.__version__),
                    'nltk=={}'.format(nltk.__version__),
                    'pandas=={}'.format(pd.__version__),
                    'numpy=={}'.format(np.__version__),
                    'scikit-learn=={}'.format(sklearn.__version__),
                    'tqdm=={}'.format(tqdm.__version__)
                ],
            },
        ],
        'name': 'nlp_keras_env'
    }

    # Save and register the MLflow Model
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.pyfunc.save_model(
            path=mlflow_pyfunc_model_path,
            python_model=Model(),
            conda_env=conda_env,
            artifacts=artifacts)

        result = mlflow.register_model(
            f"runs:/{run.info.run_id}/{mlflow_pyfunc_model_path}",
            f"{mlflow_pyfunc_model_path}"
        )
```
