Fyyur
-----

### Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

### Tech Stack

Our tech stack will include:

* **SQLAlchemy ORM** to be our ORM library of choice
* **PostgreSQL** as our database of choice
* **Python3** and **Flask** as our server language and server framework
* **Flask-Migrate** for creating and running schema migrations
* **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend

### Main Files: Project Structure

  ```sh
  ├── README.md
  ├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                    "python app.py" to run after installing dependences
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── error.log
  ├── forms.py *** Your forms
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ├── static
  │   ├── css 
  │   ├── font
  │   ├── ico
  │   ├── img
  │   └── js
  └── templates
      ├── errors
      ├── forms
      ├── layouts
      └── pages
  ```

Overall:
* Models are located in the `MODELS` section of `app.py`.
* Controllers are also located in `app.py`.
* The web frontend is located in `templates/`, which builds static assets deployed to the web server at `static/`.
* Web forms for creating data are located in `form.py`


Highlight folders:
* `templates/pages` -- Defines the pages that are rendered to the site. These templates render views based on data passed into the template’s view, in the controllers defined in `app.py`. These pages successfully represent the data to the user, and are already defined for you.
* `templates/layouts` -- Defines the layout that a page can be contained in to define footer and header code for a given page.
* `templates/forms` -- Defines the forms used to create new artists, shows, and venues.
* `app.py` -- Defines routes that match the user’s URL, and controllers which handle data and renders views to the user. This file has code that connects to and manipulate the database and render views with data to the user, based on the URL.
* Models in `app.py` -- Defines the data models that set up the database tables.
* `config.py` -- Stores configuration variables and instructions, separate from the main application code. This is where you will need to connect to the database.


### Development Setup

First, [install Flask](http://flask.pocoo.org/docs/1.0/installation/#install-flask) if you haven't already.

  ```
  $ sudo pip3 install Flask
  ```

To start and run the local development server,

1. Initialize and activate a virtualenv:
  ```
  $ cd YOUR_PROJECT_DIRECTORY_PATH/
  $ virtualenv --no-site-packages env
  $ source env/bin/activate
  ```

2. Install the dependencies:
  ```
  $ pip install -r requirements.txt
  ```

3. Run the development server:
  ```
  $ export FLASK_APP=myapp
  $ export FLASK_ENV=development # enables debug mode
  $ python3 app.py
  ```

4. Navigate to Home page [http://localhost:5000](http://localhost:5000)


### Fyyur Home page

<img src="/media/fyyurHomePage.png" width="700" height="400" />

Here is the list of features provided under Fyyur home page
* **Find a Venue/Venues Mega Menu** - Navigates to the **Venue** home page where User can see all the venues that are listed and also search capability is enabled through **Find a Venue** search bar as shown below.

<p float="left">
  <img src="/media/venueHomePage.png" width="300" />
  <img src="/media/searchVenue.png" width="300" height="282"/>
</p>

* **Find an Artist/Artists Mega Menu** - Navigates to the **Artist** home page where User can see all the artist that are listed and also search capability is enabled through **Find an Artist** search bar as shown below.
<p float="left">
<img src="/media/artistHomePage.png" width="320" height="300" />
<img src="/media/searchArtist.png" width="320" height="300" />
</p>

* **Post a Venue** - Navigates to a new form where User can List a **New Venue**.
All the required fields has to be filled before submitting the form. When the form is submitted successfuly a new record is created in the database and the same is listed in the venue home page

<img src="/media/postAVenue.gif" width="700" height="400" />

* **Post an Artist** - Navigates to a new form where User can List a **New Artist**.
All the required fields has to be filled before submitting the form. When the form is submitted successfuly a new record is created in the database and the same is listed in the Artist home page

<img src="/media/postAnArtist.gif" width="700" height="400" />

* **Post a Show** - Navigates to a new form where User can Publicize their **Show**.
All the required fields has to be filled before submitting the form.
Artist ID and Venue ID details can be found in their respective Artist and Venue page.
When the form is submitted successfuly, a new record is created in the database and the same is listed in the Shows home page with their respective Artist name and Venue name along with the show time.

<img src="/media/postAShow.png" width="700" height="400" />

* **Shows Mega Menu** - Navigates to the **Shows** home page where User can see all the shows that are listed.

<img src="/media/ShowsHomePage.png" width="700" height="400" />