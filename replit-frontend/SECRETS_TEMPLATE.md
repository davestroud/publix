# Frontend Replit Secrets Configuration

Copy these secrets to your Replit Secrets tab. Replace placeholder values with your actual backend Repl URL.

## Required Secrets

### API Configuration
```
VITE_API_URL=https://publix-backend.yourusername.repl.co/api
```

**Important**: Replace `publix-backend.yourusername.repl.co` with your actual backend Repl URL.

## How to Set Secrets in Replit

1. Click the **lock icon** (🔒) in the left sidebar
2. Click **"New secret"**
3. Enter the secret name: `VITE_API_URL`
4. Enter the secret value: `https://<your-backend-repl-url>/api`
5. Click **"Add secret"**

## Alternative: Using .env File

You can also create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=https://publix-backend.yourusername.repl.co/api
```

**Note**: If using `.env` file, make sure it's in the `frontend/` directory, not the root of the Repl.

## Important Notes

- The `VITE_` prefix is required for Vite to expose the variable to your code
- After setting `VITE_API_URL`, restart your Repl for changes to take effect
- For development mode, Vite will use this URL for API calls
- For production builds, this URL is baked into the build at compile time

