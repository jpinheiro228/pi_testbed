DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS vm;

CREATE TABLE user (
  username TEXT PRIMARY KEY UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE vm (
  name TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  FOREIGN KEY (owner) REFERENCES user (username)
);

CREATE TABLE usrp (
  id INT PRIMARY KEY,
  in_use_on TEXT,
  FOREIGN KEY (in_use_on) REFERENCES vm (name)
);

CREATE TABLE pi (
  id INT PRIMARY KEY,
  in_use TEXT,
  FOREIGN KEY (in_use_on) REFERENCES user (username)
);