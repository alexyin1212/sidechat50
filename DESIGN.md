# Sidechat50

The structure of our CS50 Final Project is influenced by the Finance pset structure. We continued to use Flask and HTML, but incorporated more complex Javascript as well as Ajax and Json. 

Our app keeps the same structure of the register and sign in pages from Finance. In index.html, we display the various posts created by different users. For this page, we used cards from boostrap as well as jinja, looping through all the posts from our Sqlite database and displaying it to the user. Every post has upvote and downvote arrows created by CSS, and when they are clicked our database is updated. We use JQuery to send the variable from our javascript functions into our database.

Our database has a couple tables. We have a table called users with id (primary key), their user_id, and their hashed password. The posts table has an id of the post (primary key), the user_id that created the post (foreign key), the time of the post, and the number of likes. The tables called likes and dislikes store all the liked and disliked posts from the users, which helps us keep track if a user has liked a post or not so that their upvote or downvote status is locked in even when the page is refreshed or the user logs out and back in.

The file post.html has a form that allows users to submit their post into the database. my_posts.html is similar to the index page, however the posts are queried so that they are only from the current use that's logged in. The "Sort By" drop down gives the user the option to sort the posts by "New" or "Top", which is querying recent or how many likes a post has. 

The feedback page allows the users to contact the developers because our website is still in development. The user types in their name, email address, and message into the form, and submitting the form sends an email directly to us (adapted from https://formsubmit.co/). This keeps our email hidden to the user while still giving them access to contact us. 

The profile page allows the user to change their username of password. We created forms to allow user to input their desired new username/password after they click on the respective buttons, and we are then able to receive that data submitted from our server end app.py. We can then access the users database in sql to change the user's password/username.

We also implemented the "karma" system, which records how many total likes a usergets from their posts. This will incentivize users to create more high quality posts that gain lots of attention. The amount of karma can be seen in the user profile. 