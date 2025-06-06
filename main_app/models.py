from django.db import models

class count_user(models.Model):
    usercount = models.CharField(max_length=10, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    device = models.CharField(max_length=50, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class Comment(models.Model):
    text = models.TextField(max_length=500)  # Limit to 500 characters for efficiency
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Anonymous comment: {self.text[:50]}"