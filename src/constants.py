import os
FILES_LOCATION = os.path.join(os.path.dirname(__file__), 'files') 


#print the file names at FILES_LOCATION
print(os.listdir(FILES_LOCATION))