from django.shortcuts import render

# Create your views here.
import json
from django.conf import settings
import redis
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from redis.commands.json.path import Path
from typing import  Mapping
from rest_framework.views import APIView

redis_instance = redis.StrictRedis(host='127.0.0.1',port=6379, db=0)



class manage_hash_person(APIView):
    def get(self, request):
        # zrange = sorted set , save key 
        result = redis_instance.smembers('person:keys')
        allDB ={}
        for personKey in result:
            persondata = {}
            persondata["name"] = redis_instance.hget(personKey,"name")
            persondata["age"] = redis_instance.hget(personKey,"age")
            allDB[str(personKey.decode('utf-8'))] = persondata
        return Response(allDB,status=200)
    def post(self, request):
        request_data = json.loads(request.body)
        name = request_data['name']
        age = request_data['age']
        person_key = redis_instance.scard('person:keys') + 1
        redis_instance.hset(person_key,"name",name)
        redis_instance.hset(person_key,"age",age)
        redis_instance.sadd('person:keys',person_key)
        return Response(request_data,status=200)

class manage_hash_person_detail(APIView):
    def get(self,request,pk):
        print(redis_instance.sismember('person:keys',pk))
        if redis_instance.sismember('person:keys',pk):
            persondata ={}
            persondata["name"] = redis_instance.hget(pk,"name")
            persondata["age"] = redis_instance.hget(pk,"age")
            return Response(persondata, status=200)
        else:
            return Response(status=404)
    def put(self,request,pk):
        if redis_instance.sismember('person:keys',pk):
            request_data = json.loads(request.body)
            name = request_data['name']
            age = request_data['age']
            redis_instance.hset(pk,"name",name)
            redis_instance.hset(pk,"age",age)
            return Response(request_data, status=200)
        else:
            return Response(status=400)
    def delete(self,request,pk):
        if redis_instance.sismember('person:keys',pk):
            redis_instance.hdel(pk,"name")
            redis_instance.hdel(pk,"age")
            return Response(status=200)
        else:
            return Response(status=400)


@api_view(['GET','POST'])
def manage_json(request,*args,**kwargs):
    if request.method == 'GET':
        result = redis_instance.zrange('person',0,-1)
        return Response(result,status=200)
    elif request.method == 'POST':
        request_data = json.loads(request.body)
        count = redis_instance.zcard('person')
        redis_instance.zadd('person',Mapping[request_data['name'],count])
        result = redis_instance.zrange('person',0,-1)
        return Response(result,status=200)

@api_view(['GET','PUT','DELETE'])
def manage_json_detail(request, pk, *args,**kwargs):
    if request.method == 'GET':
        result = redis_instance.sismember('person:keys',pk)
        return Response(result, status=200)
    elif request.method == 'PUT':
        request_data = json.loads(request.body)
        result = redis_instance.zrange('person',0,-1)
        redis_instance.zremrangebyscore(pk)
        count = redis_instance.zcard('person')
        redis_instance.zadd('person',Mapping[request_data['name'],count])
        result = redis_instance.zrange('person',0,-1)
        return Response(result, status=200)

@api_view(['GET','POST'])
def manage_items(request,*args,**kwargs):
    if request.method =='GET':
        items={}
        count=0
        for key in redis_instance.keys("*"):
            items[key.decode("utf-8")] = redis_instance.get(key)
            count+=1
        response = {
            'count':count,
            'msg':f"Found {count} itmes.",
            'items':items
        }
        return Response(response, status=200)
    elif request.method == 'POST':
        item =json.loads(request.body)
        key=list(item)[0]
        value = item[key]
        redis_instance.set(key,value)
        response ={
            'msg':f"{key} successfully set to {value}"
        }
        return Response(response, 201)

@api_view(['GET','PUT','DELETE'])
def manage_item(request, * args, **kwargs):
    if request.method =='GET':
        if kwargs['key']:
            value = redis_instance.get(kwargs['key'])
            if value:
                response ={
                    'key':kwargs['key'],
                    'value':value,
                    'msg':'success',
                }
                return Response(response, status=200)
            else:
                response ={
                    'key':kwargs['key'],
                    'value':None,
                    'msg':'Not found'
                }
                return Response(response, status=404)
    elif request.method=='PUT':
        if kwargs['key']:
            request_data = json.loads(request.body)
            new_value = request_data['new_value']
            value = redis_instance.get(kwargs['key'])
            if value:
                redis_instance.set(kwargs['key'], new_value)
                response ={
                    'key':kwargs['key'],
                    'value':value,
                    'msg':f"Successfully update {kwargs['key']}"
                }
                return Response(response, status=200)
            else:
                response ={
                    'key':kwargs['key'],
                    'value':None,
                    'msg':'Not found',
                }
                return Response(response, status=404)
    elif request.method == 'DELETE':
        if kwargs['key']:
            result = redis_instance.delete(kwargs['key'])
            if 1 == result:
                response ={
                    'msg':f"{kwargs['key']} successfully deleted."
                }
                return Response(response, status=404)
            else:
                response ={
                    'key':kwargs['key'],
                    'valeu':None,
                    'msg':'Not found'
                }
                return Response(response,status=404)