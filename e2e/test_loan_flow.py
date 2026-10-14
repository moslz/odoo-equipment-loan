import re
import uuid
from datetime import date, timedelta

from playwright.sync_api import expect

LOAN_ACTION = '/odoo/action-equipment_loan.action_equipment_loan'
ITEM_ACTION = '/odoo/action-equipment_loan.action_equipment_item'
CURRENT_STATE = '.o_statusbar_status .o_arrow_button_current'
TIME_PATTERN = re.compile(r'\d{1,2}:\d{2}')


def _unique_name(prefix):
    return f'{prefix} {uuid.uuid4().hex[:6]}'


def _select_autocomplete_option(page, text):
    page.locator(
        '.o-autocomplete--dropdown-item:not(.o_m2o_dropdown_option)',
        has_text=text,
    ).first.click()


def _create_borrower_inline(page):
    name = _unique_name('E2E Borrower')
    page.locator('div[name="borrower_id"] input').fill(name)
    page.locator('.o_m2o_dropdown_option_create').first.click()
    return name


def _set_due_date(page, days, date_format):
    value = (date.today() + timedelta(days=days)).strftime(date_format)
    page.locator('div[name="date_end"] input').fill(value)
    page.keyboard.press('Tab')


def _create_item_with_name(page, odoo_url, name):
    page.goto(odoo_url + ITEM_ACTION)
    page.get_by_role('button', name='New').click()
    page.locator('div[name="name"] input').fill(name)
    page.locator('.o_form_button_save').click()


def _create_unique_item(page, odoo_url):
    name = _unique_name('E2E Laptop')
    _create_item_with_name(page, odoo_url, name)
    expect(page.locator('.o_form_button_save')).to_be_hidden()
    return name


def _fill_loan(page, odoo_url, item_name, date_format, due_in):
    page.goto(odoo_url + LOAN_ACTION)
    page.get_by_role('button', name='New').click()
    page.locator('div[name="equipment_id"] input').fill(item_name)
    _select_autocomplete_option(page, item_name)
    _create_borrower_inline(page)
    _set_due_date(page, due_in, date_format)


def test_loan_workflow_and_button_visibility(logged_in_page, odoo_url, date_format):
    page = logged_in_page
    item = _create_unique_item(page, odoo_url)
    _fill_loan(page, odoo_url, item, date_format, due_in=7)

    expect(page.locator(CURRENT_STATE)).to_have_text('Draft')
    expect(page.get_by_role('button', name='Confirm Loan')).to_be_visible()
    expect(page.get_by_role('button', name='Mark as Returned')).to_have_count(0)

    page.get_by_role('button', name='Confirm Loan').click()
    expect(page.locator(CURRENT_STATE)).to_have_text('Borrowed')
    expect(page.get_by_role('button', name='Confirm Loan')).to_have_count(0)
    expect(page.get_by_role('button', name='Mark as Returned')).to_be_visible()

    page.get_by_role('button', name='Mark as Returned').click()
    expect(page.locator(CURRENT_STATE)).to_have_text('Returned')
    expect(page.get_by_role('button', name='Mark as Returned')).to_have_count(0)
    expect(page.locator('div[name="returned_at"]')).to_contain_text(TIME_PATTERN)


def test_overlapping_loan_shows_error(logged_in_page, odoo_url, date_format):
    page = logged_in_page
    item = _create_unique_item(page, odoo_url)
    _fill_loan(page, odoo_url, item, date_format, due_in=7)
    page.get_by_role('button', name='Confirm Loan').click()
    expect(page.locator(CURRENT_STATE)).to_have_text('Borrowed')

    _fill_loan(page, odoo_url, item, date_format, due_in=3)
    page.locator('.o_form_button_save').click()
    expect(page.get_by_text('is already loaned in this period')).to_be_visible()


def test_due_date_before_loan_date_shows_error(logged_in_page, odoo_url, date_format):
    page = logged_in_page
    item = _create_unique_item(page, odoo_url)
    _fill_loan(page, odoo_url, item, date_format, due_in=-3)
    page.locator('.o_form_button_save').click()
    expect(page.get_by_text('due date cannot be before the loan date')).to_be_visible()


def test_near_duplicate_equipment_name_shows_error(logged_in_page, odoo_url):
    page = logged_in_page
    item = _create_unique_item(page, odoo_url)
    variant = item.lower().replace(' ', '-')
    _create_item_with_name(page, odoo_url, variant)
    expect(page.get_by_text('already exists')).to_be_visible()
