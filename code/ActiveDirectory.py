from ldap3 import Server, Connection

# Replace with your actual Domain Controller
SERVER = "192.168.1.10"

# Replace with your domain account
USERNAME = "LAB\\administrator"
PASSWORD = "Password123!"

# Replace with your domain
BASE_DN = "DC=lab,DC=local"

try:
    server = Server(SERVER)

    conn = Connection(
        server,
        user=USERNAME,
        password=PASSWORD,
        auto_bind=True
    )

    print("[+] Connected to Active Directory")

    conn.search(
        search_base=BASE_DN,
        search_filter="(objectClass=user)",
        attributes=["cn", "sAMAccountName"]
    )

    print("\nUsers Found:\n")

    for user in conn.entries:
        print(f"Name: {user.cn}")
        print(f"Username: {user.sAMAccountName}")
        print("-" * 30)

    conn.unbind()

except Exception as e:
    print(f"Error: {e}")