# PyPG Client - Implementation Plan

## Project Overview

Build a Gmail-like web email client on port 5005 that connects to the mail server API at port 5003.

## Phase 1: Project Setup & Core Infrastructure

### 1.1 Directory Structure Setup
```
~/git/py_pg_client/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── api_client.py         # Mail server API wrapper
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Login/logout
│   │   ├── emails.py         # Inbox, compose, read
│   │   ├── folders.py        # Folder management
│   │   ├── whitelist.py      # Domain whitelist
│   │   └── blacklist.py      # IP blacklist view
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── inbox.html
│   │   ├── email_detail.html
│   │   ├── compose.html
│   │   ├── folders.html
│   │   ├── whitelist.html
│   │   └── blacklist.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── coding_agent/
│   └── plan.md
├── requirements.txt
├── run.py
└── AGENTS.md
```

### 1.2 Configuration & Dependencies

**requirements.txt**:
```
flask>=2.0.0
requests>=2.28.0
psycopg2-binary>=2.9.0
python-dotenv>=0.19.0
flask-wtf>=1.0.0
wtforms>=3.0.0
flask-login>=0.6.0
email-validator>=1.3.0
```

**config.py**:
- Port: 5005
- Mail server API URL: http://localhost:5003
- Database: Use separate client DB or same as server (recommend separate for client-only data)
- Secret key for sessions

### 1.3 Database Setup

**Create client database**: `mail_server_client`

**Schema**:
```sql
-- Domain Whitelist
CREATE TABLE domain_whitelist (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) UNIQUE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User sessions (optional, for remembering logged in users)
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);
```

### 1.4 API Client Module

**app/api_client.py**:
- Class `MailServerAPI`
- Methods for each endpoint:
  - `login(email, password)` → returns JWT token
  - `get_emails(token, folder_id=None, page=1, limit=20)`
  - `get_email(token, email_id)`
  - `send_email(token, to, subject, body)`
  - `mark_read(token, email_id)`
  - `toggle_star(token, email_id)`
  - `delete_email(token, email_id)`
  - `move_email(token, email_id, folder_id)`
  - `get_folders(token)`
  - `create_folder(token, name)`
  - `search_emails(token, query, filters)`
  - `get_blacklist(token)`
  - `remove_from_blacklist(token, ip_id)`
  - `get_blacklist_stats(token)`

All methods should:
- Handle 401 errors (redirect to login)
- Handle network errors
- Return parsed JSON or raise appropriate exceptions

## Phase 2: Authentication

### 2.1 Login Page

**Template**: `app/templates/login.html`

**Features**:
- Email input (pre-fill with michael@protophysics.com.au)
- Password input
- Submit button
- Error message display
- Remember me checkbox (optional)

**Route**: `GET/POST /login`

**Flow**:
1. Show login form
2. On POST, call `MailServerAPI.login(email, password)`
3. If success: store token in server-side session, redirect to inbox
4. If failure: show error message

### 2.2 Logout

**Route**: `GET /logout`

**Actions**:
- Clear session
- Redirect to login

### 2.3 Authentication Decorator

**Create**: `@login_required` decorator
- Check if session has valid token
- If not, redirect to login
- If yes, proceed

## Phase 3: Inbox & Email Reading

### 3.1 Base Template

**app/templates/base.html**:
- Gmail-style layout (sidebar + main content)
- Navigation: Compose, Inbox, Sent, Drafts, Starred, Trash, Folders
- Top bar: Search, User menu, Logout
- CSS framework: Use TailwindCSS via CDN or plain CSS

### 3.2 Inbox View

**Route**: `GET /inbox` (default route after login)

**Template**: `app/templates/inbox.html`

**Features**:
- Email list with columns: Star icon, Sender, Subject (bold if unread), Preview, Date
- Click to open email
- Star/unstar toggle
- Checkbox for bulk actions (optional for MVP)
- Pagination (20 per page)
- Show current folder name

**Data needed**:
- Call `GET /api/emails` with folder filter
- Parse response and render

### 3.3 Email Detail View

**Route**: `GET /emails/<id>`

**Template**: `app/templates/email_detail.html`

**Features**:
- Subject line (large)
- Sender info
- Date
- To/CC recipients
- Email body (HTML or plain text)
- Action bar: Reply, Forward, Delete, Move, Star, Mark read/unread
- Navigation: Back to inbox, Previous/Next email

**Data needed**:
- Call `GET /api/emails/<id>`
- Render body safely (escape if plain text, sanitize if HTML)

## Phase 4: Email Composition

### 4.1 Compose Page

**Route**: `GET/POST /compose`

