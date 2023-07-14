# AN DAILY QUIZ WEBSITE
#### Description:

This is a simple web-based application I created for a quiz club. The club was newly formed and this was actually an idea to improve
our reach and member-participation. We have an Instagram page where we post quiz questions everyday. But we were unable to keep track
of the members' scores. Hence this idea came into existence.

The user can register themselves through the Register page. The user can login using the Login page. The Index page displays the leaderboard
and a button to take the present day's question. There is a "Previous questions" page that displays the questions that was posted the previous days.
The users can not attempt a question more than once per day. The user who logs in as the admin has the facility to add questions.

I have used examples from the previous weeks of CS50 work in this project too. The CSS was the hardest part. The SQL and Python part was easy. I had tried
different versions prior to submitting this. I had tried to implement something that would accept descriptive answers but couldn't
accomplish that properly.

I have learnt a lot about Flask sessions when working on this project. I tried to implement it so that an user cannot attempt
the same question twice in a day (and hence score higher). I had to go through some many StackOverflow pages and the official docs for this.
I also faced some issue with the leaderboard and how the users can be ranked. I initially thought of using the time difference between
when the question was posted to when it was answered, but later I had realised that just arranging the users in the ascending order of
the time when they answered was enough (and also in the descending order of the score).

I also tried to implement it so that in the "Previous Questions page", the user would have to click on a button that says "View answer"
to view the answer. But I couldn't implement that since I was using a for loop for the table and I had to rewrite it.

I also tried to log the user in after they registered. Initially, the user had to register and was redirected to the login page where they had to log in with their credentials, again. I then modified it so that the user goes straight to their homepage after registration.

Its a simple application that I could use as a prototype to propose to my club members the idea. There is definitely still a lot of work to do and it has to be deployed in Heroku in some time.