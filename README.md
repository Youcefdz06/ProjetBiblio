<div align="center">

# 📚 ProjetBiblio

### A terminal library manager that actually respects your database credentials

*(a rare quality in student projects, we know)*

<p>
  <a href="https://github.com/Youcefdz06/ProjetBiblio">📖 Repository</a>
  &nbsp;•&nbsp;
  <a href="#-getting-started">▶️ Run it</a>
  &nbsp;•&nbsp;
  <a href="https://github.com/Youcefdz06/ProjetBiblio/releases/latest">⬇️ Download .exe</a>
  &nbsp;•&nbsp;
  <a href="#-the-library-shelves">🗂️ Architecture</a>
</p>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Turso](https://img.shields.io/badge/Turso-cloud_database-4FF8D2?style=flat-square&logo=sqlite&logoColor=111111)
![FastAPI](https://img.shields.io/badge/FastAPI-server-009688?style=flat-square&logo=fastapi&logoColor=white)
![Build](https://img.shields.io/badge/build-GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Status](https://img.shields.io/badge/status-learning_project-1F7A8C?style=flat-square)

</div>

<br>

> 💬 **ProjetBiblio** is a terminal-first library manager, built the way you'd
> actually want a client-server app built: the CMD client is just a pretty
> face that fires HTTPS requests, and the FastAPI server is the only thing
> on Earth that knows the Turso credentials. Revolutionary concept. We know.

## ✨ At A Glance

| Layer | What it does | Trusts your secrets? |
| --- | --- | --- |
| 💻 CMD client | Renders menus, sends HTTPS requests, judges your book choices silently | Never |
| 🌐 FastAPI server | Authenticates users, enforces permissions, does the actual thinking | Yes, exclusively |
| 🧑‍💼 Administrator | Adds books, edits stock, stares at sales stats | — |
| 🎓 Student | Browses, buys, rents, returns, and racks up a transaction history | — |
| 🗄️ Database | Turso, holding all the state so nobody has to `git commit` a `.db` file again | — |

## 🪵 The Library Shelves

<table>
  <tr>
    <td width="25%" align="center">💻<br><strong>CLIENT</strong><br><br><code>main.py</code><br>Terminal menus, powered by mild dread</td>
    <td width="25%" align="center">📡<br><strong>REQUESTS</strong><br><br><code>api_client.py</code><br>The only file allowed to know the API exists</td>
    <td width="25%" align="center">🔐<br><strong>SERVER</strong><br><br><code>api.py</code> · <code>auth.py</code> · <code>admin.py</code> · <code>user.py</code><br>Auth, roles, and business rules, now properly split up instead of living in one 900-line file</td>
    <td width="25%" align="center">🗄️<br><strong>DATABASE</strong><br><br><code>database.py</code><br>Private Turso access. The vault. Do not touch.</td>
  </tr>
  <tr>
    <td colspan="4" align="center">📕 📘 📗 📙 📕 📘 📗 📙 📕 📘 📗 📙<br>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</td>
  </tr>
</table>

## 🧭 The Current Journey

```text
CMD client
   |
   | HTTPS + expiring session token
   v
FastAPI server  ──(admin.py / user.py / auth.py handle the specifics)
   |
   | private Turso token, never leaves this box
   v
Turso database
```

### 🧑‍💼 Administrator path

1. Log in with an `admin` account.
2. Enter book details and prices. Try not to typo the price into four digits.
3. Review what you're about to commit to the shelves.
4. Confirm the entry. Congratulations, it's in Turso now, forever-ish.

### 🎓 Student path

1. Sign up, or log in if you already exist as a person in this system.
2. Browse book IDs, prices, and stock like it's 1998 but make it HTTPS.
3. Buy or rent a book — the API checks your balance so you can't cheat the economy.
4. Confirm the operation.
5. Check active rentals, due dates, and your ever-growing transaction history.
6. Return a rental before the 14-day timer judges you.

## ✅ What Works Now

- Role-based login using the `users` table.
- **Public sign-up flow** — new students no longer need an admin to hand-insert them into Turso.
- Public clients never receive the Turso URL or database token. Not even a little bit.
- Expiring server sessions protect every catalog and account endpoint.
- Admin permissions are checked server-side by the API — the menu isn't the security model, it's just the UI.
- Legacy plain-text passwords are upgraded to PBKDF2 automatically on next login. No migration script guilt required.
- Admin book creation with numeric validation for prices and stock (so "banana" is not a valid price).
- Admin book editing and inventory/sales statistics.
- Duplicate-book and database-error messages during inserts, instead of a silent shrug.
- Student stock display and purchase flow.
- Rental due dates set automatically to 14 days after checkout.
- Active-rental display, book returns, and transaction history.
- Transactional updates for stock, balance, purchases, and rentals — no half-finished writes.
- Turso-compatible foreign keys and database constraints.
- Automated API and schema tests in `tests/`.
- **CI-built Windows `.exe`** — GitHub Actions builds it on a real Windows runner and attaches it to the release, because cross-compiling PyInstaller from Linux is a myth told to scare junior devs.

## 🗺️ Project Map

```text
ProjetBiblio/
|-- main.py                  Public CMD client and role menus
|-- api_client.py            HTTPS communication with the API
|-- api.py                   FastAPI app, routes delegate out to:
|-- auth.py                  Login, sign-up, session handling
|-- admin.py                 Admin-only operations
|-- user.py                  Student-facing operations
|-- database.py              Private Turso connection and schema creation
|-- menus.py                 Interactive client menus
|-- utilities.py             Shared yes/no input helper
|-- tests/                   API and database test suite
|-- .github/workflows/       CI: builds the Windows .exe and uploads it to Releases
|-- render.yaml              Render deployment blueprint
|-- requirements-api.txt     Server dependencies
|-- requirements-client.txt  Public client dependency (just `requests`, we're not monsters)
|-- .env.example             Server-only Turso configuration
`-- README.md                You are here
```

## 🗃️ Database Design

The hosted Turso database has four related tables:

| Table | Purpose |
| --- | --- |
| `users` | Usernames, passwords (hashed, we promise), roles, and balances |
| `books` | Titles, authors, prices, and stock |
| `purchases` | Student purchase history |
| `rentals` | Rental records and return status |

Balances, prices, stock, and quantities are all protected at the schema level.
Books are unique by `title` + `author`, so no, you cannot accidentally list
*1984* four times because you fat-fingered the form.

## 🚀 Getting Started

### 1. 📥 Clone the project (owner/developer)

```bash
git clone https://github.com/Youcefdz06/ProjetBiblio.git
cd ProjetBiblio
```

### 2. 🧪 Test locally

```bash
python -m pip install -r requirements-dev.txt
```

Create a server-only `.env` (never commit this, we mean it):

```env
TURSO_DATABASE_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your-private-token
SESSION_TTL_HOURS=12
```

Start the API:

```bash
uvicorn api:app --reload
```

In another Windows terminal, point the client at your local API:

```bat
set PROJETBIBLIO_API_URL=http://127.0.0.1:8000
python main.py
```

### 3. ☁️ Deploy the API on Render

1. Open Render, choose **New → Blueprint**.
2. Connect this repository.
3. Render reads `render.yaml` and creates `projetbiblio-api`.
4. Paste in `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` when asked.
5. Deploy, then copy the resulting URL — something like:

```text
https://projetbiblio-api.onrender.com
```

That token stays in Render's private environment. The CMD client never sees it. Ever.

### 4. 🔗 Point the client at your API (one-time, owner-side)

Replace `DEFAULT_API_URL` in `api_client.py`:

```python
DEFAULT_API_URL = "https://projetbiblio-api.onrender.com"
```

This URL is public, not a secret — commit it. After this, nobody downloading
the client needs a `.env`, a Turso URL, or a Turso token. They just run the app.

### 5. 👤 Accounts

Students can now **sign up themselves** through the client. For manual seeding
(e.g. bootstrapping an admin), you can still insert directly:

```sql
INSERT INTO users (username, password, role, balance)
VALUES ('admin', 'admin123', 'admin', 0);
```

The first successful login upgrades any legacy plain-text password to a
salted PBKDF2 hash automatically — no manual migration needed.

### 6. ▶️ Just run the thing

Grab the latest `.exe` from **[Releases](https://github.com/Youcefdz06/ProjetBiblio/releases/latest)**
and double-click it like a normal person. Or, if you enjoy typing:

```bash
python -m pip install -r requirements-client.txt
python main.py
```

The client never asks for database credentials, because it will never need them.

### 7. 🏗️ Building the `.exe` yourself

You don't have to — CI does it for you on every manual trigger (Actions →
**Build Windows EXE** → Run workflow → give it a release tag). But if you're
nostalgic for doing things the hard way:

```bash
python -m pip install pyinstaller
pyinstaller --onefile --name ProjetBiblio main.py
```

Output lands in `dist/ProjetBiblio.exe`. PyInstaller only builds for the OS
it's running on, so do this on Windows — or just let the workflow handle it.

### 8. 🧫 Run the tests

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## ☁️ Turso Workflow

Only the FastAPI server ever loads `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN`.
It uses the `libsql` driver, creates missing schema objects on startup, and
handles every balance, stock, purchase, and rental transaction. The CMD
client receives nothing but an expiring session token — useless for touching
Turso directly, even if someone tried.

## 🛣️ Roadmap

- ~~Build and attach the Windows executable to GitHub Releases~~ ✅ done, automated, never doing it by hand again
- Add password-change endpoints alongside sign-up.
- Replace in-memory sessions with signed tokens or Redis before scaling past one worker.
- Add rate limiting for repeated failed logins, because someone will try.

## 🤝 Collaboration Notes

Shared learning project. Before pushing, do the polite thing:

```bash
git pull --rebase origin main
git status
git push origin main
```

Keep schema changes intentional, never commit `.env`, and describe database
migrations in the commit message — future you will not remember why you did that.

## 🔒 Security Note

Never commit `.env`, Turso tokens, or private database contents. The API
checks the authenticated user's role on every protected operation — the
client-side menu is not, and has never been, the security boundary. Legacy
passwords are accepted once and upgraded to PBKDF2; new account-management
code should store only hashes, no exceptions. In-memory sessions are fine for
this learning deployment with one API worker, and are intentionally wiped on
every restart.

<div align="center">

Built with Python, Turso, a lot of terminal prompts, and questionable amounts of coffee.

</div>