**Template**: `app/templates/compose.html`

**Features**:
- To field (with validation)
- Subject field
- Body textarea (rich text optional, plain text for MVP)
- Send button
- Save draft button (optional)
- Discard button

**Flow**:
1. Show compose form
2. On POST, call `POST /api/emails`
3. On success: redirect to sent folder with success message
4. On error: show error message

### 4.2 Reply & Forward

**Routes**:
- `GET /emails/<id>/reply`
- `GET /emails/<id>/forward`

**Features**:
- Pre-fill subject (Re: or Fw:)
- Pre-fill body with quoted original
- Pre-fill To field (original sender for reply)
- Same compose UI

## Phase 5: Email Actions

### 5.1 Mark Read/Unread

**Route**: `POST /emails/<id>/read` (toggle)

**Action**:
- Call `POST /api/emails/<id>/read`
- Redirect back to inbox or stay on email detail

### 5.2 Star/Unstar

**Route**: `POST /emails/<id>/star` (toggle)

**Action**:
- Call `POST /api/emails/<id>/star`
- Update UI with AJAX (no page reload) or redirect

### 5.3 Delete

**Route**: `POST /emails/<id>/delete`

**Action**:
- Call `DELETE /api/emails/<id>`
- Redirect to inbox with success message

### 5.4 Move to Folder

**Route**: `POST /emails/<id>/move`

**Features**:
- Dropdown of available folders
- Submit to move
- Call `POST /api/emails/<id>/move`

## Phase 6: Folder Management

### 6.1 Folder List

**Route**: `GET /folders`

**Template**: `app/templates/folders.html`

**Features**:
- List all folders (system + custom)
- Show email count per folder (optional)
- Create new folder button
- Delete custom folders

### 6.2 Create Folder

**Route**: `POST /folders/create`

**Features**:
- Simple form with name input
- Call `POST /api/folders`

### 6.3 Delete Folder

**Route**: `POST /folders/<id>/delete`

**Features**:
- Confirmation dialog
- Call appropriate API endpoint

## Phase 7: Search

### 7.1 Search Bar

**Location**: Top bar in base template

**Features**:
- Text input
- Search button
- Optional filters (folder, date range)

### 7.2 Search Results

**Route**: `GET /search?q=<query>`

**Template**: Same as inbox or dedicated search results

**Features**:
- Display search results
- Show "Searching for: <query>"
- Pagination

## Phase 8: Domain Whitelist (NEW FEATURE)

### 8.1 Database

**Already in Phase 1.3**

### 8.2 Whitelist Management Page

**Route**: `GET /whitelist`

**Template**: `app/templates/whitelist.html`

**Features**:
- List all whitelisted domains
- Add new domain form
- Remove domain button
- Notes field for each domain
- Search/filter whitelist

### 8.3 Add Domain

**Route**: `POST /whitelist/add`

**Validation**:
- Validate domain format
- Check for duplicates
- Insert into `domain_whitelist` table

### 8.4 Remove Domain

**Route**: `POST /whitelist/<id>/remove`

**Action**:
- Delete from database
- Show success message

### 8.5 Integration with Email Display

**In email detail view**:
- Show indicator if sender domain is whitelisted
- Show "Add to whitelist" button for non-whitelisted domains
- Show warning if sender domain looks suspicious

## Phase 9: IP Blacklist View

### 9.1 Blacklist Dashboard

**Route**: `GET /blacklist`

**Template**: `app/templates/blacklist.html`

**Features**:
- Summary statistics (from `GET /api/blacklist/stats`)
- List all blacklisted IPs
- Columns: IP Address, Reason, Source, Hit Count, Added Date, Actions
- Filter by source
- Remove IP button
- Pagination

### 9.2 Remove IP from Blacklist

**Route**: `POST /blacklist/<id>/remove`

**Action**:
- Call `DELETE /api/blacklist/ip/<id>`
- Show success/error message
- Refresh blacklist view

### 9.3 IP Check Utility

**Route**: `GET /blacklist/check?ip=<ip>`

**Features**:
- Quick check if an IP is blacklisted
- Useful for debugging
- Call `GET /api/blacklist/ip/check/<ip>`

## Phase 10: Polish & Testing

### 10.1 UI/UX Improvements

- [ ] Loading spinners for async operations
- [ ] Toast notifications for actions (success/error)
- [ ] Keyboard shortcuts (j/k navigation, r for reply, etc.)
- [ ] Responsive design for mobile
- [ ] Dark mode toggle (optional)

### 10.2 Error Handling

- [ ] 401 errors → auto-logout
- [ ] 5xx errors → show friendly error page
- [ ] Network errors → retry logic with exponential backoff
- [ ] Form validation errors → inline display

