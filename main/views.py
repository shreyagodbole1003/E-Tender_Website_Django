from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.http import JsonResponse
import json
import datetime, time
from datetime import date
import pytz
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.models import Group
from django.contrib.auth import login as auth_login
from django import template, forms
from django.utils import timezone
from django.contrib.admin.widgets import AdminSplitDateTime

#Home Page
def home(request):
	# utc=pytz.UTC
	# tenders = Tender.objects.filter(status="Open")                #Tender Entries with Open Status
	# today = datetime.datetime.now()
	# today = utc.localize(today)
	# for tender in tenders:
	# 	if today > tender.duedate:
	# 		tender.status = "Closed"

	tenders = Tender.objects.filter(status="Open")   				#Tender Entries with Open Status
	context = {'tenders': tenders}
	return render(request, 'main/home.html', context)

#Register Page - Seller
@unauthenticated_user
def registerPageseller(request):
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			group = Group.objects.get(name='Seller')
			user.groups.add(group)
			return redirect('home')

	context = {'form': form}
	return render(request, 'main/registerseller.html', context)

#Register Page - Buyer
@unauthenticated_user
def registerPagebuyer(request):
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			group = Group.objects.get(name='Buyer')
			user.groups.add(group)
			messages.success(request, 'Account was created for ' + username)
			return redirect('home')

	context = {'form': form}
	return render(request, 'main/registerbuyer.html', context)

#login Page
@unauthenticated_user
def login1(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('/')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'main/login.html', context)

#logout
def logoutUser(request):
	logout(request)
	return redirect('login')

#Float a new tender
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','Buyer'])
def tenderfloat(request):
	form2 = TenderForm()
	if request.method == 'POST':
		form2 = TenderForm(request.POST)
		if form2.is_valid():
			note1 = form2.save(commit=False)
			note1.user = request.user
			note1.status = "Open"
			note1.save()
			return redirect('/')

	context = {'form':form2}
	return render(request, 'main/tenderfloat.html',context)

# Bid a new quotation
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','Seller'])
def quotation(request):
	form1 = QuotReceivedForm()
	if request.method == 'POST':
		form1 = QuotReceivedForm(request.POST)
		if form1.is_valid():
			note = form1.save(commit=False)
			note.user = request.user
			# print(note)
			note.status = "Open"
			note.save()
			# print(note)
			return redirect('/')

	context = {'form1': form1}
	return render(request, 'main/quotation.html',context)

#Quotations received for the tenders floated by request user
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','Buyer'])
def received(request):
	quotations = Quotation.objects.all()
	context = {'quotations': quotations}
	return render(request, 'main/received.html', context)

#update the status as Awarded for the quotation
@allowed_users(allowed_roles=['admin','Buyer'])
def updateasclosed(request, pk):
	q = Quotation.objects.get(id=pk)
	q.status = "Awarded"
	q.save()
	t=q.tender.id
	print(t)
	quotations = Quotation.objects.filter(tender=t)
	print(quotations)
	for q1 in quotations:
		if q1.id != pk:
			q1.status="Closed"
			q1.save()
	return redirect('received')

#Awarded Quotations
def awarded(request):
	quotations = Quotation.objects.filter(status="Awarded")
	context = {'quotations': quotations}
	return render(request, 'main/awarded.html', context)

# Contact Us page
def contactus(request):
	return render(request, 'main/contactus.html')

# About us Page
def aboutus(request):
	return render(request, 'main/aboutus.html')