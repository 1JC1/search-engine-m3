Hi! Here you will find how to use our software.

How to run the code that creates the index:
The code that runs the index is in the index.py file that starts in the indexer() function. 
However, to run the index, you have to run main.py and set the createIndex to True (it is set to False by default). 
So the user will call "python3 main.py" in the terminal and our code will run.


How to start the search interface:
The search interface can be used through a virtual environment with flask.
First, you will have to create a virtual environment if you do not already have one.
This can be done by calling "python3 -m venv venv" in the terminal. Next, you will activiate 
the environment by calling ". venv/bin/activate". If you have not already downloaded
Flask, you will need to call "pip install Flask", otherwise you're ready to start 
running the program.
Once you have set up your virtual environment, in order to run the search interface 
you will need to call "flask --app web_try.py run". A GUI should appear with a 
text bar and a search button.


How to perform a simple query:
By utilizing the index and search interface together, the user will be able to perform
simple search queries. Please type your desired query search into the text bar and
click the "Search" button. A list of the 10 most relevant URLs will appear on screen.
