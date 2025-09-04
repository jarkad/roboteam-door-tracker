# RFID Tracker

## Get started

First, [install UV](https://docs.astral.sh/uv/getting-started/installation/).

Most things are done using the `manage.py` script. Launch it like this:

```
cd door_tracker
uv run manage.py
```

> [!WARNING]
> You must be in the door_tracker directory, or the script won't launch.

### Bring your database up-to-date

```
uv run manage.py migrate
```

### Create yourself an account for the admin page

```
uv run manage.py createsuperuser
```

Don't worry much about this account, it only exists on your machine.

### Recover your password

```
uv run manage.py changepassword
```

### Create a migration (run this every time you change `models.py`!)

```
uv run manage.py makemigrations
```

Don't forget to apply your new migration.

### Launch the development server

```
uv run manage.py runserver
```
