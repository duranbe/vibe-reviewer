# Setting up Mistral API Key

## Step 1: Get your Mistral API Key

1. Go to the [Mistral AI Console](https://console.mistral.ai/)
2. Navigate to the "API Keys" section
3. Create a new API key or use an existing one
4. Copy the API key value

## Step 2: Add the API Key to GitHub Secrets

### Method A: Using GitHub UI

1. Go to your repository on GitHub: `https://github.com/your-username/vibe-reviewer`
2. Click on "Settings" (top tab)
3. In the left sidebar, click on "Secrets and variables" > "Actions"
4. Click on "New repository secret"
5. Enter "MISTRAL_API_KEY" as the name
6. Paste your API key as the value
7. Click "Add secret"


## Step 3: Verify the Setup

1. Create a test pull request
2. Check the workflow logs to see if the Mistral API call is successful
3. You should see debug messages like:
   ```
   DEBUG: Sending diff to Mistral API for review
   DEBUG: Mistral review: [AI review content]
   ```

## Troubleshooting

### If you see "DEBUG: MISTRAL_API_KEY not set"
- Verify the secret name is exactly "MISTRAL_API_KEY" (case-sensitive)
- Check that the secret is in the correct repository
- Ensure the workflow has permission to access secrets

### If you see API errors
- Verify your API key is valid and not expired
- Check your Mistral account has sufficient quota
- Ensure you're using the correct API endpoint

### If the workflow fails
- Check the workflow logs for detailed error messages
- The debug logs will show exactly where the failure occurred
