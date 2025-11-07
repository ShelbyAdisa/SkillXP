from django.core.management.base import BaseCommand
from users.models import School

class Command(BaseCommand):
    help = 'Create test schools for development'

    def handle(self, *args, **options):
        # Create test school
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
            self.stdout.write(self.style.SUCCESS('✅ School created successfully!'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️ School already exists!'))

        self.stdout.write(f'\nSchool Name: {school.name}')
        self.stdout.write(f'School Code: {school.code}')
        self.stdout.write(self.style.SUCCESS('\n✨ Use code "TEST001" to register!\n'))

        # Create additional sample schools
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

        self.stdout.write('\n🏫 Creating additional sample schools...')
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
            status = '✅ Created' if created else 'ℹ️ Already exists'
            self.stdout.write(f'{status}: {school.name} (Code: {school.code})')

        # List all schools
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎉 Setup complete! Available school codes:'))
        self.stdout.write('='*60)
        for s in School.objects.all():
            self.stdout.write(f'  • {s.code} - {s.name}')
        self.stdout.write('='*60 + '\n')

