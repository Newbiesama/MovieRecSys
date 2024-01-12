import os
from app01 import models

queryset = models.Admin.objects.all()
print(queryset)