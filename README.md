# 🌸 TaskNest — Task Manager System

A full-featured Django task management web application with personal task tracking, group collaboration, calendar view, notifications, and discussion threads — styled in a soft pink pastel theme.

---

## ✨ Features

### 👤 User Authentication
- Register, Login, Logout
- User profiles with initials avatar

### ✅ Personal Task Management
- Create / Edit / Delete tasks
- Mark tasks as Completed (toggle)
- Priority: Low / Medium / High
- Category: School / Work / Personal / Urgent
- Status: Pending / Ongoing / Completed
- Filter tasks by category, priority, status

### 👥 Group Collaboration
- Create groups with auto-generated invite codes
- Join groups via invite code
- Group admin role assigned to creator
- View all group members

### 📋 Group Task Management
- Create tasks inside groups
- Assign tasks to specific members
- Quick status updates inline
- "Assigned to Me" view across all groups

### 🔔 Notifications
- Automatic alerts when tasks are due tomorrow
- Alerts when tasks are overdue
- Notification badge in sidebar/topbar
- Mark all as read

### 📅 Calendar
- Monthly calendar view
- Personal and group tasks shown on due dates
- Click any date to see tasks in a modal
- Previous/next month navigation

### 💬 Group Discussions
- Post messages in each group's discussion feed
- Reply/comment on messages
- Admin can pin important messages (appear at top)
- Delete own messages (admin can delete any)

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.10 or higher
- pip

### One-command setup
```bash
cd tasknest
bash setup.sh
```

### Manual setup
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations accounts tasks groups_app
python manage.py migrate

# 4. Create admin user (optional)
python manage.py createsuperuser

# 5. Start server
python manage.py runserver
```

Then open **http://127.0.0.1:8000** in your browser.

---

## 📁 Project Structure

```
tasknest/
├── manage.py
├── requirements.txt
├── setup.sh
├── tasknest/           ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/           ← User auth app
│   ├── models.py       (Profile)
│   ├── views.py        (register, login, logout, profile)
│   ├── forms.py
│   └── urls.py
├── tasks/              ← Personal tasks app
│   ├── models.py       (Task, Notification)
│   ├── views.py        (dashboard, task CRUD, calendar, notifications)
│   ├── forms.py
│   ├── context_processors.py
│   ├── templatetags/
│   │   └── task_filters.py
│   └── urls.py
├── groups_app/         ← Group collaboration app
│   ├── models.py       (Group, GroupMembership, GroupTask, Discussion, Message)
│   ├── views.py        (group CRUD, group tasks, discussion, assigned tasks)
│   ├── forms.py
│   └── urls.py
├── templates/          ← All HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── tasks/
│   └── groups_app/
└── static/
    ├── css/main.css    ← Full pink pastel design system
    └── js/main.js
```

---

## 🔐 Security Rules
- Users can only see their own personal tasks
- Users can only view groups they are members of
- Group tasks are only visible to group members
- Only group admins can pin discussion messages
- Notifications are private per user

---

## 🎨 Design
- **Theme:** Soft pink pastel
- **Fonts:** Playfair Display (headings) + DM Sans (body)
- **Icons:** Font Awesome 6
- **Responsive:** Mobile-friendly sidebar with toggle
