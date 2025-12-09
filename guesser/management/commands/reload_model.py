from django.core.management.base import BaseCommand
from guesser.utils import get_guesser

class Command(BaseCommand):
    help = 'Reload the celebrity guesser model'

    def handle(self, *args, **options):
        global _guesser_instance
        from guesser import utils
        
        # Force reload
        utils._guesser_instance = None
        guesser = get_guesser()
        
        self.stdout.write(self.style.SUCCESS('✅ Model reloaded successfully!'))