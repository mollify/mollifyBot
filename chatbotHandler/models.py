from djongo import models


# Create your models here.


class MongoModel(models.Model):
    objects = models.DjongoManager()

    class Meta:
        db_table = "user_history"
