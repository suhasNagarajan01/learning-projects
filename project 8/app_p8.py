import json
import re

# --- 1. Load Test Set ---
test_set = [
    ("Enjoying a beautiful day at the park!", "positive"),
    ("Traffic was terrible this morning.", "negative"),
    ("Attending a virtual conference on AI.", "neutral"),
    ("Fuming with anger after a heated argument.", "anger"),
    ("The unknown is keeping me up at night.", "fear"),
    ("Heartbroken after hearing the news about a natural disaster.", "sadness"),
    ("The state of the world's environment is just disgusting.", "disgust"),
    ("Pure happiness: celebrating a loved one's achievement!", "happiness"),
    ("Laughter is the best medicine—enjoying a comedy show.", "joy"),
    ("Sending love to all my followers on this beautiful day!", "love"),
    ("An amusing incident brightened up my day!", "amusement"),
    ("Enjoying a quiet evening with a book and some tea.", "enjoyment"),
    ("Admiring the beauty of nature during a peaceful hike.", "admiration"),
    ("Sending affectionate vibes to all my followers!", "affection"),
    ("Experiencing awe at the breathtaking sunset.", "awe"),
    ("Disappointed with the service at a local restaurant.", "disappointed"),
    ("A surprise gift from a friend made my day!", "surprise"),
    ("Finding acceptance in the midst of life's challenges.", "acceptance"),
    ("Overflowing with adoration for my adorable pet!", "adoration"),
    ("Anticipating a thrilling adventure in the coming weeks.", "anticipation"),
    ("A bitter experience turned into a valuable lesson.", "bitter"),
    ("Finding calmness in the midst of a busy day.", "calmness"),
    ("Confusion clouds my mind as I navigate through decisions.", "confusion"),
    ("Excitement building up for the upcoming vacation!", "excitement"),
    ("Kindness witnessed today restored my faith in humanity.", "kind"),
    ("Pride in achieving a personal milestone.", "pride"),
    ("A moment of shame for not standing up against injustice.", "shame"),
    ("Elation after a surprise reunion with friends.", "elation"),
    ("The victory of our team brought euphoria to the city.", "euphoria"),
    ("Contentment in the simplicity of a quiet Sunday.", "contentment"),
    ("Meditating by the serene lake, finding inner peace.", "serenity"),
    ("Overflowing with gratitude for life's blessings.", "gratitude"),
    ("Hopeful for a brighter tomorrow, despite challenges.", "hope"),
    ("Empowered to make a difference in my community.", "empowerment"),
    ("Compassion in action: supporting a local charity event.", "compassion"),
    ("A moment of tenderness, connecting with loved ones.", "tenderness"),
    ("Arousal of excitement as I await a special announcement.", "arousal"),
    ("Enthusiastically diving into a new project.", "enthusiasm"),
    ("Feeling a sense of fulfillment after reaching a milestone.", "fulfillment"),
    ("Reverence for the beauty of a historic landmark.", "reverence"),
    ("Suffering from despair after another setback.", "despair"),
    ("Overwhelmed by grief, missing a loved one dearly.", "grief"),
    ("Loneliness creeps in as the night grows colder.", "loneliness"),
    ("Jealousy consumes me as I witness others' success.", "jealousy"),
    ("Resentment building up over past betrayals.", "resentment"),
    ("Frustration mounts as obstacles block my path.", "frustration"),
    ("Boredom sets in, the day feels endlessly dull.", "boredom"),
    ("Anxiety grips my heart, worry clouds my thoughts.", "anxiety"),
    ("Intimidation by the unknown future ahead.", "intimidation"),
    ("Helplessness sinks in as challenges pile up.", "helplessness"),
    ("Envy eats away at me as I see others' prosperity.", "envy"),
    ("Regret over missed opportunities haunts my thoughts.", "regret"),
    ("Embarking on a journey of discovery, fueled by curiosity.", "curiosity"),
    ("Floating through the day with an air of indifference.", "indifference"),
    ("A numbness settles over me, a shield against overwhelming emotions.", "numbness"),
    ("Gazing at the sunset, a melancholic longing for moments that slip away.", "melancholy"),
    ("Caught in the embrace of nostalgia's bittersweet symphony.", "nostalgia"),
    ("Torn between two conflicting choices, feeling complete ambivalence.", "ambivalence"),
    ("Unwavering determination to conquer every challenge in my path.", "determination"),
    ("Approaching every new task with unbridled zest and passion.", "zest"),
    ("Deeply empathetic toward everyone going through hard times.", "empathetic")
]

# --- 2. Load JSON dataset (Learned Knowledge Base) ---
try:
    with open("new-dataset/dataset.json", "r", encoding="utf-8") as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: Could not find 'new-dataset/dataset.json'. Check your file path.")
    exit()

sentiments = list(data.keys())

# --- 3. Diagnostic Check ---
test_labels = set(label for _, label in test_set)
json_labels = set(sentiments)
missing_labels = test_labels - json_labels

if missing_labels:
    print("--- DIAGNOSTICS ---")
    print(f"Still missing {len(missing_labels)} labels from dataset.json: {missing_labels}")
    print(f"Available keys in your JSON: {sorted(sentiments)}\n")

# --- 4. Classifier Function ---
def classify(user_text):
    words = re.findall(r'\b\w+\b', user_text.lower())
    sentiment_scores = {sentiment: 0.0 for sentiment in sentiments}
    
    for word in words:
        for sentiment, word_dict in data.items():
            if isinstance(word_dict, dict) and word in word_dict:
                # Normalize by sum of counts in category to compute relative weight
                category_total = sum(word_dict.values()) or 1
                sentiment_scores[sentiment] += (word_dict[word] / category_total)

    max_score = max(sentiment_scores.values(), default=0)
    
    if max_score == 0:
        return None

    return max(sentiment_scores, key=sentiment_scores.get)


# --- 5. Measure Accuracy & Evaluate ---
correct = 0
unmatched_sentences = 0

for text, true_label in test_set:
    guess = classify(text)
    if guess == true_label:
        correct += 1
    elif guess is None:
        unmatched_sentences += 1
    else:
        print(text , [true_label], guess)

total_tests = len(test_set)
accuracy = (correct / total_tests) * 100 if total_tests > 0 else 0

print("--- RESULTS ---")
print(f"Testing on {total_tests} unseen examples...")
print(f"Correct predictions: {correct}/{total_tests}")
print(f"Sentences with no vocabulary matches: {unmatched_sentences}/{total_tests}")
print(f"Accuracy: {accuracy:.1f}%")