# General info

It's simple django blog project for posting reviews and opinions about watched/read titles or whatever I liked.  
 
The main reason for starting this project was to create my own blog with posts about titles that I liked and to practice my skills with django, but over time it grew into something bigger. 

# Features

- [x] List for watched anime or read manga 
- [x] Filtering with title's attributes
- [x] Relationship between titles
- [x] Celery tasks for update or set score for given title from **MyAnimeList** using api
- [x] Blog with posts about watched title
- [x] Creating post system with  order content (still in progress)
- [x] Real time tree comment system with channels 
- [x] REST API for project
- [x] Token authentification
- [x] Real time count views for specific post using redis

# Future ideas and what's in progress

- [ ] Add more content types for post objects (currently only file,text,image and video)
- [ ] Import anime/manga from MyAnimeList/Shiki
- [ ] Improve frond-end part of project

# Used technologies

- Python 3.10
- Django 4.0.1
- Channels 3.0.5
- Celery 5.2.7
- Redis 4.3.4

# Screenshots

<details>
  <summary>List of titles</summary>
<img src="https://user-images.githubusercontent.com/93401048/185488335-189cce5e-e3da-42e4-8be8-7c0c30736900.png" >
 </details>
 <details>
  <summary>Title details</summary>
<img src="https://user-images.githubusercontent.com/93401048/185491952-f86c8999-c3ad-4205-804f-b74d85dfb611.png" >
 </details>
<details>
  <summary>List of posts</summary>
<img src="https://user-images.githubusercontent.com/93401048/185488485-919ec1ca-1091-4718-abd8-8bbb0a2a6485.png" >
 </details>   
<details>
  <summary>Post details</summary>
<img src="https://user-images.githubusercontent.com/93401048/185491844-91c5d728-e102-4a0b-a2a5-721eaff84eca.png" >
 </details> 
<details>
  <summary>Comment tree</summary>
<img src="https://user-images.githubusercontent.com/93401048/185492209-47e0c7f0-3ce3-4f64-aa2e-5075eb6cfeb2.png" >
 </details> 
<details>
  <summary>Edit post</summary>
<img src="https://user-images.githubusercontent.com/93401048/185493959-fa9c1b5f-7478-4d75-b2ed-b47b11b2f019.png" >
 </details> 




