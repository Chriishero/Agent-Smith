from pydantic import BaseModel, Field
import resource


class LimitGuard(BaseModel):
    resource: int
    max_memory_mb: int = Field(ge=1)

    def install(self) -> None:
        max_memory_b = int(self.max_memory_mb * 1e6)
        resource.setrlimit(self.resource, (max_memory_b, max_memory_b))
