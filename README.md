# XPense API


## Specification

### Users
- [ ] Sign-up user
- [ ] Login user

### Groups
- [ ] Create group
- [ ] Add user to group
- [ ] Remove user from group

### Expenses
- [ ] Create expense
    - Any user in the group can create an expense
    - When an expense is created, the user who created it is the payer
    - The payer can add participants to the expense, specifying the amount each participant owes
- [ ] Update expense

### Debts
- A user should be able to see how much they owe and how much they are owed, for each group they are in
- They user can pay the expenses they owe to the group and they can collect the expenses owed to them from the group


## Etc.
The server should track all transfers into and out of the group, and the user should be able to see a history of all transfers.

## Setup
```
$ python3 -m venv venv
$ source venv/bin/activate # or venv\Scripts\activate.bat on Windows
$ pip install -e .
$ make dev
```