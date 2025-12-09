from decision_tree import  Guessify
import os

# Initialize the guesser
guesser = Guessify()

# Load data - CHANGE THE FILENAME HERE
data_path = os.path.join('guesser/data', 'guessify_simple.csv')
guesser.load_data(data_path)

# Train model
guesser.train_model()

# Show most important features
print("\nTop 10 Most Important Features:")
print(guesser.get_feature_importance().head(10))

# Test prediction
test_answers = {
    'actor': 'yes',
    'male': 'yes',
    'still_alive': 'yes',
    'has_oscar': 'yes'
}

result = guesser.predict(test_answers)
print(f"\nPrediction: {result['name']}")
print(f"Confidence: {result['confidence']:.2%}")