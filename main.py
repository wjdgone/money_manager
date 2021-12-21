import os
import time
import locale

from account import Account


# set directory where files and plots are saved
ROOT_DIR = './accounts'

DEFAULT_ACCOUNT = 'testing'
DEFAULT_CURRENCY = 'won'


def get_csv_path(account, currency): 
    ''' Parse account name and currency type. '''

    account_dir = os.path.join(ROOT_DIR, account)
    
    if not os.path.isdir(account_dir): 
        os.mkdir(account_dir)

    return account_dir, os.path.join(account_dir, f'bank_account_{account}_{currency}.csv')


if __name__ == '__main__': 

    start_time = time.time()

    # INITIALIZATION
    account = input('select your account (default: testing): ').lower()
    currency = input('select your currency (default: won): ').lower()

    account = DEFAULT_ACCOUNT if account == '' else account
    currency = DEFAULT_CURRENCY if currency == '' else currency

    if currency == 'won': 
        locale.setlocale(locale.LC_ALL, 'kr_KR.UTF-8')
    elif currency == 'usd': 
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    # print(locale.localeconv())

    # parse csv path
    save_dir, csv_path = get_csv_path(account, currency)
    print(f'reading account: {os.path.basename(csv_path)}')

    # read csv
    acc = Account(csv_path, currency, save_dir)
    print(acc.save_dir)
    acc.view_entries()

    # ACTIONS
    actions = ['deposit', 'withdraw', 'generate monthly report', 'generate yearly report', 'view tags', 'remove (last) entry', 'end session']
    active = True
    while active: 
        print('what would you like to do? ')
        for idx, action in enumerate(actions): 
            print(f'{idx+1}. {action}')
        choice = input('\nyour choice: ')

        # deposit, withdraw
        if choice in ('1', '2'): 
            acc.add_entry(choice)
            acc.view_entries()

        # generate monthly report
        elif choice == '3': 
            year, month = input('choose a year and month (yy-mm): ').split('-')
            acc.gen_monthly_report(year, month)

        # generate yearly report
        elif choice == '4': 
            year = input('choose a year (yy): ')
            acc.gen_yearly_report(year)

        # view tags
        elif choice == '5': 
            print('\n* CURRENT TAGS *')
            print(acc.get_tags())

        # remove last entry
        elif choice == '6': 
            acc.remove_entry()
            acc.view_entries()

        # end session
        elif choice == '7': 
            acc.view_entries()
            break
        
        choose_active = input('\nwould you like to choose another action (y/n)? ')
        active = False if choose_active == 'n' else True


    print(f'Finished. Time elapsed: {(time.time() - start_time)/60:.4f} mins.')