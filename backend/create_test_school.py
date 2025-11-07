import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkillNexus.settings')
django.setup()

from users.models import School

# Create a test school
school, created = School.objects.get_or_create(
    code='TEST001',
    defaults={
        'name': 'Test High School',
        'address': '123 Education Street',
        'phone': '+1234567890',
        'email': 'admin@testschool.edu',
        'website': 'https://testschool.edu',
        'is_anonymous_allowed': True,
        'max_students': 1000,
        'theme_color': '#3B82F6'
    }
)

if created:
    print('✅ School created successfully!')
    print(f'   School Name: {school.name}')
    print(f'   School Code: {school.code}')
    print(f'\n📝 Use this code to register: {school.code}')
else:
    print('ℹ️  School already exists!')
    print(f'   School Name: {school.name}')
    print(f'   School Code: {school.code}')
    print(f'\n📝 Use this code to register: {school.code}')

# Create a few more sample schools
sample_schools = [
    {
        'code': 'LHS001',
        'name': 'Lincoln High School',
        'address': '456 Lincoln Ave',
        'phone': '+1234567891',
        'email': 'admin@lincolnhs.edu'
    },
    {
        'code': 'WMS001',
        'name': 'Washington Middle School',
        'address': '789 Washington St',
        'phone': '+1234567892',
        'email': 'admin@washingtonms.edu'
    }
]

print('\n🏫 Creating additional sample schools...')
for school_data in sample_schools:
    school, created = School.objects.get_or_create(
        code=school_data['code'],
        defaults={
            **school_data,
            'website': f'https://{school_data["code"].lower()}.edu',
            'is_anonymous_allowed': True,
            'max_students': 1000,
            'theme_color': '#3B82F6'
        }
    )
    status = '✅ Created' if created else 'ℹ️  Already exists'
    print(f'{status}: {school.name} (Code: {school.code})')

print('\n' + '='*60)
print('🎉 Setup complete! You can now register with these codes:')
print('='*60)
for s in School.objects.all():
    print(f'  • {s.code} - {s.name}')
print('='*60)

