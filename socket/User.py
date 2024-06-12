import dataclasses
import json
import secrets
import uuid


@dataclasses.dataclass(order=True)
class User:
	id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
	name: str = ""
	token: str = dataclasses.field(default_factory=lambda: secrets.token_hex(16))
	
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
	u = User()
	print(u)


if __name__ == "__main__":
	main()
