#!/usr/bin/env python3
"""Test script to verify LangSmith connection"""
import os
from dotenv import load_dotenv

load_dotenv()

# Set environment variables BEFORE importing LangChain
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT", "publix-expansion-predictor")

if langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = langsmith_project

print("=" * 60)
print("LangSmith Connection Test")
print("=" * 60)
if langsmith_api_key:
    key_preview = (
        langsmith_api_key[:15] + "..."
        if len(langsmith_api_key) > 15
        else langsmith_api_key
    )
    print(f"API Key: ✅ Set ({key_preview})")
else:
    print("API Key: ❌ Not set")
print(f"Project: {langsmith_project}")
print()

# Test LangSmith API directly
try:
    from langsmith import Client

    client = Client(api_key=langsmith_api_key)

    # Try to list projects
    print("Testing LangSmith API connection...")
    projects = list(client.list_projects(limit=10))

    print(f"✅ Connected to LangSmith!")
    print(f"   Found {len(projects)} projects:")
    for proj in projects[:5]:
        print(f"   - {proj.name} (id: {proj.id})")

    # Check if our project exists
    project_names = [p.name for p in projects]
    if langsmith_project in project_names:
        print(f'\n✅ Project "{langsmith_project}" found!')
    else:
        print(f'\n⚠️  Project "{langsmith_project}" not found.')
        if project_names:
            print(f'   Available projects: {", ".join(project_names[:5])}')
            print(f"   Update LANGSMITH_PROJECT in .env to match an existing project")
        else:
            print("   No projects found. Create one in LangSmith dashboard first.")

except Exception as e:
    print(f"❌ Error connecting to LangSmith: {e}")
    print("   Check that your LANGSMITH_API_KEY is correct")

print()
print("=" * 60)
