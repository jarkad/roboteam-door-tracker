# RFID Tracker

## Get started

First, [install UV](https://docs.astral.sh/uv/getting-started/installation/).

Most things are done using the `manage.py` script. Launch it like this:

```
uv run door_tracker/manage.py
```

### Create yourself an account for the admin page

```
uv run door_tracker/manage.py createsuperuser
```

Don't worry much about this account, it only exists on your machine.

If you get an error, try migrating the database first.

### Launch the development server

```
uv run door_tracker/manage.py runserver
```

### Create a migration (do this every time you change `models.py`!)

```
uv run door_tracker/manage.py makemigrations
```

### Bring your database up-to-date

```
uv run door_tracker/manage.py migrate
```
