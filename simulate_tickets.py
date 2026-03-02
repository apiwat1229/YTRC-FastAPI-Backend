"""
Ticket Simulation Script for YTRC Backend
This script creates realistic test tickets with various statuses, priorities, and comments.
"""
import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.it_ticket import ITTicket
from app.models.ticket_comment import TicketComment
from app.models.user import User


CATEGORIES = [
    "Hardware > Computer > Slow Performance",
    "Hardware > Computer > Not Booting",
    "Hardware > Computer > Blue Screen",
    "Hardware > Printer > Paper Jam",
    "Hardware > Printer > Not Printing",
    "Hardware > Printer > Toner Issue",
    "Hardware > Monitor > Display Issues",
    "Hardware > Keyboard > Keys Not Working",
    "Hardware > Mouse > Not Responding",
    "Software > Application > Installation",
    "Software > Application > Error",
    "Software > Application > License Issue",
    "Software > Email > Cannot Send",
    "Software > Email > Cannot Receive",
    "Software > Email > Spam Issues",
    "Software > Operating System > Update Failed",
    "Software > Operating System > Crash",
    "Network > Internet > Slow Connection",
    "Network > Internet > No Connection",
    "Network > WiFi > Cannot Connect",
    "Network > WiFi > Weak Signal",
    "Network > VPN > Connection Failed",
    "Access > Account > Password Reset",
    "Access > Account > Locked Account",
    "Access > Permissions > File Access",
    "Access > Permissions > Folder Access",
    "Access > Permissions > Application Access",
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "In Progress", "Pending", "Resolved", "Closed"]
LOCATIONS = [
    "Floor 1 - Office",
    "Floor 2 - Office",
    "Floor 3 - Office",
    "Floor 4 - Executive",
    "Meeting Room A",
    "Meeting Room B",
    "Meeting Room C",
    "Conference Hall",
    "Office 101",
    "Office 102",
    "Office 201",
    "Office 202",
    "Lab 1",
    "Lab 2",
    "Warehouse",
]

TICKET_TEMPLATES = [
    {
        "title": "Computer running very slow",
        "description": "My computer has been running extremely slow for the past few days. Applications take forever to load and the system freezes frequently. This is affecting my productivity significantly.",
    },
    {
        "title": "Cannot access network printer",
        "description": "I'm unable to print documents. The printer doesn't show up in my available devices list. I've tried restarting my computer but the issue persists.",
    },
    {
        "title": "Email not working properly",
        "description": "I cannot send or receive emails since this morning. Getting error messages when trying to access my mailbox. This is urgent as I need to respond to client emails.",
    },
    {
        "title": "Internet connection keeps dropping",
        "description": "My internet connection is very unstable. It disconnects every 10-15 minutes and I have to reconnect manually. This is disrupting my video conferences.",
    },
    {
        "title": "Need software installation",
        "description": "I need Adobe Acrobat Pro installed on my workstation for document editing. Please install the latest version with full features.",
    },
    {
        "title": "Password reset required",
        "description": "I forgot my password and cannot log into the system. Please reset my password so I can access my account and continue working.",
    },
    {
        "title": "File access permission needed",
        "description": "I need access to the shared drive folder for the Q1 project. Currently getting 'Access Denied' error when trying to open it.",
    },
    {
        "title": "Application showing error message",
        "description": "The ERP system keeps showing 'Runtime Error 5' whenever I try to generate reports. This started happening after yesterday's update.",
    },
    {
        "title": "System crashes randomly",
        "description": "My computer crashes without warning 2-3 times per day. I lose unsaved work each time. Please investigate and fix this issue urgently.",
    },
    {
        "title": "Network drive not accessible",
        "description": "Cannot access the network drive (Z:). Getting 'Network path not found' error. Other colleagues can access it without issues.",
    },
    {
        "title": "VPN connection failed",
        "description": "Unable to connect to company VPN from home. Getting 'Connection timeout' error. I need this to work remotely.",
    },
    {
        "title": "Monitor display flickering",
        "description": "My monitor screen flickers constantly. It's causing eye strain and headaches. Might need a replacement monitor.",
    },
    {
        "title": "Keyboard keys not responding",
        "description": "Several keys on my keyboard (E, R, T) are not working properly. Need a replacement keyboard to continue working efficiently.",
    },
    {
        "title": "Mouse cursor jumping around",
        "description": "The mouse cursor moves erratically and is very difficult to control. This makes it nearly impossible to work accurately.",
    },
    {
        "title": "Headset microphone not working",
        "description": "My headset microphone is not working during Teams calls. Others cannot hear me. The speakers work fine but mic is dead.",
    },
    {
        "title": "Blue screen error on startup",
        "description": "Getting blue screen of death (BSOD) when starting the computer. Error code: 0x0000007B. Cannot boot into Windows.",
    },
    {
        "title": "Printer paper jam issue",
        "description": "The office printer keeps jamming. Already cleared the paper tray multiple times but the problem continues. May need maintenance.",
    },
    {
        "title": "Software license expired",
        "description": "Microsoft Office license has expired. Cannot open Word or Excel files. Need license renewal urgently for daily work.",
    },
    {
        "title": "Email spam filter too aggressive",
        "description": "Important client emails are being marked as spam. Need to adjust spam filter settings to prevent legitimate emails from being blocked.",
    },
    {
        "title": "Windows update failed",
        "description": "Windows update keeps failing with error code 0x80070002. System is stuck in update loop. Please help resolve this.",
    },
    {
        "title": "WiFi signal very weak",
        "description": "WiFi signal in my office area is extremely weak. Connection drops frequently. May need additional access point installed.",
    },
    {
        "title": "Cannot access shared folder",
        "description": "Getting permission denied error when accessing \\\\server\\shared\\finance folder. I had access last week but not anymore.",
    },
    {
        "title": "Application won't launch",
        "description": "The inventory management software won't start. Double-clicking the icon does nothing. Tried reinstalling but same issue.",
    },
    {
        "title": "Laptop battery not charging",
        "description": "My laptop battery shows 'plugged in, not charging'. Battery percentage stuck at 0%. Need to check if battery needs replacement.",
    },
    {
        "title": "Toner replacement needed",
        "description": "Printer showing 'Replace Toner' message. Print quality is very poor with faded text. Please replace toner cartridge.",
    },
]

