import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split


# Step 1: Data Collection and Preprocessing

# Load the Online Retail dataset
data = pd.read_csv('online_retail.csv', encoding='ISO-8859-1')

# Remove rows with missing values
data = data.dropna()

# Remove rows with negative quantities or prices
data = data[(data['Quantity'] > 0) & (data['UnitPrice'] > 0)]

# Encode categorical variables
label_encoder = LabelEncoder()
data['Country'] = label_encoder.fit_transform(data['Country'])

# Create a new column 'TotalPrice' by multiplying Quantity and UnitPrice
data['TotalPrice'] = data['Quantity'] * data['UnitPrice']

# Select relevant columns for recommendation
columns_to_keep = ['CustomerID', 'StockCode', 'Description', 'Country', 'TotalPrice']
data = data[columns_to_keep]

# Split the data into features (X) and target (y)
X = data.drop(['CustomerID', 'StockCode'], axis=1)
y = data['StockCode']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Data preprocessing completed.")
print("Training data shape:", X_train.shape)
print("Testing data shape:", X_test.shape)

# Step 2: Model Development

# Load the preprocessed data into a Surprise Dataset
reader = Reader(rating_scale=(0, data['TotalPrice'].max()))
dataset = Dataset.load_from_df(data[['CustomerID', 'StockCode', 'TotalPrice']], reader)

# Split the dataset into training and testing sets
trainset, testset = train_test_split(dataset, test_size=0.2, random_state=42)

# Create an instance of the SVD algorithm
algo = SVD()

# Train the model
algo.fit(trainset)

# Evaluate the model
predictions = algo.test(testset)

# Compute evaluation metrics

rmse = accuracy.rmse(predictions)
mae = accuracy.mae(predictions)

print("Model training completed.")
print("RMSE:", rmse)
print("MAE:", mae)