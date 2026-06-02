from django.db import models


class Employee(models.Model):
	employee_id = models.CharField(max_length=16, unique=True)
	name = models.CharField(max_length=128)
	role = models.CharField(max_length=64, blank=True)
	department = models.CharField(max_length=64, blank=True)
	email = models.EmailField(blank=True)

	class Meta:
		ordering = ['employee_id']

	def __str__(self):
		return f"{self.employee_id} - {self.name}"
