# AI-Powered Recommendation Engine

This project implements an AI-powered recommendation engine for an e-commerce platform. It provides personalized product recommendations to users based on their browsing and purchase history, as well as other relevant data.

## Project Structure

The project consists of the following files:

- `app.py`: The main Flask application file that defines the API endpoints and handles the recommendation logic.
- `dataset.py`: The file containing the preprocessed data used for training the recommendation model.
- `requirements.txt`: The file listing all the required dependencies for the project.
- `README.md`: This file providing an overview of the project and setup instructions.

## Setup Instructions

1. Clone the project repository:
   ```
   git clone https://github.com/arpan-iiitp/recommendation-engine.git
   ```

2. Navigate to the project directory:
   ```
   cd recommendation-engine
   ```

3. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate
   ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Make sure Redis is installed and running on your local machine. If not, you can install it by following the instructions for your operating system.

6. Start the Redis server:
   ```
   redis-server
   ```

7. Open a new terminal window and start a Celery worker:
   ```
   celery -A app.celery_app worker --loglevel=info
   ```

8. Open another terminal window and run the Flask application:
   ```
   python app.py
   ```

9. The API will be accessible at `http://localhost:5000`.

## API Endpoints

- `/recommend` (POST): Generates personalized product recommendations for a user.
  - Request payload: `{ "user_id": "12345" }`
  - Response: `{ "user_id": "12345", "recommendations": [{ "item_id": "abc123", "predicted_rating": 4.5 }, ...] }`

- `/feedback` (POST): Collects user feedback for a recommended item.
  - Request payload: `{ "user_id": "12345", "item_id": "abc123", "rating": 4 }`
  - Response: `{ "message": "Feedback received successfully" }`

## Configuration

- The Redis server is expected to be running on `localhost` with the default port `6379`. If your Redis server is configured differently, update the `redis_client` and `celery_app` instances in `app.py` accordingly.

- The feedback data is stored in a CSV file named `feedback.csv`. You can modify the file path in the `/feedback` endpoint in `app.py` if needed.

- The recommendation model is retrained every 24 hours using the Celery periodic task. You can adjust the retraining frequency by modifying the `setup_periodic_tasks` function in `app.py`.

## Additional Notes

- The project assumes that the preprocessed data is stored in `dataset.py`. Make sure to update the file with your own preprocessed data.

- The recommendation model used in this project is the SVD algorithm from the Surprise library. You can experiment with different algorithms and hyperparameters to improve the recommendation quality.

- For production deployment, consider using a more robust web server like Gunicorn or uWSGI instead of the built-in Flask development server.

If you have any further questions or need assistance, please feel free to reach out!
