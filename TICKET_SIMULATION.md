# Ticket Simulation Guide

This guide explains how to use the ticket simulation script to generate realistic test data for the IT Help Desk system.

## Overview

The `simulate_tickets.py` script creates realistic IT tickets with:
- Various categories (Hardware, Software, Network, Access)
- Different priorities (Low, Medium, High, Critical)
- Multiple statuses (Open, In Progress, Pending, Resolved, Closed)
- Realistic timestamps spanning the past 60 days
- Comments and conversation history
- Proper assignee relationships

## Features

### Ticket Generation
- **50+ ticket templates** with realistic titles and descriptions
- **27 categories** covering common IT issues
- **15 locations** representing different office areas
- **Automatic ticket numbering** (T-1000, T-1001, etc.)
- **Random timestamps** distributed over the past 60 days

### Realistic Data
- **Status distribution**: 
  - Open: 15%
  - In Progress: 25%
  - Pending: 10%
  - Resolved: 30%
  - Closed: 20%
- **Comments**: Tickets get 0-8 comments based on status
- **Assignments**: Non-open tickets are assigned to IT department users
- **Resolution dates**: Resolved/Closed tickets have proper resolution timestamps

## Usage

### Basic Usage

```bash
# Create 50 tickets (default)
python simulate_tickets.py

# Create specific number of tickets
python simulate_tickets.py 100

# Keep existing tickets (don't delete)
python simulate_tickets.py 50 --keep-existing
```

### Prerequisites

1. **Database must be running** and accessible
2. **Users must exist** in the database
3. **At least one IT department user** recommended for assignments

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `num_tickets` | Number of tickets to create | 50 |
| `--keep-existing` | Don't delete existing tickets | False (will delete) |

### Examples

```bash
# Generate 30 tickets, delete existing ones
python simulate_tickets.py 30

# Generate 100 tickets, keep existing ones
python simulate_tickets.py 100 --keep-existing

# Generate default 50 tickets
python simulate_tickets.py
```

## Output

The script provides detailed output:

```
🚀 Starting ticket simulation...

📊 Configuration:
   - Number of tickets: 50
   - Delete existing: True
   - Time range: Past 60 days

👥 Found 15 users in database

🗑️  Deleting all existing tickets and comments...
✅ Deleted 23 tickets and 47 comments

📝 Creating 50 tickets with realistic data...

🆕 Created: T-1000 - Computer running very slow... [Open] (2026-01-15)
🔄 Created: T-1001 - Cannot access network printer... [In Progress] (2026-01-18)
✅ Created: T-1002 - Email not working properly... [Resolved] (2026-01-20)
...

💾 Saved batch 1
...

================================================================================
✅ Successfully created 50 tickets!
================================================================================

📊 Summary by Status:
   Closed          :   9 ( 18.0%)
   In Progress     :  13 ( 26.0%)
   Open            :   8 ( 16.0%)
   Pending         :   5 ( 10.0%)
   Resolved        :  15 ( 30.0%)

📊 Summary by Priority:
   Critical        :  11 ( 22.0%)
   High            :  14 ( 28.0%)
   Low             :  12 ( 24.0%)
   Medium          :  13 ( 26.0%)

🎉 Simulation completed successfully!
```

## Data Structure

### Ticket Categories

The script includes 27 realistic categories:

**Hardware**
- Computer (Slow Performance, Not Booting, Blue Screen)
- Printer (Paper Jam, Not Printing, Toner Issue)
- Monitor (Display Issues)
- Keyboard (Keys Not Working)
- Mouse (Not Responding)

**Software**
- Application (Installation, Error, License Issue)
- Email (Cannot Send, Cannot Receive, Spam Issues)
- Operating System (Update Failed, Crash)

**Network**
- Internet (Slow Connection, No Connection)
- WiFi (Cannot Connect, Weak Signal)
- VPN (Connection Failed)

**Access**
- Account (Password Reset, Locked Account)
- Permissions (File Access, Folder Access, Application Access)

### Ticket Templates

20+ realistic ticket scenarios including:
- Computer performance issues
- Printer problems
- Email issues
- Network connectivity
- Software installation requests
- Access permission requests
- Hardware failures
- System errors

### Comment Templates

15+ IT technician responses and 10+ user responses for realistic conversations.

## Technical Details

### Database Models

The script works with:
- `ITTicket` - Main ticket model
- `TicketComment` - Comment/conversation model
- `User` - User model for requesters and assignees

### Time Distribution

- Tickets are created with random timestamps over the past 60 days
- Business hours preference (8 AM - 5 PM)
- Comments are added with realistic time gaps
- Resolution times vary from 1-72 hours

### Assignment Logic

- Open tickets: No assignee
- Other statuses: Randomly assigned to IT department users
- Falls back to any user if no IT users exist

## Troubleshooting

### No users found
```
❌ No users found in database. Please create users first.
```
**Solution**: Create users in the database before running simulation

### Database connection error
**Solution**: Ensure database is running and `.env` file is configured correctly

### Import errors
**Solution**: Make sure you're running from the project root directory

## Integration

This script is designed to work with:
- FastAPI backend
- SQLAlchemy async ORM
- PostgreSQL database
- IT Help Desk module

## Best Practices

1. **Run in development only** - Don't use in production
2. **Backup data** before running with `--keep-existing`
3. **Create users first** - Ensure users exist before generating tickets
4. **Adjust count** based on testing needs
5. **Review output** to verify data quality

## Future Enhancements

Potential improvements:
- Asset request tickets
- Approval workflows
- Attachments simulation
- Email notifications
- SLA tracking
- Custom date ranges
- Specific user assignments

## Support

For issues or questions:
1. Check database connection
2. Verify user data exists
3. Review error messages
4. Check application logs
