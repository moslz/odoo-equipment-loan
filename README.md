# Equipment Loan (Odoo 19 CE)

An Odoo 19 Community module for lending equipment (laptops, projectors, cameras) to
contacts and keeping track of who has what and until when.

## What the module does

You create equipment items and then loans for them. A loan links an item to a borrower
(a normal Odoo contact) with a loan date and a due date. It goes through three states:
Draft, Borrowed, Returned. When a loan is returned, the exact date and time is saved.

Rules the module enforces:

- The due date can't be before the loan date.
- The same item can't be loaned twice in overlapping periods. Draft and borrowed loans
  both count, returned loans don't. Dates are inclusive, so a new loan can start the day
  after the previous one ends, but not on the same day.
- Equipment names must be unique. Case, spaces and punctuation are ignored, so
  "Laptop 12", "laptop12" and "LAPTOP-12" count as the same name. Archived items count too.
- Only draft loans can be confirmed and only borrowed loans can be returned.

Other things:

- Borrowed loans that are past their due date are shown in red, get an "Overdue" ribbon,
  and can be found with the "Overdue" filter.
- Loans use Odoo's chatter (`mail.thread`), so changes to status, borrower, equipment and
  due date are logged with user and time.
- There are two roles. "Equipment Loan: User" can create, confirm and return loans but
  can't delete anything or change equipment. "Equipment Loan: Manager" can do everything.
  The Odoo admin is a manager automatically. Users without either role can't see the app.

## Approach

I hadn't used Odoo before this task, so I started with a Docker setup to have a clean
Odoo 19 with PostgreSQL, and built the module in small steps with a commit after each one.

The first version stored the equipment as a text field on the loan. I changed that to a
separate model because a typo in the name ("Laptop 12" vs "laptop12") would have let
the same device be loaned twice.

All business rules are in the models (`@api.constrains` and the state methods), not in
the views, so they also apply to imports or API calls. The state methods check every
record first and only then write, so a batch action either fully succeeds or changes nothing.

For the tests I focused on the parts most likely to break: date boundaries in the
overlap and overdue checks, name normalization, invalid state changes and access rights.
To make sure the tests actually catch mistakes, I broke the code on purpose (for example
changed `<=` to `<` in the overlap check) and checked that the right test failed.
The Playwright tests cover what Python tests can't see: which buttons are visible in which
state and whether error messages actually reach the user.


## How to run it

You need Docker Desktop (or Docker with Compose). Commands are for PowerShell on Windows,
Linux/macOS alternatives are noted.

**1. Get the code**

```
git clone <repository-url>
cd odoo-equipment-loan
```

**2. Create your `.env` file**

The `.env` file holds the database credentials and isn't committed. Copy the template:

```
Copy-Item .env.example .env        # Linux/macOS: cp .env.example .env
```

Open `.env` and set `POSTGRES_PASSWORD` to any value. `ODOO_PORT` is the port Odoo
will use (default 8069).

**3. Create the database and install the module**

```
docker compose run --rm odoo odoo -d odoo_dev -i equipment_loan --stop-after-init
```

This downloads the images on the first run, creates the database `odoo_dev` and installs
the module. It takes a minute the first time. 

**4. Start Odoo**

```
docker compose up -d
```

Open http://localhost:8069 and log in with `admin` / `admin`. "Equipment Loans" is in the
main menu.

To stop it: `docker compose stop`. To remove everything including the database:
`docker compose down -v`.

## Tests

### Module tests (37 tests)

They use Odoo's own test framework and run inside Docker, in a separate database so
your data isn't touched:

```
docker compose run --rm odoo odoo -d odoo_test -i equipment_loan --test-enable --test-tags /equipment_loan --stop-after-init
```

For later runs, replace `-i` with `-u`. The last lines of the output should say
`0 failed, 0 error(s) of 37 tests`.

### End-to-end tests (4 tests, pytest + Playwright)

These run in a real browser against the running Odoo from step 4. You need Python 3.

```
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
pip install -r e2e/requirements.txt
playwright install chromium
pytest -v
```

Expected: `4 passed`. Add `--headed` to watch the browser.

The tests log in as `admin` / `admin`. If your setup is different, set these environment
variables before running pytest (PowerShell: `$env:ODOO_LOGIN="..."`):

- `ODOO_LOGIN`, `ODOO_PASSWORD`: login (default `admin` / `admin`)
- `ODOO_URL`: default `http://localhost:8069`
- `ODOO_DB`: only needed if there is more than one database, e.g. after running the
  module tests, which create `odoo_test`. Then set it to `odoo_dev`.
- `ODOO_DATE_FORMAT`: default `%m/%d/%Y`, which matches English (US)

### Code style

```
pip install flake8
flake8
```

No output means no findings. The configuration is in `.flake8`.

## Time spent

| Day | Hours | What |
|---|---|---|
| Monday | 1 | Docker setup, getting to know Odoo, module skeleton, first model |
| Tuesday | 2 | Equipment model, views, menus, security groups |
| Wednesday | 2 | Overdue feature, return time, tests, flake8 |
| Thursday | 1 | README, final check |
| Total | 6 | |

## Definition of Done

- The module installs on a fresh Odoo 19 CE database using the steps above.
- Models, views, menus, security groups and access rights are in place.
- Invalid input is rejected with a clear message (date order, overlap, duplicate names,
  invalid state changes).
- All 37 module tests and 4 end-to-end tests pass.
- flake8 reports nothing.
- Every step is a separate commit with a meaningful message.
- This README covers features, approach, installation, time spent and Definition of Done.

## Known limitations

- There are no record rules, so every user with a role sees all loans.
