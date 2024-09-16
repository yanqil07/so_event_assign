
# Prep
Download the Course Data and Student Course Data from August Systems
Remove the extra header on the Course Data and Student Course Data files

# so_event_assign
Step 0. Modify assignevents.py so that the columns match those in the course data and Student course data files

Step 1. Read Course Data and Student Course Data to generate a database of filtered preferred events.

run assignevents.py <Student Data> <Course Data>

Step 2. Use the filtered events database to form teams based on event preference

Step 2b. Create a csv file with candidate team

Step 3. Check candidate teams for conflicts
run assignevents.py <Student Data> <Course Data> <Candidate Team>

