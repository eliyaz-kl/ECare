import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecare.settings')
django.setup()

from django.contrib.auth.models import User, Group
from apps.customers.models import Customer
from apps.engagements.models import Engagement
from datetime import datetime, timedelta

# Create Users
print("Creating users...")
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@ecare.com',
        'is_staff': True,
        'is_superuser': True,
        'first_name': 'Admin',
        'last_name': 'User'
    }
)
admin_user.set_password('admin123')
admin_user.save()

agent1, _ = User.objects.get_or_create(
    username='agent1',
    defaults={
        'email': 'agent1@ecare.com',
        'is_staff': True,
        'first_name': 'John',
        'last_name': 'Smith'
    }
)
agent1.set_password('agent123')
agent1.save()

agent2, _ = User.objects.get_or_create(
    username='agent2',
    defaults={
        'email': 'agent2@ecare.com',
        'is_staff': True,
        'first_name': 'Sarah',
        'last_name': 'Johnson'
    }
)
agent2.set_password('agent123')
agent2.save()

supervisor, _ = User.objects.get_or_create(
    username='supervisor',
    defaults={
        'email': 'supervisor@ecare.com',
        'is_staff': True,
        'first_name': 'Mike',
        'last_name': 'Wilson'
    }
)
supervisor.set_password('super123')
supervisor.save()

print(f"Created users: {admin_user}, {agent1}, {agent2}, {supervisor}")

# Create Groups
print("Creating groups...")
agents_group, _ = Group.objects.get_or_create(name='Agents')
supervisors_group, _ = Group.objects.get_or_create(name='Supervisors')

agent1.groups.add(agents_group)
agent2.groups.add(agents_group)
supervisor.groups.add(supervisors_group)

# Create Customers
print("Creating customers...")
customers_data = [
    {
        'platform': 'X',
        'external_user_id': 'x_user_001',
        'username': '@john_tech',
        'display_name': 'John Tech Enthusiast',
        'profile_image': 'https://example.com/avatar1.jpg',
        'followers_count': 5420
    },
    {
        'platform': 'X',
        'external_user_id': 'x_user_002',
        'username': '@sarah_mobile',
        'display_name': 'Sarah Mobile User',
        'profile_image': 'https://example.com/avatar2.jpg',
        'followers_count': 2100
    },
    {
        'platform': 'FB',
        'external_user_id': 'fb_user_001',
        'username': 'mike.customer',
        'display_name': 'Mike Customer',
        'profile_image': 'https://example.com/avatar3.jpg',
        'followers_count': 890
    },
    {
        'platform': 'X',
        'external_user_id': 'x_user_003',
        'username': '@emma_support',
        'display_name': 'Emma Wilson',
        'profile_image': 'https://example.com/avatar4.jpg',
        'followers_count': 15200
    },
    {
        'platform': 'FB',
        'external_user_id': 'fb_user_002',
        'username': 'david.jones',
        'display_name': 'David Jones',
        'profile_image': 'https://example.com/avatar5.jpg',
        'followers_count': 450
    },
]

customers = []
for data in customers_data:
    customer, _ = Customer.objects.get_or_create(
        external_user_id=data['external_user_id'],
        defaults=data
    )
    customers.append(customer)

print(f"Created {len(customers)} customers")

