from .decision_tree import Guessify
import os
from django.conf import settings

# Global instance of the guesser
_guesser_instance = None

def get_guesser():
    """Get or create the celebrity guesser instance"""
    global _guesser_instance
    
    if _guesser_instance is None:
        _guesser_instance = Guessify()
        data_path = os.path.join(settings.BASE_DIR, 'guesser', 'data', 'guessify_simple.csv')
        _guesser_instance.load_data(data_path)  # Loads from CSV
        _guesser_instance.train_model()          # Retrains the model
        
        print("Celebrity Guesser model loaded and trained!")
    
    return _guesser_instance