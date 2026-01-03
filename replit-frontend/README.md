# Publix Expansion Predictor - Frontend Repl

This is the frontend Repl for the Publix Expansion Predictor application.

## Setup Instructions

1. **Upload Files**: Upload the entire `frontend/` directory from your local project to this Repl

2. **Install Dependencies**: Run `npm install` in the Replit shell

3. **Configure Environment Variables**: 
   - In Replit Secrets tab, add:
     - `VITE_API_URL` - Backend Repl URL (e.g., `https://publix-backend.yourusername.repl.co/api`)
   - Or create a `.env` file in the frontend directory:
     ```
     VITE_API_URL=https://publix-backend.yourusername.repl.co/api
     ```

4. **Development Mode**: 
   - Click "Run" to start Vite dev server
   - The app will be available at your Repl URL

5. **Production Mode** (Optional):
   - Run `npm run build` to create production build
   - Update `.replit` file to use `node serve.js` instead of `npm run dev`
   - The `serve.js` file will serve the built static files

## File Structure

```
replit-frontend/
├── .replit              # Replit configuration
├── serve.js             # Production server (optional)
├── README.md            # This file
└── frontend/            # Upload your frontend directory here
    ├── src/
    ├── public/
    ├── package.json
    ├── vite.config.js
    └── ...
```

## Development vs Production

**Development Mode** (default):
- Uses Vite dev server with hot reload
- Set `.replit` run command to: `npm run dev`
- Good for development and testing

**Production Mode**:
- Builds static files: `npm run build`
- Serves with Express: `node serve.js`
- Update `.replit` run command to: `npm run build && node serve.js`
- Better performance, but requires rebuild on changes

## Notes

- Make sure `VITE_API_URL` points to your backend Repl URL
- The frontend will run on the port provided by Replit
- CORS must be configured in the backend to allow requests from this frontend URL

