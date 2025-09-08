# RFID Tracker

## Get started

1. [Install VSCode](https://code.visualstudio.com/).

2. When you open the repo, you should see the notification `Do you
   want to install the recommended extensions from Microsoft for this
   repository?`. Click `Install`.

3. A new notification should open: `Folder contains a Dev Container
   configuration file. Reopen folder to develop in a container (learn
   more).`. Press `Reopen in Container`.

4. You should see `Running the onCreateCommand from
   devcontainer.json...` in the terminal. This will take a minute or
   two. Lean back and relax.

5. After a while, you'll see `dev: command not found` in the terminal.
   Wait for a minute, and if it doesn't disappear, run `direnv: Reset
   and reload environment`.

6. VSCode should restart. Congrats, you have won!

7. (optional) If you don't have a local database yet, run the `scripts:
   init` task. It'll create a new database and a user for you.

## Development server

The development server should start automatically. If it dies, or you
want to restart it, press <kbd>Ctrl+Shift+B</kbd>. You might need to
press <kbd>Enter</kbd> afterwards.

> [!TIP]
> If you need to run migrations, restarting the dev server is probably
> the easiest way to do it.

## Daily operations

Most common operations are available from `Tasks: Run Task`. They come in three flavours:

1. scripts: these perform common tasks. You'll run them the most often
   They are also available in the terminal.

2. packages: these build parts of the project. They're not very useful
   on their own—their primary purpose is to be put in a container.

3. containers: these build & upload docker containers to Docker Hub.

### Scripts

To create a new database, run `init`. It'll set up a new admin user.
It's safe to run this command if you already have a database.

The most-used script is `makemigrations`. it creates migrations (d'oh!).
Run it when you change `models.py`.

If a tutorial, Stack Overflow, etc. asks you to run `python manage.py
foo bar`, run `django foo bar` instead. This script works from any
directory, in contrast to `manage.py`.

## Pitfalls

### Pre-commit

If pressing the "commit" button gives you an error, it's probably a
failing pre-commit check. Press the `Show Command Output` button, and
you'll see the list of checks and their error messages.

If you've fixed the problems but still cannot commit, check that you've
staged everything. Some pre-commit hooks run code formatters, and you
need to manually stage their output.

### Devcontainers

On first load, you'll see notifications like "cannot find git
executable". This is normal. After a while, vscode will restart and
those notifications should go away. This might take a minute on first
boot.

### Direnv

direnv extension fails silently. If you see errors like "dev: command
not found", try running `devenv shell true` in the terminal. It should
finish with no errors. If it didn't, then Dmytro broke Nix again.

Terminal will not pick up the new environment until you restart it. You
should see a warning sign if direnv wants you to do it.
