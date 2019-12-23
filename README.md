# Okta User Lifecycle Management

DELETE the Okta users in BULK based on its status. 

This code is written in Python language and uses multi-threading to furiously delete the Okta users.

	Please update the variables as below:
  
    OKTA_SERVER   [https://<>.okta.com]
    API_TOKEN     [Use your API Token which has privilege to delete users ]

    DELETE_FLAG   [YES | NO]
    GETUSER_FLAG  [YES | NO]

    DELETE_FILTER   ["DEPROVISIONED" (Deactivated) | "PROVISIONED" | "SUSPENDED" | "STAGED" | "ACTIVE"]
         (Delete users based on it's current status.)
    GETUSER_FILTER  ["DEPROVISIONED" (Deactivated) | "PROVISIONED" | "SUSPENDED" | "STAGED" | "ACTIVE"]
		    (to list all Staged users before deleting or activating users)

    Developed By : Vipul Kaneriya.