# Create Engagements
print("Creating engagements...")
engagements_data = [
    {
        'customer': customers[0],
        'engagement_type': 'DM',
        'external_id': 'eng_001',
        'content': 'I was charged twice for my last purchase. Can you help me get a refund?',
        'ai_response': 'I understand your concern about being charged twice. Let me look into this for you right away.',
        'priority': 'High',
        'category': 'Overcharge',
        'status': 'ASSIGNED',
        'assigned_agent': agent1,
        'is_auto_replied': True
    },
    {
        'customer': customers[1],
        'engagement_type': 'POST_REPLY',
        'external_id': 'eng_002',
        'content': 'Your app keeps crashing on my Android device. This is very frustrating!',
        'ai_response': 'We apologize for the inconvenience. Could you provide us with your device model and OS version?',
        'priority': 'High',
        'category': 'Technical Issue',
        'status': 'ASSIGNED',
        'assigned_agent': agent2,
        'is_auto_replied': True
    },
    {
        'customer': customers[2],
        'engagement_type': 'MENTION',
        'external_id': 'eng_003',
        'content': '@yourcompany great service! Just had an amazing experience with your support team!',
        'priority': 'Low',
        'category': 'General Inquiry',
        'status': 'CLOSED',
        'final_response': 'Thank you so much for your kind words! We really appreciate your feedback.',
        'is_auto_replied': False
    },
    {
        'customer': customers[3],
        'engagement_type': 'DM',
        'external_id': 'eng_004',
        'content': 'How do I update my billing information? I got a new credit card.',
        'ai_response': 'You can update your billing information by going to Settings > Billing > Payment Methods.',
        'priority': 'Medium',
        'category': 'Billing',
        'status': 'AI_REVIEW',
        'is_auto_replied': True
    },
    {
        'customer': customers[0],
        'engagement_type': 'POST_REPLY',
        'external_id': 'eng_005',
        'content': 'Still waiting for my refund. It has been 3 days!',
        'priority': 'High',
        'category': 'Refund',
        'status': 'ASSIGNED',
        'assigned_agent': agent1
    },
    {
        'customer': customers[4],
        'engagement_type': 'DM',
        'external_id': 'eng_006',
        'content': 'I cannot access my account. It says my password is incorrect but I am sure it is right.',
        'ai_response': 'I can help you reset your password. Would you like me to send a password reset link to your email?',
        'priority': 'High',
        'category': 'Account Support',
        'status': 'ASSIGNED',
        'assigned_agent': agent2,
        'is_auto_replied': True
    },
    {
        'customer': customers[1],
        'engagement_type': 'MENTION',
        'external_id': 'eng_007',
        'content': '@yourcompany when will you add dark mode? Been waiting forever!',
        'priority': 'Low',
        'category': 'General Inquiry',
        'status': 'NEW'
    },
    {
        'customer': customers[3],
        'engagement_type': 'DM',
        'external_id': 'eng_008',
        'content': 'What are your business hours?',
        'ai_response': 'Our customer support is available 24/7. You can reach us anytime!',
        'priority': 'Low',
        'category': 'General Inquiry',
        'status': 'CLOSED',
        'final_response': 'Our customer support is available 24/7. You can reach us anytime!',
        'is_auto_replied': True
    },
    {
        'customer': customers[2],
        'engagement_type': 'POST_REPLY',
        'external_id': 'eng_009',
        'content': 'The new update broke the search feature. Please fix this ASAP!',
        'priority': 'High',
        'category': 'Technical Issue',
        'status': 'ASSIGNED',
        'assigned_agent': agent1
    },
    {
        'customer': customers[4],
        'engagement_type': 'DM',
        'external_id': 'eng_010',
        'content': 'I want to cancel my subscription. How do I do that?',
        'ai_response': 'I can help you with that. May I ask why you would like to cancel?',
        'priority': 'Medium',
        'category': 'Account Support',
        'status': 'AI_REVIEW',
        'is_auto_replied': True
    },
]

for data in engagements_data:
    engagement, created = Engagement.objects.get_or_create(
        external_id=data['external_id'],
        defaults=data
    )
    if created:
        print(f"Created engagement: {engagement.request_number}")

print(f"\nSample data creation completed!")
print(f"\nLogin credentials:")
print(f"Admin: username=admin, password=admin123")
print(f"Agent 1: username=agent1, password=agent123")
print(f"Agent 2: username=agent2, password=agent123")
print(f"Supervisor: username=supervisor, password=super123")
