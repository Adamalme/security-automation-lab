from ldap3 import Server, Connection

# Active Directory Server
#server = Server('DC.mydomain.com')
#server = Server('dc01.contoso.local')
server = Server('192.168.77.0')

# Connect to AD
conn = Connection(
    server,
    user='CONTOSO\\administrator',
    password='Password123!',
    auto_bind=True
)

# Search for users
conn.search(
    'DC=contoso,DC=local',
    '(objectClass=user)',
    attributes=['sAMAccountName']
)

# Print usernames
for user in conn.entries:
    print(user.sAMAccountName)

conn.unbind()