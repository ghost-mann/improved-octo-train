# Welcome to hazina crafts flask project 
a flask e-com store dedicated to retail of traditional african artefacts and clothing across the continent

# starting the project 
```
flask run
```

# accessing the database
```
psql -h pg-3e06a654-austin-ace9.e.aivencloud.com -p 15559 -U avnadmin -d defaultdb
```

# adding admins
# Find your user by username
```
flask shell
user = User.query.filter_by(username='your_username').first()
```
# Make them admin
```
user.admin = True
```
# Commit the change
```
db.session.commit()
```
# Verify
```
print(user.admin)
```

# creating and applying migrations 
```
flask db migrate -m "message"
flask db upgrade
```

# manually telling alembic that db is up to date
```
flask db stamp head
```

