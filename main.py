from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import dbhandler as db 
import re
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

#from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()
db.createDBIfNotExists()

#db.createDB()



#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"]
#)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class Item(BaseModel):
        name: str = "My Task"
        desc: str = "This is my task that I have to do"
        done: bool = False

db.createDBIfNotExists

items = []

def checkIfUserLoggedIn(token: str):

    if not token:
        return False
    
    userData = db.getUserInfoFromToken(token)
    
    if userData:
        return userData
    
    return False

@app.get("/logout")
def logout():
  
  response = RedirectResponse('/', status_code= 302)
  response.delete_cookie(key='token')

  return response

@app.get("/signup",response_class = HTMLResponse)
def root(request: Request):

    if not checkIfUserLoggedIn(request.cookies.get("token")):
        try:
            return templates.TemplateResponse(
                request=request, name="signup.html", context={}
            )
        except:
            return templates.TemplateResponse(
                request=request, name="error.html", context={}
            )
    
    try:
        return RedirectResponse(url='/', status_code=302)
    except:
        return templates.TemplateResponse(
            request=request, name="error.html", context={}
        )

@app.get("/",response_class = HTMLResponse)
def root(request: Request):
    user = checkIfUserLoggedIn(request.cookies.get("token"))

    if not user:
        try:
            return templates.TemplateResponse(
                request=request, name="login.html", context={}
            )
        except:
            return templates.TemplateResponse(
                request=request, name="error.html", context={}
            )

    try:
        items = db.getItems(request.cookies.get("token"), 0, 5, 0)

        return RedirectResponse(url='/1', status_code=302)
    except:
        return templates.TemplateResponse(
            request=request, name="error.html", context={}
        )


@app.get("/{page}",response_class = HTMLResponse)
def root(request: Request, page: int):
    user = checkIfUserLoggedIn(request.cookies.get("token"))

    if not user:
        try:
            return templates.TemplateResponse(
                request=request, name="login.html", context={}
            )
        except:
            return templates.TemplateResponse(
                request=request, name="error.html", context={}
            )

    try:
        items = db.getItems(request.cookies.get("token"), 0, 5, (page * 5) - 5)

        return templates.TemplateResponse(
            request=request, name="index.html", context={"user": user, "items": items}
        )
    except:
        return templates.TemplateResponse(
            request=request, name="error.html", context={}
        )
    
usernameRegex = r'''[\s_!"£$%^&*()\[\]:@~<>?|\\'#,./]'''
passwordRegex = r'''[\s_!"£$%^&*()\[\]:@~<>?|\\'#,./]'''
numberPasswordRegex = '''[0-9]'''

@app.post("/create-user")
async def userCreate(request: Request):
    json = await request.json()

    username = json["username"]
    password = json["password"]
    conpassword = json["conpassword"]

    usernameErrors = []
    passwordErrors = []
    conpasswordErrors = []

    errors = []

    if len(username) < 3 or len(username) > 20:
        errors.append("Username has to be 3-20 chars")

    if len(re.findall(usernameRegex, username)):
        errors.append("Username can't have special chars")
    
    if len(password) < 8 or len(password) > 255:
        errors.append("Password has to be 8-255 chars")
    
    if not len(re.findall(passwordRegex, password)):
        errors.append("Password must have at least 1 special char and a number")

    if not len(re.findall(numberPasswordRegex, password)):
        errors.append("Password must have at least 1 special char and a number")
    
    if conpassword != password:
        errors.append("Passwords must match")

    if db.checkIfUsernameTaken(username):
        errors.append("Username taken")
    
    if len(errors) != 0:
        raise HTTPException(status_code=400, detail=errors)
    
    token = db.createUser(username, password)
    
    content = {"message": "User made"}
    response = JSONResponse(content=content)
    response.set_cookie(key="token", value=token)

    return response

@app.post("/login-user")
async def loginUser(request: Request):
    json = await request.json()

    username = json["username"]
    password = json["password"]

    errors = []

    if not db.passwordMatches(password, username):
        errors.append("Either password or username is wrong")
    
    if len(errors) != 0:
        raise HTTPException(status_code=400, detail=errors)
    
    token = db.loginUser(username)
    
    content = {"message": "User logged in"}
    response = JSONResponse(content=content)
    response.set_cookie(key="token", value=token)

    return response


@app.post("/create-item")
async def itemCreate(request: Request):

    if checkIfUserLoggedIn(request.cookies.get("token")):
        json = await request.json()

        errors = []

        name = json["name"]
        if name.isspace() or len(name) == 0:
            name = Item().name

        desc = json["desc"] 
        if desc.isspace() or len(desc) == 0:
            desc = Item().desc

        if len(name) > 50:
            errors.append("Title has to shorter than 50 chars")

        if len(desc) > 255:
            errors.append("Description has to be shorter than 255 chars")

        if len(errors) != 0:
            raise HTTPException(status_code=400, detail=errors)

        db.createTask(request.cookies.get("token"), name, desc)

        raise HTTPException(status_code=200, detail={"name": name, "desc": desc})

    

    #items.append(Item)

@app.post("/get-info/{id}")
def itemGet(id: int):

    if id < len(items):
        item = items[id]
        return item
        
    raise HTTPException(status_code=404, detail='Not found')
    

@app.post("/get-bulk/")
async def itemGet(request: Request):
    if checkIfUserLoggedIn(request.cookies.get("token")):

        json = await request.json()

        errors = []

        done = int(json["done"])
        offset = int(json["offset"])
        amount = int(json["amount"])

        if offset < 0:
            HTTPException(status_code=400, detail="Bad request")

        if amount < 0 :
            HTTPException(status_code=400, detail="Bad request")   

        if amount > 10:
            HTTPException(status_code=400, detail="Bad request")   

        items = db.getItems(request.cookies.get("token"), done, amount, offset)

        raise HTTPException(status_code=200, detail=items)
    
client = OpenAI(
    api_key=os.environ.get("GPT_KEY"),  # This is the default and can be omitted
)
'''
assistant = client.beta.assistants.create(
    name="Description writer",
    instructions="You are made to generate a to-do list description when given a prompt. Return a single exclamation mark '!' when you are unable to",
    #tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106-preview"
)`
'''

def generateDesc(title):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Create a short description of a task (with less than 255 characters) with the prompt '{title}', If you are unable to create a good description with the prompt, just respond with an exclamation mark '!'",
            }
        ],
        model="gpt-4o",
    )
    if chat_completion.choices[0].message.content == "!":
        return False

    return chat_completion.choices[0].message.content

    
@app.post("/item-desc-suggestion")
async def aiSuggestion(request: Request):
    if checkIfUserLoggedIn(request.cookies.get("token")):
        json = await request.json()
        desc = generateDesc(json["name"])

        if desc == False:
            raise HTTPException(status_code=400, detail="Bad Request")

        raise HTTPException(status_code=200, detail={"desc": desc})
    
@app.get("/delete-item/{id}/{page}")
async def deleteItem(request: Request, id: int, page: int):
    if checkIfUserLoggedIn(request.cookies.get("token")):
        
        if db.deleteItem(request.cookies.get("token"), id):
            response = RedirectResponse(f'/{page}', status_code= 302)
            return response
        
        response = RedirectResponse(f'/{page}', status_code= 400)
        return response
