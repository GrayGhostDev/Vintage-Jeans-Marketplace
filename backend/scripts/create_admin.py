#!/usr/bin/env python3
"""
Create the first admin user for Vintage Jeans Marketplace.

This script:
1. Registers a new user via the API
2. Updates their role to 'admin' in Supabase
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, str(backend_dir))

from research.db.supabase_client import get_supabase_client


def create_admin_user(
    email: str,
    password: str,
    full_name: str,
    api_url: str = "http://localhost:8000"
):
    """Create an admin user."""

    print(f"🚀 Creating admin user: {email}")
    print(f"📍 API URL: {api_url}")

    # Step 1: Register user via API
    print("\n1️⃣ Registering user via API...")
    register_data = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "location": "Platform Admin"
    }

    try:
        response = requests.post(
            f"{api_url}/api/sellers/register",
            json=register_data,
            timeout=10
        )
        response.raise_for_status()
        user_data = response.json()
        user_id = user_data.get("id")
        print(f"✅ User registered successfully!")
        print(f"   User ID: {user_id}")
        print(f"   Email: {user_data.get('email')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to register user: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return False

    # Step 2: Update role to admin in Supabase
    print("\n2️⃣ Updating role to admin in Supabase...")
    try:
        supabase = get_supabase_client()
        result = supabase.table("sellers").update({
            "role": "admin"
        }).eq("id", user_id).execute()

        if result.data:
            print(f"✅ User role updated to admin!")
        else:
            print(f"⚠️  Warning: Update returned no data")
    except Exception as e:
        print(f"❌ Failed to update role: {e}")
        return False

    # Step 3: Verify admin user
    print("\n3️⃣ Verifying admin user...")
    try:
        result = supabase.table("sellers").select("*").eq("id", user_id).execute()
        if result.data:
            user = result.data[0]
            print(f"✅ Admin user verified!")
            print(f"   ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"   Name: {user['full_name']}")
            print(f"   Role: {user['role']}")
            print(f"   Created: {user['created_at']}")
        else:
            print(f"⚠️  Warning: Could not verify user")
    except Exception as e:
        print(f"❌ Failed to verify user: {e}")
        return False

    print("\n✨ Admin user created successfully!")
    print(f"\n📧 Login credentials:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"\n🔗 Login at: https://vintage-jeans-marketplace.vercel.app/login")

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create the first admin user for Vintage Jeans Marketplace"
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Admin user email"
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Admin user password"
    )
    parser.add_argument(
        "--name",
        default="Platform Admin",
        help="Admin user full name (default: Platform Admin)"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Use production API URL (https://vintage-jeans-api.onrender.com)"
    )

    args = parser.parse_args()

    # Determine API URL
    if args.production:
        api_url = "https://vintage-jeans-api.onrender.com"
    else:
        api_url = args.api_url

    # Create admin user
    success = create_admin_user(
        email=args.email,
        password=args.password,
        full_name=args.name,
        api_url=api_url
    )

    sys.exit(0 if success else 1)
