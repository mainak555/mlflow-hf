# MySQL Connection SSL configuration
import os

ca_path = "/home/user/app/ca.pem"
with open(ca_path, "w") as f:
    f.write(os.environ["MLFLOW_MYSQL_CA"])

os.environ['MLFLOW_MYSQL_CONN'] = f"{os.environ['MLFLOW_MYSQL_CONN']}?ssl={{\"ca\":\"{ca_path}\"}}"