COMMENT_TEMPLATES = [
    "I've started looking into this issue. Will update soon.",
    "Could you please provide more details about when this started happening?",
    "I've assigned this to our senior technician for investigation.",
    "This appears to be a network configuration issue. Working on it.",
    "Please try restarting your computer and let me know if the issue persists.",
    "I've scheduled a visit to your desk tomorrow at 10 AM.",
    "The issue has been identified. Preparing the fix now.",
    "This is related to the recent system update. Rolling back the changes.",
    "I've ordered the replacement part. Should arrive by tomorrow.",
    "Can you send me a screenshot of the error message?",
    "This is affecting multiple users. Escalating to IT management.",
    "I've applied a temporary workaround. Permanent fix coming soon.",
    "The problem is resolved. Please test and confirm.",
    "Thank you for reporting this. We'll prioritize it.",
    "I need remote access to your computer to diagnose this properly.",
]

USER_RESPONSES = [
    "Thank you for the quick response!",
    "The issue is still occurring. Please help.",
    "Yes, I can provide more information. What do you need?",
    "The problem seems to be getting worse.",
    "I tried your suggestion but it didn't work.",
    "This is very urgent. I cannot work without this.",
    "Confirmed! The issue is now resolved. Thank you!",
    "When can I expect this to be fixed?",
    "Is there a temporary solution I can use?",
    "I appreciate your help with this.",
]


async def get_users(db: AsyncSession) -> list[User]:
    """Get all users from database"""
    result = await db.execute(select(User))
    return list(result.scalars().all())


async def delete_all_tickets(db: AsyncSession):
    """Delete all existing tickets and comments"""
    print("🗑️  Deleting all existing tickets and comments...")
    
    await db.execute(select(TicketComment))
    comments_result = await db.execute(select(TicketComment))
    comments = comments_result.scalars().all()
    for comment in comments:
        await db.delete(comment)
    
    tickets_result = await db.execute(select(ITTicket))
    tickets = tickets_result.scalars().all()
    for ticket in tickets:
        await db.delete(ticket)
    
    await db.commit()
    print(f"✅ Deleted {len(list(tickets))} tickets and {len(list(comments))} comments\n")


async def create_ticket_with_history(
    db: AsyncSession,
    ticket_no: str,
    template: dict,
    category: str,
    priority: str,
    location: str,
    requester: User,
    created_at: datetime,
    assignee: User | None = None,
    status: str = "Open",
) -> ITTicket:
    """Create a ticket with realistic history"""
    
    ticket = ITTicket(
        id=str(uuid4()),
        ticket_no=ticket_no,
        title=template["title"],
        description=template["description"],
        category=category,
        priority=priority,
        location=location,
        status=status,
        requester_id=requester.id,
        assignee_id=assignee.id if assignee else None,
        created_at=created_at,
        updated_at=created_at,
    )
    
    if status in ["Resolved", "Closed"]:
        ticket.resolved_at = created_at + timedelta(
            hours=random.randint(1, 72),
            minutes=random.randint(0, 59)
        )
    
    db.add(ticket)
    await db.flush()
    
    return ticket


