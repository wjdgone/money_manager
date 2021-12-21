# MONEY MANAGER

> Track how much money is coming in and out of your bank account. 
> Use visualization tools to plot monthly and yearly trends. 

## Setting up an account
1. Run main.py

```python
python main.py
```

2. Create a new bank account with choosing an account name and currency (KRW or USD). 
3. Add initial funds to complete the set up. 

## Features
- Create and maintain your account with a csv file (e.g. bank_account_ACCOUNTNAME_CURRENCY.csv).
- Submit deposits and withdrawals to your account and view remaining balance. 
- Organize types of spending with tags and view monthly activity. 
- Plot yearly trends in deposits and withdrawals.

## Other (smaller) functionalities
- Currently supports both Korean won and American USD.
- Every time a session is started, a backup csv file of the previous session will be automatically generated (e.g. bank_account_won.csv.bak). 