class Category:
    def __init__(
        self,
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        is_deleted: bool = False,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.is_deleted = is_deleted

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
