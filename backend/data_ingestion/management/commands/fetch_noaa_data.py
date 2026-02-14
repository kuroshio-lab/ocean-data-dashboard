"""
Management command to fetch ocean data from NOAA ERDDAP.
"""
from django.core.management.base import BaseCommand
from data_ingestion.services.noaa_service import NOAAERDDAPService


class Command(BaseCommand):
    help = 'Fetch ocean data from NOAA ERDDAP'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days of historical data to fetch (default: 1)'
        )
        parser.add_argument(
            '--dataset',
            type=str,
            default='cwwcNDBCMet',
            help='ERDDAP dataset ID (default: cwwcNDBCMet)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dataset = options['dataset']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting NOAA data fetch for last {days} day(s)...')
        )
        
        try:
            service = NOAAERDDAPService()
            result = service.fetch_buoy_data(dataset_id=dataset, days_back=days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Fetch completed: {result['records_inserted']} records inserted"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error: {str(e)}')
            )
            raise
