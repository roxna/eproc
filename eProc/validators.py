import os
from django.core.exceptions import ValidationError

# Validate file extensions of uploaded file
# See: http://stackoverflow.com/questions/3648421/only-accept-a-certain-file-type-in-filefield-server-side
def validate_file_extension(value):    
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')