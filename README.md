<div align="center">

# 📚 ProjetBiblio

### 🕯️ A quiet terminal library for books, members, and shared learning

<p>
  <a href="https://github.com/Youcefdz06/ProjetBiblio">📖 <strong>Repository</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="#getting-started">▶️ <strong>Run it</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="#the-library-shelves">🗂️ <strong>Explore the shelves</strong></a>
</p>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Turso](https://img.shields.io/badge/Turso-cloud_database-4FF8D2?style=flat-square&logo=sqlite&logoColor=111111)
![Status](https://img.shields.io/badge/status-learning_project-1F7A8C?style=flat-square)

</div>

<br>

> 💬 ProjetBiblio is a terminal-first library manager. A FastAPI server keeps the
> Turso credentials private, while the public CMD client only talks to the API.

## ✨ At A Glance

| Layer | What it does |
| --- | --- |
| 💻 CMD client | Displays menus and sends HTTPS requests |
| 🌐 FastAPI server | Authenticates users and enforces permissions |
| 🧑‍💼 Administrator | Adds, edits, and reviews catalog statistics |
| 🎓 Student | Browses, buys, rents, returns, and reviews history |
| 🗄️ Database | Stores shared data in Turso; credentials stay server-side |

## 🪵 The Library Shelves

<table>
  <tr>
    <td width="25%" align="center">💻<br><strong>CLIENT</strong><br><br><code>main.py</code><br>Terminal menus</td>
    <td width="25%" align="center">📡<br><strong>REQUESTS</strong><br><br><code>api_client.py</code><br>HTTPS client</td>
    <td width="25%" align="center">🔐<br><strong>SERVER</strong><br><br><code>api.py</code><br>Auth and business rules</td>
    <td width="25%" align="center">🗄️<br><strong>DATABASE</strong><br><br><code>database.py</code><br>Private Turso access</td>
  </tr>
  <tr>
    <td colspan="4" align="center">📕 📘 📗 📙 📕 📘 📗 📙 📕 📘 📗 📙<br>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</td>
  </tr>
</table>

## 🧭 The Current Journey

```text
CMD client
   |
   | HTTPS + session token
   v
FastAPI server
   |
   | private Turso token
   v
Turso database
```

### 🧑‍💼 Administrator path

1. Log in with an account whose role is `admin`.
2. Enter the book details and prices.
3. Review the displayed information.
4. Confirm the entry to save it in Turso.

### 🎓 Student path

1. Log in with an account whose role is `student`.
2. View book IDs, prices, and stock.
3. Select a book to purchase or rent.
4. Confirm the operation when the account has enough balance.
5. View active rentals, due dates, and transaction history.
6. Return a rental to restore its copies to the stock.

## ✅ What Works Now

- Role-based login using the `users` table.
- Public clients never receive the Turso URL or database token.
- Expiring server sessions protect all catalog and account endpoints.
- Admin permissions are checked by the API, not only by the menu.
- Existing plain-text passwords are upgraded to PBKDF2 after a successful login.
- Admin book creation with numeric validation for prices and stock.
- Admin book editing and inventory/sales statistics.
- Duplicate-book and database-error messages during inserts.
- Student stock display and purchase flow.
- Rental due dates set automatically to 14 days after checkout.
- Active-rental display, book returns, and transaction history.
- Transactional updates for stock, balance, purchases, and rentals.
- Turso-compatible foreign keys and database constraints.
- Automated schema tests in `test_database.py`.

## 🗺️ Project Map

```text
ProjetBiblio/
|-- main.py                 Public CMD client and role menus
|-- api_client.py           HTTPS communication with the API
|-- api.py                  FastAPI routes, sessions, permissions, operations
|-- database.py             Private Turso connection and schema creation
|-- utilities.py     Shared yes/no input helper
|-- test_api.py              API and authorization tests
|-- test_database.py         Database schema tests
|-- render.yaml              Render deployment blueprint
|-- requirements-api.txt     Server dependencies
|-- requirements-client.txt  Public client dependency
|-- run.bat                  Windows client launcher
|-- .env.example             Server-only Turso configuration
`-- README.md                Project guide
```

## 🗃️ Database Design

The hosted Turso database uses four related tables:

| Table | Purpose |
| --- | --- |
| `users` | Usernames, passwords, roles, and balances |
| `books` | Titles, authors, prices, and stock |
| `purchases` | Student purchase history |
| `rentals` | Rental records and return status |

The schema protects important values such as balances, prices, stock, and quantities. Books are unique by the combination of `title` and `author`.

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

Create a server-only `.env`:

```env
TURSO_DATABASE_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your-private-token
SESSION_TTL_HOURS=12
```

Start the API:

```bash
uvicorn api:app --reload
```

In another Windows terminal, point the client to the local API:

```bat
set PROJETBIBLIO_API_URL=http://127.0.0.1:8000
python main.py
```

### 3. ☁️ Deploy the API on Render

1. Open Render and choose **New > Blueprint**.
2. Connect this GitHub repository.
3. Render reads `render.yaml` and creates `projetbiblio-api`.
4. Enter `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` when requested.
5. Deploy and copy the resulting URL, for example:

```text
https://projetbiblio-api.onrender.com
```

The token is stored only in Render's private environment. It is never sent to
the CMD client.

### 4. 🔗 Configure the public API address once

Replace `DEFAULT_API_URL` in `api_client.py` with the real Render URL:

```python
DEFAULT_API_URL = "https://projetbiblio-api.onrender.com"
```

Commit that public URL. It is not a secret. After this one owner-side change,
users do not need an `.env`, a Turso URL, or a Turso token.

### 5. 👤 Add accounts

Accounts can be inserted into the hosted `users` table. Example test accounts:

```sql
INSERT INTO users (username, password, role, balance)
VALUES ('admin', 'admin123', 'admin', 0);

INSERT INTO users (username, password, role, balance)
VALUES ('student', 'student123', 'student', 100.00);
```

The first successful API login automatically replaces each legacy plain-text
password with a salted PBKDF2 hash.

### 6. ▶️ Public user instructions

A user only needs to download the project and double-click:

```bat
run.bat
```

The launcher installs the HTTP client package if necessary. It never asks for
database credentials.

To create a single Windows executable for distribution:

```bash
python -m pip install pyinstaller
pyinstaller --onefile --name ProjetBiblio main.py
```

The distributable file will be `dist/ProjetBiblio.exe`.

### 7. 🧫 Run the tests

```bash
python -m pip install -r requirements-dev.txt
python -m unittest -v
```

## ☁️ Turso Workflow

Only the FastAPI server loads `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN`. The
server uses the `libsql` driver, creates missing schema objects, and performs all
balance, stock, purchase, and rental transactions. The CMD application only
receives an expiring session token that cannot be used to access Turso directly.

## 🛣️ Roadmap

- Add account creation and password-change endpoints.
- Replace in-memory sessions with signed tokens or Redis before scaling to
  multiple API workers.
- Add rate limiting for repeated failed login attempts.
- Build and attach the Windows executable to GitHub Releases.

## 🤝 Collaboration Notes

This is a shared learning project. Before pushing:

```bash
git pull --rebase origin main
git status
git push origin main
```

Keep schema changes intentional, never commit `.env`, and describe database
migrations in the commit message.

## 🔒 Security Note

Never commit `.env`, Turso tokens, or private database contents. The API checks
the authenticated user's role for every protected operation. Legacy passwords
are accepted once and upgraded to PBKDF2; new account-management code should
store only hashes. In-memory sessions are suitable for this learning deployment
with one API worker and are intentionally invalidated whenever the server restarts.

<div align="center">

Built with Python, Turso, and a lot of terminal prompts.

</div>
