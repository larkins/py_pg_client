# PyPG Client - AI Agent Instructions

## Overview

You are building a Gmail-like web email client that connects to the mail server at `py_pg_email`. This client provides a user-friendly interface for manual email inspection, making it easier than using Swagger or database queries.

## Project Structure

**Location**: `~/git/py_pg_client`
**Port**: 5005 (must use this exact port)
**Access**: localhost only (for now)

## Mail Server API Reference

The client connects to the mail server API documented in:
- `~/git/py_pg_email/coding_agent/API_INTEGRATION_GUIDE.md`
- `~/git/py_pg_email/API_DOCUMENTATION.md`

**Key Server Details**:
- API Base URL: `http://localhost:5003`
- Authorized User: michael@protophysics.com.au
- All endpoints require JWT Bearer token (except /health)

## Required Features

### 1. Authentication
- **Login page**: Email/password form
- **JWT token management**: Store in localStorage/sessionStorage
- **Logout**: Clear tokens and redirect to login
- Use the existing user from the mail server

### 2. Email Management
- **Inbox view**: List emails with sender, subject, preview, date
- **Read email**: Full email display with HTML/text support
- **Compose**: Create and send new emails
- **Reply/Forward**: Email threading actions
- **Mark read/unread**: Toggle read status
- **Star/Unstar**: Toggle starred status
- **Delete**: Move to trash
- **Move to folder**: Change email folder

### 3. Folders (Gmail-style)
- Inbox
- Sent
- Drafts
- Trash/Spam
- Starred
- Custom folders (create/list/delete)

### 4. Search
- Search emails by subject, body, sender
- Filter by folder, read/unread, starred

### 5. Domain Whitelist (NEW)
**Purpose**: Mark domains as "safe" to prevent false positives in spam filtering

**Requirements**:
- Database table: `domain_whitelist`
  - `id`, `domain` (VARCHAR, UNIQUE), `created_at`, `notes`
- API endpoints:
  - `GET /api/whitelist/domains` - List all whitelisted domains
  - `POST /api/whitelist/domains` - Add domain to whitelist
  - `DELETE /api/whitelist/domains/<id>` - Remove domain
  - `GET /api/whitelist/check/<domain>` - Check if domain is whitelisted
- UI: Settings page to manage whitelisted domains
- Usage: When displaying emails, show whitelist status; when processing incoming emails, check against whitelist

### 6. IP Blacklist Management (Server Feature)
**Purpose**: View/manage IPs blocked at the SMTP level

**Client Requirements**:
- Read-only view of blacklist (client can display, but server manages)
- Display list of blacklisted IPs with reason, source, hit count
- Ability to remove IPs from blacklist (via server API)
- Statistics dashboard showing blacklist stats

**Server Endpoints** (from `~/git/py_pg_email`):
- `GET /api/blacklist/ip` - List blacklisted IPs
- `DELETE /api/blacklist/ip/<id>` - Remove IP
- `GET /api/blacklist/stats` - Get statistics

## Technical Stack

