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

> 💬 ProjetBiblio is a terminal-first library manager. It uses Python for the application flow and a hosted Turso database for shared persistent data.

## ✨ At A Glance

| Layer | What it does |
| --- | --- |
| 🔐 Authentication | Finds a user and routes them by role |
| 🧑‍💼 Administrator | Reviews and adds books to the catalog |
| 🎓 Student | Browses, buys, rents, returns, and reviews history |
| 🗄️ Database | Stores shared data in Turso using SQL over HTTP |
| 🤝 Collaboration | Keeps the project easy to pull, test, and extend |

## 🪵 The Library Shelves

<table>
  <tr>
    <td width="25%" align="center">🔑<br><strong>ACCESS</strong><br><br><code>auth.py</code><br>Role-based login</td>
    <td width="25%" align="center">📚<br><strong>CATALOG</strong><br><br><code>admin.py</code><br>Add and review books</td>
    <td width="25%" align="center">🔄<br><strong>CIRCULATION</strong><br><br><code>user.py</code><br>Buy, rent, and return</td>
    <td width="25%" align="center">🗄️<br><strong>ARCHIVE</strong><br><br><code>database.py</code><br>Turso persistence</td>
  </tr>
  <tr>
    <td colspan="4" align="center">📕 📘 📗 📙 📕 📘 📗 📙 📕 📘 📗 📙<br>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</td>
  </tr>
</table>

## 🧭 The Current Journey

```text
Start
  |
  v
Login ----------------------+
  |                         |
  +--> Administrator         +--> Student
       |                          |
       +--> Add a book            +--> View stock
            |                     +--> Buy or rent a book
            +--> Confirm          +--> Return a rental
                                  +--> View activity history
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
- Admin book creation with numeric validation for prices and stock.
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
|-- main.py          Application entry point and role menus
|-- auth.py          Login query and user session data
|-- admin.py         Book model, input, and catalog insertion
|-- user.py          Catalog, purchases, rentals, returns, and history
|-- database.py      Turso connection and schema creation
|-- utilities.py     Shared yes/no input helper
|-- test_database.py Database schema tests
|-- run.bat          Windows launcher
|-- requirements.txt Python dependencies
|-- .env.example     Turso configuration template
|-- README.md        Project guide
`-- .gitignore       Local files excluded from Git
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

### 🧰 Requirements

- Python 3.10 or newer
- A Turso database URL and authentication token
- The packages listed in `requirements.txt`

### 1. 📥 Clone the project

```bash
git clone https://github.com/Youcefdz06/ProjetBiblio.git
cd ProjetBiblio
```

### 2. 📦 Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. 🔐 Configure Turso

Copy `.env.example` to `.env`, then add your private database credentials:

```env
TURSO_DATABASE_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your-private-token
```

Never commit `.env`. It is excluded by `.gitignore`.

Initialize the remote schema:

```bash
python database.py
```

To migrate users from an existing local `library.db` once:

```bash
python migrate_users_to_turso.py
```

### 4. ▶️ Run the application

On Windows, double-click `run.bat` or run:

```bat
run.bat
```

The launcher checks Python, installs missing dependencies, and starts the app.

You can also launch it directly:

```bash
python main.py
```

### 5. 👤 Add test users

Accounts can be inserted into the hosted `users` table. Example test accounts:

```sql
INSERT INTO users (username, password, role, balance)
VALUES ('admin', 'admin123', 'admin', 0);

INSERT INTO users (username, password, role, balance)
VALUES ('student', 'student123', 'student', 100.00);
```

### 6. 🧫 Run the tests

```bash
python -m unittest -v
```

## ☁️ Turso Workflow

The application loads `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` from `.env`,
then connects with `turso_serverless`. `database.py` creates missing tables,
indexes, and triggers without deleting existing remote data. Local `*.db` files
are ignored and are used only by automated tests or one-time migration tools.

## 🛣️ Roadmap

- Add admin edit and delete actions.
- Add inventory and sales statistics.
- Improve menu loops and input validation.
- Replace plain-text passwords with Argon2, bcrypt, or scrypt hashes.

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

This project is for education. Passwords are currently stored as plain text in Turso, so the application is not suitable for production use. Never commit personal credentials, `.env`, access tokens, or private database contents.

<div align="center">

Built with Python, Turso, and a lot of terminal prompts.

</div>
