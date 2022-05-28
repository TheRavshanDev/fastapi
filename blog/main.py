from ctypes.wintypes import tagSIZE
from fastapi import FastAPI, Depends, status, Response, HTTPException
from . import schemas, models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from .models import Blog, User
from typing import List
from .hashing import Hash


models.Base.metadata.create_all(engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/blog', status_code=status.HTTP_201_CREATED, tags=["Blog"], response_model=schemas.ShowBlog)
def create(request: schemas.Blog, db: Session=Depends(get_db)):
    blog_data = models.Blog(title=request.title, text=request.text, author=request.author)
    db.add(blog_data)
    db.commit()
    db.refresh(blog_data)
    return blog_data

@app.get("/blog", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowBlog], tags=["Blog"])
def all_blogs(db:Session=Depends(get_db)):
    blogs = db.query(Blog).all()
    return blogs

@app.get("/blog/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ShowBlog, tags=["Blog"])
def blog(id,response:Response, db:Session=Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} is not available")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"detail":f"Blog with id {id} is not available"}
    return blog

@app.delete("/blog/delete/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Blog"])
def destroy(id, db:Session=Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found")
    blog.delete(synchronize_session=False)
    db.commit()
    return 'done'
    
@app.put("/blog/update/{id}/", status_code=status.HTTP_202_ACCEPTED, tags=["Blog"])
def update_blog(id, request: schemas.Blog, db:Session=Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    # if not blog.first():
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with {id} id not found")
    blog.update(request)
    db.commit()
    return 'Successfully'

@app.post("/create/user/", status_code=status.HTTP_201_CREATED, response_model=schemas.ShowUser, tags=["User"])
async def create_user(request: schemas.User, db:Session = Depends(get_db)):
    new_user = User(name=request.name, email=request.email, username=request.username, country=request.country, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return request

@app.get("/user/{id}/", tags=["User"])
async def get_user(id: int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} is notfound!")
    return user