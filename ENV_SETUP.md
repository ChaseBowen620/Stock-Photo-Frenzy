# Environment Variables Setup Guide

## For Local Development

Create a `.env` file in the `stock-photo-frenzy` folder with the following format:

```env
SECRET_KEY=any-random-string-here-for-sessions
SHUTTERSTOCK_BASE_URL=https://api.shutterstock.com/v2
SHUTTERSTOCK_ACCESS_TOKEN=v2/UTdBUElYYXQ0OGJYR054b0NLOGFKd2hUdlBkNTBCbWQvNDQ1MjY2NjQzL2N1c3RvbWVyLzQvYUhOcmlHRlVGLWtTQklnY0ZSLUprdTdFbTBWWmpKSDNvaWpxejNsRkk2aWVOdWJObnRzVS1zYlpyTDdtVTBxb3NSd2hGX1JtYVZGTG5rY2JNQjdtdHdmaDY5R3VsdXRMX1NuOC1kZDNyMHdZR2R5clB6MEVZU28xd3JrUURwX0tPdC1Fa3I5TG03ZHI5cno4UTFpSG1iQ1QxNHBRX0xhaEdGQlpfYjNUcXRWX19rWWNKRExrZTRyRE1IS1JZWEZ3ZVFVOFFzRmRjblU4VWJCTlYyYkFUQS9aMVhZSlVDZnFJdmFTeEdyVFd3WkVB
```

## Format Rules

1. **No quotes needed** - Environment variables should NOT have quotes around values
2. **No spaces around =** - Use `KEY=value` not `KEY = value`
3. **One per line** - Each variable on its own line
4. **No trailing spaces** - Don't add spaces at the end of lines

## Example .env File

```env
# Flask Secret Key (generate a random string)
SECRET_KEY=my-super-secret-key-change-this-in-production-12345

# Database (optional - defaults to SQLite if not set)
DATABASE_URL=sqlite:///stock_photo_frenzy.db

# Shutterstock API
SHUTTERSTOCK_BASE_URL=https://api.shutterstock.com/v2
SHUTTERSTOCK_ACCESS_TOKEN=your-full-access-token-here
```

## For Render Deployment

In the Render dashboard, add environment variables one by one:

1. Go to your service → **Environment** tab
2. Click **Add Environment Variable**
3. For each variable:
   - **Key**: `SHUTTERSTOCK_ACCESS_TOKEN`
   - **Value**: `v2/UTdBUElYYXQ0OGJYR054b0NLOGFKd2hUdlBkNTBCbWQvNDQ1MjY2NjQzL2N1c3RvbWVyLzQvYUhOcmlHRlVGLWtTQklnY0ZSLUprdTdFbTBWWmpKSDNvaWpxejNsRkk2aWVOdWJObnRzVS1zYlpyTDdtVTBxb3NSd2hGX1JtYVZGTG5rY2JNQjdtdHdmaDY5R3VsdXRMX1NuOC1kZDNyMHdZR2R5clB6MEVZU28xd3JrUURwX0tPdC1Fa3I5TG03ZHI5cno4UTFpSG1iQ1QxNHBRX0xhaEdGQlpfYjNUcXRWX19rWWNKRExrZTRyRE1IS1JZWEZ3ZVFVOFFzRmRjblU4VWJCTlYyYkFUQS9aMVhZSlVDZnFJdmFTeEdyVFd3WkVB`
   - Click **Save Changes**

**Important**: In Render, just paste the value directly - no quotes, no extra formatting needed.

## Common Mistakes to Avoid

❌ **Wrong:**
```env
SHUTTERSTOCK_ACCESS_TOKEN="v2/UTdBUElYYXQ0OGJY..."
SHUTTERSTOCK_ACCESS_TOKEN = v2/UTdBUElYYXQ0OGJY...
SHUTTERSTOCK_ACCESS_TOKEN=v2/UTdBUElYYXQ0OGJY... (with trailing space)
```

✅ **Correct:**
```env
SHUTTERSTOCK_ACCESS_TOKEN=v2/UTdBUElYYXQ0OGJY...
```

## Security Note

- **Never commit `.env` files to Git** - They're already in `.gitignore`
- **Never share your access tokens** publicly
- Use different tokens for development and production if possible

