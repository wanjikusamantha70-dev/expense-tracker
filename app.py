import streamlit as st
import pandas as pd
import sqlite3

st.title('Expense Tracker')
st.set_page_config(
    page_title = 'Expense Tracker',
    page_icon = '💸',
    layout ='wide'
)
with sqlite3.connect('expenses.db') as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')

if 'expenses' not in st.session_state:
    with sqlite3.connect('expenses.db') as conn:
        rows = conn.execute(
            'SELECT name, category, amount FROM expenses'
        ).fetchall()

        st.session_state.expenses = [
            {
                'name': row[0],
                'category': row[1],
                'amount': row[2]
            }
            for row in rows
        ]
    with sqlite3.connect('expenses.db') as conn:
        conn.execute(
            'INSERT INTO expenses (name, category, amount) VALUES(?,?,?)',
            (expense['name'], expense['category'], expense['amount'])
        )
        st.session_state.expenses.append(expense)
        st.success('Expense added successfully!')

st.title('Expense Tracker')
st.caption('Track your spending and stay within budget')


st.header('Budget Input')
budget = st.number_input('Enter your budget: ',min_value = 0.0, step =50.0)
st.write('Your Budget is : Ksh ', budget)


st.header('Expense Input')
expense_name = st.text_input('Enter Expense name:  ')
expense_category = st.selectbox('Select Expesnse Category', ['Food', 'Transport', 'Clothes', 'Entertainment', 'Other'])
expense_amount = st.number_input('Enter Expense Amount: Ksh', min_value = 0.0, step = 50.0)
if st.button('Add Expense'):
    if not expense_name:
        st.error('Please enter a valid expense name')

    elif expense_amount <= 0:
        st.error('Amount must be greater than 0')

    else:
        expense ={
            'name' : expense_name,
            'category' : expense_category,
            'amount' : expense_amount
        }
        st.session_state.expenses.append(expense)
    st.success('Expense Added Successfully!')
    
    st.write('Expense Added:')
    st.write('Name:', expense_name)
    st.write('Category:', expense_category)


st.header('All Expenses')
if st.session_state.expenses:
    st.dataframe(
        st.session_state.expenses,
        use_container_width = True,
        hide_index = True
    )
else:
    st.info('No expenses recorded yet.')
st.write('-------------------------------')

category_totals = {
    'Food': 0,
    'Transport': 0,
    'Clothes': 0,
    'Entertainment': 0,
    'Other': 0
}

for expense in st.session_state.expenses:
    category = expense['category']
    amount = expense['amount']
    category_totals[category] += amount

st.header('Group Expenses by Category')
if st.button('Group Expenses'):
    st.session_state.show_grouping = True

if 'show_grouping' not in st.session_state:
    st.session_state.show_grouping = False

if st.session_state.show_grouping:
    
    total_spent = sum(category_totals.values())

    for category, amount in category_totals.items():
        st.write(f'{category}: Ksh {amount:,.2f}')
        if total_spent > 0:
            progress = amount / total_spent
        else:
            progress = 0.0
        st.progress(progress)


st.header('Spending Summary')

total_spent = sum(
     expense['amount']
     for expense in st.session_state.expenses
)

remaining = budget - total_spent

col1, col2, col3 = st.columns(3)

col1.metric(
    'Total Budget', 
    f'Ksh {budget:,.2f}'
)
   
col2.metric(
    'Total Spent',
    f'Ksh {total_spent:,.2f}'
)

col3.metric(
    'Remaining Balance',
    f'Ksh {remaining:,.2f}'
)

if remaining < 0:
    st.error(f'You have exceeded your budget by Ksh {abs(remaining):,.2f}')
else:
    st.success(f'You are within your budget. You have Ksh {remaining:,.2f} left.')

chart_data = pd.DataFrame(
    {
        'Category': list(category_totals.keys()),
        'Amount': list(category_totals.values())
    }
)
st.subheader('Spending by Category')

st.bar_chart(
    chart_data,
    x = 'Category',
    y = 'Amount'
)

