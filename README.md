# Mactaquac DAMS
The Mactaquac Digital Asset Management Sysem is a minimal DAMS that indexes media files in a locally mounted directory and serves them in a web application with basic search functionality. 

The file `.env.example` contains all the variables needed for the production `.env` file.

The directory `support_scripts` contains scripts that are now handled through Celery background tasks. However, the directory remains to illustrate how the same tasks can be accomplished by interacting with the API.

