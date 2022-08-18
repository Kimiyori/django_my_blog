# General info

 It's simple django project for posting reviews and opinions about watched/read titles or whatever I liked.  
 
The main reason for starting this project was to create my own blog with posts about titles that I liked and to practice my skills with django, but over time it grew into something bigger.
# Features

- [x] List for watched anime or read manga 
- [x] Celery tasks for update or set score for given title from MyAnimeList using api
- [x] Blog with posts about watched title
- [x] Creating post system
- [x] Real time tree comment system with channels 
- [x] REST API for project
- [x] Token authentification
- [x] Real time count views for specific post using redis

# Future ideas and in process

- [ ] Add more content types for post objects
- [ ] Import anime/manga from MyAnimeList/Shiki

# Technologies

- Python 3.10
- Django 4.0.1
- Channels 3.0.5
- Celery 5.2.7
- Redis 4.3.4
