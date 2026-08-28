<div align="center">

# ProjetBiblio

### A quiet terminal library for books, members, and shared learning

<p>
  <a href="https://github.com/Youcefdz06/ProjetBiblio"><strong>Repository</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="#getting-started"><strong>Run it</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="#the-current-journey"><strong>Explore the flow</strong></a>
</p>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-local_database-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/status-learning_project-1F7A8C?style=flat-square)

</div>

<br>

> ProjetBiblio is a terminal-first library manager. It uses Python for the application flow, SQLite for persistent data, and DB Browser for SQLite for hands-on database work.

## At A Glance

| Layer | What it does |
| --- | --- |
| Authentication | Finds a user and routes them by role |
| Administrator | Reviews and adds books to the catalog |
| Student | Browses stock and purchases available books |
| Database | Stores users, books, purchases, and rentals |
| Collaboration | Keeps the project easy to pull, test, and extend |

## The Library Shelves

<table>
  <tr>
    <td width="25%" align="center"><strong>ACCESS</strong><br><br><code>auth.py</code><br>Role-based login</td>
    <td width="25%" align="center"><strong>CATALOG</strong><br><br><code>admin.py</code><br>Add and review books</td>
    <td width="25%" align="center"><strong>CIRCULATION</strong><br><br><code>user.py</code><br>Stock and purchases</td>
    <td width="25%" align="center"><strong>ARCHIVE</strong><br><br><code>database.py</code><br>SQLite persistence</td>
  </tr>
  <tr>
    <td colspan="4" align="center">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</td>
  </tr>
</table>

## The Current Journey

```text
Start
  |
  v
Login ----------------------+
  |                         |
  +--> Administrator         +--> Student
       |                          |
       +--> Add a book            +--> View stock
            |                     +--> Buy a book
            +--> Confirm          +--> Future rental flow
```

### Administrator path

1. Log in with an account whose role is `admin`.
2. Enter the book details and prices.
3. Review the displayed information.
4. Confirm the entry to save it in SQLite.

### Student path

1. Log in with an account whose role is `student`.
2. View book IDs, prices, and stock.
3. Select a book to purchase.
4. Confirm the purchase when the account has enough balance.

## What Works Now

- Role-based login using the `users` table.
- Admin book creation with numeric validation for prices and stock.
- Duplicate-book and database-error messages during inserts.
- Student stock display and purchase flow.
- Transactional updates for stock, balance, and purchase history.
- SQLite foreign keys and database constraints.
- Automated schema tests in `test_database.py`.

## Project Map

```text
ProjetBiblio/
|-- main.py          Application entry point and role menus
|-- auth.py          Login query and user session data
|-- admin.py         Book model, input, and catalog insertion
|-- user.py          Catalog display, balances, and purchases
|-- database.py      SQLite connection and schema creation
|-- utilities.py     Shared yes/no input helper
|-- test_database.py Database schema tests
|-- library.db       Local SQLite database
|-- README.md        Project guide
`-- .gitignore       Local files excluded from Git
```

## Database Design

The application uses four related tables:

| Table | Purpose |
| --- | --- |
| `users` | Usernames, passwords, roles, and balances |
| `books` | Titles, authors, prices, and stock |
| `purchases` | Student purchase history |
| `rentals` | Rental records and return status |

The schema protects important values such as balances, prices, stock, and quantities. Books are unique by the combination of `title` and `author`.

## Getting Started

### Requirements

- Python 3.10 or newer
- DB Browser for SQLite for manual database editing
- No third-party Python packages

### 1. Clone the project

```bash
git clone https://github.com/Youcefdz06/ProjetBiblio.git
cd ProjetBiblio
```

### 2. Prepare the database

Open `library.db` in DB Browser for SQLite. Create or verify the schema, add test users, then select **Write Changes** before starting the application.

Example test accounts:

```sql
INSERT INTO users (username, password, role, balance)
VALUES ('admin', 'admin123', 'admin', 0);

INSERT INTO users (username, password, role, balance)
VALUES ('student', 'student123', 'student', 100.00);
```

### 3. Run the application

```bash
python main.py
```

### 4. Run the tests

```bash
python -m unittest -v
```

## Manual Database Workflow

Because the database is managed manually during development:

1. Close the running Python program before editing `library.db`.
2. Open the database in DB Browser for SQLite.
3. Make schema or data changes.
4. Click **Write Changes**.
5. Close the database in DB Browser before running `main.py`.

Keeping DB Browser closed while Python is running helps prevent `database is locked` errors.

## Roadmap

- Complete rent and return operations.
- Show active rentals for students.
- Add admin edit and delete actions.
- Add inventory and sales statistics.
- Improve menu loops and input validation.
- Replace plain-text passwords with Argon2, bcrypt, or scrypt hashes.

## Collaboration Notes

This is a shared learning project. Before pushing:

```bash
git pull --rebase origin main
git status
git push origin main
```

Keep database edits intentional and describe schema changes in the commit message.

## Security Note

This project is for education. Passwords are currently stored as plain text in SQLite, so the application is not suitable for production use. Never commit personal credentials, access tokens, or private database contents.

<div align="center">

Built with Python, SQLite, and a lot of terminal prompts.

</div>
