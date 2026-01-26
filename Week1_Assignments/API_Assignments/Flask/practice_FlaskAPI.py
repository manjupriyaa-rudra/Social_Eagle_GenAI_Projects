# Importing flask packages after installation

from flask import Flask

# Creating an operject fr the Flask

app = Flask(__name__)

# Defining flask method (Get, Post, Put, Delete) using route method

@app.route('/')

# Function creation to return a value

def printfn() :
    return("Hi, Welcome to social eagles community!!!")

# Creating main function to call the sub function

if __name__ == '__main__' :
    app.run(debug=True)
