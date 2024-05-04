from flask import Flask, request, jsonify
from surprise import Dataset, Reader, SVD
from dataset import X_train, X_test, y_train, y_test, data
from redis import Redis
from celery import Celery

app = Flask(__name__)
redis_client = Redis(host='localhost', port=6379)
celery_app = Celery('tasks', broker='redis://localhost:6379')

# Load the preprocessed data and train the model
reader = Reader(rating_scale=(0, data['TotalPrice'].max()))
dataset = Dataset.load_from_df(data[['CustomerID', 'StockCode', 'TotalPrice']], reader)
trainset = dataset.build_full_trainset()
algo = SVD()
algo.fit(trainset)

@celery_app.task
def generate_recommendations(user_id):
    # Get the list of all item IDs
    item_ids = list(data['StockCode'].unique())

    # Generate recommendations for the user
    recommendations = []
    for item_id in item_ids:
        prediction = algo.predict(user_id, item_id)
        recommendations.append((item_id, prediction.est))

    # Sort the recommendations by predicted rating in descending order
    recommendations.sort(key=lambda x: x[1], reverse=True)

    # Get the top 10 recommendations
    top_recommendations = recommendations[:10]

    return top_recommendations

@app.route('/recommend', methods=['POST'])
def recommend():
    # Get the user ID from the request
    user_id = request.json['user_id']

    # Check if the recommendations are already cached
    cached_recommendations = redis_client.get(user_id)

    if cached_recommendations:
        # If cached, return the cached recommendations
        recommendations = eval(cached_recommendations)
    else:
        # If not cached, generate recommendations asynchronously
        recommendations = generate_recommendations.delay(user_id).get()

        # Cache the recommendations for future requests
        redis_client.set(user_id, str(recommendations))

    # Prepare the response
    response = {
        'user_id': user_id,
        'recommendations': [{'item_id': item_id, 'predicted_rating': rating}
                            for item_id, rating in recommendations]
    }

    return jsonify(response)

@app.route('/feedback', methods=['POST'])
def feedback():
    # Get the feedback data from the request
    user_id = request.json['user_id']
    item_id = request.json['item_id']
    rating = request.json['rating']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Append the feedback data to the CSV file
    with open('feedback.csv', 'a') as file:
        file.write(f"{user_id},{item_id},{rating},{timestamp}\n")

    return jsonify({'message': 'Feedback received successfully'})

@celery_app.task
def retrain_model():
    # Load the feedback data from the CSV file
    feedback_data = pd.read_csv('feedback.csv', names=['CustomerID', 'StockCode', 'Rating', 'Timestamp'])

    # Merge the feedback data with the original data
    merged_data = pd.concat([data, feedback_data], ignore_index=True)

    # Retrain the model with the merged data
    reader = Reader(rating_scale=(0, merged_data['TotalPrice'].max()))
    dataset = Dataset.load_from_df(merged_data[['CustomerID', 'StockCode', 'TotalPrice']], reader)
    trainset = dataset.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)

    print("Model retrained successfully")

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Set up a periodic task to retrain the model every 24 hours
    sender.add_periodic_task(24 * 60 * 60, retrain_model.s(), name='retrain_model')


if __name__ == '__main__':
    app.run(debug=True)