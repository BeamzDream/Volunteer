DESIGN
The website has two parts in general: one for volunteers and one for charity organizations. Using different decorators and session IDs,
the pages load different by changing tabs or actually being directed to different html pages.
By utilizing two different databases for volunteers and charities, the website is able to access information that are submitted from
both sides to achieve certain effect. For example, in volunteers database, there are profile, experience as well as volunteering time
tables that each entity uploads their data to. In the case of history, organizations add data according to the volunteer’s name
corresponding to a certain ID in volunteer database and that is accessed to generate a list for students to check their volunteering
history and see the details.
Another is image submission for profile picture through defining the path and storing the path in the database and not the image for
quicker access to the images and displayed well using CSS and html styles.
The website uses Google Maps API to store the address of an individual as well as that of an organization. The main purpose was to
be able to search also through distance by doing calculations that allow calculating distance from geolocation points. But, that is
left as comments as checking through each and every location just for distance can take time and will not be a good design. Other
searches such as category and name of organization are fully functioning.
With around 21 html pages, 2 databases with 4 tables in total as well as application and helper function, this website is able to
utilize big amount of data and display in a user friendly way.
FUNCTIONS AND GOALS EARLIER IN THE SEMESTER
Sign up, sign in, log out or delete pages for students willing to volunteer
Student database, accessible only through password and changed using account confirmation through email, containing details important
for registering such as name, contact, image and more
Number of hours worked as well as recommendations that can be uploaded into database by organizations and keep track of those
Organizations search page using categories or location (through integration with Google maps)
Gmail integration for communication between volunteers and volunteer organization
Multiple HTMLs beautifully designed with CSS and JavaScript containing student profiles, organization profiles and more
