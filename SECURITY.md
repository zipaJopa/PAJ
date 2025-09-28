# ⚠️ CRITICAL SECURITY NOTICE

## 🔴 PUBLIC REPOSITORY WARNING

**PAI is a PUBLIC version of the personal PAI_DIRECTORY infrastructure**

### NEVER COPY BLINDLY FROM PAI_DIRECTORY TO PUBLIC PAI

This repository is **PUBLIC** and visible to everyone on the internet. It's a sanitized, public instance of the personal PAI_DIRECTORY infrastructure. When moving functionality from PAI_DIRECTORY to PAI:

### ❌ NEVER INCLUDE:
- Personal API keys or tokens
- Private email addresses or phone numbers
- Financial account information
- Health or medical data
- Personal context files
- Business-specific information
- Client or customer data
- Internal URLs or endpoints
- Security credentials
- Personal file paths beyond ${PAI_DIR}

### ✅ SAFE TO INCLUDE:
- Generic command structures
- Public documentation
- Example configurations (with placeholder values)
- Open-source integrations
- General-purpose tools
- Public API documentation

### 🔍 BEFORE EVERY COMMIT:

1. **Audit all changes** - Review every file being committed
2. **Search for sensitive data** - grep for emails, keys, tokens
3. **Check context files** - Ensure no personal context is included
4. **Verify paths** - All paths should use ${PAI_DIR}, not personal directories
5. **Test with fresh install** - Ensure it works without your personal setup

### 📋 TRANSFER CHECKLIST:

When copying from PAI_DIRECTORY to PAI:

- [ ] Remove all API keys (replace with placeholders)
- [ ] Remove personal information
- [ ] Replace specific paths with ${PAI_DIR}
- [ ] Remove business-specific context
- [ ] Sanitize example data
- [ ] Update documentation to be generic
- [ ] Test in clean environment

### 🚨 IF YOU ACCIDENTALLY COMMIT SENSITIVE DATA:

1. **Immediately** remove from GitHub
2. Revoke any exposed API keys
3. Change any exposed passwords
4. Use `git filter-branch` or BFG to remove from history
5. Force push cleaned history
6. Audit for any data that may have been scraped

### 💡 BEST PRACTICES:

- Keep PAI_DIRECTORY private and local
- PAI should be the generic, public template
- Use environment variables for all sensitive config
- Document what needs to be configured by users
- Provide example env-example files, never real .env

---

**Remember**: PAI is meant to help everyone build their own personal AI infrastructure. Keep it clean, generic, and safe for public consumption.

**When in doubt, DON'T include it in PAI.**