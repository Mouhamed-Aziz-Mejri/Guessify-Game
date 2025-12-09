import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
# from sklearn.model_selection import train_test_split 
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

class Guessify:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.celebrities = None
        self.data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.accuracy = None
        
    def load_data(self, filepath):
        """Load the celebrity dataset"""
        # Read the file - use comma separator
        self.data = pd.read_csv(filepath, sep=',')
        self.data = self.data.drop_duplicates()
        
        # Remove any rows with missing values (like Lady Gaga's incomplete row)
        self.data = self.data.dropna()
        
        self.celebrities = self.data['name'].values
        
        # Get feature columns (all except 'name')
        self.feature_names = [col for col in self.data.columns if col != 'name']
        
        # Convert 'yes'/'no' to 1/0 for all feature columns
        for col in self.feature_names:
            self.data[col] = self.data[col].map({'yes': 1, 'no': 0})
        
        # Print info for debugging
        print(f"Loaded {len(self.data)} celebrities")
        print(f"Features: {len(self.feature_names)}")
        
        return self.data
    
    def train_model(self):
        """Train the decision tree classifier on full dataset (no split for small data)"""
        # Features (X) and target (y)
        X = self.data[self.feature_names]
        y = self.data['name']
        
        print(f"\n{'='*80}")
        print(f"Training on FULL dataset: {len(X)} celebrities")
        print(f"{'='*80}")
        
        # Create and train the decision tree on ALL data
        
        self.model = DecisionTreeClassifier(
            criterion='gini',           # Use gini impurity
            max_depth=None,             # No limit - learn everything
            min_samples_split=2,        # Minimum to split a node
            min_samples_leaf=1,         # Allow leaves with 1 sample
            max_features=None,          # Consider all features
            random_state=42,
            splitter='best'             # Use best split
        )
        
        # Train on ALL data (no split needed for small dataset)
        self.model.fit(X, y)
        
        # Check training accuracy (should be 100%)
        train_predictions = self.model.predict(X)
        train_accuracy = accuracy_score(y, train_predictions)
        
        print(f"\n✅ Model Training Accuracy: {train_accuracy * 100:.2f}%")
        
        if train_accuracy < 1.0:
            print("⚠️  Warning: Model couldn't learn all celebrities perfectly!")
            print(f"   Current accuracy: {train_accuracy * 100:.2f}%")
            
            # Find which celebrities are being confused
            misclassified = []
            for i, (true, pred) in enumerate(zip(y, train_predictions)):
                if true != pred:
                    misclassified.append((true, pred))
            
            if misclassified:
                print(f"\n   Misclassified celebrities ({len(misclassified)}):")
                for true_name, pred_name in misclassified:
                    print(f"   - {true_name} → predicted as {pred_name}")
            
            print("\n   💡 This might happen if two celebrities have identical features.")
            print("   Consider adding more distinctive features to differentiate them.")
        else:
            print("🎉 Perfect! Model learned all celebrities!")
        
        print(f"{'='*80}\n")
        
        return self.model
    
    def get_feature_importance(self):
        """Get the most important features for asking questions"""
        if self.model is None:
            return None
        
        importances = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return feature_importance
    
    def predict(self, answers):
        """
        Predict celebrity based on answers
        answers: dict with feature names as keys and yes/no as values
        """
        if self.model is None:
            return None
        
        # Create a feature vector from answers
        feature_vector = []
        for feature in self.feature_names:
            if feature in answers:
                feature_vector.append(1 if answers[feature] == 'yes' else 0)
            else:
                feature_vector.append(0)  # Default to 'no' if not answered
        
        # Reshape for prediction
        feature_vector = np.array(feature_vector).reshape(1, -1)
        
        # Get prediction
        prediction = self.model.predict(feature_vector)[0]
        
        # Get probability
        probabilities = self.model.predict_proba(feature_vector)[0]
        max_prob = max(probabilities)
        
        return {
            'name': prediction,
            'confidence': max_prob
        }
    
    def get_next_question(self, answered_features):
        """Get the next best feature to ask about with improved selection"""
        import random
        
        # Get unanswered features
        unanswered = [f for f in self.feature_names if f not in answered_features]
        
        if not unanswered:
            return None
        
        # Get feature importances
        importances = self.get_feature_importance()
        
        # Get top important unanswered features
        important_unanswered = []
        for _, row in importances.iterrows():
            if row['feature'] in unanswered and row['importance'] > 0.01:  # Filter low importance
                important_unanswered.append((row['feature'], row['importance']))
        
        # If we have important features, use weighted random selection
        if important_unanswered:
            # For first 5 questions, pick from top 5 most important
            if len(answered_features) < 5:
                candidates = [f for f, _ in important_unanswered[:5]]
            else:
                # For later questions, pick from top 15 to add variety
                candidates = [f for f, _ in important_unanswered[:min(15, len(important_unanswered))]]
            
            return random.choice(candidates)
        
        # Fallback: random selection from all unanswered
        return random.choice(unanswered)
    
    def predict_with_filtering(self, answers):
        """
        Predict celebrity based on answers with strict filtering
        """
        if self.model is None:
            return None
        
        # First, filter the dataset based on exact answers
        filtered_data = self.data.copy()
        
        for feature, answer in answers.items():
            if feature in self.feature_names:
                if answer == 'yes':
                    filtered_data = filtered_data[filtered_data[feature] == 1]
                elif answer == 'no':
                    filtered_data = filtered_data[filtered_data[feature] == 0]
                # 'unknown', 'probably', 'probably_not' don't filter strictly
        
        # If we have exact matches, return the best one
        if len(filtered_data) > 0:
            # If only one match, return it with high confidence
            if len(filtered_data) == 1:
                return {
                    'name': filtered_data.iloc[0]['name'],
                    'confidence': 1.0
                }
            
            # Multiple matches - use the model to pick the best one
            # Create feature vector
            feature_vector = []
            for feature in self.feature_names:
                if feature in answers:
                    feature_vector.append(1 if answers[feature] == 'yes' else 0)
                else:
                    feature_vector.append(0)
            
            feature_vector = np.array(feature_vector).reshape(1, -1)
            
            # Get probabilities for all celebrities
            probabilities = self.model.predict_proba(feature_vector)[0]
            classes = self.model.classes_
            
            # Find the best match among filtered celebrities
            best_match = None
            best_prob = 0
            
            for idx, celebrity in enumerate(classes):
                if celebrity in filtered_data['name'].values:
                    if probabilities[idx] > best_prob:
                        best_prob = probabilities[idx]
                        best_match = celebrity
            
            if best_match:
                return {
                    'name': best_match,
                    'confidence': best_prob
                }
        
        # Fallback: use regular prediction if no filtered matches
        return self.predict(answers)
    def format_feature_question(self, feature):
        """Convert feature name to a readable question"""
        # Replace underscores with spaces and capitalize
        readable = feature.replace('_', ' ').title()
        
        # Handle special cases for better questions
        question_map = {
            'Male': 'Is the person male?',
            'Still Alive': 'Is the person still alive?',
            'Born In America': 'Was the person born in America?',
            'Actor': 'Is the person an actor?',
            'Musician': 'Is the person a musician?',
            'Athlete': 'Is the person an athlete?',
            'Entrepreneur': 'Is the person an entrepreneur?',
            'Politician': 'Is the person a politician?',
            'Scientist': 'Is the person a scientist?',
            'Has Oscar': 'Does the person have an Oscar?',
            'Has Grammy': 'Does the person have a Grammy?',
            'Has Tattoos': 'Does the person have tattoos?',
            'Has Children': 'Does the person have children?',
            'Has Major Awards': 'Does the person have major awards?',
            'Blue Eyes': 'Does the person have blue eyes?',
            'Long Hair': 'Does the person have long hair?',
            'Wears Glasses': 'Does the person wear glasses?',
            'Tall': 'Is the person tall?',
            'Bald': 'Is the person bald?',
            'Left Handed': 'Is the person left-handed?',
            'Married': 'Is the person married?',
            'Social Media Active': 'Is the person active on social media?',
            'Considered A Legend': 'Is the person considered a legend?',
            'A Rising Star': 'Is the person a rising star?',
            'Famous': 'Is the person famous?',
            'A Billionaire': 'Is the person a billionaire?',
            'A Business Owner': 'Is the person a business owner?',
            'Multiple Championships': 'Does the person have multiple championships?',
            'Started Acting Child': 'Did the person start acting as a child?',
            'A Director': 'Is the person a director?',
            'A Producer': 'Is the person a producer?',
            'Theater Background': 'Does the person have a theater background?',
            'Primarily A Rapper': 'Is the person primarily a rapper?',
            'Primarily A Pop Musician': 'Is the person primarily a pop musician?',
            'A Multi Instrumentalist': 'Is the person a multi-instrumentalist?',
            'A Songwriter': 'Is the person a songwriter?',
            'Also A Dancer': 'Is the person also a dancer?',
            'Owns Company': 'Does the person own a company?',
            'A Mentor Figure': 'Is the person a mentor figure?',
            'Funny': 'Is the person funny?',
            'Controversial': 'Is the person controversial?',
            'Fashion Icon': 'Is the person a fashion icon?',
            'Educated': 'Is the person educated?',
            'Perfectionist': 'Is the person a perfectionist?',
            'Quirky': 'Is the person quirky?',
            'Vegan': 'Is the person vegan?',
            'An Activist': 'Is the person an activist?',
            'Humanitarian Work': 'Does the person do humanitarian work?',
            'An Environmental Activist': 'Is the person an environmental activist?',
            'A Political Activist': 'Is the person a political activist?',
            'Loves Dogs': 'Does the person love dogs?',
            'A Gamer': 'Is the person a gamer?',
            'Plays Poker': 'Does the person play poker?',
            'A Motorcycle Enthusiast': 'Is the person a motorcycle enthusiast?',
            'Comeback Story': 'Does the person have a comeback story?',
            'Troubled Past': 'Does the person have a troubled past?',
            'Multilingual': 'Is the person multilingual?',
            'Speaks French': 'Does the person speak French?',
            'Speaks Spanish': 'Does the person speak Spanish?',
            'British Irish': 'Is the person British or Irish?',
            'Canadian': 'Is the person Canadian?',
            'Australian': 'Is the person Australian?',
        }
        
        if readable in question_map:
            return question_map[readable]
        else:
            return f'Is the person {readable.lower()}?'