import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "yojanasaathi.db")
print(f"Connecting to {db_path} to clear accounts...")
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Enable foreign keys
c.execute("PRAGMA foreign_keys = ON")

# Delete sessions, consents, profiles, user_roles, users
c.execute("DELETE FROM auth_sessions")
c.execute("DELETE FROM consents")
c.execute("DELETE FROM action_plans")
c.execute("DELETE FROM farmer_profiles")
c.execute("DELETE FROM user_roles WHERE role != 'ADMIN'")
c.execute("DELETE FROM users WHERE email_normalized != 'admin@yojanasaathi.up.gov.in'")

conn.commit()

c.execute("SELECT email_normalized, display_name FROM users")
remaining = c.fetchall()
print("Remaining users in DB after reset:", remaining)

conn.close()
print("Account reset complete! Ready for fresh registration.")

