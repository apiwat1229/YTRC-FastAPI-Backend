# Quick Start - Ticket Simulation

## Backend (Python)

### Install & Run

```bash
# Make sure you're in the BackEnd-FastAPI directory
cd C:\Users\apiwa\Desktop\BackEnd-FastAPI

# Run simulation (default 50 tickets)
python simulate_tickets.py

# Custom number of tickets
python simulate_tickets.py 100

# Keep existing tickets
python simulate_tickets.py 50 --keep-existing
```

### What You Get

- ✅ 50+ realistic ticket templates
- ✅ 27 categories (Hardware, Software, Network, Access)
- ✅ 15 office locations
- ✅ 4 priority levels
- ✅ 5 status types with proper distribution
- ✅ Automatic comments (0-8 per ticket)
- ✅ IT staff assignments
- ✅ 60-day historical data
- ✅ Realistic timestamps

### Example Output

```
🚀 Starting ticket simulation...
👥 Found 15 users in database
🗑️  Deleted 23 tickets and 47 comments
📝 Creating 50 tickets...

🆕 Created: T-1000 - Computer running very slow... [Open]
🔄 Created: T-1001 - Cannot access printer... [In Progress]
✅ Created: T-1002 - Email not working... [Resolved]

📊 Summary by Status:
   Open            :   8 ( 16.0%)
   In Progress     :  13 ( 26.0%)
   Pending         :   5 ( 10.0%)
   Resolved        :  15 ( 30.0%)
   Closed          :   9 ( 18.0%)

🎉 Simulation completed successfully!
```

### Requirements

- Database running and accessible
- Users exist in database
- Python environment configured

---

## Frontend (TypeScript)

### Install & Run

```bash
# Make sure you're in the Desktop-ServiceHub directory
cd C:\Users\apiwa\Desktop\Desktop-ServiceHub

# Get your auth token first (see below)

# Run enhanced simulation (default 50 tickets)
AUTH_TOKEN=your_token npm run simulate:tickets

# Custom number of tickets
AUTH_TOKEN=your_token npm run simulate:tickets 100

# Keep existing tickets
AUTH_TOKEN=your_token npm run simulate:tickets 50 --keep-existing

# Original simple simulation
AUTH_TOKEN=your_token npm run manage:tickets
```

### Get Auth Token

1. Login to the application
2. Press **F12** (DevTools)
3. Go to **Application** → **Local Storage**
4. Copy the `accessToken` value
5. Use it in the command above

### What You Get

Same features as backend simulation:
- ✅ 20+ realistic tickets
- ✅ 27 categories
- ✅ Comments and conversations
- ✅ Proper status distribution
- ✅ IT staff assignments
- ✅ 60-day time range

### Example Output

```
🚀 Starting enhanced ticket simulation...
👥 Found 15 users
🗑️  Deleted 23 tickets successfully
📝 Creating 50 tickets...

🆕 Created: T-1000 - Computer running very slow... [Open]
🔄 Created: T-1001 - Printer issues... [In Progress]

💾 Progress: 10/50 tickets created

✅ Successfully created 50 tickets!

📊 Summary by Status:
   Open            :   8 ( 16.0%)
   In Progress     :  13 ( 26.0%)
   Resolved        :  15 ( 30.0%)

🎉 Simulation completed successfully!
```

### Requirements

- Backend API running (http://localhost:2530)
- Valid authentication token
- Users exist in database

---

## Comparison

| Feature | Backend Script | Frontend Script |
|---------|---------------|-----------------|
| Language | Python | TypeScript |
| Direct DB | ✅ Yes | ❌ No (via API) |
| Speed | ⚡ Very Fast | 🐢 Slower (API calls) |
| Auth Required | ❌ No | ✅ Yes |
| Comments | ✅ Yes | ✅ Yes |
| Assignments | ✅ Yes | ✅ Yes |

### When to Use Which?

**Use Backend Script when:**
- You have direct database access
- You want faster execution
- You're doing backend development
- You don't want to deal with auth tokens

**Use Frontend Script when:**
- You only have API access
- You want to test API endpoints
- You're doing frontend development
- You want to simulate real user behavior

---

## Tips

1. **Start small**: Test with 10-20 tickets first
2. **Backup data**: Use `--keep-existing` if unsure
3. **Check users**: Ensure users exist before running
4. **Monitor output**: Watch for errors in the logs
5. **Review data**: Check generated tickets in the UI

## Troubleshooting

### Backend Script

**"No users found"**
→ Create users in database first

**Database connection error**
→ Check `.env` file and database status

### Frontend Script

**"AUTH_TOKEN required"**
→ Provide token: `AUTH_TOKEN=xxx npm run simulate:tickets`

**"No users found"**
→ Create users through admin panel

**API connection error**
→ Ensure backend is running on port 2530

---

## Full Documentation

- Backend: See `TICKET_SIMULATION.md` in BackEnd-FastAPI
- Frontend: See `TICKET_SIMULATION.md` in Desktop-ServiceHub
