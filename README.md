# Delete Okta Users in Bulk

===== delete_okta_users.py =====

DELETE the Okta users in BULK based on its status.

This code is written in Python language and uses multi-threading to furiously delete the Okta users.

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
