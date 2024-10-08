from django.db import models
from django.contrib.auth.models import User
import shortuuid

# Create your models here.
class ChatGroup(models.Model):
    groupName = models.CharField(max_length=128,unique=True,default=shortuuid.uuid)
    isPrivate = models.BooleanField(default=True)
    admin = models.ForeignKey(User,on_delete=models.CASCADE,related_name='adminChat')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='userChat')

    def __str__(self):
        return self.groupName
    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup,related_name='chatMessage',on_delete=models.CASCADE)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author}:{self.body}'
    
    class Meta:
        ordering = ['-created']