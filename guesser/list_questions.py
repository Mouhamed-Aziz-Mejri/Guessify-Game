import pandas as pd
import os
from django.conf import settings

# Add this to see all questions
def list_all_questions():
    # Load the data
    data_path = os.path.join('data', 'guessify_simple.csv')
    data = pd.read_csv(data_path, sep=',')
    
    # Get all feature columns (exclude 'name')
    features = [col for col in data.columns if col != 'name']
    
    print(f"\n{'='*80}")
    print(f"TOTAL FEATURES: {len(features)}")
    print(f"{'='*80}\n")
    
    # Question mapping for better readability
    question_map = {
        'male': 'Is the person male?',
        'still_alive': 'Is the person still alive?',
        'born_in_america': 'Was the person born in America?',
        'actor': 'Is the person an actor?',
        'musician': 'Is the person a musician?',
        'athlete': 'Is the person an athlete?',
        'entrepreneur': 'Is the person an entrepreneur?',
        'politician': 'Is the person a politician?',
        'scientist': 'Is the person a scientist?',
        'has_tattoos': 'Does the person have tattoos?',
        'tall': 'Is the person tall?',
        'left_handed': 'Is the person left-handed?',
        'blue_eyes': 'Does the person have blue eyes?',
        'bald': 'Is the person bald?',
        'long_hair': 'Does the person have long hair?',
        'wears_glasses': 'Does the person wear glasses?',
        'married': 'Is the person married?',
        'has_children': 'Does the person have children?',
        'social_media_active': 'Is the person social media active?',
        'considered_a_legend': 'Is the person considered a legend?',
        'a_rising_star': 'Is the person a rising star?',
        'famous': 'Is the person famous?',
        'has_major_awards': 'Does the person have major awards?',
        'a_billionaire': 'Is the person a billionaire?',
        'a_business_owner': 'Is the person a business owner?',
        'has_oscar': 'Does the person have an Oscar?',
        'has_grammy': 'Does the person have a Grammy?',
        'multiple_championships': 'Does the person have multiple championships?',
        'started_acting_child': 'Did the person start acting as a child?',
        'a_director': 'Is the person a director?',
        'a_producer': 'Is the person a producer?',
        'theater_background': 'Does the person have a theater background?',
        'primarily_a_rapper': 'Is the person primarily a rapper?',
        'primarily_a_pop_musician': 'Is the person primarily a pop musician?',
        'a_multi_instrumentalist': 'Is the person a multi-instrumentalist?',
        'a_songwriter': 'Is the person a songwriter?',
        'also_a_dancer': 'Is the person also a dancer?',
        'owns_company': 'Does the person own a company?',
        'a_mentor_figure': 'Is the person a mentor figure?',
        'funny': 'Is the person funny?',
        'controversial': 'Is the person controversial?',
        'fashion_icon': 'Is the person a fashion icon?',
        'educated': 'Is the person educated?',
        'perfectionist': 'Is the person a perfectionist?',
        'quirky': 'Is the person quirky?',
        'vegan': 'Is the person vegan?',
        'an_activist': 'Is the person an activist?',
        'humanitarian_work': 'Does the person do humanitarian work?',
        'an_environmental_activist': 'Is the person an environmental activist?',
        'a_political_activist': 'Is the person a political activist?',
        'loves_dogs': 'Does the person love dogs?',
        'a_gamer': 'Is the person a gamer?',
        'plays_poker': 'Does the person play poker?',
        'a_motorcycle_enthusiast': 'Is the person a motorcycle enthusiast?',
        'comeback_story': 'Does the person have a comeback story?',
        'troubled_past': 'Does the person have a troubled past?',
        'multilingual': 'Is the person multilingual?',
        'speaks_french': 'Does the person speak French?',
        'speaks_spanish': 'Does the person speak Spanish?',
        'American': 'Is the person American?',
'Canadian': 'Is the person Canadian?',
'British': 'Is the person British?',
'Portuguese': 'Is the person Portuguese?',
'Argentine': 'Is the person Argentine?',
'Brazilian': 'Is the person Brazilian?',
'Barbadian': 'Is the person Barbadian?',
'Swiss': 'Is the person Swiss?',
'Serbian': 'Is the person Serbian?',
'Spanish': 'Is the person Spanish?',
    }
    
    for i, feature in enumerate(features, 1):
        question = question_map.get(feature, f'Is the person {feature.replace("_", " ")}?')
        print(f"{i:2d}. {question}")
        print(f"    Feature: {feature}\n")

if __name__ == '__main__':
    list_all_questions()