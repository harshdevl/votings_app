from django.db import models
from django.contrib.auth.models import User

class UserInfo(models.Model):
    profile_pic = models.ImageField(default = "profilepic.png",blank=True,null=True)
    name = models.OneToOneField(User,on_delete = models.CASCADE,related_name="name")
    
    def __str__(self):
       return self.name.username

class UserFollowing(models.Model):
    user = models.ForeignKey(User ,on_delete=models.CASCADE, related_name = 'user', blank=True, null=True)
    following = models.ForeignKey(User ,on_delete=models.CASCADE, related_name = 'following', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
       return self.following.username 


class QuestionTable(models.Model):

    question_text = models.CharField(max_length = 300 ,null = False )
    pub_date = models.DateTimeField(auto_now_add=True)
    groupcode = models.CharField(max_length = 15,null=True,blank=True)    
    op1 = models.CharField(max_length = 100)
    op2 = models.CharField(max_length = 100)
    op3 = models.CharField(max_length = 100 ,null = True,blank=True)
    op4 = models.CharField(max_length = 100 ,null = True,blank=True)
    auther = models.ForeignKey(User,on_delete = models.CASCADE)
    def __str__(self):
        return self.auther.username
