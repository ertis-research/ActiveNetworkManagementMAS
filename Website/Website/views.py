from django.http import HttpResponse
from django.shortcuts import render, redirect
from pymongo import MongoClient
# Create your views here.

def index(request):

    return redirect('/DataMonitoring/Login')