**Choose one of these** (pick what's most appropriate for a lean Gmail clone):
- **Option 1**: Flask + Jinja2 templates (server-side rendering, simple)
- **Option 2**: Flask + React/Vue (SPA, more interactive)
- **Option 3**: FastAPI + HTMX (modern, lightweight)

**Recommendation**: Flask + Jinja2 for simplicity, or Flask + minimal JavaScript for interactivity.

**Database**: PostgreSQL (separate from mail server DB, or share if appropriate)

## Project Architecture

```
~/git/py_pg_client/
├── app/
│   ├── __init__.py          # Flask app setup
│   ├── routes.py            # Main routes
│   ├── api_client.py        # Mail server API wrapper
│   ├── db.py                # Database connection
│   ├── models.py            # Database models
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── inbox.html
│   │   ├── email_detail.html
│   │   ├── compose.html
│   │   ├── folders.html
│   │   ├── whitelist.html   # Domain whitelist management
│   │   └── blacklist.html   # IP blacklist view
│   └── static/
│       ├── css/
│       └── js/
├── coding_agent/
│   └── plan.md              # Detailed implementation plan
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── run.py                   # Entry point
└── AGENTS.md               # This file
```

## API Integration Pattern

### Authentication Flow
```python
# Store token in session
session['jwt_token'] = token

# Use in API calls
headers = {'Authorization': f'Bearer {session["jwt_token"]}'}
response = requests.get('http://localhost:5003/api/emails', headers=headers)
```

### Error Handling
- 401 Unauthorized → Redirect to login
- 5xx Server Error → Show error message
- Network errors → Retry with exponential backoff

### Session Management
- Use Flask sessions for web state
- Store JWT token server-side (more secure than localStorage)
- Token refresh not needed (24h validity)

## Database Schema (Client-only tables)

```sql
-- Domain Whitelist (NEW)
CREATE TABLE domain_whitelist (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) UNIQUE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User preferences (optional)
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    setting_name VARCHAR(100) NOT NULL,
    setting_value TEXT,
    UNIQUE(user_email, setting_name)
);
```

## UI Design Guidelines

### Gmail-like Layout
```
┌─────────────────────────────────────────────────┐
│  Logo    Search...              User ▼  Logout  │
├────────┬────────────────────────────────────────┤
│ Compose│                                        │
│        │  Subject              Sender      Date │
│ Inbox  │  ────────────────────────────────────│
│ Sent   │  ★ Email subject      John       2m   │
│ Drafts │  Email subject 2      Jane       1h   │
│ Trash  │                                        │
│        │                                        │
│ Folders│                                        │
│   -Work│                                        │
│   -Home│                                        │
├────────┴────────────────────────────────────────┤
│  ← 1-25 of 100 →                                │
└─────────────────────────────────────────────────┘
```

### Key UI Principles
- Clean, minimal design (TailwindCSS or similar)
- Responsive layout
- Keyboard shortcuts (j/k for navigation, r for reply, etc.)
- Loading states for async operations
- Toast notifications for actions

## Implementation Priority

### Phase 1: Core (MVP)
1. Project setup (Flask, config, DB connection)
2. Login/logout
3. Inbox list view
4. Read email view
5. Compose email

### Phase 2: Email Management
6. Reply/Forward
7. Mark read/unread
8. Star/unstar
9. Delete/move to trash

### Phase 3: Organization
10. Folder management (create, list, delete)
11. Move emails between folders
12. Search functionality

### Phase 4: Admin Features
13. Domain whitelist (database + UI)
14. IP blacklist view/management (integrate with server API)
15. Settings page

## Security Considerations

1. **CSRF Protection**: Use Flask-WTF or similar
2. **XSS Prevention**: Escape all user input in templates
3. **Session Security**: Use secure session cookies
4. **API Security**: Never expose mail server JWT to client-side JS
5. **Input Validation**: Validate all form inputs
6. **SQL Injection**: Use parameterized queries

## Testing Strategy

- Unit tests for API client functions
- Integration tests for full flows
- Manual testing checklist:
  - [ ] Login/logout
  - [ ] View inbox
  - [ ] Read email
  - [ ] Compose and send
  - [ ] Reply to email
  - [ ] Star/unstar
  - [ ] Delete
  - [ ] Manage folders
  - [ ] Search
  - [ ] Domain whitelist
  - [ ] IP blacklist view

## Common Pitfalls

1. **Don't** store JWT in localStorage (use server-side session)
2. **Don't** expose mail server API credentials to browser
3. **Do** handle token expiration gracefully
4. **Do** validate all user inputs
5. **Do** use transactions for DB operations
6. **Don't** hardcode credentials in code

## Dependencies

Core requirements (add to requirements.txt):
```
flask>=2.0.0
requests>=2.28.0
psycopg2-binary>=2.9.0
python-dotenv>=0.19.0
flask-wtf>=1.0.0  # For forms and CSRF
wtforms>=3.0.0
```

Optional for better UI:
```
flask-assets>=2.0  # Asset pipeline
tailwindcss  # Via CDN or npm
htmx>=1.8.0  # For interactivity without React
```

## Getting Started

1. Read the full plan in `coding_agent/plan.md`
2. Set up the project structure
3. Implement Phase 1 (MVP)
4. Test with the mail server running on port 5003
5. Iterate through remaining phases

## Questions?

If unclear on requirements:
1. Check the API integration guide: `~/git/py_pg_email/coding_agent/API_INTEGRATION_GUIDE.md`
2. Review the mail server API docs: `~/git/py_pg_email/API_DOCUMENTATION.md`
3. Ask for clarification on specific features

## Success Criteria

- [ ] Runs on port 5005
- [ ] Can login with michael@protophysics.com.au credentials
- [ ] Can view inbox and read emails
- [ ] Can compose and send emails
- [ ] Can manage folders
- [ ] Can search emails
- [ ] Domain whitelist feature works
- [ ] IP blacklist view works
- [ ] Clean, Gmail-like UI
- [ ] All 133 server tests still pass
