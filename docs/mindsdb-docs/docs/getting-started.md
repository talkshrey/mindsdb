# Getting Started

MindsDB can be integrated with the most popular databases, as well as with the DBT and MLFlow workflows.

To try out MindsDB right away without bringing in your own data or models, follow our [Quickstart Guide](/).

1. Choose your MindsDB installation path.

    === "MindsDB Cloud"

        Create your [free MindsDB Cloud account](https://cloud.mindsdb.com/signup).

    === "Docker"

        To get started with a Docker installation, follow the MindsDB installation instructions using [Docker](/setup/self-hosted/docker/).

    === "pip"

        You can also install MindsDB from source using pip [Windows](/setup/self-hosted/pip/windows/) , [Mac](/setup/self-hosted/pip/macos/), [Linux](/setup/self-hosted/pip/linux/), 

1. Open your SQL client and connect to MindsDB.

    !!! Tip ""
        If you do not have a preferred SQL client yet, we recommend using the [MindsDB SQL Editor](https://cloud.mindsdb.com/editor) or [DBeaver Community Edition](https://dbeaver.io/download/). Follow [this guide](setup/cloud/) to set up your MindsDB SQL Editor. And [here](/connect/dbeaver/), you'll find how to connect to MindsDB from DBeaver.

    === "MindsDB Cloud"

        1. Create a new MySQL connection.

            ![DBeaver Create Connection](/assets/dbeaver-create-connection.png)
            
        2. Configure it using the following parameters, as well as the username and password you created above.

            ```
                Host: mysql.mindsdb.com
                Port: 3306
                Database: mindsdb
            ```

            ![DBeaver Configure Connection](/assets/dbeaver-configure-cloud-connection.png)

    === "Docker"

        1. Create a new MySQL connection.

            ![DBeaver Create Connection](/assets/dbeaver-create-connection.png)
            
        1. Configure it using the following parameters:

            ```
                Host: localhost
                Port: 47335
                Database: mindsdb
                Username: mindsdb
                Password: [leave it empty]
            ```

            ![DBeaver Configure Connection](/assets/dbeaver-configure-docker-connection.png)

1. Connect your data to MindsDB using [`CREATE DATABASE`](https://docs.mindsdb.com/sql/create/databases/).

    ![DBeaver Create Database](/assets/dbeaver-create-database.png)

1. You can now preview the available data with a standard `SELECT` statement.

    ![DBeaver Preview Data](/assets/dbeaver-preview-data.png)

1. Now you are ready to create your model, using [`CREATE MODEL`](https://docs.mindsdb.com/sql/create/predictor/). If you already have a model in MLFlow, you can connect to your model.

    === "MindsDB is creating my model"

        ![DBeaver Create Predictor](/assets/dbeaver-create-predictor-simple.png)

    === "My model is in MLflow"

        ```
        <div id="create-predictor">
        <style>
            #create-predictor code { background-color: #353535; color: #f5f5f5 }
        </style>
        
        mysql> CREATE MODEL mindsdb.home_rentals_predictor
            -> FROM example_data (select * from demo_data.home_rentals)
            -> PREDICT rental_price
            -> USING url.predict='http://host.docker.internal:1234/invocations',
            -> format='mlflow',
            -> dtype_dict={"alcohol": "integer", "chlorides": "integer", "citric acid": "integer", "density": "integer", "fixed acidity": "integer", "free sulfur dioxide": "integer", "pH": "integer", "residual sugar": "integer", "sulphates": "integer", "total sulfur dioxide": "integer", "volatile acidity": "integer"};
        Query OK, 0 rows affected (0.21 sec)
            
        </div>
        ```

1. The [`SELECT`](/sql/api/select) statement allows you to make predictions based on features.

    ![DBeaver Home Rentals Prediction](/assets/dbeaver-home-rentals-prediction.png)
    ![DBeaver Home Rentals Prediction Results](/assets/dbeaver-home-rentals-prediction-results.png)

1. To integrate your predictions into your DBT workflow, you will need to make four changes:

    === "profiles.yml"

        ```
        mindsdb:
            type: mysql
            host: mysql.mindsdb.com
            user: mindsdb.user@example.com
            password: mindsdbpassword
            port: 3306
            dbname: mindsdb
            schema: example_data
            threads: 1
            keepalives_idle: 0 # default 0, indicating the system default
            connect_timeout: 10 # default 10 seconds
        ```

    === "schema.yml"

        ```
        version: 2

        models:
              - name: predicted_rentals
                description: "Integrating MindsDB predictions and historical   data"
        ```

    === "predicted_rentals.sql"

        ```
        with predictions as (
            SELECT hrp.rental_price as predicted_price, hr.rental_price as actual_price
            FROM mindsdb.home_rentals_predictor hrp
            JOIN exampleData.demo_data.home_rentals hr
            WHERE hr.number_of_bathrooms=2 AND hr.sqft=1000;
        )
        select * from predictions;
        ```

    === "dbt_project.yml"

        ```
        models:
            home_rentals:
                +materialized: view
        ```
