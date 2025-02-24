# Welcome to hazina crafts flask project 

# starting the project 
```
flask run
```

# accessing the database
```
psql -U austin -h localhost -p 5433 -d hazina_db
```

# adding admins 
```
# Find your user by username
user = User.query.filter_by(username='your_username').first()

# Make them admin
user.admin = True

# Commit the change
db.session.commit()

# Verify
print(user.admin)  # Should output True
exit()

```