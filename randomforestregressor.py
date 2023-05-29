import pandas
import numpy
from model_selection import train_test_split
from ensemble import RandomForestRegressor
from metrics import mean_absolute_error, mean_squared_error
from metrics import r2_score
import tree

# Training the Random Forest Regressor model using the training data set.
data_frame = pandas.read_csv("random_forest_data.csv")
X = numpy.array(data_frame["Water Today"])
y = data_frame.drop(["Water Today"], axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
regressor = RandomForestRegressor()
regressor.fit(X_train.reshape(-1, 1), y_train)
y_training_prediction = regressor.predict(X_train.reshape(-1, 1))
y_prediction = regressor.predict(X_test.reshape(-1, 1))
print("Mean absolute error: " + str(mean_absolute_error(y_test, y_prediction)))
print("Mean squared error: " + str(mean_squared_error(y_test, y_prediction)))
print("R2 test score: " + str(r2_score(y_test, y_prediction)))
print("R2 training score: " + str(r2_score(y_train, y_training_prediction)))

tree_regressor = tree.DecisionTreeRegressor()
tree_regressor.fit(X_train.reshape(-1, 1), y_train)
ytrainpredict = tree_regressor.predict(X_train.reshape(-1, 1))
ytestpredict = tree_regressor.predict(X_test.reshape(-1, 1))
print("Mean absolute error: " + str(mean_absolute_error(y_test, ytestpredict)))
print("Mean squared error: " + str(mean_squared_error(y_test, ytestpredict)))
print("R2 test score: " + str(r2_score(y_test, ytestpredict)))
print("R2 training score: " + str(r2_score(y_train, ytrainpredict)))
