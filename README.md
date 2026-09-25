# BHS Lost and Found

A digitised version of the lost property system at BHS. Users can upload items they've found, submit requests for items they've lost, and admins can match and return items, with email notifications sent along the way.

For videos of the website in action click here --> https://www.youtube.com/playlist?list=PLBvyGZ1emK9U 

## Setup

### 1. Install the requirements

From the project folder, run:

```
pip install -r requirements.txt
```

This installs Flask and the extensions the app needs (Flask-Login, Flask-Mail, Flask-Session, Flask-SQLAlchemy).

### 2. Create `auth.py`

The app needs an `auth.py` file in the same folder as `app.py` to send emails. This file isn't included in the project, since it holds a real email login. Create a new file called `auth.py` with the following three variables:

```python
sender_email = "your.email@example.com"
sender_email_password = "your-app-password"
domain_name = "@burnside.school.nz"
```

- `sender_email` — the Gmail address the app sends emails from, as a string.
- `sender_email_password` — an app password for that Gmail account (not the normal account password — see below), as a string.
- `domain_name` — set to `"@burnside.school.nz"`. The app appends this to a user's school code to get their email address.

If `auth.py` is missing, or the details in it don't work, the app still runs. Instead of sending real emails, it prints the email contents (including confirmation codes) to the terminal, so it can still be tested without an email login set up.

### 3. Run the app

```
python app.py
```

The app runs at `http://127.0.0.1:5000` by default.

## Creating a Gmail app password

`sender_email_password` needs to be an **app password**, not the Gmail account's normal login password. Google only allows app passwords once 2-Step Verification is turned on. It's recommended to use a spare or throwaway Gmail account for this rather than a personal one, since the app password gives the app full access to send mail from it.

1. Go to [myaccount.google.com](https://myaccount.google.com) and sign in to the Gmail account you want to send from.
2. In the left-hand menu, click **Security**.
3. Under "How you sign in to Google", check whether **2-Step Verification** is on. If it's off, click it and follow the prompts to turn it on. App passwords aren't available until this is done.
4. Still under **Security**, click **2-Step Verification**. You may need to sign in again to confirm it's you.
5. Scroll down to **App passwords** and click it.
6. Type a name for the app (e.g. `BHS Lost and Found`) and click **Create**.
7. Google will show a 16-character password. Copy it exactly as shown, without spaces, and paste it in as `sender_email_password` in `auth.py`. It's only shown once, so if you lose it, generate a new one.

If **App passwords** doesn't appear under Security, it usually means 2-Step Verification isn't fully turned on yet, or the account is managed by a school/workplace that has app passwords disabled.

You can revoke an app password at any time from the same **App passwords** page, which immediately stops it from being able to send email.

## Notes

- `auth.py`, the SQLite database file, and the session folder are all excluded from the repository via `.gitignore`, since they either hold secrets or are recreated automatically.
- If the database schema changes (for example, new columns), delete the existing `.db` file and let the app recreate it — the old data won't carry over automatically.
