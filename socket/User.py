import dataclasses
import json
import secrets
import sqlite3
import uuid
from typing import ClassVar, Self


@dataclasses.dataclass(order=True)
class User:
	id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
	name: str = ""
	token: str = dataclasses.field(default_factory=lambda: secrets.token_hex(16))
	cur: ClassVar[sqlite3.Cursor] = None
	
	def save(self):
		if User.exists(self.id):
			User.cur.execute("UPDATE users SET name=?,token=? WHERE id=?", (self.name, self.token, str(self.id)))
		else:
			User.cur.execute(
				"INSERT INTO users (id, name, token) VALUES (?, ?, ?);",
				(str(self.id), self.name, self.token),
			)
	
	@staticmethod
	def all():
		return [User(uuid.UUID(id), name, token) for (id, name, token) in User.cur.execute("SELECT * FROM users")]
	@staticmethod
	def exists(id: str | uuid.UUID):
		if isinstance(id, uuid.UUID):
			id = str(id)
		return User.cur.execute("SELECT * FROM users WHERE id = ?", (id,)).fetchone() is not None
	
	@staticmethod
	def get_by_id(id: str | uuid.UUID):
		if isinstance(id, uuid.UUID):
			id = str(id)
		for (id, name, token) in list(User.cur.execute("SELECT * FROM users WHERE id = ?", (id,))):
			u = User(uuid.UUID(id), name, token)
			return u
	
	@staticmethod
	def name_in_user(name: str) -> bool:
		return not (User.cur.execute("SELECT * FROM users WHERE name = ?",
		                             (name,)).fetchone() is None)
	
	@staticmethod
	def name_to_user(name: str) -> Self:
		for (id, name, token) in list(User.cur.execute("SELECT * FROM users WHERE name = ?", (name,))):
			u = User(uuid.UUID(id), name, token)
			return u
		raise Exception(f"Cannot not find user by the name {name} in the database!")
	
	@staticmethod
	def setCursor(cur):
		User.cur = cur
	
	def toJSON(self):
		return json.dumps(self.toJSONDict())
	
	def toJSONDict(self):
		return {
			"id": str(self.id),
			"name": self.name,
			"token": self.token,
		}
	
	@staticmethod
	def fromJSON(data):
		data = json.loads(data)
		return User.fromJSONDict(data)
	
	@staticmethod
	def fromJSONDict(data):
		return User(
			uuid.UUID(data["id"]),
			data["name"],
			data["token"],
		)


def main():
	u = User(
		uuid.uuid4(),
		"Alfredo",
		"secret token",
	)
	
	print(u)
	print(u.toJSON())
	print(User.fromJSON(u.toJSON()))
	print(u == User.fromJSON(u.toJSON()))
	conn = sqlite3.connect(":memory:")
	cur = conn.cursor()
	cur.execute(
		"CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, token TEXT NOT NULL);"
	)
	cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_name ON users (name);")
	
	User.setCursor(cur)
	
	u = User(name="Alfredo")
	print(u)
	u.save()
	u.save()
	u2 = User.get_by_id(u.id)
	print(u2)
	print(u == u2)
	u2 = User.name_to_user("Alfredo")
	print(u2)
	print(u == u2)


if __name__ == "__main__":
	main()