### 10.3 Security

- [ ] CSRF protection on all forms
- [ ] XSS prevention (escape output)
- [ ] Secure session cookies
- [ ] Rate limiting (optional)

### 10.4 Testing

**Manual Testing Checklist**:
- [ ] Login/logout works
- [ ] Can view inbox with correct emails
- [ ] Can open and read email
- [ ] Can compose and send email
- [ ] Reply and forward work
- [ ] Star/unstar works
- [ ] Mark read/unread works
- [ ] Delete works
- [ ] Can create custom folders
- [ ] Can move emails between folders
- [ ] Search works
- [ ] Domain whitelist: add/remove/list works
- [ ] Can see whitelist status on emails
- [ ] Blacklist view shows data from server
- [ ] Can remove IPs from blacklist
- [ ] All actions have proper feedback

### 10.5 Documentation

- [ ] Update AGENTS.md with any changes
- [ ] Add README.md with setup instructions
- [ ] Add inline code comments

## Implementation Order for Efficiency

### Sprint 1: Core (Days 1-2)
1. Setup project structure
2. Config and dependencies
3. Database setup
4. API client module
5. Login/logout
6. Base template

### Sprint 2: Inbox (Days 3-4)
7. Inbox view
8. Email detail view
9. Mark read/unread
10. Star/unstar
11. Delete

### Sprint 3: Composition (Days 5-6)
12. Compose email
13. Reply
14. Forward
15. Move to folder

### Sprint 4: Organization (Days 7-8)
16. Folder management
17. Search functionality

### Sprint 5: Advanced Features (Days 9-10)
18. Domain whitelist (database + UI)
19. IP blacklist view
20. Testing and polish

## Key Technical Decisions

### Architecture Choice: Flask + Server-Side Rendering
**Rationale**: 
- Simpler than full SPA
- Easier to secure (JWT stays server-side)
- Faster initial development
- Gmail-like feel can still be achieved with HTMX or minimal JS

### API Integration Pattern
```python
# api_client.py pattern
class MailServerAPI:
    def __init__(self):
        self.base_url = "http://localhost:5003"
    
    def _make_request(self, method, endpoint, token, **kwargs):
        headers = {'Authorization': f'Bearer {token}'}
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            raise AuthenticationError()
        
        response.raise_for_status()
        return response.json()
```

### Session Management
- Store JWT in Flask session (server-side, encrypted)
- Never expose JWT to client-side JavaScript
- Session timeout = JWT expiration (24 hours)

### Database Pattern
- Use SQLAlchemy ORM or raw psycopg2 with dict cursors
- Transactions for all write operations
- Connection pooling (optional for MVP)

## Dependencies Between Features

```
Login → Inbox → Email Detail → Compose
                    ↓              ↓
               Mark Read      Reply/Forward
               Star/Unstar
               Delete
               Move
                    ↓
               Folder Management
                    ↓
               Search
                    ↓
            Domain Whitelist
            IP Blacklist View
```

## Risk Mitigation

### Risk: Mail server API changes
**Mitigation**: Centralize all API calls in `api_client.py`, easy to update

### Risk: Token expiration during use
**Mitigation**: 401 handler redirects to login with "session expired" message

### Risk: Database connection issues
**Mitigation**: Connection retries, clear error messages

### Risk: Complex UI interactions
**Mitigation**: Start simple (server-rendered), add JS enhancements later

## Success Metrics

- [ ] Runs on port 5005
- [ ] All core features work without errors
- [ ] UI is clean and intuitive
- [ ] Gmail-like workflow feels natural
- [ ] Can manage whitelist and view blacklist
- [ ] Tests pass (if automated tests added)

## Notes for Implementing Agent

1. **Start simple**: Get login and inbox working first, then iterate
2. **Use the mail server API docs**: Keep `~/git/py_pg_email/coding_agent/API_INTEGRATION_GUIDE.md` open
3. **Test frequently**: After each feature, test it manually
4. **CSS framework**: Recommend TailwindCSS via CDN for quick styling
5. **Icons**: Use Font Awesome or Heroicons via CDN
6. **Date formatting**: Use Python's datetime or JavaScript's Intl.DateTimeFormat
7. **Email body display**: Be careful with HTML emails - sanitize or use iframes
8. **Error messages**: Make them user-friendly, not technical

## Questions for User (if unclear)

1. Should the client share the database with the mail server or have its own?
2. Do you want real-time updates (WebSocket) or page refresh?
3. Should emails be cached locally or always fetched from server?
4. What color scheme preference? (Gmail-like blue/white, or custom?)
