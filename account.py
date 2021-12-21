import sys
import os
import shutil
import pandas as pd
import locale
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

import time


class Account: 

    def __init__(self, csv_path, currency, save_dir):

        self.csv_path = csv_path
        self.currency = currency
        self.save_dir = save_dir
        self.currency_symbol = locale.localeconv()['currency_symbol']
        self.col_names = ['DATE', 'AMT', 'BAL', 'ACTION', 'TAG']

        # read account
        if os.path.isfile(csv_path):
            self.info = pd.read_csv(csv_path)
            shutil.copyfile(csv_path, csv_path + '.bak') # create backup
        else:
            self.init_acc()


    def init_acc(self): 
        'Initialize account. Occurs when there is no existing csv.'

        print('\naccount is empty. let\'s initialize it!' )

        cur_date = input('enter the date (yy-mm-dd): ')

        cur_bal = float(input('enter your starting balance: '))
        cur_bal_fmt = locale.currency(cur_bal, grouping=True, symbol=False)
        self.info = pd.DataFrame([[cur_date, 0, cur_bal_fmt, 'deposit', 'init deposit']], columns=self.col_names)
        
        # save to csv
        self.save_acc()


    def view_entries(self): 
        'View the last 5 entries of the current account.'
        
        print('\n* CURRENT ACCOUNT (LAST 5 ENTRIES) *')
        print(self.info.tail())


    def save_acc(self): 
        'Save acc info to csv.'

        # self.info.sort_values(['DATE'], inplace=True)
        try: 
            self.info.to_csv(self.csv_path, index=False)
        except PermissionError: 
            input('please close the csv, then press enter to continue. ')
            self.info.to_csv(self.csv_path, index=False)
        
        print(f'account info saved at {self.csv_path}.')


    def get_tags(self): 
        'Get list of existing tags. '
        return self.info['TAG'].unique()


    def add_entry(self, action): 
        'Add money to your account. '
        
        cur_date = input('enter the date (yy-mm-dd): ')
        amount = float(input('enter the amount: '))
        tag = input('enter a tag: ')

        # check that inputted date is either the same or later as the last recorded date
        prev_date = self.info['DATE'].iloc[-1]
        assert int(cur_date.replace('-','')) >= int(prev_date.replace('-','')), 'current implementation only allows for chronological submissions!'

        # convert str to float
        prev_bal = locale.atof(self.info['BAL'].iloc[-1])

        if action == '1': # deposit
            cur_bal = prev_bal + amount
            action_name = 'deposit'
        elif action == '2': # withdrawal
            cur_bal = prev_bal - amount
            action_name = 'withdraw'
        else: 
            sys.exit(f'no such action as: {action}')

        if cur_bal < 0: 
            print('warning! you have a negative balance.')

        # convert float to str
        cur_bal_fmt = locale.currency(cur_bal, grouping=True, symbol=False)
        amount_fmt = locale.currency(amount, grouping=True, symbol=False)

        entry = pd.DataFrame([[cur_date, amount_fmt, cur_bal_fmt, action_name, tag]], columns=self.col_names)
        self.info = pd.concat([self.info, entry], ignore_index=True)
        
        self.save_acc()

    def remove_entry(self): 
        'Remove entry. Doesn\'t update values that need to be changed; recommended that only the last value is removed.'

        self.view_entries()

        choice = input('proceed with removing the last row (y/n)? ')

        if choice == 'y': 
            self.info.drop(self.info.tail(1).index, inplace=True)
        else: 
            print('no entries were removed.')


    def gen_monthly_report(self, year, month): 
        '''Generate a monthly report. 
            Monthy reports include: 
            - A pie chart for each deposits and withdrawals per tag.
        '''

        # convert dates to datetime format
        dates_conv = pd.Series([datetime.strptime(date, '%y-%m-%d') for date in self.info['DATE']])

        # find first and last day of month
        start_date = datetime.strptime(f'{year}-{month}-01', '%y-%m-%d').date()
        end_date = pd.date_range(f'20{year}-{month}-01', periods=1, freq='M').date[0]
        print(f'getting all entries between {start_date} and {end_date}')

        # get all dates within the range
        dates_in_month = pd.Series([date.date().strftime('%Y-%m-%d')[2:] for date in dates_conv if date >= start_date and date <= end_date])

        # get all entires in date range
        info_select = self.info.loc[self.info['DATE'].isin(dates_in_month)]
        print(info_select)

        # seperate into deposits and withdraws
        deposits = info_select.loc[info_select['ACTION'] == 'deposit']
        withdraws = info_select.loc[info_select['ACTION'] == 'withdraw']

        # per tag
        amt_per_tag = {'deposit':{}, 'withdraw':{}}
        for tag in deposits['TAG'].unique(): 
            deposits_tag = deposits.loc[deposits['TAG'] == tag]
            amt = np.sum([locale.atof(amt) for amt in deposits_tag['AMT']])
            amt_per_tag['deposit'][tag] = amt

        for tag in withdraws['TAG'].unique(): 
            withdraws_tag = withdraws.loc[withdraws['TAG'] == tag]
            amt = np.sum([locale.atof(amt) for amt in withdraws_tag['AMT']])
            amt_per_tag['withdraw'][tag] = amt

        plt.figure(figsize=(15,10))
        fig = plt.gcf()
        plt.subplot(121)
        plt.pie(amt_per_tag['deposit'].values(), 
                labels=amt_per_tag['deposit'].keys(),
                startangle=90,
                autopct=lambda x:np.round(x/100.*np.sum(list(amt_per_tag['deposit'].values())), 0),
                counterclock=False,
                )
        plt.title(f"Deposits ({locale.localeconv()['currency_symbol']})\nTotal: {np.sum(list(amt_per_tag['deposit'].values()))}")

        plt.subplot(122)
        plt.pie(amt_per_tag['withdraw'].values(), 
                labels=amt_per_tag['withdraw'].keys(),
                startangle=90,
                autopct=lambda x:np.round(x/100.*np.sum(list(amt_per_tag['withdraw'].values())), 0),
                counterclock=False,
                )
        plt.title(f"Withdrawals ({locale.localeconv()['currency_symbol']})\nTotal: {np.sum(list(amt_per_tag['withdraw'].values()))}")

        fig.suptitle(f'Monthly report for {year}-{month}')
        # plt.show()
        plt.savefig(os.path.join(self.save_dir, f'monthly_report_{year}{month}_{self.currency}.png'))
        print('report saved at', os.path.join(self.save_dir, f'monthly_report_{year}{month}_{self.currency}.png'))


    def gen_yearly_report(self, year): 
        '''Generate a yearly report. 
            Yearly reports include: 
            - Line graph with a point for each month. 
        '''
        
        # convert dates to datetime format
        dates_conv = pd.Series([datetime.strptime(date, '%y-%m-%d') for date in self.info['DATE']])

        # find first and last day of month
        start_date = datetime.strptime(f'{year}-01-01', '%y-%m-%d').date()
        end_date = datetime.strptime(f'{year}-12-31', '%y-%m-%d').date()
        print(f'getting all entries between {start_date} and {end_date}')

        # get all dates within the range
        dates_in_month = pd.Series([date.date().strftime('%Y-%m-%d')[2:] for date in dates_conv if date >= start_date and date <= end_date])

        # get all entires in date range
        info_select = self.info.loc[self.info['DATE'].isin(dates_in_month)]
        # print(info_select)

        # seperate into deposits and withdraws
        deposits = info_select.loc[info_select['ACTION'] == 'deposit']
        withdraws = info_select.loc[info_select['ACTION'] == 'withdraw']

        # get all months with at least one entry
        months = pd.Series([datetime.strptime(date, '%y-%m-%d').month for date in info_select['DATE']])
        
        # initialize plotting data
        amt_per_month = {'deposit':{}, 'withdraw':{}}
        for month in range(1,13): 
            amt_per_month['deposit'][month] = 0
            amt_per_month['withdraw'][month] = 0

        # get total deposits and withdrawals per month
        for month in months.unique(): 
            deposits_per_month = deposits.loc[months==month]
            withdrawals_per_month = withdraws.loc[months==month]

            deposit_tot_per_month = np.sum([locale.atof(amt) for amt in deposits_per_month['AMT']])
            withdrawals_tot_per_month = np.sum([locale.atof(amt) for amt in withdrawals_per_month['AMT']])

            amt_per_month['deposit'][month] = deposit_tot_per_month
            amt_per_month['withdraw'][month] = withdrawals_tot_per_month

        # plot!
        plt.figure(figsize=(15,10))
        fig = plt.gcf()
        plt.subplot(121)
        plt.plot(range(1,13), amt_per_month['deposit'].values(), marker='o', linestyle='dashed')
        plt.xticks(range(1,13))
        plt.xlabel('Month'), plt.ylabel(locale.localeconv()['currency_symbol'])
        plt.title(f"Deposits ({locale.localeconv()['currency_symbol']})\nTotal: {np.sum(list(amt_per_month['deposit'].values()))}")

        plt.subplot(122)
        plt.plot(range(1,13), amt_per_month['withdraw'].values(), marker='o', linestyle='dashed')
        plt.xticks(range(1,13))
        plt.xlabel('Month'), plt.ylabel(locale.localeconv()['currency_symbol'])
        plt.title(f"Withdrawals ({locale.localeconv()['currency_symbol']})\nTotal: {np.sum(list(amt_per_month['withdraw'].values()))}")

        fig.suptitle(f'Yearly report for {year}')
        # plt.show()
        plt.savefig(os.path.join(self.save_dir, f'yearly_report_{year}_{self.currency}.png'))
        print('report saved at', os.path.join(self.save_dir, f'yearly_report_{year}_{self.currency}.png'))


if __name__ == '__main__': 

    csv_path = './bank_account_won.csv'
    acc = Account(csv_path)
    print('check passed: load csv')

    tags = acc.get_tags()
    print('check passed: get tags')