import os
import requests
import csv
import time
import datetime
import threading


"""
    This code is to DELETE the Okta users in BULK based on its status. It will write user detail output in csv file.

    This code uses multi-threading to furiously delete the Okta users.

    Please update the environment variables in a file named '.env' as below:
        OKTA_URL=[https://<>.okta.com]
        OKTA_API_TOKEN=[Use your API Token which has privilege to delete users ]

    Please initialize the variables as per your requirement:
        DELETE_FLAG   [YES | NO]
        GETUSER_FLAG  [YES | NO]
        DELETE_FILTER   ["DEPROVISIONED" (Deactivated) | "PROVISIONED" | "SUSPENDED" | "STAGED" | "ACTIVE"]
            (Delete users based on its current status.)
        GETUSER_FILTER  ["DEPROVISIONED" (Deactivated) | "PROVISIONED" | "SUSPENDED" | "STAGED" | "ACTIVE"]
            (to list all Staged users before deleting or activating users)

    Developed By : Vipul Kaneriya.
"""


"""
    initialize variables
"""

okta_server = os.environ.get('OKTA_URL')            # Update your Okta tenant https://<yourOrg>.okta.com in .env file
api_token   = os.environ.get('OKTA_API_TOKEN')      # Update your Okta API token in .env file
headers     = {'Content-Type': "application/json",
           'Accept': "application/json", 'Authorization': f"SSWS {api_token}"}

getuser_flag    = 'YES'     # [YES or NO]
getuser_filter  = 'DEPROVISIONED'
delete_flag     = 'NO'      # [YES or NO] Change to 'YES' to DELETE users
delete_filter   = 'DEPROVISIONED'


def main():
    if getuser_flag == 'YES':
        print('\n****************** Listing Users ******************')
        get_users()

    if delete_flag == 'YES':
        print('\n****************** Deleting Users ******************')
        delete_users()


def get_users():
    """Print Users list in CSV file, filter by STATUS (To confirm the users before
    deleting it)"""
    url = f'{okta_server}/api/v1/users?limit=200&filter=status eq "{getuser_filter}"'
    okta_get_resp = requests.get(url, headers=headers)
    csv_file = os.getcwd() + '\Get_Okta_Users.csv'

    if okta_get_resp.status_code > 200:
        print('\nUnable to get response from Okta - get_users(). status_code = ', okta_get_resp)
        raise Exception(okta_get_resp)
    else:
        employee_data = open(csv_file, 'w')
        csvwriter = csv.writer(employee_data, lineterminator='\n')
        print('\nWriting output to ' + csv_file)
        # Write Header in CSV
        csvwriter.writerow(['Okta_ID', 'Status', 'FirstName',
                            'LastName', 'FirmCode', 'Email', 'OktaLogin', 'sAMAccountName']),

        while True:
            for emp in okta_get_resp.json():
                # Write each employee data in a separate row
                csvwriter.writerow([emp.get('id'), emp.get('status'), emp.get('profile').get('firstName'), emp.get('profile').get(
                    'lastName'), emp.get('profile').get('firmCode'), emp.get('profile').get('email'), emp.get('profile').get('login'), emp.get('profile').get('sAMAccountName')])

            # Terminate if next url not found in 'Link' (response header)

            nextLink = okta_get_resp.links.get('next')

            if nextLink is None:
                employee_data.close()
                break

            #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
            elif okta_get_resp.status_code == 429:
                sleep = int(okta_get_resp.headers.get(
                    'X-Rate-Limit-Reset')) - int(time.time())
                print(
                    f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
                time.sleep(5) if sleep < 5 else time.sleep(sleep)

            # Get the nextLink URL and make a request
            else:
                okta_get_resp = requests.get(nextLink['url'], headers=headers)


def delete_users_thread(row):
    """Delete users based on various filters"""
    while True:
        # This operation on a user that hasn't been deactivated causes that user to be deactivated. A second delete operation is required to actually DELETE the user.
        okta_delete_resp = requests.delete(row["DeleteAPI"], headers=headers)

        #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
        if okta_delete_resp.status_code == 429:
            sleep = int(okta_delete_resp.headers.get(
                'X-Rate-Limit-Reset')) - int(time.time())
            print(
                f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
            time.sleep(5) if sleep < 5 else time.sleep(sleep)

        # status_code = 404 meaning user id not found. (user deleted successfully)
        if okta_delete_resp.status_code == 404:
            break

        # status_code = 400 meaning cannot delete Technical contact for the Org.
        # status_code = 403 meaning cannot delete Okta Org Admin.
        if okta_delete_resp.status_code in [400, 403]:
            print(f'Cannot delete Okta Org Admin user {row["FirstName"]} {row["LastName"]} {okta_delete_resp.text}')
            break

    print(f'\tDeleted = {row["FirstName"]} {row["LastName"]}')


def delete_users():
    url = f'{okta_server}/api/v1/users?limit=200&filter=status eq "{delete_filter}"'
    okta_get_resp = requests.get(url, headers=headers)
    csv_file = os.getcwd() + '\Delete_Okta_Users.csv'

    if okta_get_resp.status_code > 200:
        print('\nUnable to get response from Okta - delete_users(). status_code = ', okta_get_resp)
        raise Exception(okta_get_resp)
    else:
        employee_data = open(csv_file, 'w')
        csvwriter = csv.writer(employee_data, lineterminator='\n')
        print('\nWriting output to ' + csv_file)
        # Write Header in CSV
        csvwriter.writerow(['Okta_ID', 'Status', 'FirstName',
                            'LastName', 'FirmCode', 'Email', 'OktaLogin', 'sAMAccountName', 'DeleteAPI'])
        while True:
            for emp in okta_get_resp.json():
                # Write each employee data in a separate row
                csvwriter.writerow([emp.get('id'), emp.get('status'), emp.get('profile').get('firstName'), emp.get('profile').get(
                    'lastName'), emp.get('profile').get('firmCode'), emp.get('profile').get('email'), emp.get('profile').get('login'), emp.get('profile').get('sAMAccountName'), okta_server + '/api/v1/users/' +
                    emp.get('id') + '?sendEmail=false'])

            # Terminate if next url not found in 'Link' (response header)

            nextLink = okta_get_resp.links.get('next')

            if nextLink is None:
                employee_data.close()
                break

            #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
            elif okta_get_resp.status_code == 429:
                sleep = int(okta_get_resp.headers.get(
                    'X-Rate-Limit-Reset')) - int(time.time())
                print(
                    f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
                time.sleep(5) if sleep < 5 else time.sleep(sleep)

            # Get the nextLink URL and make a request
            else:
                okta_get_resp = requests.get(nextLink['url'], headers=headers)

    # Delete users starts from here
    with open(csv_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                line_count += 1

            x = threading.Thread(target=delete_users_thread, args=(row,))
            x.start()

            line_count += 1
        if line_count == 0:
            print(f'Total {line_count} users deleted successfully')
        else:
            print(f'Total {line_count - 1} users deleted successfully')


main()
