import os

import pytest


@pytest.fixture(scope='session')
def odoo_url():
    return os.environ.get('ODOO_URL', 'http://localhost:8069').rstrip('/')


@pytest.fixture(scope='session')
def date_format():
    return os.environ.get('ODOO_DATE_FORMAT', '%m/%d/%Y')


@pytest.fixture
def logged_in_page(page, odoo_url):
    login_url = f'{odoo_url}/web/login'
    database = os.environ.get('ODOO_DB')
    if database:
        login_url += f'?db={database}'
    page.goto(login_url)
    if '/web/database/selector' in page.url:
        pytest.fail(
            'Odoo shows the database selector because several databases '
            'exist. Set ODOO_DB to the database name, for example '
            '$env:ODOO_DB="odoo_dev" (PowerShell) or export ODOO_DB=odoo_dev.'
        )
    page.fill('input[name="login"]', os.environ.get('ODOO_LOGIN', 'admin'))
    page.fill('input[name="password"]', os.environ.get('ODOO_PASSWORD', 'admin'))
    page.click('button[type="submit"]')
    page.wait_for_url('**/odoo**')
    return page