async def add_comments_to_ticket(
    db: AsyncSession,
    ticket: ITTicket,
    users: list[User],
    num_comments: int = 0
):
    """Add realistic comments to a ticket"""
    if num_comments == 0:
        return
    
    requester = next((u for u in users if u.id == ticket.requester_id), None)
    assignee = next((u for u in users if u.id == ticket.assignee_id), None) if ticket.assignee_id else None
    
    comment_time = ticket.created_at
    
    for i in range(num_comments):
        comment_time += timedelta(
            hours=random.randint(0, 24),
            minutes=random.randint(5, 59)
        )
        
        if i % 2 == 0 and assignee:
            commenter = assignee
            content = random.choice(COMMENT_TEMPLATES)
        elif requester:
            commenter = requester
            content = random.choice(USER_RESPONSES)
        else:
            continue
        
        comment = TicketComment(
            id=str(uuid4()),
            ticket_id=ticket.id,
            user_id=commenter.id,
            content=content,
            created_at=comment_time,
        )
        db.add(comment)


async def simulate_tickets(num_tickets: int = 50, delete_existing: bool = True):
    """Main simulation function"""
    print(f"🚀 Starting ticket simulation...\n")
    print(f"📊 Configuration:")
    print(f"   - Number of tickets: {num_tickets}")
    print(f"   - Delete existing: {delete_existing}")
    print(f"   - Time range: Past 60 days\n")
    
    async with AsyncSessionLocal() as db:
        users = await get_users(db)
        
        if not users:
            print("❌ No users found in database. Please create users first.")
            return
        
        print(f"👥 Found {len(users)} users in database\n")
        
        if delete_existing:
            await delete_all_tickets(db)
        
        print(f"📝 Creating {num_tickets} tickets with realistic data...\n")
        
        now = datetime.now()
        start_date = now - timedelta(days=60)
        
        it_users = [u for u in users if u.department in ["Information Technology", "เทคโนโลยีสารสนเทศ (IT)"]]
        regular_users = [u for u in users if u not in it_users]
        
        if not regular_users:
            regular_users = users
        
        created_tickets = []
        
        for i in range(num_tickets):
            random_time = start_date + timedelta(
                days=random.randint(0, 60),
                hours=random.randint(8, 17),
                minutes=random.randint(0, 59)
            )
            
            template = random.choice(TICKET_TEMPLATES)
            category = random.choice(CATEGORIES)
            priority = random.choice(PRIORITIES)
            location = random.choice(LOCATIONS)
            requester = random.choice(regular_users)
            
            status_weights = [0.15, 0.25, 0.10, 0.30, 0.20]
            status = random.choices(STATUSES, weights=status_weights)[0]
            
            assignee = None
            if status != "Open" and it_users:
                assignee = random.choice(it_users)
            
            ticket_no = f"T-{1000 + i}"
            
            ticket = await create_ticket_with_history(
                db=db,
                ticket_no=ticket_no,
                template=template,
                category=category,
                priority=priority,
                location=location,
                requester=requester,
                created_at=random_time,
                assignee=assignee,
                status=status,
            )
            
            num_comments = 0
            if status in ["In Progress", "Pending"]:
                num_comments = random.randint(1, 5)
            elif status in ["Resolved", "Closed"]:
                num_comments = random.randint(2, 8)
            
            await add_comments_to_ticket(db, ticket, users, num_comments)
            
            created_tickets.append(ticket)
            
            status_emoji = {
                "Open": "🆕",
                "In Progress": "🔄",
                "Pending": "⏸️",
                "Resolved": "✅",
                "Closed": "🔒"
            }
            
            print(f"{status_emoji.get(status, '📋')} Created: {ticket_no} - {template['title'][:50]}... [{status}] ({random_time.strftime('%Y-%m-%d')})")
            
            if (i + 1) % 10 == 0:
                await db.commit()
                print(f"\n💾 Saved batch {(i + 1) // 10}\n")
        
        await db.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ Successfully created {len(created_tickets)} tickets!")
        print(f"{'='*80}\n")
        
        status_counts = {}
        priority_counts = {}
        
        for ticket in created_tickets:
            status_counts[ticket.status] = status_counts.get(ticket.status, 0) + 1
            priority_counts[ticket.priority] = priority_counts.get(ticket.priority, 0) + 1
        
        print("📊 Summary by Status:")
        for status, count in sorted(status_counts.items()):
            percentage = (count / len(created_tickets)) * 100
            print(f"   {status:15} : {count:3} ({percentage:5.1f}%)")
        
        print("\n📊 Summary by Priority:")
        for priority, count in sorted(priority_counts.items()):
            percentage = (count / len(created_tickets)) * 100
            print(f"   {priority:15} : {count:3} ({percentage:5.1f}%)")
        
        print(f"\n🎉 Simulation completed successfully!")


if __name__ == "__main__":
    import sys
    
    num_tickets = 50
    delete_existing = True
    
    if len(sys.argv) > 1:
        try:
            num_tickets = int(sys.argv[1])
        except ValueError:
            print("Usage: python simulate_tickets.py [num_tickets] [--keep-existing]")
            sys.exit(1)
    
    if "--keep-existing" in sys.argv:
        delete_existing = False
    
    asyncio.run(simulate_tickets(num_tickets, delete_existing))
