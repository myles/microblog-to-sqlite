# microblog-to-sqlite

Save data from [Micro.blog](https://micro.blog/) to a SQLite database.

## Install

```console
foo@bar:~$ pip install -e git+https://github.com/myles/microblog-to-sqlite.git#egg=mastodon-to-sqlite
```

## Authentication

First you will need to create an application at Micro.blog.

```console
foo@bar:~$ microblog-to-sqlite auth
Micro.blog username: xxx

Create a new application here: https://micro.blog/account/apps
Then navigate to newly created application and paste in the following:

Your application token: xxx
```

## Retrieving Micro.blog posts

The `posts` command will retrieve all the details about your Micro.blog 
posts.

```console
foo@bar:~$ microblog-to-sqlite posts microblog.db
```
