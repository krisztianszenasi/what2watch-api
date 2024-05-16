# what2watch

**what2watch** is `REST-api`  written in **python**  that I made as an
assignment for my [promptenginerring](https://portal.vik.bme.hu/kepzes/targyak/VITMAV82/hu/)
class at [budapest institue of economy and engineering](https://www.bme.hu/).

## Installation and First Steps

### 1. Simply clone the git repository then install the **requirements** via **pip**.

```
pip install -r requirements.txt
```

> I recommend using a **python virtual enviroment** for example [pyenv](https://github.com/pyenv/pyenv)


### 2. Set the environmental variables

Here is a template for the `.env` file. It should be created at the root of the project.

```
FLASK_APP=what2watch
OPENAI_API_KEY=...
VIDEO_LENGTH_LIMIT=...
```

`VIDEO_LENGTH_LIMIT` can be used to limit how long videos can be used for the `llm`
requests. It defaults to 15 minutes. Use `-1` if you want no limits.
The reason for the limit is the prevent requesting **summaries** and **key points** for
longer videos which can result in wasting a lot of **tokens**.

### 3. Initialize the database

The project uses [Flask-SQLAlchemy](https://pypi.org/project/Flask-SQLAlchemy/) for
storing objects permanently in a **sqlite** database with [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/).

```
flask db init
flask db migarte -m "initial"
flask db upgrade
```

### 3. start the development server

```
flask run
```

## Running Tests

The project uses the [Flask-Testing](https://pythonhosted.org/Flask-Testing/) package.

To run tests execute the following command:

```
python -m unittest
```

## Used Technologies / Packages

* [Flask](https://flask.palletsprojects.com/en)
* [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en)
* [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)
* [Langchain](https://www.langchain.com/)
* [OpenAI](https://platform.openai.com/docs/api-reference)
  